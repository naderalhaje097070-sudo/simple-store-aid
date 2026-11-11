"""C-DEFPRIV-01 catalog guard on the isolated local stack.

1. Baseline: tests/catalog-guard/violations.sql must return no rows on the candidate.
2. Negative controls: each rule is shown to fire on a deliberately broken object
   created inside a transaction that is always rolled back.
3. Compatibility controls (also rolled back): what the new default means for the next
   migration: a new public function is callable by authenticated and service_role
   but not anon; a new monjez_private function needs an explicit grant.
Nothing is committed. Loopback only.
"""
import json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIOLATIONS = (HERE / 'violations.sql').read_text()
PSQL = ['psql', '-X', '-q', '-At', '-F', '|', '-v', 'ON_ERROR_STOP=1']


def guard():
    bad = []
    if os.environ.get('CI_ISOLATED_SUPABASE') != '1': bad.append('CI_ISOLATED_SUPABASE must equal 1')
    if os.environ.get('PGHOST') not in ('127.0.0.1', 'localhost'): bad.append('PGHOST must be loopback')
    if os.environ.get('PGPORT') != '54322': bad.append('PGPORT must equal 54322')
    if os.environ.get('PGUSER') != 'postgres' or os.environ.get('PGDATABASE') != 'postgres':
        bad.append('PGUSER/PGDATABASE must equal postgres')
    if os.environ.get('PGSERVICE') or os.environ.get('PGSERVICEFILE') or os.environ.get('PGHOSTADDR'):
        bad.append('PGSERVICE/PGSERVICEFILE/PGHOSTADDR not allowed')
    if bad:
        sys.exit('CATALOG_GUARD_BLOCKED: ' + '; '.join(bad))


def run(setup, query):
    """BEGIN; setup; query; ROLLBACK. Returns (ok, stdout rows, stderr)."""
    r = subprocess.run(PSQL, input=f'BEGIN;\n{setup}\n{query}\nROLLBACK;\n',
                       capture_output=True, text=True, timeout=60)
    rows = [tuple(line.split('|')) for line in r.stdout.splitlines() if line.strip()]
    return r.returncode == 0, rows, r.stderr.strip()


