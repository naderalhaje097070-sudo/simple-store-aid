-- C-DEFPRIV-01 catalog guard: one row per violation (rule | object | detail).
-- Read-only. Scope: schemas public and monjez_private (the application schemas).
-- Rules carry no environment switches; the only exceptions are named objects in
-- the CTE "allowed_anon_exec", each with its reason.
WITH app_ns AS (
  SELECT oid, nspname FROM pg_namespace WHERE nspname IN ('public','monjez_private')
),
client AS (SELECT unnest(ARRAY['anon','authenticated']) AS r),
-- Trigger functions cannot be called through /rpc; these two predate the guard.
allowed_anon_exec(sig, reason) AS (VALUES
  ('public.touch_updated_at()', 'trigger function, RETURNS trigger'),
  ('public.update_updated_at_column()', 'trigger function, RETURNS trigger')
),
rels AS (
  SELECT c.oid, c.relname, c.relkind, n.nspname, c.relowner, c.relrowsecurity, c.reloptions
  FROM pg_class c JOIN app_ns n ON n.oid = c.relnamespace
  WHERE c.relkind IN ('r','p','v','m','S','f')
),
funcs AS (
  SELECT p.oid, n.nspname||'.'||p.proname||'('||pg_get_function_identity_arguments(p.oid)||')' AS sig, n.nspname, p.proowner, p.prosecdef, p.proconfig, p.prorettype
  FROM pg_proc p JOIN app_ns n ON n.oid = p.pronamespace
)
-- R1 owner: every application object is owned by postgres. Extension members are
-- reported too (no blanket extension exception).
SELECT 'R1_owner_not_postgres' AS rule, nspname||'.'||relname AS object, pg_get_userbyid(relowner) AS detail
  FROM rels WHERE pg_get_userbyid(relowner) <> 'postgres'
UNION ALL
SELECT 'R1_owner_not_postgres', sig, pg_get_userbyid(proowner) FROM funcs WHERE pg_get_userbyid(proowner) <> 'postgres'
UNION ALL
-- R2 a table a client can touch must have RLS and the restrictive live-actor policy.
SELECT 'R2_client_table_without_rls_or_live_actor', r.nspname||'.'||r.relname,
       'rls='||r.relrowsecurity||' live_actor='||EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid=r.oid
          AND p.polname='monjez_live_actor' AND NOT p.polpermissive)
  FROM rels r
  WHERE r.relkind IN ('r','p','f')
    AND EXISTS (SELECT 1 FROM client WHERE has_table_privilege(client.r, r.oid, 'SELECT,INSERT,UPDATE,DELETE'))
    AND (NOT r.relrowsecurity OR NOT EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid=r.oid
          AND p.polname='monjez_live_actor' AND NOT p.polpermissive))
UNION ALL
-- R2b a view a client can read must run with the caller's rights.
SELECT 'R2b_client_view_not_security_invoker', r.nspname||'.'||r.relname, coalesce(array_to_string(r.reloptions,','),'')
  FROM rels r
  WHERE r.relkind IN ('v','m')
    AND EXISTS (SELECT 1 FROM client WHERE has_table_privilege(client.r, r.oid, 'SELECT'))
    AND NOT coalesce('security_invoker=true' = ANY (r.reloptions) OR 'security_invoker=on' = ANY (r.reloptions), false)
UNION ALL
-- R3 anon (directly or through PUBLIC) may execute no application function, except named triggers.
SELECT 'R3_anon_can_execute', f.sig, CASE WHEN f.prorettype='trigger'::regtype THEN 'trigger' ELSE 'callable' END
  FROM funcs f
  WHERE has_function_privilege('anon', f.oid, 'EXECUTE')
    AND NOT EXISTS (SELECT 1 FROM allowed_anon_exec a WHERE a.sig = f.sig AND f.prorettype='trigger'::regtype)
UNION ALL
-- R4 no client TRUNCATE on any application relation.
SELECT 'R4_client_truncate', r.nspname||'.'||r.relname, client.r
  FROM rels r CROSS JOIN client
  WHERE r.relkind IN ('r','p') AND has_table_privilege(client.r, r.oid, 'TRUNCATE')
UNION ALL
-- R5 SECURITY DEFINER functions pin search_path.
SELECT 'R5_definer_without_search_path', f.sig, ''
  FROM funcs f
  WHERE f.prosecdef AND NOT EXISTS (SELECT 1 FROM unnest(coalesce(f.proconfig,'{}')) c WHERE c LIKE 'search_path=%')
UNION ALL
-- R6 future-object defaults: postgres's new functions are not executable by PUBLIC, and
-- postgres's defaults never give TRUNCATE or anything at all to anon.
SELECT 'R6_postgres_function_default_public_execute', 'pg_default_acl(postgres, global, f)',
       coalesce((SELECT defaclacl::text FROM pg_default_acl WHERE defaclrole='postgres'::regrole
                 AND defaclnamespace=0 AND defaclobjtype='f'), '<none: built-in default grants PUBLIC>')
  WHERE NOT EXISTS (SELECT 1 FROM pg_default_acl WHERE defaclrole='postgres'::regrole
                    AND defaclnamespace=0 AND defaclobjtype='f')
     OR EXISTS (SELECT 1 FROM pg_default_acl d, aclexplode(d.defaclacl) a WHERE d.defaclrole='postgres'::regrole
                AND d.defaclnamespace=0 AND d.defaclobjtype='f' AND a.grantee=0)
UNION ALL
SELECT 'R6_postgres_default_grants_client', CASE WHEN d.defaclnamespace=0 THEN '<global>' ELSE d.defaclnamespace::regnamespace::text END||'/'||d.defaclobjtype::text,
       pg_get_userbyid(a.grantee)||':'||a.privilege_type
  FROM pg_default_acl d, aclexplode(d.defaclacl) a
  WHERE d.defaclrole='postgres'::regrole
    AND (d.defaclnamespace=0 OR d.defaclnamespace IN (SELECT oid FROM app_ns))
    AND (a.grantee = 'anon'::regrole OR (a.grantee='authenticated'::regrole AND a.privilege_type='TRUNCATE'))
UNION ALL
-- R7 compatibility: every function an RLS policy on an application table depends on is
-- executable by the roles the policy applies to (authenticated, or PUBLIC = 0). After
-- C-DEFPRIV-01 a new helper outside public needs an explicit grant; this catches a miss.
SELECT DISTINCT 'R7_policy_function_not_executable', pr.oid::regprocedure::text,
       'policy '||pol.polname||' on '||c.relname||' for '||CASE WHEN rl.role=0 THEN 'PUBLIC' ELSE pg_get_userbyid(rl.role) END
  FROM pg_policy pol
  JOIN pg_class c ON c.oid = pol.polrelid
  JOIN app_ns n ON n.oid = c.relnamespace
  JOIN pg_depend d ON d.classid = 'pg_policy'::regclass AND d.objid = pol.oid AND d.refclassid = 'pg_proc'::regclass
  JOIN pg_proc pr ON pr.oid = d.refobjid
  CROSS JOIN LATERAL unnest(pol.polroles) AS rl(role)
  WHERE (rl.role = 0 AND NOT has_function_privilege('authenticated', pr.oid, 'EXECUTE'))
     OR (rl.role <> 0 AND NOT has_function_privilege(rl.role, pr.oid, 'EXECUTE'))
ORDER BY 1, 2;
