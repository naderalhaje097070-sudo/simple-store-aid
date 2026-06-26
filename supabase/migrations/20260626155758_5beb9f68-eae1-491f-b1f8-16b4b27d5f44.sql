
-- Auto-assign owner role and link profile when a tenant is created.
CREATE OR REPLACE FUNCTION public.handle_new_tenant()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.owner_user_id IS NULL THEN
    RAISE EXCEPTION 'owner_user_id required';
  END IF;
  INSERT INTO public.user_roles(user_id, tenant_id, role)
    VALUES (NEW.owner_user_id, NEW.id, 'owner')
    ON CONFLICT (user_id, tenant_id, role) DO NOTHING;
  UPDATE public.profiles SET tenant_id = NEW.id
    WHERE id = NEW.owner_user_id AND tenant_id IS NULL;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS on_tenant_created ON public.tenants;
CREATE TRIGGER on_tenant_created
  AFTER INSERT ON public.tenants
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_tenant();
