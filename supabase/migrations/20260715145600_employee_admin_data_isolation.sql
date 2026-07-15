-- Delivery employees receive the tenant name through get_my_courier_portal().
-- They do not need direct access to tenant billing metadata or subscriptions.

DO $$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT policyname
      FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename = 'tenants'
       AND cmd IN ('SELECT', 'ALL')
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.tenants', r.policyname);
  END LOOP;

  FOR r IN
    SELECT policyname
      FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename = 'subscriptions'
       AND cmd = 'SELECT'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.subscriptions', r.policyname);
  END LOOP;
END $$;

CREATE POLICY "owners read their tenant" ON public.tenants
FOR SELECT TO authenticated USING (
  owner_user_id = auth.uid()
  OR public.has_owner_role(auth.uid(), id)
);

CREATE POLICY "owners read tenant subscriptions" ON public.subscriptions
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
