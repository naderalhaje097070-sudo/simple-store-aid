"""C-TENANT-01: a signed-in owner may write only the tenant columns the app writes.

Runs on the isolated local stack only, as the role PostgREST uses
(SET ROLE authenticated with JWT claims), each case in its own transaction that
is always rolled back. Synthetic owner and tenant, removed at the end.

App writes on integration (src/routes/_authenticated/onboarding.tsx, src/lib/db.ts):
  INSERT tenants(name, owner_user_id) RETURNING id
  UPDATE tenants SET name | business_type | timezone WHERE id = ...
Expected after 20261110140000_tenants_narrow_client_grants_01:
  allowed: those writes, plus INSERT of timezone/business_type
  denied (42501): INSERT id/created_at/updated_at; UPDATE id/owner_user_id/created_at/updated_at
  unchanged: entitlement columns denied; updated_at still set by the touch trigger.
"""
import json, os, subprocess, sys
from pathlib import Path

USER = '00000000-0000-4000-8000-0000000c0b01'
TENANT = '00000000-0000-4000-8000-0000000c0b02'
OTHER = '00000000-0000-4000-8000-0000000c0b03'
PSQL = ['psql', '-X', '-q', '-At', '-v', 'ON_ERROR_STOP=1']


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
        sys.exit('TENANT_GRANTS_PROBE_BLOCKED: ' + '; '.join(bad))


def sql(text):
    return subprocess.run(PSQL, input=text, capture_output=True, text=True, timeout=30)


def as_owner(statement, check=''):
    """One statement as the signed-in owner, then an optional postgres-side read; always rolled back."""
    r = sql(f"""\\set VERBOSITY verbose
BEGIN;
SELECT set_config('request.jwt.claims','{{"sub":"{USER}","role":"authenticated"}}',true);
SELECT set_config('request.jwt.claim.sub','{USER}',true);
SET LOCAL ROLE authenticated;
{statement};
RESET ROLE;
SELECT 'CHECK', ({check or 'true'});
ROLLBACK;
""")
    ok = r.returncode == 0
    checked = ok and 'CHECK|t' in r.stdout
    return ok, checked, ('42501' in r.stderr), r.stderr.strip().splitlines()[:1]


