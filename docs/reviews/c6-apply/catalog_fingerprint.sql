begin transaction read only;
with ns as (select oid, nspname from pg_namespace where nspname in ('public','monjez_private')),
obj as (
 select 'schema' k, nspname n, md5(coalesce(nspacl::text,'')) h from pg_namespace where nspname in ('public','monjez_private')
 union all
 select 'table', ns.nspname||'.'||c.relname, md5(c.relkind::text||'|'||c.relrowsecurity||'|'||c.relforcerowsecurity||'|'||coalesce(c.relacl::text,'')||'|'||coalesce((select string_agg(attname||':'||format_type(atttypid,atttypmod)||':'||attnotnull||':'||coalesce(pg_get_expr(d.adbin,d.adrelid),'')||':'||coalesce(a.attacl::text,''),',' order by attnum) from pg_attribute a left join pg_attrdef d on d.adrelid=a.attrelid and d.adnum=a.attnum where a.attrelid=c.oid and attnum>0 and not attisdropped),''))
  from pg_class c join ns on ns.oid=c.relnamespace where c.relkind in ('r','p','v','m','S','f')
 union all
 select 'view', ns.nspname||'.'||c.relname, md5(pg_get_viewdef(c.oid)) from pg_class c join ns on ns.oid=c.relnamespace where c.relkind in ('v','m')
 union all
 select 'constraint', ns.nspname||'.'||c.relname||'.'||co.conname, md5(pg_get_constraintdef(co.oid)) from pg_constraint co join pg_class c on c.oid=co.conrelid join ns on ns.oid=c.relnamespace
 union all
 select 'index', ns.nspname||'.'||i.relname, md5(pg_get_indexdef(i.oid)) from pg_index x join pg_class i on i.oid=x.indexrelid join ns on ns.oid=i.relnamespace
 union all
 select 'policy', ns.nspname||'.'||c.relname||'.'||p.polname, md5(p.polpermissive::text||'|'||p.polcmd::text||'|'||coalesce((select string_agg(case when r=0 then 'public' else r::regrole::text end,',' order by 1) from unnest(p.polroles) r),'')||'|'||coalesce(pg_get_expr(p.polqual,p.polrelid),'')||'|'||coalesce(pg_get_expr(p.polwithcheck,p.polrelid),'')) from pg_policy p join pg_class c on c.oid=p.polrelid join ns on ns.oid=c.relnamespace
 union all
 select 'function', p.oid::regprocedure::text, md5(pg_get_functiondef(p.oid)||'|'||coalesce(p.proacl::text,'')||'|'||p.proowner::regrole::text) from pg_proc p join ns on ns.oid=p.pronamespace where p.prokind in ('f','p','w')
 union all
 select 'trigger', ns.nspname||'.'||c.relname||'.'||t.tgname, md5(pg_get_triggerdef(t.oid)) from pg_trigger t join pg_class c on c.oid=t.tgrelid join ns on ns.oid=c.relnamespace where not t.tgisinternal
 union all
 select 'type', ns.nspname||'.'||t.typname, md5(t.typtype::text||'|'||coalesce((select string_agg(enumlabel,',' order by enumsortorder) from pg_enum where enumtypid=t.oid),'')) from pg_type t join ns on ns.oid=t.typnamespace where t.typtype in ('e','d','c') and not exists(select 1 from pg_class c where c.reltype=t.oid and c.relkind<>'c')
 union all
 select 'default_acl', coalesce(d.defaclrole::regrole::text,'')||'.'||coalesce(n.nspname,'*')||'.'||d.defaclobjtype::text, md5(d.defaclacl::text) from pg_default_acl d left join pg_namespace n on n.oid=d.defaclnamespace
 union all
 select 'role', rolname, md5(rolcanlogin::text||'|'||rolsuper||'|'||rolbypassrls||'|'||rolinherit) from pg_roles where rolname !~ '^pg_'
 union all
 select 'extension', extname, md5(extversion||'|'||extnamespace::regnamespace::text) from pg_extension
)
select coalesce(json_agg(json_build_array(k,n,h) order by k,n),'[]') as fp, current_setting('transaction_read_only') as ro, (select count(*) from supabase_migrations.schema_migrations) as ledger from obj;
rollback;