NEGATIVE = {
    # name: (setup SQL, expected rule, expected object substring)
    'R1_owner': ("GRANT CREATE ON SCHEMA public TO authenticated;"
                 " CREATE TABLE public._guard_r1(id int); ALTER TABLE public._guard_r1 OWNER TO authenticated;",
                 'R1_owner_not_postgres', 'public._guard_r1'),
    'R2_no_rls': ("CREATE TABLE public._guard_r2(id int); GRANT SELECT ON public._guard_r2 TO authenticated;",
                  'R2_client_table_without_rls_or_live_actor', 'public._guard_r2'),
    'R2_rls_without_live_actor': ("CREATE TABLE public._guard_r2b(id int); ALTER TABLE public._guard_r2b ENABLE ROW LEVEL SECURITY;"
                                  " GRANT SELECT ON public._guard_r2b TO authenticated;",
                                  'R2_client_table_without_rls_or_live_actor', 'public._guard_r2b'),
    'R2_permissive_live_actor': ("CREATE TABLE public._guard_r2c(id int); ALTER TABLE public._guard_r2c ENABLE ROW LEVEL SECURITY;"
                                 " CREATE POLICY monjez_live_actor ON public._guard_r2c AS PERMISSIVE TO authenticated USING (true);"
                                 " GRANT SELECT ON public._guard_r2c TO authenticated;",
                                 'R2_client_table_without_rls_or_live_actor', 'public._guard_r2c'),
    # DEFPRIV-R2-COLUMN: column-only grants are client access too (table defaults revoked).
    'R2_column_only_authenticated': ("CREATE TABLE public._guard_c1(id int, secret text);"
                                     " REVOKE ALL ON public._guard_c1 FROM PUBLIC, anon, authenticated;"
                                     " GRANT SELECT (secret) ON public._guard_c1 TO authenticated;",
                                     'R2_client_table_without_rls_or_live_actor', 'public._guard_c1'),
    'R2_column_only_anon_insert': ("CREATE TABLE public._guard_c2(id int, secret text);"
                                   " REVOKE ALL ON public._guard_c2 FROM PUBLIC, anon, authenticated;"
                                   " GRANT INSERT (secret) ON public._guard_c2 TO anon;",
                                   'R2_client_table_without_rls_or_live_actor', 'public._guard_c2'),
    'R2_live_actor_misses_column_role': ("CREATE TABLE public._guard_c3(id int, secret text);"
                                         " ALTER TABLE public._guard_c3 ENABLE ROW LEVEL SECURITY;"
                                         " CREATE POLICY monjez_live_actor ON public._guard_c3 AS RESTRICTIVE TO authenticated"
                                         " USING ((SELECT monjez_private.actor_is_active())) WITH CHECK ((SELECT monjez_private.actor_is_active()));"
                                         " REVOKE ALL ON public._guard_c3 FROM PUBLIC, anon, authenticated;"
                                         " GRANT SELECT (secret) ON public._guard_c3 TO anon;",
                                         'R2_client_table_without_rls_or_live_actor', 'public._guard_c3'),
    'R2b_column_readable_view': ("CREATE VIEW public._guard_cv AS SELECT 1 AS x;"
                                 " REVOKE ALL ON public._guard_cv FROM PUBLIC, anon, authenticated;"
                                 " GRANT SELECT (x) ON public._guard_cv TO authenticated;",
                                 'R2b_client_view_not_security_invoker', 'public._guard_cv'),
    'R2b_definer_view': ("CREATE VIEW public._guard_v AS SELECT 1 AS x; GRANT SELECT ON public._guard_v TO authenticated;",
                         'R2b_client_view_not_security_invoker', 'public._guard_v'),
    'R3_anon_function': ("CREATE FUNCTION public._guard_f() RETURNS int LANGUAGE sql AS 'select 1';"
                         " GRANT EXECUTE ON FUNCTION public._guard_f() TO anon;",
                         'R3_anon_can_execute', 'public._guard_f()'),
    'R3_allowlisted_name_other_args': ("CREATE FUNCTION public.touch_updated_at(int) RETURNS int LANGUAGE sql AS 'select 1';"
                                       " GRANT EXECUTE ON FUNCTION public.touch_updated_at(int) TO anon;",
                                       'R3_anon_can_execute', 'public.touch_updated_at(integer)'),
    'R3_public_grant': ("CREATE FUNCTION monjez_private._guard_pf() RETURNS int LANGUAGE sql AS 'select 1';"
                        " GRANT EXECUTE ON FUNCTION monjez_private._guard_pf() TO PUBLIC;",
                        'R3_anon_can_execute', 'monjez_private._guard_pf()'),
    'R4_truncate': ("GRANT TRUNCATE ON public.orders TO authenticated;", 'R4_client_truncate', 'public.orders'),
    'R5_definer_no_search_path': ("CREATE FUNCTION public._guard_d() RETURNS int LANGUAGE sql SECURITY DEFINER AS 'select 1';",
                                  'R5_definer_without_search_path', 'public._guard_d()'),
    'R2_live_actor_wrong_role': ("CREATE TABLE public._guard_l1(id int); ALTER TABLE public._guard_l1 ENABLE ROW LEVEL SECURITY;"
                                 " CREATE POLICY monjez_live_actor ON public._guard_l1 AS RESTRICTIVE TO service_role"
                                 " USING ((SELECT monjez_private.actor_is_active())) WITH CHECK ((SELECT monjez_private.actor_is_active()));"
                                 " GRANT SELECT ON public._guard_l1 TO authenticated;",
                                 'R2_client_table_without_rls_or_live_actor', 'public._guard_l1'),
    'R2_live_actor_select_only': ("CREATE TABLE public._guard_l2(id int); ALTER TABLE public._guard_l2 ENABLE ROW LEVEL SECURITY;"
                                  " CREATE POLICY monjez_live_actor ON public._guard_l2 AS RESTRICTIVE FOR SELECT TO authenticated"
                                  " USING ((SELECT monjez_private.actor_is_active()));"
                                  " GRANT SELECT, INSERT ON public._guard_l2 TO authenticated;",
                                  'R2_client_table_without_rls_or_live_actor', 'public._guard_l2'),
    'R2_live_actor_or_true': ("CREATE TABLE public._guard_l3(id int); ALTER TABLE public._guard_l3 ENABLE ROW LEVEL SECURITY;"
                              " CREATE POLICY monjez_live_actor ON public._guard_l3 AS RESTRICTIVE TO authenticated"
                              " USING ((SELECT monjez_private.actor_is_active()) OR true) WITH CHECK ((SELECT monjez_private.actor_is_active()) OR true);"
                              " GRANT SELECT ON public._guard_l3 TO authenticated;",
                              'R2_client_table_without_rls_or_live_actor', 'public._guard_l3'),
    'R2_live_actor_other_function': ("CREATE TABLE public._guard_l4(id int); ALTER TABLE public._guard_l4 ENABLE ROW LEVEL SECURITY;"
                                     " CREATE POLICY monjez_live_actor ON public._guard_l4 AS RESTRICTIVE TO authenticated"
                                     " USING (public.is_platform_admin() OR true) WITH CHECK (true);"
                                     " GRANT SELECT ON public._guard_l4 TO authenticated;",
                                     'R2_client_table_without_rls_or_live_actor', 'public._guard_l4'),
    'R2_live_actor_without_check': ("CREATE TABLE public._guard_l5(id int); ALTER TABLE public._guard_l5 ENABLE ROW LEVEL SECURITY;"
                                    " CREATE POLICY monjez_live_actor ON public._guard_l5 AS RESTRICTIVE FOR ALL TO authenticated"
                                    " USING ((SELECT monjez_private.actor_is_active()));"
                                    " GRANT SELECT ON public._guard_l5 TO authenticated;",
                                    'R2_client_table_without_rls_or_live_actor', 'public._guard_l5'),
    'R2c_open_permissive_on_real_table': ("CREATE POLICY _guard_open ON public.orders FOR SELECT TO authenticated USING (true);",
                                          'R2c_open_permissive_policy', 'public.orders / _guard_open'),
    'R2c_open_permissive_public_role': ("CREATE POLICY _guard_open2 ON public.customers AS PERMISSIVE FOR ALL USING (1 = 1) WITH CHECK (1 = 1);",
                                        'R2c_open_permissive_policy', 'public.customers / _guard_open2'),
    'R5b_client_writable_schema': ("CREATE SCHEMA _guard_open; GRANT CREATE ON SCHEMA _guard_open TO authenticated;"
                                   " CREATE FUNCTION public._guard_sp1() RETURNS int LANGUAGE sql SECURITY DEFINER"
                                   " SET search_path = _guard_open, pg_temp AS 'select 1';",
                                   'R5b_definer_untrusted_search_path', 'public._guard_sp1()'),
    'R5b_pg_temp_first': ("CREATE FUNCTION public._guard_sp2() RETURNS int LANGUAGE sql SECURITY DEFINER"
                          " SET search_path = pg_temp, public AS 'select 1';",
                          'R5b_definer_untrusted_search_path', 'public._guard_sp2()'),
    'R5b_dollar_user': ("CREATE FUNCTION public._guard_sp3() RETURNS int LANGUAGE sql SECURITY DEFINER"
                        " SET search_path = \"$user\", public, pg_temp AS 'select 1';",
                        'R5b_definer_untrusted_search_path', 'public._guard_sp3()'),
    'R5b_missing_schema': ("CREATE FUNCTION public._guard_sp4() RETURNS int LANGUAGE sql SECURITY DEFINER"
                           " SET search_path = _guard_absent, pg_temp AS 'select 1';",
                           'R5b_definer_untrusted_search_path', 'public._guard_sp4()'),
    'R8_sql_calls_ungranted': ("CREATE FUNCTION monjez_private._guard_in8() RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
                               " CREATE FUNCTION public._guard_out8() RETURNS boolean LANGUAGE sql STABLE"
                               " AS 'select monjez_private._guard_in8()';",
                               'R8_sql_function_calls_function_caller_cannot_execute', 'public._guard_out8()'),
    'R8_sql_calls_ungranted_unqualified': ("CREATE FUNCTION public._guard_in8b() RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
                                           " REVOKE EXECUTE ON FUNCTION public._guard_in8b() FROM PUBLIC, authenticated, anon;"
                                           " CREATE FUNCTION public._guard_out8b() RETURNS boolean LANGUAGE sql STABLE"
                                           " AS 'select _guard_in8b()';",
                                           'R8_sql_function_calls_function_caller_cannot_execute', 'public._guard_out8b()'),
    # Static only: the caller is created, never called. One overload granted, the one
    # the body names (text) not: the name-only check missed this (773af30).
    'R8_overload_ungranted': ("CREATE FUNCTION monjez_private._guard_ov(int) RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
                              " GRANT EXECUTE ON FUNCTION monjez_private._guard_ov(int) TO authenticated, anon;"
                              " CREATE FUNCTION monjez_private._guard_ov(text) RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
                              " CREATE FUNCTION public._guard_ov_caller() RETURNS boolean LANGUAGE sql STABLE"
                              " AS $f$select monjez_private._guard_ov('x'::text)$f$;",
                              'R8_sql_function_calls_function_caller_cannot_execute', 'public._guard_ov_caller()'),
    'R6_default_public_execute': ("ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT EXECUTE ON FUNCTIONS TO PUBLIC;",
                                  'R6_postgres_function_default_public_execute', 'pg_default_acl'),
    'R6_default_truncate': ("ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT TRUNCATE ON TABLES TO authenticated;",
                            'R6_postgres_default_grants_client', 'public/r'),
    'R6_default_anon': ("ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO anon;",
                        'R6_postgres_default_grants_client', 'public/r'),
    'R7_policy_helper_without_grant': (
        "CREATE FUNCTION monjez_private._guard_helper() RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
        " CREATE TABLE public._guard_r7(id int); ALTER TABLE public._guard_r7 ENABLE ROW LEVEL SECURITY;"
        " CREATE POLICY monjez_live_actor ON public._guard_r7 AS RESTRICTIVE TO authenticated USING (monjez_private._guard_helper());"
        " CREATE POLICY p_read ON public._guard_r7 FOR SELECT TO authenticated USING (true);"
        " GRANT SELECT ON public._guard_r7 TO authenticated;",
        'R7_policy_function_not_executable', '_guard_helper()'),
}

