-- read only: c6_dx_* and c6_fx_* footprint in the isolated lab. Expected: all zero.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_exists', to_regclass('supabase_migrations.schema_migrations') is not null,
  'c6_dx_tables', (select count(*) from pg_tables where schemaname = 'public' and tablename like 'c6\_dx\_%'),
  'c6_dx_functions', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname like 'c6\_dx\_%'),
  'public_tables_total', (select count(*) from pg_tables where schemaname = 'public'),
  'public_functions_total', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace)
) as c6_dx_baseline;
rollback;
