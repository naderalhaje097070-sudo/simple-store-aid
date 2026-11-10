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
