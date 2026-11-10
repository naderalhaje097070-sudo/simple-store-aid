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
-- A live-actor policy only counts if it is the account guard in substance: RESTRICTIVE,
-- for ALL commands, applying to every client role that holds a privilege on the table,
-- both USING and WITH CHECK present, each one of PostgreSQL's own deparsed forms of
-- calling monjez_private.actor_is_active() (21 tables use the SELECT-wrapped form, one
-- the direct call), and depending on that function and on no column or other function.
-- A deparse change after a PostgreSQL upgrade makes this fail closed, never pass.
live_forms(expr) AS (VALUES
  ('( SELECT monjez_private.actor_is_active() AS actor_is_active)'),
  ('monjez_private.actor_is_active()')
),
good_live AS (
  SELECT p.polrelid
  FROM pg_policy p
  WHERE p.polname = 'monjez_live_actor' AND NOT p.polpermissive AND p.polcmd = '*'
    AND pg_get_expr(p.polqual, p.polrelid) IN (SELECT expr FROM live_forms)
    AND pg_get_expr(p.polwithcheck, p.polrelid) IN (SELECT expr FROM live_forms)
    AND NOT EXISTS (SELECT 1 FROM client
                    WHERE has_table_privilege(client.r, p.polrelid, 'SELECT,INSERT,UPDATE,DELETE')
                      AND NOT (client.r::regrole::oid = ANY (p.polroles) OR 0 = ANY (p.polroles)))
    AND (SELECT array_agg(DISTINCT d.refobjid::regprocedure::text) FROM pg_depend d
         WHERE d.classid='pg_policy'::regclass AND d.objid=p.oid AND d.refclassid='pg_proc'::regclass)
        = ARRAY['monjez_private.actor_is_active()']
    AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid='pg_policy'::regclass AND d.objid=p.oid
                    AND d.refclassid='pg_class'::regclass AND d.refobjsubid > 0)
),
-- search_path entries of SECURITY DEFINER functions, in order.
sp AS (
  SELECT p.oid, e.entry, e.pos, count(*) OVER (PARTITION BY p.oid) AS n
  FROM pg_proc p JOIN app_ns n ON n.oid = p.pronamespace
  CROSS JOIN LATERAL unnest(p.proconfig) AS c(cfg)
  CROSS JOIN LATERAL unnest(string_to_array(substr(c.cfg, 13), ',')) WITH ORDINALITY AS e0(raw, pos)
  CROSS JOIN LATERAL (SELECT btrim(btrim(e0.raw), '"') AS entry, e0.pos) e
  WHERE p.prosecdef AND c.cfg LIKE 'search_path=%'
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
       'rls='||r.relrowsecurity||' live_actor_valid='||(r.oid IN (SELECT polrelid FROM good_live))
  FROM rels r
  WHERE r.relkind IN ('r','p','f')
    AND EXISTS (SELECT 1 FROM client WHERE has_table_privilege(client.r, r.oid, 'SELECT,INSERT,UPDATE,DELETE'))
    AND (NOT r.relrowsecurity OR r.oid NOT IN (SELECT polrelid FROM good_live))
UNION ALL
-- R2c a PERMISSIVE policy that applies to a client role and depends on nothing but its own
-- table is a constant; anything but constant false opens every row to that role.
SELECT 'R2c_open_permissive_policy', n.nspname||'.'||c.relname||' / '||p.polname,
       'using='||coalesce(pg_get_expr(p.polqual,p.polrelid),'-')||' check='||coalesce(pg_get_expr(p.polwithcheck,p.polrelid),'-')
  FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid JOIN app_ns n ON n.oid=c.relnamespace
  WHERE p.polpermissive
    AND (0 = ANY (p.polroles) OR EXISTS (SELECT 1 FROM client WHERE client.r::regrole::oid = ANY (p.polroles)))
    AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.classid='pg_policy'::regclass AND d.objid=p.oid
                    AND NOT (d.refclassid='pg_class'::regclass AND d.refobjid=p.polrelid AND d.refobjsubid=0))
    AND NOT (coalesce(pg_get_expr(p.polqual,p.polrelid),'false')='false'
             AND coalesce(pg_get_expr(p.polwithcheck,p.polrelid),'false')='false')
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
-- R5b every search_path entry is trusted: '' or pg_catalog; pg_temp only in last place;
-- no "$user"; otherwise an existing schema in which no client role (nor PUBLIC) may CREATE.
SELECT 'R5b_definer_untrusted_search_path', f.sig, sp.pos||':'||coalesce(nullif(sp.entry,''),'""')
  FROM sp JOIN funcs f ON f.oid = sp.oid
  WHERE NOT (
    sp.entry IN ('', 'pg_catalog')
    OR (sp.entry = 'pg_temp' AND sp.pos = sp.n)
    OR (sp.entry NOT IN ('pg_temp', '$user')
        AND EXISTS (SELECT 1 FROM pg_namespace ns WHERE ns.nspname = sp.entry
                    AND NOT has_schema_privilege('anon', ns.oid, 'CREATE')
                    AND NOT has_schema_privilege('authenticated', ns.oid, 'CREATE')))
  )
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
UNION ALL
-- R8 crash guard (observed 2026-11-10, local Supabase PostgreSQL 17.6 image): calling a
-- non-definer SQL-language function that itself calls a function the caller may not
-- EXECUTE terminated the backend with signal 11 instead of raising 42501 (8 reproductions,
-- volatile/stable/BEGIN ATOMIC alike; plpgsql raises 42501 cleanly). Static text scan of the
-- body: any name( ... ) that resolves to an application/auth/extensions function the
-- client role cannot execute. Heuristic by design: it can over-report, never execute.
SELECT DISTINCT 'R8_sql_function_calls_function_caller_cannot_execute', f.sig,
       cr.r||' -> '||m[1]||coalesce('.'||m[2],'')
  FROM funcs f
  JOIN pg_proc p ON p.oid = f.oid JOIN pg_language l ON l.oid = p.prolang AND l.lanname = 'sql'
  CROSS JOIN client cr
  CROSS JOIN LATERAL regexp_matches(p.prosrc, '(?:^|[^.a-z0-9_"])([a-z_][a-z0-9_]*)(?:\.([a-z_][a-z0-9_]*))?\s*\(', 'gi') AS m
  WHERE NOT f.prosecdef AND has_function_privilege(cr.r, f.oid, 'EXECUTE')
    AND EXISTS (SELECT 1 FROM pg_proc q JOIN pg_namespace qn ON qn.oid = q.pronamespace
                WHERE (CASE WHEN m[2] IS NULL THEN q.proname = lower(m[1])
                            AND qn.nspname IN ('public','monjez_private','auth','extensions')
                            ELSE qn.nspname = lower(m[1]) AND q.proname = lower(m[2]) END))
    AND NOT EXISTS (SELECT 1 FROM pg_proc q JOIN pg_namespace qn ON qn.oid = q.pronamespace
                WHERE (CASE WHEN m[2] IS NULL THEN q.proname = lower(m[1])
                            ELSE qn.nspname = lower(m[1]) AND q.proname = lower(m[2]) END)
                  AND has_function_privilege(cr.r, q.oid, 'EXECUTE'))
ORDER BY 1, 2;
