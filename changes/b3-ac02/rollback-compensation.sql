-- Owner-run forward containment only. Temporarily disables client onboarding/settings.
-- Does not restore writable billing fields. Service-role rights and data remain intact.
BEGIN;
REVOKE INSERT, UPDATE ON TABLE public.tenants FROM authenticated;
REVOKE INSERT (id, name, owner_user_id, created_at, updated_at, timezone, business_type), UPDATE (id, name, owner_user_id, created_at, updated_at, timezone, business_type) ON public.tenants FROM authenticated;
COMMIT;
