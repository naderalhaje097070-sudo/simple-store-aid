-- C-TENANT-01: a signed-in client may write only the tenant columns the app writes.
-- App writes: INSERT(name, owner_user_id) at onboarding; UPDATE(name | business_type | timezone).
-- Before: authenticated held INSERT and UPDATE on (id, name, owner_user_id, created_at,
-- updated_at, timezone, business_type) from 20261021080927_tenant_entitlement_01.
-- After:  INSERT(name, owner_user_id, timezone, business_type); UPDATE(name, timezone, business_type).
-- id, created_at and updated_at keep their defaults and the touch trigger; ownership is
-- set only at insert (RLS CHECK owner_user_id = auth.uid()). service_role is unchanged.
BEGIN;
REVOKE INSERT (id, created_at, updated_at) ON public.tenants FROM authenticated;
REVOKE UPDATE (id, owner_user_id, created_at, updated_at) ON public.tenants FROM authenticated;
COMMIT;
