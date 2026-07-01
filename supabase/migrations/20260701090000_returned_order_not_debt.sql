-- ============================================================
-- Fix C (P0-1): a returned courier order must never be customer debt
-- ============================================================
-- return_courier_order sets courier_state='returned', restores stock, and
-- flips the row to delivery='direct', courier_id=NULL, collected_by_courier=0,
-- but leaves status='debt' (there is no 'returned' order_status enum value).
-- That made the debt CASE below (delivery='direct' OR courier_id IS NULL)
-- count the full total as a phantom, collectible customer debt.
--
-- This migration:
--   1) close_day: give courier_state='returned' priority → debt = 0.
--   2) collect_order_debt: reject collection on returned orders.
-- No RLS, grants, profit logic, or "Delivered ≠ Settled" semantics change.

-- ----- close_day: returned orders contribute 0 to customer_debts -----
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
      WHEN courier_state = 'returned' THEN 0
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

-- ----- collect_order_debt: block collection on returned orders -----
CREATE OR REPLACE FUNCTION public.collect_order_debt(p_order_id uuid, p_amount numeric, p_method payment_method)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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

  -- A returned order carries no customer debt (stock was restored). Never collectible.
  IF v_order.courier_state = 'returned' THEN
    RAISE EXCEPTION 'cannot_collect_returned_order';
  END IF;

  -- Block collecting against orders still in courier custody.
  -- Allowed only when delivery is direct, or courier has no pending custody
  -- (e.g. delivered_none with collected=0 — rare but valid as customer debt).
  IF v_order.delivery = 'courier' AND v_order.courier_id IS NOT NULL THEN
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
END $function$;