IMPLICIT_PG_TEMP = """
SELECT n.nspname||'.'||p.proname||'('||pg_get_function_identity_arguments(p.oid)||')'
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE p.prosecdef AND n.nspname IN ('public','monjez_private')
  AND NOT EXISTS (SELECT 1 FROM unnest(coalesce(p.proconfig,'{}')) c
                  WHERE c LIKE 'search_path=%' AND (c LIKE '%, pg_temp' OR c LIKE '%,pg_temp' OR c = 'search_path=pg_temp'))
ORDER BY 1;
"""

CLIENT_TABLES = """
SELECT n.nspname||'.'||c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN ('public','monjez_private') AND c.relkind IN ('r','p','v','m')
  AND has_table_privilege('authenticated', c.oid, 'SELECT') ORDER BY 1;
"""

GU = '00000000-0000-4000-8000-0000000c0e01'
GT = '00000000-0000-4000-8000-0000000c0e02'


# Representative non-NULL row per table for the second R7 evaluation: uuid columns get the
# synthetic tenant (tenant_id), the synthetic owner (owner_user_id, user_id, profiles.id) or a
# fixed uuid; numeric 1, text 'x', boolean true, date/time now(); other types stay NULL.
REPRESENTATIVE_ROW = """(SELECT coalesce(jsonb_object_agg(a.attname, CASE
    WHEN a.atttypid = 'uuid'::regtype AND a.attname = 'tenant_id' THEN to_jsonb('{GT}'::text)
    WHEN a.atttypid = 'uuid'::regtype AND (a.attname IN ('owner_user_id','user_id')
         OR (c.relname = 'profiles' AND a.attname = 'id')) THEN to_jsonb('{GU}'::text)
    WHEN a.atttypid = 'uuid'::regtype THEN to_jsonb('00000000-0000-4000-8000-0000000c0e09'::text)
    WHEN t.typcategory = 'N' THEN to_jsonb(1)
    WHEN t.typcategory = 'S' THEN to_jsonb('x'::text)
    WHEN t.typcategory = 'B' THEN to_jsonb(true)
    WHEN t.typcategory = 'D' THEN to_jsonb(now()) END) FILTER (WHERE a.atttypid = 'uuid'::regtype
         OR t.typcategory IN ('N','S','B','D')), '{{}}'::jsonb)
  FROM pg_attribute a JOIN pg_type t ON t.oid = a.atttypid
  WHERE a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped)"""


