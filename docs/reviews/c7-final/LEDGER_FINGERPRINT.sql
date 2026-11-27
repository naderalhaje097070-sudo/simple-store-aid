-- The exact ledger fingerprint SQL used by the C6/C7 guards, PRECHECK_target_ledger_read.sql, VERIFY_C7_FINAL.sql
-- and tests/c6-upgrade/c7_final_selftest.sh (copied verbatim; read only).
begin transaction read only;
select count(*) as ledger_rows,
       md5(coalesce(string_agg(version, ',' ORDER BY version), '')) as versions_md5,
       md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) as content_md5
from supabase_migrations.schema_migrations;
rollback;
