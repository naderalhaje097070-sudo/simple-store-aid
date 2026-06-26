
-- 1) Owner-only close_day
CREATE OR REPLACE FUNCTION public._assert_owner(_tid uuid)
RETURNS void
LANGUAGE plpgsql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF _tid IS NULL OR _tid <> public.current_tenant_id() THEN
    RAISE EXCEPTION 'forbidden_tenant';
  END IF;
  IF NOT public.has_owner_role(auth.uid(), _tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
END $$;

REVOKE EXECUTE ON FUNCTION public._assert_owner(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public._assert_owner(uuid) TO authenticated;

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

  SELECT COALESCE(SUM(amount), 0) INTO v_collected
    FROM public.payments WHERE tenant_id = v_tenant AND created_at::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_expenses
    FROM public.expenses WHERE tenant_id = v_tenant AND created_at::date = v_today;

  SELECT COALESCE(SUM(total - paid), 0) INTO v_customer_debts
    FROM public.orders
    WHERE tenant_id = v_tenant
      AND status IN ('partial','debt')
      AND (delivery = 'direct' OR courier_id IS NULL);

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

-- 2) Lock down internal trigger functions from direct invocation
REVOKE EXECUTE ON FUNCTION public.handle_new_tenant() FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated;
