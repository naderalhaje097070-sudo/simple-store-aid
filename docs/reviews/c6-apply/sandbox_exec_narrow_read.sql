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
  'table_privs_outside_public', (select coalesce(json_agg(json_build_object('t', table_schema||'.'||table_name, 'p', p) order by table_schema, table_name), '[]')
     from (select table_schema, table_name, string_agg(privilege_type, ',' order by privilege_type) p
           from information_schema.role_table_grants
           where grantee = 'sandbox_exec' and table_schema not in ('public')
           group by 1, 2) g),
  'function_execute', (select count(*) from pg_proc p where has_function_privilege('sandbox_exec', p.oid, 'EXECUTE')
                       and p.pronamespace in ('public'::regnamespace, 'monjez_private'::regnamespace)
                       and not has_function_privilege('public', p.oid, 'EXECUTE')),
  'sessions_now', (select count(*) from pg_stat_activity where usename = 'sandbox_exec')
) as sandbox_exec_facts;
rollback;
