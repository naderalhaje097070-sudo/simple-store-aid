-- C2 owner-approved fractional quantities; original two-decimal item precision.
BEGIN;
SET LOCAL lock_timeout = '5s';
LOCK TABLE public.products, public.order_items IN ACCESS EXCLUSIVE MODE;
DO $preflight$
BEGIN
  IF EXISTS (SELECT 1 FROM public.products WHERE NOT (stock >= 0 AND stock <= 9999999999.99 AND stock = trunc(stock::numeric, 2)))
     OR EXISTS (SELECT 1 FROM public.order_items WHERE NOT (qty > 0 AND qty <= 9999999999.99 AND qty = trunc(qty, 2))) THEN
    RAISE EXCEPTION 'fractional_quantity_historical_data_requires_review';
  END IF;
END $preflight$;
-- No typemod: constraints reject excess precision rather than rounding before CHECK.
ALTER TABLE public.products ALTER COLUMN stock TYPE numeric USING stock::numeric;
ALTER TABLE public.order_items ALTER COLUMN qty TYPE numeric USING qty::numeric;
ALTER TABLE public.products ADD CONSTRAINT products_stock_quantity_precision
  CHECK (stock >= 0 AND stock <= 9999999999.99 AND stock = trunc(stock, 2));
ALTER TABLE public.order_items ADD CONSTRAINT order_items_quantity_precision
  CHECK (qty > 0 AND qty <= 9999999999.99 AND qty = trunc(qty, 2));

CREATE OR REPLACE FUNCTION public.create_sale_with_items(p_customer_id uuid, p_delivery delivery_kind, p_courier_id uuid, p_paid numeric, p_method payment_method, p_items jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid    uuid := auth.uid();
  v_total  numeric(12,2) := 0;
  v_status order_status;
  v_order  public.orders%ROWTYPE;
  v_tnum   int;
  v_item   jsonb;
  v_pid    uuid;
  v_qty    numeric;
  v_prod   public.products%ROWTYPE;
  v_order_paid          numeric(12,2);
  v_order_collected     numeric(12,2);
  v_order_courier_state courier_state;
BEGIN
  PERFORM monjez_private.assert_active_actor();
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
    IF v_pid IS NULL OR v_qty IS NULL OR NOT (v_qty > 0 AND v_qty <= 9999999999.99 AND v_qty = trunc(v_qty, 2)) THEN
      RAISE EXCEPTION 'invalid_item';
    END IF;
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
END $function$;

NOTIFY pgrst, 'reload schema';
COMMIT;
