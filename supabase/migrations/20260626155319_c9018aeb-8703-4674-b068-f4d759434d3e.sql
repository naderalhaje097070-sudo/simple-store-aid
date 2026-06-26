
-- ============================================================
-- Financial hardening for Mongezz pilot
-- ============================================================

-- 1) Database-level constraints --------------------------------
ALTER TABLE public.products
  DROP CONSTRAINT IF EXISTS products_stock_nonneg;
ALTER TABLE public.products
  ADD CONSTRAINT products_stock_nonneg CHECK (stock >= 0) NOT VALID;

ALTER TABLE public.orders
  DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_customer_required_when_unpaid
    CHECK (paid >= total OR customer_id IS NOT NULL) NOT VALID;

ALTER TABLE public.orders
  DROP CONSTRAINT IF EXISTS orders_courier_requires_courier_id;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_courier_requires_courier_id
    CHECK (delivery <> 'courier' OR courier_id IS NOT NULL) NOT VALID;

ALTER TABLE public.orders
  DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_courier_requires_customer_id
    CHECK (delivery <> 'courier' OR customer_id IS NOT NULL) NOT VALID;

ALTER TABLE public.orders
  DROP CONSTRAINT IF EXISTS orders_collected_not_over_total;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_collected_not_over_total
    CHECK (collected_by_courier <= total) NOT VALID;

-- 2) Helper: assert caller is staff/owner of given tenant ------
CREATE OR REPLACE FUNCTION public._assert_staff(_tid uuid)
RETURNS void
LANGUAGE plpgsql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF _tid IS NULL OR _tid <> public.current_tenant_id() THEN
    RAISE EXCEPTION 'forbidden_tenant';
  END IF;
  IF NOT public.has_staff_or_owner_role(auth.uid(), _tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
END $$;

-- 3) RPC: create_sale_with_items -------------------------------
CREATE OR REPLACE FUNCTION public.create_sale_with_items(
  p_customer_id uuid,
  p_delivery    delivery_kind,
  p_courier_id  uuid,
  p_paid        numeric,
  p_method      payment_method,
  p_items       jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid    uuid := auth.uid();
  v_total  numeric(12,2) := 0;
  v_status order_status;
  v_order  public.orders%ROWTYPE;
  v_number int;
  v_item   jsonb;
  v_pid    uuid;
  v_qty    numeric(12,2);
  v_prod   public.products%ROWTYPE;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN
    RAISE EXCEPTION 'invalid_paid';
  END IF;
  IF p_delivery = 'courier' AND (p_courier_id IS NULL OR p_customer_id IS NULL) THEN
    RAISE EXCEPTION 'courier_requires_customer_and_courier';
  END IF;

  -- Lock & validate each product, compute trusted total
  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0 THEN
      RAISE EXCEPTION 'invalid_item';
    END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN
      RAISE EXCEPTION 'product_not_found';
    END IF;
    IF NOT v_prod.is_active THEN
      RAISE EXCEPTION 'product_inactive: %', v_prod.name;
    END IF;
    IF v_prod.stock < v_qty THEN
      RAISE EXCEPTION 'insufficient_stock: %', v_prod.name;
    END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN
    RAISE EXCEPTION 'paid_exceeds_total';
  END IF;
  IF p_paid < v_total AND p_customer_id IS NULL THEN
    RAISE EXCEPTION 'customer_required_for_debt';
  END IF;

  v_status := CASE
    WHEN p_paid >= v_total THEN 'paid'::order_status
    WHEN p_paid > 0        THEN 'partial'::order_status
    ELSE 'debt'::order_status
  END;

  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by
  ) VALUES (
    v_tenant, p_customer_id, v_total, p_paid, v_status, p_delivery, p_courier_id,
    CASE WHEN p_delivery = 'courier' THEN 'pending'::courier_state ELSE NULL END,
    0, v_uid
  ) RETURNING * INTO v_order;
  v_number := v_order.number;

  -- Insert items with locked prices and decrement stock
  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid;
    INSERT INTO public.order_items(tenant_id, order_id, product_id, name, qty, unit_price, unit_cost)
      VALUES (v_tenant, v_order.id, v_pid, v_prod.name, v_qty, v_prod.price, v_prod.cost);
    UPDATE public.products SET stock = stock - v_qty WHERE id = v_pid;
  END LOOP;

  -- Record payment only for direct sales with cash in hand
  IF p_delivery = 'direct' AND p_paid > 0 THEN
    INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, created_by)
      VALUES (v_tenant, 'sale', p_method, p_paid, v_order.id, p_customer_id, v_uid);
  END IF;

  RETURN jsonb_build_object('success', true, 'order_id', v_order.id, 'number', v_number);
