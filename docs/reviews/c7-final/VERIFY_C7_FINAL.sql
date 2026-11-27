-- C7 final read-only verification (production ledger constants). Review-only candidate.
-- Expected after BUNDLE_C1_C10.sql then BUNDLE_C7_FINAL.sql: every *_ok and every function field true.
-- Ledger fingerprints use the same expressions as the bundle guard and PRECHECK_target_ledger_read.sql.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from supabase_migrations.schema_migrations),
  'ledger_rows_ok', (select count(*) from supabase_migrations.schema_migrations) = 64,
  'ledger_versions_ok', (select md5(coalesce(string_agg(version, ',' ORDER BY version), '')) from supabase_migrations.schema_migrations) = 'a6ca71705682237fc4bc6b93c4f782b5',
  'ledger_content_ok', (select md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) from supabase_migrations.schema_migrations) = '1c671404c3969bc09f451c3cea7b608b',
  'f1_content_ok', (select md5(array_to_string(statements, E'\n')) from supabase_migrations.schema_migrations where version = '20261120140000') = 'af9502633216755ebbcc1613c6553897',
  'f2_content_ok', (select md5(array_to_string(statements, E'\n')) from supabase_migrations.schema_migrations where version = '20261120150000') = '52238e8a3bc99b9eefb7008efdf5dbab',
  'functions', json_build_object(
  'update_courier_outcome_v2', (select json_build_object(
      'body_ok', md5(p.prosrc) = 'd00b901b863f1cce3c54cc4720d4ec47',
      'security_definer', p.prosecdef,
      'search_path_public', p.proconfig = array['search_path=public'],
      'owner_postgres', pg_get_userbyid(p.proowner) = 'postgres',
      'authenticated_execute', has_function_privilege('authenticated', p.oid, 'EXECUTE'),
      'anon_no_execute', not has_function_privilege('anon', p.oid, 'EXECUTE'),
      'public_no_execute', not coalesce((select bool_or(a.grantee = 0) from aclexplode(p.proacl) a where a.privilege_type = 'EXECUTE'), false))
    from pg_proc p where p.oid = to_regprocedure('public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)')),
  'settle_courier_orders', (select json_build_object(
      'body_ok', md5(p.prosrc) = '412a7d5566df54a79b00056551153c2f',
      'security_definer', p.prosecdef,
      'search_path_public', p.proconfig = array['search_path=public'],
      'owner_postgres', pg_get_userbyid(p.proowner) = 'postgres',
      'authenticated_execute', has_function_privilege('authenticated', p.oid, 'EXECUTE'),
      'anon_no_execute', not has_function_privilege('anon', p.oid, 'EXECUTE'),
      'public_no_execute', not coalesce((select bool_or(a.grantee = 0) from aclexplode(p.proacl) a where a.privilege_type = 'EXECUTE'), false))
    from pg_proc p where p.oid = to_regprocedure('public.settle_courier_orders(uuid,uuid[])')),
  'close_day', (select json_build_object(
      'body_ok', md5(p.prosrc) = 'be592feb81af4f0ccbc64fba59d3067f',
      'security_definer', p.prosecdef,
      'search_path_public', p.proconfig = array['search_path=public'],
      'owner_postgres', pg_get_userbyid(p.proowner) = 'postgres',
      'authenticated_execute', has_function_privilege('authenticated', p.oid, 'EXECUTE'),
      'anon_no_execute', not has_function_privilege('anon', p.oid, 'EXECUTE'),
      'public_no_execute', not coalesce((select bool_or(a.grantee = 0) from aclexplode(p.proacl) a where a.privilege_type = 'EXECUTE'), false))
    from pg_proc p where p.oid = to_regprocedure('public.close_day(text)')))
) as c7_final_verify;
rollback;
