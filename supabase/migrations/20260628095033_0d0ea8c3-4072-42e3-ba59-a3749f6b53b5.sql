CREATE OR REPLACE FUNCTION public.__test_force_delete_e2e_order(
  p_order_id   uuid,
  p_product_id uuid,
  p_tag        text
) RETURNS jsonb
  LANGUAGE plpgsql
  SECURITY DEFINER
  SET search_path = public
AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_order  public.orders%ROWTYPE;
  v_prod   public.products%ROWTYPE;
  v_now    timestamptz := now();
BEGIN
  -- Hard guard: tag must look like an E2E test tag (E2E-<unix-ts>).
  IF p_tag IS NULL OR p_tag !~ '^E2E-[0-9]+$' THEN
    RAISE EXCEPTION 'invalid_e2e_tag';
  END IF;

  -- Only owners of the current tenant may invoke. Test runner signs in as owner.
  PERFORM public._assert_owner(v_tenant);

  -- Order: must be in tenant, recent, and carry the E2E tag in its items.
  IF p_order_id IS NOT NULL THEN
    SELECT * INTO v_order FROM public.orders WHERE id = p_order_id;
    IF FOUND THEN
      IF v_order.tenant_id <> v_tenant THEN
        RAISE EXCEPTION 'order_not_in_tenant';
      END IF;
      IF v_order.created_at < v_now - interval '24 hours' THEN
        RAISE EXCEPTION 'order_too_old_for_test_cleanup';
      END IF;
      IF NOT EXISTS (
        SELECT 1 FROM public.order_items
        WHERE order_id = p_order_id AND name LIKE p_tag || '%'
      ) THEN
        RAISE EXCEPTION 'order_not_e2e_tagged';
      END IF;

      DELETE FROM public.payments    WHERE order_id = p_order_id AND tenant_id = v_tenant;
      DELETE FROM public.order_items WHERE order_id = p_order_id AND tenant_id = v_tenant;
      DELETE FROM public.orders      WHERE id = p_order_id        AND tenant_id = v_tenant;
    END IF;
  END IF;

  -- Product: must be in tenant, recent, and its name must start with the E2E tag.
  IF p_product_id IS NOT NULL THEN
    SELECT * INTO v_prod FROM public.products WHERE id = p_product_id;
    IF FOUND THEN
      IF v_prod.tenant_id <> v_tenant THEN
        RAISE EXCEPTION 'product_not_in_tenant';
      END IF;
      IF v_prod.created_at < v_now - interval '24 hours' THEN
        RAISE EXCEPTION 'product_too_old_for_test_cleanup';
      END IF;
      IF v_prod.name NOT LIKE p_tag || '%' THEN
        RAISE EXCEPTION 'product_not_e2e_tagged';
      END IF;
      DELETE FROM public.products WHERE id = p_product_id AND tenant_id = v_tenant;
    END IF;
  END IF;

  -- day_closes carrying this exact test tag in note.
  DELETE FROM public.day_closes
   WHERE tenant_id = v_tenant AND note = p_tag;

  RETURN jsonb_build_object('ok', true);
END
$$;

-- Lock down execution: no anon, no PUBLIC. Only authenticated owners can call,
-- and the _assert_owner guard inside the function further restricts it.
REVOKE ALL ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) FROM anon;
GRANT  EXECUTE ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) TO authenticated;