def rls_eval(extra_setup, mode='null'):
    """One rolled-back transaction with a synthetic active owner and tenant. Every USING and
    WITH CHECK expression of every policy that applies to authenticated (or PUBLIC) on an
    application table is evaluated as authenticated against a row of the table's own type
    (mode 'null': all columns NULL; mode 'representative': REPRESENTATIVE_ROW, so STRICT or
    NULL-guarded helpers called with column values really run). The functions it calls, and
    the functions those call, run even when the table is empty.
    Returns (expressions evaluated, total, error lines)."""
    script = f"""\\set VERBOSITY terse
BEGIN;
INSERT INTO auth.users(id, instance_id, aud, role, email, created_at, updated_at)
  VALUES ('{GU}','00000000-0000-0000-0000-000000000000','authenticated','authenticated','c-defpriv@mongezz.test',now(),now());
INSERT INTO public.tenants(id, name, owner_user_id) VALUES ('{GT}','C-DEFPRIV synthetic','{GU}');
UPDATE public.profiles SET tenant_id='{GT}' WHERE id='{GU}';
{extra_setup}
CREATE TEMP TABLE _guard_eval(label text, stmt text) ON COMMIT DROP;
INSERT INTO _guard_eval
SELECT n.nspname||'.'||c.relname||' / '||p.polname||' / '||v.kind,
       CASE WHEN '{mode}' = 'null'
            THEN format('SELECT (%s) FROM (SELECT (NULL::%s).*) AS %I', v.expr, c.oid::regclass, c.relname)
            ELSE format('SELECT (%s) FROM jsonb_populate_record(NULL::%s, %L::jsonb) AS %I',
                        v.expr, c.oid::regclass, {REPRESENTATIVE_ROW.format(GT=GT, GU=GU)}, c.relname) END
FROM pg_policy p JOIN pg_class c ON c.oid = p.polrelid JOIN pg_namespace n ON n.oid = c.relnamespace
CROSS JOIN LATERAL (VALUES ('using', pg_get_expr(p.polqual, p.polrelid)),
                           ('check', pg_get_expr(p.polwithcheck, p.polrelid))) AS v(kind, expr)
WHERE n.nspname IN ('public','monjez_private') AND v.expr IS NOT NULL
  AND ('authenticated'::regrole::oid = ANY (p.polroles) OR 0 = ANY (p.polroles));
GRANT SELECT ON _guard_eval TO authenticated;
SELECT 'TOTAL', count(*) FROM _guard_eval;
SELECT set_config('request.jwt.claims','{{"sub":"{GU}","role":"authenticated"}}',true);
SELECT set_config('request.jwt.claim.sub','{GU}',true);
SET LOCAL ROLE authenticated;
DO $g$ DECLARE r record; k int := 0; BEGIN
  FOR r IN SELECT * FROM _guard_eval ORDER BY label LOOP
    BEGIN EXECUTE r.stmt; k := k + 1;
    EXCEPTION WHEN OTHERS THEN RAISE NOTICE 'GUARD_EVAL_ERROR|%|%|%', r.label, SQLSTATE, SQLERRM; END;
  END LOOP;
  RAISE NOTICE 'GUARD_EVAL_DONE|%', k;
END $g$;
ROLLBACK;
"""
    r = subprocess.run(['psql', '-X', '-q', '-At', '-F', '|', '-v', 'ON_ERROR_STOP=1'], input=script,
                       capture_output=True, text=True, timeout=120)
    total = next((int(l.split('|')[1]) for l in r.stdout.splitlines() if l.startswith('TOTAL|')), -1)
    done = next((int(l.split('GUARD_EVAL_DONE|')[1]) for l in r.stderr.splitlines() if 'GUARD_EVAL_DONE|' in l), -1)
    errors = [l.split('NOTICE:', 1)[-1].strip() for l in r.stderr.splitlines() if 'GUARD_EVAL_ERROR|' in l]
    if r.returncode != 0:
        errors.append('SCRIPT_FAILED ' + r.stderr.strip()[-300:])
    return done, total, errors


