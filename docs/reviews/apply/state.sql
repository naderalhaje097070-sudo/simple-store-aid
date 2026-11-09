with
fpub as (select p.proname||':'||md5(pg_get_functiondef(p.oid)) x from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public'),
fprv as (select p.proname||':'||md5(pg_get_functiondef(p.oid)) x from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='monjez_private'),
facl as (select n.nspname||'.'||p.proname||':'||a.grantee::regrole::text||':'||a.privilege_type x from pg_proc p join pg_namespace n on n.oid=p.pronamespace cross join lateral aclexplode(coalesce(p.proacl, acldefault('f',p.proowner))) a where n.nspname in ('public','monjez_private')),
pol as (select c.relname||':'||p.polname||':'||p.polpermissive::text||':'||p.polcmd::text||':'||coalesce(pg_get_expr(p.polqual,p.polrelid),'')||':'||coalesce(pg_get_expr(p.polwithcheck,p.polrelid),'') x from pg_policy p join pg_class c on c.oid=p.polrelid join pg_namespace n on n.oid=c.relnamespace where n.nspname='public'),
tacl as (select c.relname||':'||a.grantee::regrole::text||':'||a.privilege_type x from pg_class c join pg_namespace n on n.oid=c.relnamespace cross join lateral aclexplode(coalesce(c.relacl, acldefault('r',c.relowner))) a where n.nspname='public' and c.relkind='r'),
cacl as (select c.relname||'.'||at.attname||':'||a.grantee::regrole::text||':'||a.privilege_type x from pg_attribute at join pg_class c on c.oid=at.attrelid join pg_namespace n on n.oid=c.relnamespace cross join lateral aclexplode(at.attacl) a where n.nspname='public' and at.attacl is not null),
dacl as (select d.defaclrole::regrole::text||':'||coalesce(d.defaclnamespace::regnamespace::text,'-')||':'||d.defaclobjtype::text||':'||a.grantee::regrole::text||':'||a.privilege_type x from pg_default_acl d cross join lateral aclexplode(d.defaclacl) a),
dat as (select c.relname||':'||(xpath('/row/h/text()', query_to_xml(format('select md5(coalesce(string_agg(t::text, %L order by t::text collate "C"),%L)) h from public.%I t','|','',c.relname), false, true, '')))[1]::text x from pg_class c join pg_namespace s on s.oid=c.relnamespace where s.nspname='public' and c.relkind='r')
select json_build_object(
 'ledger', (select count(*) from supabase_migrations.schema_migrations),
 'fn_public', (select md5(coalesce(string_agg(x, ',' order by x),'')) from fpub),
 'fn_private', (select md5(coalesce(string_agg(x, ',' order by x),'')) from fprv),
 'fn_acl', (select md5(coalesce(string_agg(x, ',' order by x),'')) from facl),
 'functions_public', (select count(*) from fpub),
 'policies', (select md5(coalesce(string_agg(x, ',' order by x),'')) from pol),
 'policies_n', (select count(*) from pol),
 'table_acl', (select md5(coalesce(string_agg(x, ',' order by x),'')) from tacl),
 'col_acl', (select md5(coalesce(string_agg(x, ',' order by x),'')) from cacl),
 'default_acl', (select md5(coalesce(string_agg(x, ',' order by x),'')) from dacl),
 'email_service_only', (select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname in ('enqueue_email','read_email_batch','delete_email','move_to_dlq','email_queue_dispatch') and not has_function_privilege('authenticated',p.oid,'execute')),
 'private_tables', (select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='monjez_private' and c.relkind='r'),
 'data_hash', (select md5(string_agg(x, ',' order by x)) from dat)
);