def main():
    guard()
    evidence = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    controls = []

    def control(name, ok, detail=None):
        controls.append({'name': name, 'passed': bool(ok), **({'detail': detail} if detail is not None else {})})

    setup = sql(f"""BEGIN;
INSERT INTO auth.users(id, instance_id, aud, role, email, created_at, updated_at)
  VALUES ('{USER}','00000000-0000-0000-0000-000000000000','authenticated','authenticated',
          'c-tenant-01@mongezz.test', now(), now()) ON CONFLICT (id) DO NOTHING;
INSERT INTO public.tenants(id, name, owner_user_id, created_at, updated_at)
  VALUES ('{TENANT}','C-TENANT-01 synthetic','{USER}','2026-11-01T00:00:00Z','2026-11-01T00:00:00Z')
  ON CONFLICT (id) DO NOTHING;
COMMIT;""")
    if setup.returncode != 0:
        raise SystemExit('TENANT_GRANTS_SETUP_FAILED ' + setup.stderr[:400])
    try:
        before = sql(f"SELECT row_to_json(t)::text FROM public.tenants t WHERE id='{TENANT}'").stdout.strip()

        # Real app writes must keep working.
        ok, chk, _, err = as_owner(
            "INSERT INTO public.tenants(name, owner_user_id) VALUES ('C-TENANT-01 onboarding','" + USER + "') RETURNING id",
            f"(SELECT count(*) FROM public.user_roles r JOIN public.tenants t ON t.id=r.tenant_id "
            f"WHERE t.owner_user_id='{USER}' AND t.name='C-TENANT-01 onboarding' AND r.role='owner')=1")
        control('app_onboarding_insert_allowed_and_owner_role_linked', ok and chk, err)
        for col, val in (('name', "'C-TENANT-01 renamed'"), ('business_type', "'grocery'"), ('timezone', "'Africa/Cairo'")):
            ok, chk, _, err = as_owner(
                f"UPDATE public.tenants SET {col}={val} WHERE id='{TENANT}'",
                f"(SELECT {col}={val} AND updated_at>'2026-11-01T00:00:00Z' FROM public.tenants WHERE id='{TENANT}')")
            control(f'app_update_{col}_allowed_and_touch_trigger_sets_updated_at', ok and chk, err)
        ok, chk, _, err = as_owner(
            "INSERT INTO public.tenants(name, owner_user_id, timezone, business_type) "
            f"VALUES ('C-TENANT-01 full','{USER}','Africa/Tripoli','retail')")
        control('insert_with_timezone_and_business_type_allowed', ok, err)

        # Columns the app never writes are denied by privilege (42501), not silently ignored.
        denied = {
            'insert_id': f"INSERT INTO public.tenants(id, name, owner_user_id) VALUES ('{OTHER}','x','{USER}')",
            'insert_created_at': f"INSERT INTO public.tenants(name, owner_user_id, created_at) VALUES ('x','{USER}','2000-01-01')",
            'insert_updated_at': f"INSERT INTO public.tenants(name, owner_user_id, updated_at) VALUES ('x','{USER}','2000-01-01')",
            'update_id': f"UPDATE public.tenants SET id='{OTHER}' WHERE id='{TENANT}'",
            'update_owner_user_id': f"UPDATE public.tenants SET owner_user_id='{USER}' WHERE id='{TENANT}'",
            'update_created_at': f"UPDATE public.tenants SET created_at='2000-01-01' WHERE id='{TENANT}'",
            'update_updated_at': f"UPDATE public.tenants SET updated_at='2000-01-01' WHERE id='{TENANT}'",
            'update_trial_ends_at': f"UPDATE public.tenants SET trial_ends_at='2099-01-01' WHERE id='{TENANT}'",
            'update_subscription_status': f"UPDATE public.tenants SET subscription_status='active' WHERE id='{TENANT}'",
            'insert_subscription_status': f"INSERT INTO public.tenants(name, owner_user_id, subscription_status) VALUES ('x','{USER}','active')",
            'upsert_on_id': f"INSERT INTO public.tenants(id, name, owner_user_id) VALUES ('{TENANT}','x','{USER}') "
                            "ON CONFLICT (id) DO UPDATE SET name=excluded.name",
        }
        for name, stmt in denied.items():
            ok, _, is42501, err = as_owner(stmt)
            control(f'owner_{name}_denied_42501', (not ok) and is42501, err)

        after = sql(f"SELECT row_to_json(t)::text FROM public.tenants t WHERE id='{TENANT}'").stdout.strip()
        n = sql(f"SELECT count(*) FROM public.tenants WHERE owner_user_id='{USER}'").stdout.strip()
        control('stored_tenant_unchanged_and_no_extra_rows', before == after and before and n == '1', n)
    finally:
        sql(f"""BEGIN;
DELETE FROM public.user_roles WHERE user_id='{USER}';
DELETE FROM public.tenants WHERE owner_user_id='{USER}';
DELETE FROM auth.users WHERE id='{USER}';
COMMIT;""")
    gone = sql(f"SELECT (SELECT count(*) FROM public.tenants WHERE owner_user_id='{USER}')"
               f"+(SELECT count(*) FROM auth.users WHERE id='{USER}')").stdout.strip()
    control('synthetic_tenant_and_user_removed', gone == '0', gone)

    result = {'probe': 'c-tenant-01', 'controls': controls}
    print('TENANT_GRANTS_RESULT ' + json.dumps(result))
    if evidence:
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'tenant-grants.json').write_text(json.dumps(result, indent=2) + '\n')
    failed = [c['name'] for c in controls if not c['passed']]
    if failed:
        raise SystemExit('TENANT_GRANTS_FAILED ' + ','.join(failed))


if __name__ == '__main__':
    main()
