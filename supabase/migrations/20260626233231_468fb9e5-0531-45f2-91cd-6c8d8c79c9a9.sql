
-- ============================================================
-- Mongezz V2 — Hardening migration
-- C1: atomic delete order with stock restore
-- C2: atomic update of courier order state
-- M8: return_courier_order also clears courier from custody view
-- M6: composite index for tenant + created_at
-- M3: validate existing NOT VALID constraints
-- ============================================================

-- ---------- C1: delete_order_with_restore_stock ----------
CREATE OR REPLACE FUNCTION public.delete_order_with_restore_stock(p_order_id uuid)
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
  PERFORM public._assert_owner(v_order.tenant_id);

  -- Block deletion of courier orders that have collected money or have been settled
  IF v_order.delivery = 'courier' AND COALESCE(v_order.collected_by_courier, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_delete_courier_with_collected_money';
  END IF;
  IF COALESCE(v_order.paid, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_delete_paid_order';
  END IF;

  -- Restore stock
  FOR v_it IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
    IF v_it.product_id IS NOT NULL THEN
      UPDATE public.products SET stock = stock + v_it.qty WHERE id = v_it.product_id;
    END IF;
  END LOOP;

  DELETE FROM public.payments    WHERE order_id = p_order_id;
  DELETE FROM public.order_items WHERE order_id = p_order_id;
  DELETE FROM public.orders      WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true);
END $$;

REVOKE ALL ON FUNCTION public.delete_order_with_restore_stock(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.delete_order_with_restore_stock(uuid) TO authenticated;

-- ---------- C2: update_courier_order_state ----------
CREATE OR REPLACE FUNCTION public.update_courier_order_state(
  p_order_id uuid,
  p_state    text,
  p_collected numeric DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_collected numeric(12,2) := 0;
  v_state courier_state;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.delivery <> 'courier' THEN
    RAISE EXCEPTION 'not_a_courier_order';
  END IF;

  IF p_state = 'returned' THEN
    -- Delegate to the dedicated RPC so all return rules stay in one place
    RETURN public.return_courier_order(p_order_id);
  END IF;

  IF p_state NOT IN ('pending','delivered_none','delivered_partial','delivered_full') THEN
    RAISE EXCEPTION 'invalid_state';
  END IF;
  v_state := p_state::courier_state;

  IF p_state = 'delivered_full' THEN
    v_collected := v_order.total;
  ELSIF p_state = 'delivered_partial' THEN
    v_collected := GREATEST(0, LEAST(v_order.total, COALESCE(p_collected, 0)));
  ELSE
    v_collected := 0;
  END IF;

  IF v_collected > v_order.total THEN
    RAISE EXCEPTION 'collected_exceeds_total';
  END IF;

  UPDATE public.orders
     SET courier_state = v_state,
         collected_by_courier = v_collected
   WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true, 'collected', v_collected);
END $$;

REVOKE ALL ON FUNCTION public.update_courier_order_state(uuid, text, numeric) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_order_state(uuid, text, numeric) TO authenticated;

-- ---------- M8: improve return_courier_order to remove from custody view ----------
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
  IF COALESCE(v_order.paid, 0) > 0 OR COALESCE(v_order.collected_by_courier, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_return_partially_paid_order';
  END IF;

  FOR v_it IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
    IF v_it.product_id IS NOT NULL THEN
      UPDATE public.products SET stock = stock + v_it.qty WHERE id = v_it.product_id;
    END IF;
  END LOOP;

  -- M8: also clear courier assignment and mark as direct so it leaves custody lists.
  -- Keep customer link so historical record stays intact.
  UPDATE public.orders SET
    courier_state = 'returned',
    collected_by_courier = 0,
    courier_id = NULL,
    delivery = 'direct'
  WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true);
END $$;

-- ---------- M6: composite index for tenant scans by date ----------
CREATE INDEX IF NOT EXISTS orders_tenant_created_idx
  ON public.orders (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS payments_tenant_created_idx
  ON public.payments (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS expenses_tenant_created_idx
  ON public.expenses (tenant_id, created_at DESC);

-- ---------- M3: validate previously NOT VALID constraints (safe; raises if data violates) ----------
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT conrelid::regclass::text AS tbl, conname
    FROM pg_constraint
    WHERE NOT convalidated
      AND connamespace = 'public'::regnamespace
  LOOP
    BEGIN
      EXECUTE format('ALTER TABLE %s VALIDATE CONSTRAINT %I', r.tbl, r.conname);
    EXCEPTION WHEN others THEN
      RAISE NOTICE 'Could not validate %.% : %', r.tbl, r.conname, SQLERRM;
    END;
  END LOOP;
END $$;
