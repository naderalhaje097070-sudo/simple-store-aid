-- C6 read-only pre-check of the TARGET database (no rows of application data are read).
-- Run through the same tool as the apply, right before BUNDLE_C1_C10*.sql. Both *_ok must be true.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'db', current_database(), 'usr', current_user, 'pg', split_part(version(), ' ', 2),
  'ledger_rows', (select count(*) from supabase_migrations.schema_migrations),
  'ledger_versions_ok', (select md5(coalesce(string_agg(version, ',' ORDER BY version), '')) from supabase_migrations.schema_migrations) = '9235c3834be88ce50dba444bb15b5262',
  'ledger_content_ok', (select md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) from supabase_migrations.schema_migrations) = 'a3de2f506b1da505ae41c9fd553c87d7',
  'c6_versions_present', (select count(*) from supabase_migrations.schema_migrations where version in
     ('20260815170000','20260815171000','20261028213608','20261029044024','20261103060658',
      '20261106145346','20261110090000','20261110130000','20261110140000','20261110150000'))
) as c6_precheck;
rollback;
