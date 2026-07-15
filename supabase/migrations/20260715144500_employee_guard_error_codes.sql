CREATE OR REPLACE FUNCTION public.protect_profile_access_fields()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  IF auth.uid() = OLD.id THEN
    IF NEW.disabled_at IS DISTINCT FROM OLD.disabled_at THEN
      RAISE EXCEPTION 'profile_access_fields_locked' USING ERRCODE = '42501';
    END IF;

    IF NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
      IF NOT (
        OLD.tenant_id IS NULL
        AND NEW.tenant_id IS NOT NULL
        AND EXISTS (
          SELECT 1 FROM public.tenants t
          WHERE t.id = NEW.tenant_id AND t.owner_user_id = auth.uid()
        )
      ) THEN
        RAISE EXCEPTION 'profile_access_fields_locked' USING ERRCODE = '42501';
      END IF;
    END IF;
  END IF;
  RETURN NEW;
END $$;

REVOKE ALL ON FUNCTION public.protect_profile_access_fields() FROM PUBLIC, anon, authenticated;
