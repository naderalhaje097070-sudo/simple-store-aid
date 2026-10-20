"""Loopback-only nonfinancial lifecycle baseline; never accepts a fix by omission."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'e2e'))
from write_harness_guard import require_write_harness, _psql_command, _psql_env

EXPECTED_RED = 'ENV_NATIVE_01_CLEAN_BASELINE_EXPECTED_RED'
HARNESS_FAIL = 'ENV_NATIVE_01_LIVE_HARNESS_FAILURE'
FINANCE_TABLES = ('orders', 'order_items', 'products', 'customers', 'payments', 'expenses', 'day_closes')


class HarnessFailure(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def denial(status, body):
    """Explicit permission denial or proven empty RLS rows; never generic failure."""
    return (status == 200 and body == []) or (
        status in (401, 403) and isinstance(body, dict) and body.get('code') in ('42501', 'PGRST301', 'PGRST302'))


def auth_ban_denial(status, body):
    return status in (400, 401, 403) and isinstance(body, dict) and body.get('error_code') in (
        'user_banned', 'refresh_token_not_found', 'session_not_found')


def outcome(controls, targets):
    if not controls or not targets or any(c.get('passed') is not True for c in controls):
        raise HarnessFailure('controls incomplete')
    names = [c.get('name') for c in controls + targets]
    if any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
        raise HarnessFailure('duplicate or missing check')
    # Baseline is immutable: exactly the confirmed old-token own-tenant path must
    # reproduce. Other observed failures are retained, never used as a substitute.
    own = next((c for c in targets if c['name'] == 'banned_owner_old_jwt_own_tenant'), None)
    if not own or own.get('status') != 200 or own.get('visible_rows') != 1 or own.get('passed') is not False:
        raise HarnessFailure('named baseline regression not reproduced')
    if any(type(c.get('passed')) is not bool for c in targets):
        raise HarnessFailure('invalid target result')
    return EXPECTED_RED


class Probe:
    def __init__(self, status_file, evidence_dir, expected_source):
        # Must happen before credentials are read or any write-capable I/O.
        self.config = require_write_harness()
        if os.environ.get('CI_ISOLATED_SUPABASE') != '1':
            raise HarnessFailure('isolated runner marker missing')
        self.source = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
        if self.source != expected_source:
            raise HarnessFailure('source mismatch')
        if subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], check=False).returncode:
            raise HarnessFailure('tracked source dirty before execution')
        self.evidence_dir = evidence_dir
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.controls, self.targets = [], []
        self.status = json.loads(status_file.read_text())
        self.base = self.status.get('API_URL', '').rstrip('/')
        if self.base != self.config.supabase_url or self.base != 'http://127.0.0.1:54321':
            raise HarnessFailure('CLI API target mismatch')
        self.anon = self.status.get('ANON_KEY')
        self.admin = self.status.get('SERVICE_ROLE_KEY')
        if not isinstance(self.anon, str) or not self.anon or not isinstance(self.admin, str) or not self.admin:
            raise HarnessFailure('missing disposable stack keys')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def sql(self, sql):
        r = subprocess.run(_psql_command(self.config, '-Atq', '-v', 'ON_ERROR_STOP=1'),
                           input=sql, capture_output=True, text=True, env=_psql_env(self.config))
        if r.returncode:
            raise HarnessFailure('isolated SQL execution failed')
        return r.stdout.strip()

    def query(self, sql):
        try:
            return json.loads(self.sql(sql))
        except json.JSONDecodeError as exc:
            raise HarnessFailure('SQL result shape') from exc

    def request(self, method, path, payload=None, token=None, admin=False):
        if not path.startswith(('/auth/v1/', '/rest/v1/')) or '\n' in path:
            raise HarnessFailure('unsupported local API path')
        key = self.admin if admin else self.anon
        headers = {'apikey': key, 'Authorization': 'Bearer ' + (key if admin else token or self.anon),
                   'Content-Type': 'application/json', 'Prefer': 'return=representation'}
        req = urllib.request.Request(self.base + path, data=None if payload is None else json.dumps(payload).encode(),
                                     method=method, headers=headers)
        try:
            with self.opener.open(req, timeout=15) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise HarnessFailure('local transport failure') from exc
        if status >= 500 or 300 <= status < 400:
            raise HarnessFailure('server or redirect failure')
        try:
            return status, json.loads(raw) if raw else None
        except json.JSONDecodeError as exc:
            raise HarnessFailure('non-JSON local API result') from exc

    def control(self, name, passed, **details):
        self.controls.append({'name': name, 'passed': bool(passed), **details})
        (self.evidence_dir / 'progress.json').write_text(json.dumps({'source_sha': self.source, 'controls': self.controls}, indent=2) + '\n')
        if not passed:
            raise HarnessFailure('failed positive/isolation control: ' + name)

    def target(self, name, passed, status, **details):
        self.targets.append({'name': name, 'passed': bool(passed), 'status': status, **details})

    def counts(self):
        terms = [f"'{t}',(select count(*) from public.{t})" for t in FINANCE_TABLES]
        terms += ["'users',(select count(*) from auth.users)", "'tenants',(select count(*) from public.tenants)",
                  "'profiles',(select count(*) from public.profiles)", "'roles',(select count(*) from public.user_roles)"]
        return self.query('select jsonb_build_object(' + ','.join(terms) + ');')

    def history(self):
        # Trusted checksums exclude Auth sessions/timestamps changed by login/ban.
        result = {}
        for table in ('tenants', 'profiles', 'user_roles', 'financial_audit_log'):
            result[table] = self.query(f"select to_jsonb(md5(coalesce(jsonb_agg(to_jsonb(t) order by t.id)::text,'[]'))) from public.{table} t;")
        return result

    def fixture(self, label, tenant=None, staff=False):
        password = secrets.token_urlsafe(32) + '!aA1'
        email = 'lifecycle-' + uuid.uuid4().hex + '@example.test'
        status, body = self.request('POST', '/auth/v1/admin/users',
                                    {'email': email, 'password': password, 'email_confirm': True}, admin=True)
        self.control(label + '_created', status == 200 and isinstance(body, dict) and bool(body.get('id')), status=status)
        uid = str(uuid.UUID(body['id']))
        if tenant is None:
            tenant = str(uuid.uuid4())
            status, rows = self.request('POST', '/rest/v1/tenants', {'id': tenant, 'name': 'Fixture ' + label, 'owner_user_id': uid}, admin=True)
            self.control(label + '_tenant_seeded', status == 201 and isinstance(rows, list) and len(rows) == 1, status=status)
        status, rows = self.request('PATCH', '/rest/v1/profiles?id=eq.' + uid, {'tenant_id': tenant}, admin=True)
        self.control(label + '_profile_seeded', status == 200 and isinstance(rows, list) and len(rows) == 1, status=status)
        if staff:
            status, rows = self.request('POST', '/rest/v1/user_roles', {'user_id': uid, 'tenant_id': tenant, 'role': 'staff'}, admin=True)
            self.control(label + '_staff_seeded', status == 201, status=status)
        role = 'staff' if staff else 'owner'
        count = self.sql(f"select count(*) from public.user_roles where user_id='{uid}'::uuid and tenant_id='{tenant}'::uuid and role='{role}';")
        self.control(label + '_exactly_one_role', count == '1')
        status, session = self.request('POST', '/auth/v1/token?grant_type=password', {'email': email, 'password': password})
        self.control(label + '_login', status == 200 and isinstance(session, dict) and bool(session.get('access_token')) and bool(session.get('refresh_token')), status=status)
        return {'uid': uid, 'tenant': tenant, 'email': email, 'password': password,
                'token': session['access_token'], 'refresh': session['refresh_token']}

    def own_rows(self, actor, table):
        path = '/rest/v1/' + table + '?select=id'
        if table == 'tenants':
            path += '&id=eq.' + actor['tenant']
        elif table == 'profiles':
            path += '&id=eq.' + actor['uid']
        status, rows = self.request('GET', path, token=actor['token'])
        return status, rows

    def run(self):
        initial = self.counts()
        self.control('fresh_empty_stack', all(v == 0 for v in initial.values()))
        migration_files = sorted(Path('supabase/migrations').glob('*.sql'))
        versions = self.query('select coalesce(jsonb_agg(version order by version),\'[]\'::jsonb) from supabase_migrations.schema_migrations;')
        self.control('full_migration_chain', len(migration_files) == 41 and versions == [p.name.split('_')[0] for p in migration_files])
        self.export_catalog(migration_files)
        a, b = self.fixture('owner_A'), self.fixture('owner_B')
        s1, s2 = self.fixture('staff_A', a['tenant'], True), self.fixture('staff_B', b['tenant'], True)
        actors = [a, b, s1, s2]
        for n, actor in enumerate(actors):
            status, rows = self.own_rows(actor, 'tenants')
            self.control(f'active_{n}_own_tenant', status == 200 and isinstance(rows, list) and len(rows) == 1, status=status)
            foreign = b['tenant'] if actor['tenant'] == a['tenant'] else a['tenant']
            status, rows = self.request('GET', '/rest/v1/tenants?select=id&id=eq.' + foreign, token=actor['token'])
            self.control(f'active_{n}_foreign_read', denial(status, rows), status=status)
            status, rows = self.request('PATCH', '/rest/v1/tenants?id=eq.' + foreign, {'name': 'FORBIDDEN'}, token=actor['token'])
            self.control(f'active_{n}_foreign_update', denial(status, rows), status=status)
            status, body = self.request('PATCH', '/rest/v1/profiles?id=eq.' + actor['uid'], {'tenant_id': foreign}, token=actor['token'])
            self.control(f'active_{n}_tenant_reassignment', denial(status, body), status=status)
        self.control('foreign_mutations_stored_no_effect', self.sql("select count(*) from public.tenants where name='FORBIDDEN';") == '0')
        status, body = self.request('GET', '/rest/v1/tenants?select=id')
        self.control('anonymous_denied', denial(status, body), status=status)
        # Only a read-only tenant summary; no financial write RPC invoked.
        for name, actor in [('A', a), ('B', b)]:
            status, body = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=actor['token'])
            self.control('active_summary_' + name, status == 200 and isinstance(body, dict) and 'sales' in body, status=status)
        before = self.history()
        for name, actor in [('owner', b), ('staff', s2)]:
            status, body = self.request('PUT', '/auth/v1/admin/users/' + actor['uid'], {'ban_duration': '24h'}, admin=True)
            self.control('ban_' + name, status == 200, status=status)
            banned = self.sql(f"select (banned_until > now())::text from auth.users where id='{actor['uid']}'::uuid;")
            self.control('stored_ban_' + name, banned == 'true')
            for operation, payload, grant in [('login', {'email': actor['email'], 'password': actor['password']}, 'password'),
                                               ('refresh', {'refresh_token': actor['refresh']}, 'refresh_token')]:
                status, body = self.request('POST', '/auth/v1/token?grant_type=' + grant, payload)
                self.control('banned_' + name + '_' + operation, auth_ban_denial(status, body), status=status, error_code=body.get('error_code') if isinstance(body, dict) else None)
            for table in ('tenants', 'profiles', 'user_roles'):
                status, rows = self.own_rows(actor, table)
                if status == 200 and not isinstance(rows, list):
                    raise HarnessFailure('protected read result shape')
                self.target('banned_' + name + '_old_jwt_own_' + ('tenant' if table == 'tenants' else table), denial(status, rows), status,
                            visible_rows=len(rows) if isinstance(rows, list) else 0)
            status, body = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=actor['token'])
            self.target('banned_' + name + '_summary', denial(status, body), status)
            # Direct SQL RLS remains a distinct layer from real JWT HTTP.
            count = self.sql(f"begin; set local role authenticated; select set_config('request.jwt.claim.sub','{actor['uid']}',true) is not null; select count(*) from public.tenants where id='{actor['tenant']}'::uuid; rollback;").splitlines()[-1]
            self.target('banned_' + name + '_direct_rls', count == '0', 200, visible_rows=int(count))
        after = self.history()
        self.control('public_history_preserved', before == after)
        for name, actor in [('owner_A', a), ('staff_A', s1)]:
            status, rows = self.own_rows(actor, 'tenants')
            self.control('active_after_ban_' + name, status == 200 and isinstance(rows, list) and len(rows) == 1, status=status)
        final = self.counts()
        self.control('no_financial_rows', all(final[t] == 0 for t in FINANCE_TABLES))
        self.control('fixture_counts', {k: final[k] for k in ('users', 'tenants', 'profiles', 'roles')} == {'users': 4, 'tenants': 2, 'profiles': 4, 'roles': 4})
        self.control('tracked_source_unchanged', subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0)
        result = {'source_sha': self.source, 'outcome': outcome(self.controls, self.targets), 'controls': self.controls,
                  'targets': self.targets, 'initial_counts': initial, 'final_counts': final,
                  'history_before': before, 'history_after': after, 'integration_accepted': False,
                  'missing_coverage': ['MCP transport', 'admin RPC', 'protected-field role/disabled assignment mass assignment',
                                       'nonempty finance/audit history', 'deleted/expired-token cases', 'postban writes',
                                       'all exposed tables/RPCs', 'concurrent disable', 'upgrade/performance', 'independent review']}
        (self.evidence_dir / 'live-result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'outcome': result['outcome'], 'controls_passed': len(self.controls),
                          'targets_failed': sum(not c['passed'] for c in self.targets), 'targets_total': len(self.targets),
                          'integration_accepted': False}))

    def export_catalog(self, migration_files):
        query = """select jsonb_build_object(
          'functions',(select coalesce(jsonb_agg(jsonb_build_object('name',p.proname,'arguments',pg_get_function_identity_arguments(p.oid),'definer',p.prosecdef,'config',p.proconfig,'acl',p.proacl::text,'definition',pg_get_functiondef(p.oid)) order by p.proname,p.oid),'[]'::jsonb) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.prokind='f'),
          'policies',(select coalesce(jsonb_agg(to_jsonb(p) order by schemaname,tablename,policyname),'[]'::jsonb) from pg_policies p where schemaname='public'),
          'table_grants',(select coalesce(jsonb_agg(to_jsonb(g) order by table_name,grantee,privilege_type),'[]'::jsonb) from information_schema.table_privileges g where table_schema='public'),
          'auth_ban_columns',(select coalesce(jsonb_agg(jsonb_build_object('column',column_name,'type',data_type)),'[]'::jsonb) from information_schema.columns where table_schema='auth' and table_name='users' and column_name in ('id','banned_until','deleted_at')),
          'postgres_version',current_setting('server_version'));"""
        catalog = self.query(query)
        self.control('auth_ban_schema_present', any(c['column'] == 'banned_until' and c['type'] == 'timestamp with time zone' for c in catalog['auth_ban_columns']))
        catalog['source_sha'] = self.source
        catalog['migration_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in migration_files}
        (self.evidence_dir / 'catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status-file', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    try:
        Probe(args.status_file, args.evidence_dir, args.expected_source).run()
    except HarnessFailure as error:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'harness-failure.json').write_text(json.dumps({'outcome': HARNESS_FAIL, 'reason': str(error), 'integration_accepted': False}) + '\n')
        print(HARNESS_FAIL + ': ' + str(error))
        return 2
    except (OSError, ValueError, subprocess.SubprocessError):
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'harness-failure.json').write_text(json.dumps({'outcome': HARNESS_FAIL, 'integration_accepted': False}) + '\n')
        print(HARNESS_FAIL)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