# R2d: every PERMISSIVE policy that applies to a client role, in PostgreSQL's own deparsed
# form. PERMISSIVE policies are OR-ed, so one effectively-open policy that still references
# a column (e.g. tenant_id IS NOT NULL) defeats store isolation while passing R2/R2c.
# Whether an expression is truly tenant-scoped is not decidable from the catalog, so any
# new, changed or removed policy fails until reviewed_permissive_policies.jsonl is updated
# in the same PR (the diff is the review; store-isolation suites must cover it).
PERMISSIVE_SQL = """
SELECT json_build_object('table', n.nspname||'.'||c.relname, 'policy', p.polname, 'cmd', p.polcmd,
  'roles', (SELECT array_agg(CASE WHEN r=0 THEN 'PUBLIC' ELSE pg_get_userbyid(r) END ORDER BY 1) FROM unnest(p.polroles) r),
  'using', pg_get_expr(p.polqual, p.polrelid), 'check', pg_get_expr(p.polwithcheck, p.polrelid))::text
FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname IN ('public','monjez_private') AND p.polpermissive
  AND (0 = ANY (p.polroles) OR 'anon'::regrole::oid = ANY (p.polroles) OR 'authenticated'::regrole::oid = ANY (p.polroles))
ORDER BY 1;
"""

