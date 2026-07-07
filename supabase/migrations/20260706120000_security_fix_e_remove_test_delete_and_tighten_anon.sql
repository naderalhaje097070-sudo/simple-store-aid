-- ============================================================
-- Security Fix E — hardening before enabling agents/MCP or Pilot.
-- Migration only. No app/UI/financial-logic changes.
-- ============================================================

-- ------------------------------------------------------------
-- P1: Remove the E2E cleanup surface from production entirely.
-- ------------------------------------------------------------
-- public.__test_force_delete_e2e_order + public.__test_allowed_tenants were
-- built for E2E cleanup with the invariant "allowlist empty in production =
-- RPC inert". That invariant was broken: the allowlist was seeded out-of-band
-- (scripts/e2e/seed-allowlist.sql, via service_role) with real production
-- tenants, which turns on an owner-only, E2E-tagged, 24h-scoped delete path on
-- live tenants. It is not needed in production, so remove both objects.
--
-- Blast radius of the drop: none for business data. The RPC only ever deleted
-- rows explicitly tagged "E2E-<digits>"; dropping the allowlist table removes
-- only allowlist rows (its FK to tenants is ON DELETE CASCADE from tenants ->
-- allowlist, so dropping the allowlist never touches tenants).
DROP FUNCTION IF EXISTS public.__test_force_delete_e2e_order(uuid, uuid, text);
DROP TABLE    IF EXISTS public.__test_allowed_tenants;

-- ------------------------------------------------------------
-- P2: Tighten anon privileges (defense-in-depth).
-- ------------------------------------------------------------
-- The app performs NO unauthenticated data access: sign-in / sign-up go
-- through Supabase Auth (auth schema), and every public-schema read/write runs
-- as the authenticated role under RLS. The anon role therefore needs nothing in
-- the public schema. Today RLS already blocks anon (no anon policy,
-- current_tenant_id() is NULL for anon), but the broad default grants make RLS
-- the ONLY guard. Revoke them so a future RLS mistake cannot expose data.
REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon;

-- Keep future objects locked down for anon too (does not affect authenticated
-- or service_role, and does not re-grant anything).
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon;

-- No grant-back: no public/anon table or function is required by the auth or
-- onboarding flow (onboarding runs as an authenticated user).
--
-- NOTE ON authenticated (intentionally unchanged): it keeps RLS-scoped SELECT
-- for app usage, and its INSERT/UPDATE/DELETE on orders/order_items/payments
-- remain revoked (financial writes go through SECURITY DEFINER RPCs only).
