CREATE OR REPLACE FUNCTION public.return_courier_order(p_order_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
  IF COALESCE(v_order.paid, 0) > 0 OR COALESCE(v_order.collected_by_courier, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_return_partially_paid_order';
  END IF;

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
END $function$;