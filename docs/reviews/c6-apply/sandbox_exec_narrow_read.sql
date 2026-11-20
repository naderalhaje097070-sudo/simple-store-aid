-- Review fix 2026-11-19: schema_usage added (table grants alone do not prove access; USAGE on the schema is also needed).
-- PROPOSED production read for sandbox_exec (NOT RUN on production; needs the owner's approval of this exact scope).
-- Catalog and counts only: no application rows, no query text, no client addresses, no secrets.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'role', (select json_build_object('login', rolcanlogin, 'bypassrls', rolbypassrls, 'super', rolsuper,
            'connlimit', rolconnlimit, 'valid_until', rolvaliduntil, 'config', rolconfig)
           from pg_roles where rolname = 'sandbox_exec'),
  'member_of', (select coalesce(json_agg(r.rolname order by r.rolname), '[]') from pg_auth_members m
                join pg_roles r on r.oid = m.roleid where m.member = 'sandbox_exec'::regrole),
  'members', (select coalesce(json_agg(r.rolname order by r.rolname), '[]') from pg_auth_members m
              join pg_roles r on r.oid = m.member where m.roleid = 'sandbox_exec'::regrole),
  'table_privs_outside_public', (select coalesce(json_agg(json_build_object('t', t, 'p', p) order by t), '[]')
     from (select n.nspname||'.'||c.relname t, string_agg(distinct a.privilege_type, ',') p
           from pg_class c join pg_namespace n on n.oid = c.relnamespace, aclexplode(c.relacl) a
           where a.grantee = 'sandbox_exec'::regrole and n.nspname <> 'public' and c.relkind in ('r','p','v','m','S','f')
           group by 1) g),
  'function_execute', (select count(*) from pg_proc p where has_function_privilege('sandbox_exec', p.oid, 'EXECUTE')
                       and p.pronamespace in ('public'::regnamespace, 'monjez_private'::regnamespace)
                       and not has_function_privilege('public', p.oid, 'EXECUTE')),
  'schema_usage', (select json_object_agg(n, has_schema_privilege('sandbox_exec', n, 'USAGE'))
                   from unnest(array['public','auth','storage','extensions','monjez_private']) n),
  'sessions_now', (select count(*) from pg_stat_activity where usename = 'sandbox_exec')
) as sandbox_exec_facts;
rollback;
