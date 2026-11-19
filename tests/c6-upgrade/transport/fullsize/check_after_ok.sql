-- read only: the ten expected effects of fullsize_ok.sql, by VALUE. Expected: ok = true.
begin transaction read only;
with t as (select i, to_regclass('public.c6_fx_t' || i) rel, to_regprocedure('public.c6_fx_f' || i || '()') fn
           from generate_series(1, 10) i),
v as (select i, rel is not null as table_ok, fn is not null as fn_ok,
             (select data_type = 'numeric' from information_schema.columns where table_schema = 'public'
               and table_name = 'c6_fx_t' || i and column_name = 'qty') as numeric_ok,
             (select count(*) from public.c6_fx_ledger l where l.block = i
               and l.pad_md5 = case when i = 10 then 'f40e3f06aeefddc3b08df5a5e3dbe82d' else '5249767b6f691d5632bafe479d95001c' end) = 1 as ledger_ok
      from t),
d as (select i, xpath('/row/n/text()', query_to_xml(format('select count(*) as n from public.c6_fx_t%s', i), false, true, ''))::text[] as n,
             xpath('/row/q/text()', query_to_xml(format('select qty as q from public.c6_fx_t%s where id = 1', i), false, true, ''))::text[] as q,
             xpath('/row/r/text()', query_to_xml(format('select public.c6_fx_f%s() as r', i), false, true, ''))::text[] as r
      from t where rel is not null and fn is not null)
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from public.c6_fx_ledger),
  'per_block', (select json_agg(json_build_object('block', v.i, 'table', v.table_ok, 'numeric', v.numeric_ok, 'ledger', v.ledger_ok,
                 'rows', d.n[1], 'qty', d.q[1], 'fn', d.r[1]) order by v.i) from v left join d using (i)),
  'ok', (select count(*) from public.c6_fx_ledger) = 10
        and (select bool_and(v.table_ok and v.fn_ok and coalesce(v.numeric_ok, false) and v.ledger_ok
                             and d.n[1] = '1' and d.q[1]::numeric = v.i + 0.5 and d.r[1]::int = v.i)
             from v left join d using (i))
) as c6_fx_after_ok;
rollback;
