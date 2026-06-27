-- Fix settle_courier_orders: clamp collected to remaining instead of throwing,
-- so stale "delivered_full" rows where paid already equals total don't block settlement.
-- Also clear any orphan courier flags on already-paid orders so they leave custody lists.

-- 1) One-time cleanup: orders fully paid yet still flagged as courier custody.
UPDATE public.orders
   SET delivery = 'direct',
       courier_id = NULL,
       courier_state = NULL,
       collected_by_courier = 0
 WHERE delivery = 'courier'
   AND status = 'paid'
   AND paid >= total
   AND courier_state IS NOT NULL;

-- 2) Harden RPC: clamp v_collected to remaining (no behavior change for valid data).
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
    -- Clamp to remaining so stale rows (where paid already covers total) don't block settlement.
    v_collected := LEAST(
      COALESCE(v_order.collected_by_courier, 0),
      GREATEST(v_order.total - v_order.paid, 0)
    );

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