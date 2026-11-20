-- Count only the unpaid portion of courier invoices in new day close calculations.
-- Existing snapshots and function grants are preserved by this migration.
BEGIN;

CREATE OR REPLACE FUNCTION public.close_day(p_note text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
  PERFORM monjez_private.assert_active_actor();
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
      WHEN delivery = 'courier' AND courier_state = 'delivered_none' THEN GREATEST(total - paid, 0)
      WHEN delivery = 'courier' AND courier_state = 'delivered_partial'
        THEN GREATEST(total - paid - COALESCE(collected_by_courier, 0), 0)
      ELSE 0
    END), 0) INTO v_customer_debts
    FROM public.orders
   WHERE tenant_id = v_tenant AND status IN ('partial','debt');

  SELECT COALESCE(SUM(collected_by_courier), 0) INTO v_unsettled_custody
    FROM public.orders
   WHERE tenant_id = v_tenant AND delivery = 'courier' AND courier_id IS NOT NULL;

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
END $function$;

COMMIT;
