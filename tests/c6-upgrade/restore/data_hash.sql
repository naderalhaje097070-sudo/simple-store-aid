-- per-table row count and md5 of all rows ordered by their text form (read only)
begin; -- rolled back at the end
create temp table h(t text, n bigint, m text) on commit drop;
do $$ declare r record; n bigint; m text; begin
 for r in select format('%I.%I',schemaname,tablename) q from pg_tables
          where schemaname in ('public','monjez_private','auth','supabase_migrations') order by 1 loop
  execute format('select count(*), md5(coalesce(string_agg(x::text, E''\n'' order by x::text),'''')) from %s x', r.q) into n, m;
  insert into h values (r.q, n, m);
 end loop; end $$;
select t||'|'||n||'|'||m from h order by t;
rollback;
