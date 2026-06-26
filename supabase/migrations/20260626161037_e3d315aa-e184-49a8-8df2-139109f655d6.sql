-- 1) Fix RLS helper function grants
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT n.nspname AS schema_name, p.proname AS function_name,
           pg_get_function_identity_arguments(p.oid) AS args
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.proname IN ('current_tenant_id','has_role','has_owner_role','has_staff_or_owner_role')
  LOOP
    EXECUTE format('REVOKE ALL ON FUNCTION %I.%I(%s) FROM PUBLIC', r.schema_name, r.function_name, r.args);
    EXECUTE format('REVOKE ALL ON FUNCTION %I.%I(%s) FROM anon',   r.schema_name, r.function_name, r.args);
    EXECUTE format('GRANT EXECUTE ON FUNCTION %I.%I(%s) TO authenticated', r.schema_name, r.function_name, r.args);
  END LOOP;
END $$;

-- 2) Clean up duplicate empty tenant for pilot owner (keep tenant referenced by profile)
DO $$
DECLARE
  v_owner  uuid := 'b0b5cc7b-a577-40ea-b523-c99334b5f817';
  v_keep   uuid;
  v_dup    uuid;
  v_has_data boolean;
BEGIN
  SELECT tenant_id INTO v_keep FROM public.profiles WHERE id = v_owner;
  IF v_keep IS NULL THEN RETURN; END IF;

  FOR v_dup IN
    SELECT id FROM public.tenants
    WHERE owner_user_id = v_owner AND id <> v_keep
  LOOP
    SELECT EXISTS(
      SELECT 1 FROM public.products    WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.customers   WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.orders      WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.payments    WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.expenses    WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.couriers    WHERE tenant_id=v_dup UNION ALL
      SELECT 1 FROM public.day_closes  WHERE tenant_id=v_dup
    ) INTO v_has_data;

    IF NOT v_has_data THEN
      DELETE FROM public.user_roles WHERE tenant_id = v_dup;
      DELETE FROM public.tenants    WHERE id = v_dup;
    END IF;
  END LOOP;
END $$;
