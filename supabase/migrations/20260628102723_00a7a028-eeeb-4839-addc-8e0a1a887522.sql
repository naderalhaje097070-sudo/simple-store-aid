-- Clean, single migration for the E2E cleanup channel.
-- Production posture: allowlist table is created EMPTY with no anon/authenticated
-- grants and no policies, so the cleanup RPC is inert for every user (including
-- tenant owners). Sandbox/E2E environments populate the allowlist out-of-band
-- via service_role using scripts/e2e/seed-allowlist.sql — never via a migration.

-- 1) Internal allowlist table. Service-role-only.
CREATE TABLE IF NOT EXISTS public.__test_allowed_tenants (
  tenant_id  uuid PRIMARY KEY REFERENCES public.tenants(id) ON DELETE CASCADE,
  note       text,
  created_at timestamptz NOT NULL DEFAULT now()
);

REVOKE ALL ON public.__test_allowed_tenants FROM PUBLIC;
REVOKE ALL ON public.__test_allowed_tenants FROM anon;
REVOKE ALL ON public.__test_allowed_tenants FROM authenticated;
GRANT  ALL ON public.__test_allowed_tenants TO service_role;

ALTER TABLE public.__test_allowed_tenants ENABLE ROW LEVEL SECURITY;
-- Intentionally no policies: anon/authenticated cannot see or touch this table
-- even if a stray grant ever leaks. Only SECURITY DEFINER functions (running
-- as the function owner) and service_role can read it.

-- 2) E2E cleanup RPC. Hardened from the first definition: owner-only,
-- allowlist-gated, E2E-tag required, tenant-scoped, recent rows only.
CREATE OR REPLACE FUNCTION public.__test_force_delete_e2e_order(
  p_order_id   uuid,
  p_product_id uuid,
  p_tag        text
) RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_order  public.orders%ROWTYPE;
  v_prod   public.products%ROWTYPE;
  v_now    timestamptz := now();
BEGIN
  IF p_tag IS NULL OR p_tag !~ '^E2E-[0-9]+$' THEN
    RAISE EXCEPTION 'invalid_e2e_tag';
  END IF;

  PERFORM public._assert_owner(v_tenant);

  -- HARD GATE: tenant must be explicitly allow-listed for test cleanup.
  -- Production = empty table = RPC is inert. Only service_role can populate.
  IF NOT EXISTS (
    SELECT 1 FROM public.__test_allowed_tenants WHERE tenant_id = v_tenant
  ) THEN
    RAISE EXCEPTION 'tenant_not_in_test_allowlist';
  END IF;

  IF p_order_id IS NOT NULL THEN
    SELECT * INTO v_order FROM public.orders WHERE id = p_order_id;
    IF FOUND THEN
      IF v_order.tenant_id <> v_tenant THEN RAISE EXCEPTION 'order_not_in_tenant'; END IF;
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

  IF p_product_id IS NOT NULL THEN
    SELECT * INTO v_prod FROM public.products WHERE id = p_product_id;
    IF FOUND THEN
      IF v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_in_tenant'; END IF;
      IF v_prod.created_at < v_now - interval '24 hours' THEN
        RAISE EXCEPTION 'product_too_old_for_test_cleanup';
      END IF;
      IF v_prod.name NOT LIKE p_tag || '%' THEN
        RAISE EXCEPTION 'product_not_e2e_tagged';
      END IF;
      DELETE FROM public.products WHERE id = p_product_id AND tenant_id = v_tenant;
    END IF;
  END IF;

  DELETE FROM public.day_closes
   WHERE tenant_id = v_tenant AND note = p_tag;

  RETURN jsonb_build_object('ok', true);
END
$function$;

REVOKE ALL ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) FROM anon;
GRANT  EXECUTE ON FUNCTION public.__test_force_delete_e2e_order(uuid, uuid, text) TO authenticated;