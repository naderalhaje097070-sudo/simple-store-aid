-- ============================================================
-- Mongezz V2 — Pre-Pilot hardening
-- H3: version-control platform_admin_audit_log (idempotent / prod-safe)
-- H2: unify close_day.customer_debts with the app's debt definition
-- H4: block debt collection on courier orders still holding custody
-- No feature changes. No RLS weakening. No service_role in client.
-- ============================================================

-- ---------- H3: platform_admin_audit_log ----------
-- The table is referenced by an earlier migration and by _log_platform_admin_action,
-- but its CREATE TABLE was only ever applied directly in production (outside version
-- control). Recreate it idempotently so a fresh environment is reproducible.
CREATE TABLE IF NOT EXISTS public.platform_admin_audit_log (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action     text NOT NULL,
  details    jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

GRANT SELECT ON public.platform_admin_audit_log TO authenticated;
GRANT ALL    ON public.platform_admin_audit_log TO service_role;

ALTER TABLE public.platform_admin_audit_log ENABLE ROW LEVEL SECURITY;

-- Read-only for platform admins. No anon, no public. No write policy at all:
-- inserts happen only through the SECURITY DEFINER function _log_platform_admin_action.
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename  = 'platform_admin_audit_log'
      AND policyname = 'platform admins read audit log'
  ) THEN
    EXECUTE 'CREATE POLICY "platform admins read audit log" ON public.platform_admin_audit_log FOR SELECT TO authenticated USING (public.is_platform_admin())';
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pa_audit_created_at ON public.platform_admin_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pa_audit_user       ON public.platform_admin_audit_log (user_id, created_at DESC);