# R7b: functions any policy on an application table depends on. R7 (static) and the R7
# operational evaluation cannot prove every branch or nested call runs; a new helper must
# be listed in reviewed_policy_functions.tsv with the functional test that covers it.
POLICY_FUNCTIONS_SQL = """
SELECT DISTINCT d.refobjid::regprocedure::text
FROM pg_policy pol JOIN pg_class c ON c.oid=pol.polrelid JOIN pg_namespace n ON n.oid=c.relnamespace
JOIN pg_depend d ON d.classid='pg_policy'::regclass AND d.objid=pol.oid AND d.refclassid='pg_proc'::regclass
WHERE n.nspname IN ('public','monjez_private') ORDER BY 1;
"""


def coverage_errors(lines, passed):
    """Each line: signature<TAB>coverage text containing guard:<control_name> tokens. Every
    line must name at least one control, and every named control must have run and passed."""
    import re
    errs = []
    for line in lines:
        sig, _, cov = line.partition('\t')
        names = re.findall(r'guard:([A-Za-z0-9_]+)', cov)
        if not names:
            errs.append(sig.strip() + ': no guard:<control> coverage')
        elif any(n not in passed for n in names):
            errs.append(sig.strip() + ': named control missing or failed: ' + ','.join(n for n in names if n not in passed))
    return errs


def json_rows(rows):
    return {'|'.join(r) for r in rows}


COMPAT_SQL = """
CREATE FUNCTION public._guard_new_pub() RETURNS int LANGUAGE sql AS 'select 1';
CREATE FUNCTION monjez_private._guard_new_priv() RETURNS int LANGUAGE sql AS 'select 1';
SELECT 'pub', has_function_privilege('anon','public._guard_new_pub()','EXECUTE'),
       has_function_privilege('authenticated','public._guard_new_pub()','EXECUTE'),
       has_function_privilege('service_role','public._guard_new_pub()','EXECUTE');
SELECT 'priv', has_function_privilege('anon','monjez_private._guard_new_priv()','EXECUTE'),
       has_function_privilege('authenticated','monjez_private._guard_new_priv()','EXECUTE');
GRANT EXECUTE ON FUNCTION monjez_private._guard_new_priv() TO authenticated;
SELECT 'priv_granted', has_function_privilege('authenticated','monjez_private._guard_new_priv()','EXECUTE');
"""


