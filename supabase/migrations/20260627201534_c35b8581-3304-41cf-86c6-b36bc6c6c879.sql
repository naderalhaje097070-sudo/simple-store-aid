-- ============================================================
-- Mongezz V2 — Comprehensive Hardening Migration (Phases 1-3)
-- ============================================================

-- ----- 1.2 Bootstrap platform_admin_audit_log (idempotent) -----
CREATE TABLE IF NOT EXISTS public.platform_admin_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  action text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
REVOKE ALL ON public.platform_admin_audit_log FROM PUBLIC;
REVOKE ALL ON public.platform_admin_audit_log FROM anon;
GRANT SELECT ON public.platform_admin_audit_log TO authenticated;
GRANT ALL    ON public.platform_admin_audit_log TO service_role;
ALTER TABLE public.platform_admin_audit_log ENABLE ROW LEVEL SECURITY;

-- ----- 1.1 tenants.timezone + helpers -----
ALTER TABLE public.tenants
  ADD COLUMN IF NOT EXISTS timezone text NOT NULL DEFAULT 'Africa/Tripoli';

CREATE OR REPLACE FUNCTION public.current_tenant_timezone()
RETURNS text LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT COALESCE(
    (SELECT t.timezone FROM public.tenants t WHERE t.id = public.current_tenant_id()),
    'Africa/Tripoli'
  );
$$;
REVOKE ALL ON FUNCTION public.current_tenant_timezone() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.current_tenant_timezone() FROM anon;
GRANT EXECUTE ON FUNCTION public.current_tenant_timezone() TO authenticated;

CREATE OR REPLACE FUNCTION public.tenant_today(_tid uuid)
RETURNS date LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT (now() AT TIME ZONE COALESCE(
    (SELECT timezone FROM public.tenants WHERE id = _tid),
    'Africa/Tripoli'
  ))::date;
$$;
REVOKE ALL ON FUNCTION public.tenant_today(uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.tenant_today(uuid) FROM anon;
GRANT EXECUTE ON FUNCTION public.tenant_today(uuid) TO authenticated;

-- ----- 3.3 Per-tenant invoice numbering -----
ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS tenant_number int;

CREATE TABLE IF NOT EXISTS public.tenant_counters (
  tenant_id uuid PRIMARY KEY REFERENCES public.tenants(id) ON DELETE CASCADE,
  last_order_number int NOT NULL DEFAULT 0
);
REVOKE ALL ON public.tenant_counters FROM PUBLIC;
REVOKE ALL ON public.tenant_counters FROM anon;
REVOKE ALL ON public.tenant_counters FROM authenticated;
GRANT ALL ON public.tenant_counters TO service_role;
ALTER TABLE public.tenant_counters ENABLE ROW LEVEL SECURITY;
-- accessed only via SECURITY DEFINER RPCs; no end-user policies needed

CREATE OR REPLACE FUNCTION public.next_order_number(_tid uuid)
RETURNS int LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE v_n int;
BEGIN
  INSERT INTO public.tenant_counters(tenant_id, last_order_number)
    VALUES (_tid, 1)
  ON CONFLICT (tenant_id) DO UPDATE
    SET last_order_number = public.tenant_counters.last_order_number + 1
  RETURNING last_order_number INTO v_n;
  RETURN v_n;
END $$;
REVOKE ALL ON FUNCTION public.next_order_number(uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.next_order_number(uuid) FROM anon;
REVOKE ALL ON FUNCTION public.next_order_number(uuid) FROM authenticated;

-- Backfill historical orders + counters per tenant
DO $$
DECLARE v_tid uuid; v_max int;
BEGIN
  FOR v_tid IN SELECT DISTINCT tenant_id FROM public.orders WHERE tenant_id IS NOT NULL LOOP
    WITH ranked AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, number) AS n
      FROM public.orders WHERE tenant_id = v_tid
    )
    UPDATE public.orders o SET tenant_number = r.n
      FROM ranked r WHERE o.id = r.id AND o.tenant_number IS NULL;
    SELECT COALESCE(MAX(tenant_number), 0) INTO v_max
      FROM public.orders WHERE tenant_id = v_tid;
    INSERT INTO public.tenant_counters(tenant_id, last_order_number)
      VALUES (v_tid, v_max)
    ON CONFLICT (tenant_id) DO UPDATE
      SET last_order_number = GREATEST(public.tenant_counters.last_order_number, EXCLUDED.last_order_number);
  END LOOP;
END $$;

-- ----- 3.4 financial_audit_log + triggers -----
CREATE TABLE IF NOT EXISTS public.financial_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  user_id uuid,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id uuid,
  before jsonb,
  after jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