-- ---------- H2: close_day.customer_debts unified with the app ----------
-- Only the customer_debts query changes; every other snapshot field is untouched.
-- Definition (matches src/routes/_authenticated/app.tsx):
--   direct / settled / legacy        : total - paid
--   courier delivered_none           : total - paid                       (custody = 0)
--   courier delivered_partial        : total - paid - collected_by_courier
--   courier delivered_full / pending / returned / null : 0
-- collected_by_courier stays in unsettled_custody and is NEVER counted as customer
-- debt, so customer_debts and unsettled_custody remain disjoint (no double count).
CREATE OR REPLACE FUNCTION public.close_day(p_note text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_today date := (now() AT TIME ZONE 'UTC')::date;
  v_sales numeric(12,2) := 0;
  v_collected numeric(12,2) := 0;
  v_expenses numeric(12,2) := 0;
  v_customer_debts numeric(12,2) := 0;
  v_unsettled_custody numeric(12,2) := 0;
  v_realized_profit numeric(12,2) := 0;
BEGIN
  PERFORM public._assert_owner(v_tenant);

  SELECT COALESCE(SUM(total), 0) INTO v_sales
    FROM public.orders WHERE tenant_id = v_tenant AND created_at::date = v_today;

  -- Shop-collected cash = payments only (sale + debt_collection + courier_settlement).
  SELECT COALESCE(SUM(amount), 0) INTO v_collected
    FROM public.payments WHERE tenant_id = v_tenant AND created_at::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_expenses
    FROM public.expenses WHERE tenant_id = v_tenant AND created_at::date = v_today;

  -- Customer debt (outstanding, all-time snapshot) — unified with the app definition.
  SELECT COALESCE(SUM(
    CASE
      WHEN delivery = 'direct' OR courier_id IS NULL
        THEN GREATEST(total - paid, 0)
      WHEN courier_state = 'delivered_none'
        THEN GREATEST(total - paid, 0)
      WHEN courier_state = 'delivered_partial'
        THEN GREATEST(total - paid - collected_by_courier, 0)
      ELSE 0
    END
  ), 0) INTO v_customer_debts
  FROM public.orders
  WHERE tenant_id = v_tenant
    AND (
      ((delivery = 'direct' OR courier_id IS NULL) AND status IN ('partial','debt'))
      OR (delivery = 'courier' AND courier_state IN ('delivered_none','delivered_partial'))
    );

  -- Unsettled courier custody (money physically with couriers, not yet in the shop box).
  SELECT COALESCE(SUM(collected_by_courier), 0) INTO v_unsettled_custody
    FROM public.orders
    WHERE tenant_id = v_tenant
      AND delivery = 'courier'
      AND courier_id IS NOT NULL;

  SELECT COALESCE(SUM(
    (oi.unit_price - oi.unit_cost) * oi.qty *
    CASE WHEN o.total > 0 THEN LEAST(o.paid / o.total, 1) ELSE 0 END
  ), 0) INTO v_realized_profit
  FROM public.orders o
  JOIN public.order_items oi ON oi.order_id = o.id
  WHERE o.tenant_id = v_tenant AND o.created_at::date = v_today;

  INSERT INTO public.day_closes(
    tenant_id, closed_for, sales, collected, expenses,
    realized_profit, customer_debts, unsettled_custody, note, created_by
  ) VALUES (
    v_tenant, v_today, v_sales, v_collected, v_expenses,
    v_realized_profit, v_customer_debts, v_unsettled_custody, p_note, v_uid
  )
  ON CONFLICT (tenant_id, closed_for) DO UPDATE SET
    sales = EXCLUDED.sales,
    collected = EXCLUDED.collected,
    expenses = EXCLUDED.expenses,
    realized_profit = EXCLUDED.realized_profit,
    customer_debts = EXCLUDED.customer_debts,
    unsettled_custody = EXCLUDED.unsettled_custody,
    note = EXCLUDED.note;

  RETURN jsonb_build_object(
    'success', true,
    'sales', v_sales,
    'collected', v_collected,
    'expenses', v_expenses,
    'realized_profit', v_realized_profit,
    'customer_debts', v_customer_debts,
    'unsettled_custody', v_unsettled_custody
  );
END $$;

REVOKE EXECUTE ON FUNCTION public.close_day(text) FROM PUBLIC, anon;
GRANT  EXECUTE ON FUNCTION public.close_day(text) TO authenticated;


-- ---------- H4: collect_order_debt guard for courier custody ----------
-- A courier order must be settled (settle_courier_orders) before its remaining amount
-- can be collected at the shop. Otherwise money held by the courier (collected_by_courier)
-- could be double counted against a separate shop payment.
-- Allowed: direct orders, settled orders (become delivery='direct'), and courier orders
-- with courier_state='delivered_none' AND no custody (collected_by_courier = 0).
CREATE OR REPLACE FUNCTION public.collect_order_debt(
  p_order_id uuid,
  p_amount   numeric,
  p_method   payment_method
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_uid uuid := auth.uid();
  v_order public.orders%ROWTYPE;
  v_remaining numeric(12,2);
  v_new_paid numeric(12,2);
  v_status order_status;
BEGIN
  IF p_amount IS NULL OR p_amount <= 0 THEN
    RAISE EXCEPTION 'invalid_amount';
  END IF;
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  -- Do not let shop debt collection mix with money still in courier custody.
  IF v_order.delivery = 'courier' THEN
    IF COALESCE(v_order.collected_by_courier, 0) > 0
       OR v_order.courier_state IN ('pending','delivered_partial','delivered_full') THEN
      RAISE EXCEPTION 'settle_courier_first';
    END IF;
  END IF;

  v_remaining := v_order.total - v_order.paid;
  IF p_amount > v_remaining THEN
    RAISE EXCEPTION 'amount_exceeds_remaining';
  END IF;
  v_new_paid := v_order.paid + p_amount;
  v_status := CASE
    WHEN v_new_paid >= v_order.total THEN 'paid'::order_status
    WHEN v_new_paid > 0 THEN 'partial'::order_status
    ELSE 'debt'::order_status
  END;
  UPDATE public.orders SET paid = v_new_paid, status = v_status WHERE id = p_order_id;
  INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, created_by)
    VALUES (v_order.tenant_id, 'debt_collection', p_method, p_amount, p_order_id, v_order.customer_id, v_uid);

  RETURN jsonb_build_object('success', true, 'new_paid', v_new_paid, 'status', v_status);
END $$;

REVOKE EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, payment_method) FROM PUBLIC, anon;
GRANT  EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, payment_method) TO authenticated;