END $$;

GRANT EXECUTE ON FUNCTION public.create_sale_with_items(uuid, delivery_kind, uuid, numeric, payment_method, jsonb) TO authenticated;

-- 4) RPC: collect_order_debt -----------------------------------
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

GRANT EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, payment_method) TO authenticated;

-- 5) RPC: settle_courier_orders --------------------------------
-- p_orders = [{"order_id": uuid, "collected": numeric}, ...]
CREATE OR REPLACE FUNCTION public.settle_courier_orders(
  p_courier_id uuid,
  p_orders     jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_uid uuid := auth.uid();
  v_tenant uuid := public.current_tenant_id();
  v_item jsonb;
  v_oid uuid;
  v_collected numeric(12,2);
  v_order public.orders%ROWTYPE;
  v_remaining numeric(12,2);
  v_new_paid numeric(12,2);
  v_status order_status;
  v_count int := 0;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF NOT EXISTS (SELECT 1 FROM public.couriers WHERE id = p_courier_id AND tenant_id = v_tenant) THEN
    RAISE EXCEPTION 'courier_not_found';
  END IF;
  IF p_orders IS NULL OR jsonb_typeof(p_orders) <> 'array' THEN
    RAISE EXCEPTION 'invalid_orders';
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_orders) LOOP
    v_oid := (v_item->>'order_id')::uuid;
    v_collected := COALESCE((v_item->>'collected')::numeric, 0);
    IF v_collected < 0 THEN RAISE EXCEPTION 'invalid_collected'; END IF;
    SELECT * INTO v_order FROM public.orders WHERE id = v_oid FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found: %', v_oid; END IF;
    IF v_order.tenant_id <> v_tenant OR v_order.courier_id <> p_courier_id THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;

    v_remaining := v_order.total - v_order.paid;
    IF v_collected > v_remaining THEN
      RAISE EXCEPTION 'collected_exceeds_remaining';
    END IF;

    v_new_paid := v_order.paid + v_collected;
    v_status := CASE
      WHEN v_new_paid >= v_order.total THEN 'paid'::order_status
      WHEN v_new_paid > 0 THEN 'partial'::order_status
      ELSE 'debt'::order_status
    END;
    -- After settlement the courier no longer holds custody.
    -- Order keeps its customer_id; remaining (if any) becomes customer debt.
    UPDATE public.orders SET
      paid = v_new_paid,
      status = v_status,
      delivery = 'direct',
      courier_id = NULL,
      courier_state = NULL,
      collected_by_courier = 0
    WHERE id = v_oid;

    IF v_collected > 0 THEN
      INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, courier_id, created_by)
        VALUES (v_tenant, 'courier_settlement', 'cash', v_collected, v_oid, v_order.customer_id, p_courier_id, v_uid);
    END IF;
    v_count := v_count + 1;
  END LOOP;

  RETURN jsonb_build_object('success', true, 'settled_count', v_count);
END $$;

GRANT EXECUTE ON FUNCTION public.settle_courier_orders(uuid, jsonb) TO authenticated;

-- 6) RPC: return_courier_order ---------------------------------
CREATE OR REPLACE FUNCTION public.return_courier_order(p_order_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_it record;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);
  IF v_order.delivery <> 'courier' THEN
    RAISE EXCEPTION 'not_a_courier_order';
  END IF;
  IF v_order.paid > 0 THEN
    RAISE EXCEPTION 'cannot_return_partially_paid_order';
  END IF;

  -- Restore stock for each item
  FOR v_it IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
    IF v_it.product_id IS NOT NULL THEN
      UPDATE public.products SET stock = stock + v_it.qty WHERE id = v_it.product_id;
    END IF;
  END LOOP;

  UPDATE public.orders SET
    courier_state = 'returned',
    collected_by_courier = 0
  WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true);
END $$;

GRANT EXECUTE ON FUNCTION public.return_courier_order(uuid) TO authenticated;

-- 7) RPC: close_day --------------------------------------------
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
  PERFORM public._assert_staff(v_tenant);

  SELECT COALESCE(SUM(total), 0) INTO v_sales
    FROM public.orders WHERE tenant_id = v_tenant AND created_at::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_collected
    FROM public.payments WHERE tenant_id = v_tenant AND created_at::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_expenses
    FROM public.expenses WHERE tenant_id = v_tenant AND created_at::date = v_today;

  -- Outstanding (open) debts and custody across all time:
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

  -- Realized profit = (collected today across order payments) * margin proxy.
  -- Simpler & honest: profit on items proportional to paid share of their orders today.
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

GRANT EXECUTE ON FUNCTION public.close_day(text) TO authenticated;