REVOKE ALL ON public.financial_audit_log FROM PUBLIC;
REVOKE ALL ON public.financial_audit_log FROM anon;
GRANT SELECT ON public.financial_audit_log TO authenticated;
GRANT ALL    ON public.financial_audit_log TO service_role;
ALTER TABLE public.financial_audit_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "owner reads tenant audit log" ON public.financial_audit_log;
CREATE POLICY "owner reads tenant audit log" ON public.financial_audit_log
  FOR SELECT TO authenticated
  USING (
    tenant_id = public.current_tenant_id()
    AND public.has_owner_role(auth.uid(), tenant_id)
  );
CREATE INDEX IF NOT EXISTS idx_fin_audit_tenant_created
  ON public.financial_audit_log (tenant_id, created_at DESC);

CREATE OR REPLACE FUNCTION public._fin_audit_trigger()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO public.financial_audit_log(tenant_id, user_id, action, entity_type, entity_id, before, after)
      VALUES (OLD.tenant_id, auth.uid(), TG_OP, TG_TABLE_NAME, OLD.id, to_jsonb(OLD), NULL);
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO public.financial_audit_log(tenant_id, user_id, action, entity_type, entity_id, before, after)
      VALUES (NEW.tenant_id, auth.uid(), TG_OP, TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW));
    RETURN NEW;
  ELSE
    INSERT INTO public.financial_audit_log(tenant_id, user_id, action, entity_type, entity_id, before, after)
      VALUES (NEW.tenant_id, auth.uid(), TG_OP, TG_TABLE_NAME, NEW.id, NULL, to_jsonb(NEW));
    RETURN NEW;
  END IF;
END $$;

DROP TRIGGER IF EXISTS trg_audit_orders_upd   ON public.orders;
DROP TRIGGER IF EXISTS trg_audit_orders_del   ON public.orders;
DROP TRIGGER IF EXISTS trg_audit_payments_ins ON public.payments;
DROP TRIGGER IF EXISTS trg_audit_payments_del ON public.payments;
DROP TRIGGER IF EXISTS trg_audit_dayclose_ins ON public.day_closes;

CREATE TRIGGER trg_audit_orders_upd AFTER UPDATE ON public.orders
  FOR EACH ROW EXECUTE FUNCTION public._fin_audit_trigger();
CREATE TRIGGER trg_audit_orders_del AFTER DELETE ON public.orders
  FOR EACH ROW EXECUTE FUNCTION public._fin_audit_trigger();
CREATE TRIGGER trg_audit_payments_ins AFTER INSERT ON public.payments
  FOR EACH ROW EXECUTE FUNCTION public._fin_audit_trigger();
CREATE TRIGGER trg_audit_payments_del AFTER DELETE ON public.payments
  FOR EACH ROW EXECUTE FUNCTION public._fin_audit_trigger();
CREATE TRIGGER trg_audit_dayclose_ins AFTER INSERT ON public.day_closes
  FOR EACH ROW EXECUTE FUNCTION public._fin_audit_trigger();

-- ----- 2.1 close_day: per-tenant timezone + cash-basis realized_profit -----
CREATE OR REPLACE FUNCTION public.close_day(p_note text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_tz text := public.current_tenant_timezone();
  v_today date := (now() AT TIME ZONE v_tz)::date;
  v_sales numeric(12,2) := 0;
  v_collected numeric(12,2) := 0;
  v_expenses numeric(12,2) := 0;
  v_customer_debts numeric(12,2) := 0;
  v_unsettled_custody numeric(12,2) := 0;
  v_realized_profit numeric(12,2) := 0;
BEGIN
  PERFORM public._assert_owner(v_tenant);

  SELECT COALESCE(SUM(total), 0) INTO v_sales
    FROM public.orders
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_collected
    FROM public.payments
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_expenses
    FROM public.expenses
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(
    CASE
      WHEN delivery = 'direct' OR courier_id IS NULL THEN GREATEST(total - paid, 0)
      WHEN delivery = 'courier' AND courier_state = 'delivered_none' THEN total
      WHEN delivery = 'courier' AND courier_state = 'delivered_partial' THEN GREATEST(total - collected_by_courier, 0)
      ELSE 0
    END), 0) INTO v_customer_debts
    FROM public.orders
   WHERE tenant_id = v_tenant AND status IN ('partial','debt');

  SELECT COALESCE(SUM(collected_by_courier), 0) INTO v_unsettled_custody
    FROM public.orders
   WHERE tenant_id = v_tenant AND delivery = 'courier' AND courier_id IS NOT NULL;

  -- Cash-basis: allocate item margin by payment-share of order total, on the payment day.
  SELECT COALESCE(SUM(
    CASE WHEN o.total > 0
      THEN (p.amount / o.total) *
           (SELECT COALESCE(SUM((oi.unit_price - oi.unit_cost) * oi.qty),0)
              FROM public.order_items oi WHERE oi.order_id = o.id)
      ELSE 0 END
  ), 0) INTO v_realized_profit
  FROM public.payments p
  JOIN public.orders o ON o.id = p.order_id
  WHERE p.tenant_id = v_tenant
    AND (p.created_at AT TIME ZONE v_tz)::date = v_today
    AND p.order_id IS NOT NULL;

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
    'success', true, 'sales', v_sales, 'collected', v_collected, 'expenses', v_expenses,
    'realized_profit', v_realized_profit, 'customer_debts', v_customer_debts,
    'unsettled_custody', v_unsettled_custody
  );
