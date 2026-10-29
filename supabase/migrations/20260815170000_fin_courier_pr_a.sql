-- FIN-COURIER-001 / PR-A candidate implementation.
-- Forward-only schema/RPC change. Repository-only candidate: do not deploy before Gate-4 evidence and human approval.

ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_debt;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_customer_required_when_debt
  CHECK (
    customer_id IS NOT NULL
    OR (courier_state IS NOT NULL AND courier_state = 'returned')
    OR (delivery = 'direct' AND courier_state IS NULL AND paid >= total)
    OR (
      delivery = 'courier'
      AND courier_state IS NOT NULL
      AND courier_state IN ('pending', 'delivered_full')
    )
  ) NOT VALID;

CREATE OR REPLACE FUNCTION public._create_sale_with_items_core(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state,
  p_infer_courier_state boolean
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_total numeric(12,2) := 0;
  v_status public.order_status;
  v_order public.orders%ROWTYPE;
  v_tnum int;
  v_item jsonb;
  v_pid uuid;
  v_qty numeric(12,2);
  v_prod public.products%ROWTYPE;
  v_order_paid numeric(12,2);
  v_order_collected numeric(12,2);
  v_state public.courier_state := p_courier_state;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN RAISE EXCEPTION 'invalid_paid'; END IF;

  IF p_customer_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_tenant
  ) THEN
    RAISE EXCEPTION 'customer_not_found';
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_courier_id IS NOT NULL THEN RAISE EXCEPTION 'courier_id_must_be_null_for_direct'; END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NOT NULL THEN
      RAISE EXCEPTION 'courier_state_must_be_null_for_direct';
    END IF;
    v_state := NULL;
  ELSE
    IF p_courier_id IS NULL THEN RAISE EXCEPTION 'courier_requires_courier'; END IF;
    IF NOT EXISTS (
      SELECT 1 FROM public.couriers
       WHERE id = p_courier_id AND tenant_id = v_tenant AND is_active = true
    ) THEN
      RAISE EXCEPTION 'courier_not_found';
    END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NULL THEN RAISE EXCEPTION 'courier_state_required'; END IF;
    IF p_courier_state = 'returned' THEN RAISE EXCEPTION 'returned_not_allowed_at_creation'; END IF;
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    BEGIN
      v_pid := (v_item->>'productId')::uuid;
      v_qty := (v_item->>'qty')::numeric;
    EXCEPTION WHEN OTHERS THEN
      RAISE EXCEPTION 'invalid_item';
    END;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0 THEN RAISE EXCEPTION 'invalid_item'; END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_found'; END IF;
    IF NOT v_prod.is_active THEN RAISE EXCEPTION 'product_inactive: %', v_prod.name; END IF;
    IF v_prod.stock < v_qty THEN RAISE EXCEPTION 'insufficient_stock: %', v_prod.name; END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN RAISE EXCEPTION 'paid_exceeds_total'; END IF;

  IF p_delivery = 'courier' AND p_infer_courier_state THEN
    v_state := CASE
      WHEN p_paid = 0 THEN 'pending'::public.courier_state
      WHEN p_paid = v_total THEN 'delivered_full'::public.courier_state
      ELSE 'delivered_partial'::public.courier_state
    END;
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_paid < v_total AND p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
    v_order_paid := p_paid;
    v_order_collected := 0;
    v_status := CASE
      WHEN p_paid >= v_total THEN 'paid'::public.order_status
      WHEN p_paid > 0 THEN 'partial'::public.order_status
      ELSE 'debt'::public.order_status
    END;
  ELSE
    IF v_state IS NULL OR v_state = 'returned' THEN RAISE EXCEPTION 'invalid_state'; END IF;
    CASE v_state
      WHEN 'pending' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_none' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_partial' THEN
        IF p_paid <= 0 OR p_paid >= v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := p_paid;
      WHEN 'delivered_full' THEN
        IF p_paid <> v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := v_total;
      ELSE
        RAISE EXCEPTION 'invalid_state';
    END CASE;
    v_order_paid := 0;
    v_status := 'debt'::public.order_status;
  END IF;

  v_tnum := public.next_order_number(v_tenant);
  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by, tenant_number
  ) VALUES (
    v_tenant, p_customer_id, v_total, v_order_paid, v_status, p_delivery,
    p_courier_id, v_state, v_order_collected, v_uid, v_tnum
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
END;
$$;

REVOKE ALL ON FUNCTION public._create_sale_with_items_core(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state, boolean
) FROM PUBLIC, anon, authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items_v2(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    p_courier_state, false
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) TO authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    NULL, true
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_outcome_v2(
  p_order_id uuid,
  p_state public.courier_state,
  p_collected numeric,
  p_customer_id uuid
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_target_collected numeric(12,2);
  v_customer_id uuid;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.delivery <> 'courier' OR v_order.courier_state IS NULL THEN RAISE EXCEPTION 'not_a_courier_order'; END IF;
  IF p_state IS NULL THEN RAISE EXCEPTION 'invalid_state'; END IF;

  IF p_state = 'returned' THEN
    IF v_order.courier_state NOT IN ('pending', 'delivered_none') THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN public.return_courier_order(p_order_id);
  END IF;

  IF p_state IN ('pending', 'delivered_none') THEN
    v_target_collected := 0;
  ELSIF p_state = 'delivered_partial' THEN
    IF p_collected IS NULL OR p_collected <= 0 OR p_collected >= v_order.total THEN RAISE EXCEPTION 'invalid_collected'; END IF;
    v_target_collected := p_collected;
  ELSIF p_state = 'delivered_full' THEN
    v_target_collected := v_order.total;
  ELSE
    RAISE EXCEPTION 'invalid_state';
  END IF;

  IF p_state = v_order.courier_state THEN
    IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;
    IF v_target_collected <> COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN jsonb_build_object(
      'success', true, 'order_id', v_order.id, 'state', v_order.courier_state,
      'collected', COALESCE(v_order.collected_by_courier, 0), 'idempotent', true
    );
  END IF;

  IF NOT (
    (v_order.courier_state = 'pending' AND p_state IN ('delivered_none','delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_none' AND p_state IN ('delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_partial' AND p_state = 'delivered_full')
  ) THEN
    RAISE EXCEPTION 'invalid_transition';
  END IF;

  IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;

  v_customer_id := v_order.customer_id;
  IF p_state IN ('delivered_none', 'delivered_partial') THEN
    IF v_customer_id IS NULL THEN
      IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
      IF NOT EXISTS (
        SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_order.tenant_id
      ) THEN
        RAISE EXCEPTION 'customer_not_found';
      END IF;
      v_customer_id := p_customer_id;
    ELSIF p_customer_id IS NOT NULL AND p_customer_id <> v_customer_id THEN
      RAISE EXCEPTION 'customer_mismatch';
    END IF;
  END IF;

  UPDATE public.orders
     SET courier_state = p_state,
         collected_by_courier = v_target_collected,
         customer_id = v_customer_id
   WHERE id = p_order_id;

  RETURN jsonb_build_object(
    'success', true, 'order_id', p_order_id, 'state', p_state,
    'collected', v_target_collected, 'customer_id', v_customer_id
  );
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_order_state(
  p_order_id uuid,
  p_state text,
  p_collected numeric DEFAULT NULL
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_state public.courier_state;
BEGIN
  IF p_state IS NULL OR p_state NOT IN ('pending','delivered_none','delivered_partial','delivered_full','returned') THEN
    RAISE EXCEPTION 'invalid_state';
  END IF;
  v_state := p_state::public.courier_state;
  RETURN public.update_courier_outcome_v2(p_order_id, v_state, p_collected, NULL);
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_order_state(uuid, text, numeric) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_order_state(uuid, text, numeric) TO authenticated;
