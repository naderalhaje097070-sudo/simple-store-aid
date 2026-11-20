-- Enforce the existing courier custody and settlement rules without changing stored balances.
-- CREATE OR REPLACE preserves callers, owners, and existing privileges.
BEGIN;

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
  PERFORM monjez_private.assert_active_actor();
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
  IF v_target_collected > GREATEST(v_order.total - v_order.paid, 0) THEN
    RAISE EXCEPTION 'courier_custody_exceeds_remaining';
  END IF;

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

CREATE OR REPLACE FUNCTION public.settle_courier_orders(p_courier_id uuid, p_order_ids uuid[])
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
  PERFORM monjez_private.assert_active_actor();
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
    -- NULL-safe: return_courier_order and a prior settlement both clear courier_id.
    -- With "<>", a NULL courier_id made the check NULL (not true), so a returned
    -- order passed and settlement erased its returned mark (it became debt again).
    IF v_order.tenant_id IS DISTINCT FROM v_tenant
       OR v_order.courier_state IS NOT DISTINCT FROM 'returned'::courier_state THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;
    -- Accepted retry contract: a repeated settlement of an order already settled
    -- (custody cleared, not returned) succeeds with no second cash and no change.
    IF v_order.courier_id IS NULL AND v_order.courier_state IS NULL
       AND v_order.delivery = 'direct'::delivery_kind
       AND COALESCE(v_order.collected_by_courier, 0) = 0 THEN
      CONTINUE;
    END IF;
    IF v_order.courier_id IS DISTINCT FROM p_courier_id
       OR v_order.delivery IS DISTINCT FROM 'courier'::delivery_kind
       OR v_order.courier_state IS NULL
       OR v_order.courier_state = 'pending'::courier_state THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;

    v_collected := COALESCE(v_order.collected_by_courier, 0);
    -- Preserve inconsistent custody for reconciliation instead of clearing the excess.
    IF v_collected > GREATEST(v_order.total - v_order.paid, 0) THEN
      RAISE EXCEPTION 'courier_custody_exceeds_remaining';
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
END $function$;

COMMIT;