END $$;

-- ----- 2.2 Live today estimate (single source for UI dashboard) -----
CREATE OR REPLACE FUNCTION public.get_tenant_today_estimate()
RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_tz text := public.current_tenant_timezone();
  v_today date := (now() AT TIME ZONE v_tz)::date;
  v_sales numeric(12,2);
  v_collected numeric(12,2);
  v_expenses numeric(12,2);
  v_realized_profit numeric(12,2);
BEGIN
  PERFORM public._assert_staff(v_tenant);

  SELECT COALESCE(SUM(total),0) INTO v_sales FROM public.orders
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(amount),0) INTO v_collected FROM public.payments
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(amount),0) INTO v_expenses FROM public.expenses
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(
    CASE WHEN o.total > 0
      THEN (p.amount / o.total) *
           (SELECT COALESCE(SUM((oi.unit_price - oi.unit_cost) * oi.qty),0)
              FROM public.order_items oi WHERE oi.order_id = o.id)
      ELSE 0 END
  ), 0) INTO v_realized_profit
  FROM public.payments p JOIN public.orders o ON o.id = p.order_id
  WHERE p.tenant_id = v_tenant
    AND (p.created_at AT TIME ZONE v_tz)::date = v_today
    AND p.order_id IS NOT NULL;

  RETURN jsonb_build_object(
    'today', v_today, 'timezone', v_tz,
    'sales', v_sales, 'collected', v_collected, 'expenses', v_expenses,
    'realized_profit', v_realized_profit
  );
END $$;
REVOKE ALL ON FUNCTION public.get_tenant_today_estimate() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_tenant_today_estimate() FROM anon;
GRANT EXECUTE ON FUNCTION public.get_tenant_today_estimate() TO authenticated;