def main():
    guard()
    evidence = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    controls = []

    def control(name, ok, **detail):
        controls.append({'name': name, 'passed': bool(ok), **detail})

    ok, rows, err = run('', VIOLATIONS)
    control('baseline_no_violations', ok and rows == [], violations=[list(r) for r in rows][:20], error=err[:300])

    for name, (setup, rule, obj) in NEGATIVE.items():
        ok, rows, err = run(setup, VIOLATIONS)
        hit = any(r[0] == rule and obj in r[1] for r in rows)
        control('negative_' + name + '_detected', ok and hit, rows=[list(r) for r in rows][:6], error=err[:300])

    ok, rows, err = run('', COMPAT_SQL)
    got = {r[0]: r[1:] for r in rows}
    control('compat_new_public_function_not_anon_but_authenticated_and_service',
            ok and got.get('pub') == ('f', 't', 't'), observed=got.get('pub'), error=err[:300])
    control('compat_new_private_function_needs_explicit_grant',
            ok and got.get('priv') == ('f', 'f') and got.get('priv_granted') == ('t',), observed=[got.get('priv'), got.get('priv_granted')])

    # R2d reviewed permissive-policy manifest (exact match).
    reviewed = {l.strip() for l in (HERE / 'reviewed_permissive_policies.jsonl').read_text().splitlines() if l.strip()}
    ok, rows, err = run('', PERMISSIVE_SQL)
    current = json_rows(rows)
    control('R2d_permissive_policies_match_reviewed_manifest', ok and current == reviewed,
            added=sorted(current - reviewed)[:5], removed=sorted(reviewed - current)[:5],
            reviewed=len(reviewed), current=len(current), error=err[:300])
    # Negative: references a column, so R2/R2c accept it, yet opens every store's orders.
    open_setup = "CREATE POLICY _guard_tenant_open ON public.orders FOR SELECT TO authenticated USING (tenant_id IS NOT NULL);"
    ok, vrows, _ = run(open_setup, VIOLATIONS)
    ok2, prow, err = run(open_setup, PERMISSIVE_SQL)
    added = json_rows(prow) - reviewed
    control('negative_R2d_effectively_open_policy_detected',
            ok and ok2 and not any(r[0].startswith('R2') and '_guard_tenant_open' in '|'.join(r) for r in vrows)
            and any('_guard_tenant_open' in a for a in added), r2_rules_missed=True, error=err[:300])
    # Negative: an existing reviewed policy widened in place.
    widen = ("ALTER POLICY \"tenant members read orders\" ON public.orders"
             " USING ((tenant_id = current_tenant_id()) OR (tenant_id IS NOT NULL));")
    ok, prow, err = run(widen, PERMISSIVE_SQL)
    cur = json_rows(prow)
    control('negative_R2d_widened_existing_policy_detected',
            ok and any('tenant members read orders' in a for a in cur - reviewed)
            and any('tenant members read orders' in r for r in reviewed - cur), error=err[:300])

    # R7b reviewed list of policy helper functions (exact match).
    listed = {l.split('\t')[0].strip() for l in (HERE / 'reviewed_policy_functions.tsv').read_text().splitlines()
              if l.strip() and not l.startswith('#')}
    ok, rows, err = run('', POLICY_FUNCTIONS_SQL)
    fns = {r[0] for r in rows}
    control('R7b_policy_functions_match_reviewed_list', ok and fns == listed,
            unlisted=sorted(fns - listed), stale=sorted(listed - fns), error=err[:300])
    helper = ("CREATE FUNCTION monjez_private._guard_helper7b() RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
              " GRANT EXECUTE ON FUNCTION monjez_private._guard_helper7b() TO authenticated;"
              " CREATE POLICY _guard_r7b ON public.orders AS RESTRICTIVE FOR SELECT TO authenticated"
              " USING (monjez_private._guard_helper7b());")
    ok, rows, err = run(helper, POLICY_FUNCTIONS_SQL)
    control('negative_R7b_new_policy_helper_detected',
            ok and 'monjez_private._guard_helper7b()' in ({r[0] for r in rows} - listed), error=err[:300])

    # Positive: a column-only grant on a properly protected table is accepted (no R2/R2b row).
    protected = ("CREATE TABLE public._guard_c5(id int, secret text);"
                 " ALTER TABLE public._guard_c5 ENABLE ROW LEVEL SECURITY;"
                 " CREATE POLICY monjez_live_actor ON public._guard_c5 AS RESTRICTIVE TO authenticated"
                 " USING ((SELECT monjez_private.actor_is_active())) WITH CHECK ((SELECT monjez_private.actor_is_active()));"
                 " REVOKE ALL ON public._guard_c5 FROM PUBLIC, anon, authenticated;"
                 " GRANT SELECT (secret) ON public._guard_c5 TO authenticated;")
    ok, rows, err = run(protected, VIOLATIONS)
    control('positive_R2_column_only_protected_table_accepted',
            ok and not any('_guard_c5' in '|'.join(r) for r in rows), rows=[list(r) for r in rows][:3], error=err[:300])

    # DEFPRIV-R7-NULL: evaluate every policy expression again on a representative non-NULL row.
    done, total, errs = rls_eval('', 'representative')
    control('R7c_policy_expressions_representative_rows', total > 0 and done == total and not errs,
            evaluated=done, total=total, errors=errs[:5])
    # Negative: a granted STRICT plpgsql helper that reaches an ungranted helper only for a
    # non-NULL argument. All-NULL evaluation skips it; the representative row reaches it.
    strict = ("CREATE FUNCTION monjez_private._guard_in7c(p uuid) RETURNS boolean LANGUAGE sql STABLE AS 'select p is not null';"
              " CREATE FUNCTION monjez_private._guard_out7c(p uuid) RETURNS boolean LANGUAGE plpgsql STABLE STRICT"
              " AS 'begin return monjez_private._guard_in7c(p); end';"
              " GRANT EXECUTE ON FUNCTION monjez_private._guard_out7c(uuid) TO authenticated;"
              " CREATE POLICY _guard_strict7c ON public.orders AS RESTRICTIVE FOR SELECT TO authenticated"
              " USING (monjez_private._guard_out7c(tenant_id));")
    _, _, errs_null = rls_eval(strict, 'null')
    _, _, errs_rep = rls_eval(strict, 'representative')
    control('negative_R7c_strict_nested_helper_null_miss_representative_hit',
            not any('_guard_strict7c' in e for e in errs_null)
            and any('_guard_strict7c' in e and '42501' in e for e in errs_rep),
            null_errors=[e for e in errs_null if '_guard' in e][:2], representative_errors=errs_rep[:2])
    _, _, errs_ok = rls_eval(strict + " GRANT EXECUTE ON FUNCTION monjez_private._guard_in7c(uuid) TO authenticated;",
                             'representative')
    control('positive_R7c_strict_nested_helper_granted_passes', not errs_ok, errors=errs_ok[:2])

    # R5c ratchet: SECURITY DEFINER functions without an explicit trailing pg_temp.
    known = {l.strip() for l in (HERE / 'known_implicit_pg_temp.txt').read_text().splitlines()
             if l.strip() and not l.startswith('#')}
    ok, rows, err = run('', IMPLICIT_PG_TEMP)
    current = {r[0] for r in rows}
    control('R5c_no_new_definer_with_implicit_pg_temp', ok and current <= known,
            new=sorted(current - known), known=len(known), current=len(current), error=err[:300])
    ok, rows, err = run("CREATE FUNCTION public._guard_r5c() RETURNS int LANGUAGE sql SECURITY DEFINER"
                        " SET search_path = public AS 'select 1';", IMPLICIT_PG_TEMP)
    control('negative_R5c_new_implicit_pg_temp_detected',
            ok and 'public._guard_r5c()' in ({r[0] for r in rows} - known), error=err[:300])

    # R7 operational: pg_depend records only functions a policy calls directly. Evaluate
    # every policy expression as a real signed-in owner so a nested helper's missing grant
    # surfaces as 42501 (see rls_eval).
    done, total, errs = rls_eval('')
    control('R7_operational_policy_expressions_as_authenticated', total > 0 and done == total and not errs,
            evaluated=done, total=total, errors=errs[:5])
    nested = ("CREATE FUNCTION monjez_private._guard_inner() RETURNS boolean LANGUAGE sql STABLE AS 'select true';"
              # plpgsql outer, so the negative raises a clean 42501 (see R8).
              " CREATE FUNCTION monjez_private._guard_outer() RETURNS boolean LANGUAGE plpgsql STABLE"
              " AS 'begin return monjez_private._guard_inner(); end';"
              " GRANT EXECUTE ON FUNCTION monjez_private._guard_outer() TO authenticated;"
              " CREATE POLICY _guard_nested ON public.orders AS RESTRICTIVE FOR SELECT TO authenticated"
              " USING (monjez_private._guard_outer());")
    ok7, rows7, _ = run(nested, VIOLATIONS)
    done, total, errs = rls_eval(nested)
    control('negative_R7_nested_helper_static_miss_operational_hit',
            ok7 and not any(r[0] == 'R7_policy_function_not_executable' for r in rows7)
            and any('_guard_nested' in e and '42501' in e for e in errs), errors=errs[:3])

    # R7b coverage: every listed helper names at least one guard:<control> that ran and passed.
    passed_now = {c['name'] for c in controls if c['passed']}
    tsv = [l for l in (HERE / 'reviewed_policy_functions.tsv').read_text().splitlines() if l.strip() and not l.startswith('#')]
    cov_errors = coverage_errors(tsv, passed_now)
    control('R7b_every_listed_helper_names_passing_guard_controls', not cov_errors, errors=cov_errors[:5])
    stripped = [l.split('\t')[0] + '\t' for l in tsv]
    control('negative_R7b_missing_coverage_rejected', len(coverage_errors(stripped, passed_now)) == len(tsv))
    bogus = [l.split('\t')[0] + '\tguard:R7z_no_such_control' for l in tsv]
    control('negative_R7b_unknown_control_rejected', len(coverage_errors(bogus, passed_now)) == len(tsv))

    left = subprocess.run(PSQL, input="SELECT count(*) FROM pg_class WHERE relname LIKE '\\_guard\\_%' "
                          "UNION ALL SELECT count(*) FROM pg_proc WHERE proname LIKE '\\_guard\\_%';",
                          capture_output=True, text=True, timeout=30).stdout.split()
    control('nothing_persisted', left == ['0', '0'], observed=left)

    result = {'probe': 'c-defpriv-01', 'controls': controls}
    print('CATALOG_GUARD_RESULT ' + json.dumps(result))
    if evidence:
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'catalog-guard.json').write_text(json.dumps(result, indent=2) + '\n')
    failed = [c['name'] for c in controls if not c['passed']]
    if failed:
        raise SystemExit('CATALOG_GUARD_FAILED ' + ','.join(failed))


if __name__ == '__main__':
    main()
