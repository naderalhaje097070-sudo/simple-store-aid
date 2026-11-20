-- stage C9
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> 'f0ce5eb1d369d3dca6cb930a74e19f19' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110140000: expected exactly 60 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> 'b80939110cdcd881eb07c46b5d1c22d7' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261110140000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src137a8ad6$-- C-TENANT-01: a signed-in client may write only the tenant columns the app writes.
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
$src137a8ad6$;
  IF md5(src) <> 'ccfed6b0972c49823b4924c602cc615d' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110140000_tenants_narrow_client_grants_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110140000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110140000'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110140000', 'tenants_narrow_client_grants_01', ARRAY[src], 'claude-c6');
END
$stage$;
