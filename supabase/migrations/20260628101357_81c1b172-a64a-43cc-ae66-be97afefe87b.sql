-- Remove any sandbox/E2E rows previously seeded by a public migration into
-- public.__test_allowed_tenants. After this migration the allowlist is empty
-- in Production. Sandbox/E2E environments re-populate the allowlist
-- out-of-band via service_role (see scripts/e2e/seed-allowlist.sql), never
-- from a public migration.
DELETE FROM public.__test_allowed_tenants WHERE note = 'sandbox-e2e';