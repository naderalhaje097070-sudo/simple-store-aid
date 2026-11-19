-- read only: the ten expected effects of fullsize_ok.sql. Expected: ok = true.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from public.c6_fx_ledger),
  'ledger_md5_ok', (select count(*) from public.c6_fx_ledger where pad_md5 = '5249767b6f691d5632bafe479d95001c'),
  'tables', (select count(*) from pg_tables where schemaname = 'public' and tablename ~ '^c6_fx_t([1-9]|10)$'),
  'numeric_columns', (select count(*) from information_schema.columns where table_schema = 'public'
                      and table_name ~ '^c6_fx_t([1-9]|10)$' and column_name = 'qty' and data_type = 'numeric'),
  'functions', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname ~ '^c6_fx_f([1-9]|10)$'),
  'ok', (select count(*) from public.c6_fx_ledger) = 10
        and (select count(*) from public.c6_fx_ledger where pad_md5 = '5249767b6f691d5632bafe479d95001c') = 10
        and (select count(*) from pg_tables where schemaname = 'public' and tablename ~ '^c6_fx_t([1-9]|10)$') = 10
        and (select count(*) from information_schema.columns where table_schema = 'public'
             and table_name ~ '^c6_fx_t([1-9]|10)$' and column_name = 'qty' and data_type = 'numeric') = 10
        and (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname ~ '^c6_fx_f([1-9]|10)$') = 10
) as c6_fx_after_ok;
rollback;
