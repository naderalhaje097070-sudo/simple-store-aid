-- stage C10
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '1b94210e7c6bf663cba496d2421612ad' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110150000: expected exactly 61 known versions'; END IF;
  src := $src1b9ab46e$-- C-DEFPRIV-01: functions that postgres creates from now on are not executable by PUBLIC
-- (and therefore not by anon) unless a migration grants it explicitly.
-- Before: no global default ACL for postgres, so acldefault('f') = {=X/postgres,...}:
-- every new function, in any schema, was callable by anon until its migration
-- remembered REVOKE ... FROM PUBLIC.
-- Unchanged: existing functions keep their ACLs; the per-schema default for postgres in
-- public still grants EXECUTE on new public functions to authenticated and service_role.
-- Consequence: a new function outside public (e.g. a monjez_private helper used by an RLS
-- policy) needs an explicit GRANT EXECUTE to the roles that call it.
-- Not attempted: supabase_admin's defaults (postgres is not a member of supabase_admin).
-- Rollback: ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT EXECUTE ON FUNCTIONS TO PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
$src1b9ab46e$;
  IF md5(src) <> '731a07309336c928bc77c32cb4e3ca6b' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110150000_defpriv_function_execute_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110150000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110150000'; END IF;
  body := src;
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110150000', 'defpriv_function_execute_01', ARRAY[src], 'claude-c6');
END
$stage$;
