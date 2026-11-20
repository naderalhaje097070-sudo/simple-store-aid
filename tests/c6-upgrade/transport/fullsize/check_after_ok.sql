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
             xpath('/row/q/text()', query_to_xml(format('select max(qty) filter (where id = 1) as q from public.c6_fx_t%s', i), false, true, ''))::text[] as q,
             xpath('/row/r/text()', query_to_xml(format('select public.c6_fx_f%s() as r', i), false, true, ''))::text[] as r
      from t where rel is not null and fn is not null),
p as (select v.i, (v.table_ok and v.fn_ok and v.numeric_ok and v.ledger_ok
                  and d.n[1] = '1' and d.q[1]::numeric = v.i + 0.5 and d.r[1]::int = v.i) is true as pass,
             v.table_ok, v.numeric_ok, v.ledger_ok, d.n[1] as n, d.q[1] as q, d.r[1] as r
      from v left join d using (i))
-- Review fix (#97, Codex): each block's predicate is wrapped in IS TRUE, so NULL (a missing row or a NULL
-- function result) fails closed; ok requires ten passing blocks, and per_block.pass is the same boolean.
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from public.c6_fx_ledger),
  'per_block', (select json_agg(json_build_object('block', i, 'pass', pass, 'table', table_ok, 'numeric', numeric_ok,
                 'ledger', ledger_ok, 'rows', n, 'qty', q, 'fn', r) order by i) from p),
  'ok', (select count(*) from public.c6_fx_ledger) = 10 and (select count(*) filter (where pass) from p) = 10
) as c6_fx_after_ok;
rollback;