-- ----- 2.1b Update platform admin overview & day-close health to use tenant timezone -----
CREATE OR REPLACE FUNCTION public.get_platform_admin_overview()
RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v jsonb;
  v_total_tenants int; v_active_tenants int; v_total_products int;
  v_total_customers int; v_total_orders int; v_total_payments int;
  v_open_debts numeric(14,2); v_unsettled_custody numeric(14,2);
  v_expenses_today numeric(14,2); v_day_close_count int; v_critical_alerts int := 0;
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_overview', '{}'::jsonb);
  SELECT COUNT(*) INTO v_total_tenants FROM public.tenants;
  SELECT COUNT(DISTINCT tenant_id) INTO v_active_tenants FROM public.orders WHERE created_at >= now() - interval '30 days';
  SELECT COUNT(*) INTO v_total_products FROM public.products;
  SELECT COUNT(*) INTO v_total_customers FROM public.customers;
  SELECT COUNT(*) INTO v_total_orders FROM public.orders;
  SELECT COUNT(*) INTO v_total_payments FROM public.payments;
  SELECT COALESCE(SUM(total - paid),0) INTO v_open_debts FROM public.orders
    WHERE status IN ('partial','debt') AND (delivery = 'direct' OR courier_id IS NULL);
  SELECT COALESCE(SUM(collected_by_courier),0) INTO v_unsettled_custody FROM public.orders
    WHERE delivery = 'courier' AND courier_id IS NOT NULL;
  SELECT COALESCE(SUM(e.amount),0) INTO v_expenses_today FROM public.expenses e
    JOIN public.tenants t ON t.id = e.tenant_id
   WHERE (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date
       = (now() AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date;
  SELECT COUNT(*) INTO v_day_close_count FROM public.day_closes dc
    JOIN public.tenants t ON t.id = dc.tenant_id
   WHERE dc.closed_for = (now() AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date;
  SELECT (SELECT COUNT(*) FROM public.orders WHERE paid > total)
       + (SELECT COUNT(*) FROM public.orders WHERE paid < 0)
       + (SELECT COUNT(*) FROM public.orders WHERE total < 0)
       + (SELECT COUNT(*) FROM public.products WHERE stock < 0)
       + (SELECT COUNT(*) FROM public.orders WHERE collected_by_courier > total)
    INTO v_critical_alerts;
  v := jsonb_build_object(
    'total_tenants', v_total_tenants, 'active_tenants', v_active_tenants,
    'total_products', v_total_products, 'total_customers', v_total_customers,
    'total_orders', v_total_orders, 'total_payments', v_total_payments,
    'open_customer_debts', v_open_debts, 'unsettled_courier_custody', v_unsettled_custody,
    'expenses_today', v_expenses_today, 'day_close_count_today', v_day_close_count,
    'critical_alerts', v_critical_alerts);
  RETURN v;
END $$;

CREATE OR REPLACE FUNCTION public.get_platform_day_close_health(p_limit integer DEFAULT 30)
RETURNS TABLE(id uuid, tenant_id uuid, tenant_name text, closed_for date, sales numeric, collected numeric, expenses numeric, customer_debts numeric, unsettled_custody numeric, realized_profit numeric, created_at timestamp with time zone, sales_diff numeric, collected_diff numeric, expenses_diff numeric, status text)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public AS $$
DECLARE v_lim int := LEAST(GREATEST(COALESCE(p_limit,30),1),200);
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_day_close_health', jsonb_build_object('limit', v_lim));
  RETURN QUERY
  SELECT dc.id, dc.tenant_id, t.name, dc.closed_for, dc.sales, dc.collected, dc.expenses,
         dc.customer_debts, dc.unsettled_custody, dc.realized_profit, dc.created_at,
         dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o
           WHERE o.tenant_id = dc.tenant_id
             AND (o.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p
           WHERE p.tenant_id = dc.tenant_id
             AND (p.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e
           WHERE e.tenant_id = dc.tenant_id
             AND (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         CASE WHEN
           ABS(dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o
             WHERE o.tenant_id = dc.tenant_id AND (o.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p
             WHERE p.tenant_id = dc.tenant_id AND (p.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e
             WHERE e.tenant_id = dc.tenant_id AND (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
         THEN 'Matches' ELSE 'Mismatch' END
  FROM public.day_closes dc LEFT JOIN public.tenants t ON t.id = dc.tenant_id
  ORDER BY dc.created_at DESC LIMIT v_lim;
END $$;

-- ----- 3.3b Patch create_sale_with_items to use next_order_number + return tenant number -----
CREATE OR REPLACE FUNCTION public.create_sale_with_items(p_customer_id uuid, p_delivery delivery_kind, p_courier_id uuid, p_paid numeric, p_method payment_method, p_items jsonb)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid    uuid := auth.uid();
  v_total  numeric(12,2) := 0;
  v_status order_status;
  v_order  public.orders%ROWTYPE;
  v_tnum   int;
  v_item   jsonb;
  v_pid    uuid;
  v_qty    numeric(12,2);
  v_prod   public.products%ROWTYPE;
  v_order_paid          numeric(12,2);
  v_order_collected     numeric(12,2);
  v_order_courier_state courier_state;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN RAISE EXCEPTION 'invalid_paid'; END IF;
  IF p_delivery = 'courier' AND (p_courier_id IS NULL OR p_customer_id IS NULL) THEN
    RAISE EXCEPTION 'courier_requires_customer_and_courier';
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0 THEN RAISE EXCEPTION 'invalid_item'; END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_found'; END IF;
    IF NOT v_prod.is_active THEN RAISE EXCEPTION 'product_inactive: %', v_prod.name; END IF;
    IF v_prod.stock < v_qty THEN RAISE EXCEPTION 'insufficient_stock: %', v_prod.name; END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN RAISE EXCEPTION 'paid_exceeds_total'; END IF;
  IF p_delivery = 'direct' AND p_paid < v_total AND p_customer_id IS NULL THEN
    RAISE EXCEPTION 'customer_required_for_debt';
  END IF;

  IF p_delivery = 'courier' THEN
    v_order_paid := 0;
    v_order_collected := p_paid;
    v_order_courier_state := CASE
      WHEN p_paid = 0 THEN 'pending'::courier_state
      WHEN p_paid >= v_total THEN 'delivered_full'::courier_state
      ELSE 'delivered_partial'::courier_state END;
    v_status := 'debt'::order_status;
  ELSE
    v_order_paid := p_paid;
    v_order_collected := 0;
    v_order_courier_state := NULL;
    v_status := CASE
      WHEN p_paid >= v_total THEN 'paid'::order_status
      WHEN p_paid > 0 THEN 'partial'::order_status
      ELSE 'debt'::order_status END;
  END IF;

  v_tnum := public.next_order_number(v_tenant);

  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by, tenant_number
  ) VALUES (
    v_tenant, p_customer_id, v_total, v_order_paid, v_status, p_delivery, p_courier_id,
    v_order_courier_state, v_order_collected, v_uid, v_tnum
  ) RETURNING * INTO v_order;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid;
    INSERT INTO public.order_items(tenant_id, order_id, product_id, name, qty, unit_price, unit_cost)
      VALUES (v_tenant, v_order.id, v_pid, v_prod.name, v_qty, v_prod.price, v_prod.cost);
    UPDATE public.products SET stock = stock - v_qty WHERE id = v_pid;
  END LOOP;

  IF p_delivery = 'direct' AND p_paid > 0 THEN
    INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, created_by)
      VALUES (v_tenant, 'sale', p_method, p_paid, v_order.id, p_customer_id, v_uid);
  END IF;

  RETURN jsonb_build_object('success', true, 'order_id', v_order.id, 'number', v_tnum);
END $$;

-- ----- 3.2 settle_courier_orders: derive collected from stored value -----
DROP FUNCTION IF EXISTS public.settle_courier_orders(uuid, jsonb);
CREATE OR REPLACE FUNCTION public.settle_courier_orders(p_courier_id uuid, p_order_ids uuid[])
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_uid uuid := auth.uid();
  v_tenant uuid := public.current_tenant_id();
  v_oid uuid;
  v_order public.orders%ROWTYPE;
  v_collected numeric(12,2);
  v_new_paid numeric(12,2);
  v_status order_status;
  v_count int := 0;
  v_total_collected numeric(12,2) := 0;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF NOT EXISTS (SELECT 1 FROM public.couriers WHERE id = p_courier_id AND tenant_id = v_tenant) THEN
    RAISE EXCEPTION 'courier_not_found';
  END IF;
  IF p_order_ids IS NULL OR array_length(p_order_ids, 1) IS NULL THEN
    RAISE EXCEPTION 'invalid_orders';
  END IF;

  FOREACH v_oid IN ARRAY p_order_ids LOOP
    SELECT * INTO v_order FROM public.orders WHERE id = v_oid FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found: %', v_oid; END IF;
    IF v_order.tenant_id <> v_tenant OR v_order.courier_id <> p_courier_id THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;

    -- Source of truth: collected_by_courier set when the courier state was updated.
    v_collected := COALESCE(v_order.collected_by_courier, 0);
    IF v_collected > v_order.total - v_order.paid THEN
      RAISE EXCEPTION 'collected_exceeds_remaining';
    END IF;

    v_new_paid := v_order.paid + v_collected;
    v_status := CASE
      WHEN v_new_paid >= v_order.total THEN 'paid'::order_status
      WHEN v_new_paid > 0 THEN 'partial'::order_status
      ELSE 'debt'::order_status END;

    UPDATE public.orders SET
      paid = v_new_paid, status = v_status,
      delivery = 'direct', courier_id = NULL, courier_state = NULL, collected_by_courier = 0
    WHERE id = v_oid;

    IF v_collected > 0 THEN
      INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, courier_id, created_by)
        VALUES (v_tenant, 'courier_settlement', 'cash', v_collected, v_oid, v_order.customer_id, p_courier_id, v_uid);
      v_total_collected := v_total_collected + v_collected;
    END IF;
    v_count := v_count + 1;
  END LOOP;

  RETURN jsonb_build_object('success', true, 'settled_count', v_count, 'total_collected', v_total_collected);
END $$;
REVOKE ALL ON FUNCTION public.settle_courier_orders(uuid, uuid[]) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.settle_courier_orders(uuid, uuid[]) FROM anon;
GRANT EXECUTE ON FUNCTION public.settle_courier_orders(uuid, uuid[]) TO authenticated;

-- ----- 3.1 Lock down financial table writes to RPCs only -----
-- SECURITY DEFINER RPCs run as the function owner (postgres), so they keep working.
-- Direct supabase.from(...).insert/update/delete on these tables now requires service_role.
REVOKE INSERT, UPDATE, DELETE ON public.orders        FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.order_items   FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.payments      FROM authenticated;
