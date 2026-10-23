"""One B50 candidate: real local Auth/REST/RPC/Nitro MCP and price boundaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from live_probe import HarnessFailure, auth_ban_denial
from owner_closure_probe import ClosureProbe, claims, explicit_inactive, RPC
from oc_app_probe import PriceProbe
from scanner_auth_probe import ScannerProbe
from tenant_entitlement_probe import PROTECTED, VALUES, explicit_denial
from mcp_probe import TOOLS, tool_success, account_tool_denial
from tanstack_route_probe import publish_result
from inventory import inventory, applied

PRIVATE = ('owner_account_closures', 'billing_tenant_bindings', 'billing_webhook_receipts')


class ComposedProbe(ClosureProbe, PriceProbe):
    scan = ScannerProbe.scan

    def __init__(self, *args):
        super().__init__(*args)
        self.secrets = [self.anon, self.admin]
        self.issued = {}

    def record(self, name, passed, **details):
        if any(x['name'] == name for x in self.controls):
            raise HarnessFailure('duplicate B5 check: ' + name)
        super().record(name, passed, **details)

    def fixture(self, *args, **kwargs):
        actor = super().fixture(*args, **kwargs)
        self.secrets.extend(actor[k] for k in ('token', 'refresh', 'password', 'email'))
        return actor

    def oauth_token(self, actor, label, client_id):
        super().oauth_token(actor, label, client_id)
        self.secrets.extend([actor['token'], actor['session_token']])
        self.issued[label] = dict(actor)

    def live_token(self, actor, label):
        c = claims(actor['token'])
        self.record(label + '_genuine_token_still_live', c['sub'] == actor['uid']
                    and c['exp'] > time.time() + 5 and c['iss'] == self.base + '/auth/v1'
                    and c['aud'] == 'authenticated' and c.get('client_id') == self.client_id)

    def invoke(self, name, actor):
        self.live_token(actor, 'invocation_' + str(len(self.controls)) + '_' + name)
        return super().invoke(name, actor)

    def snapshot(self):
        names = self.query("select jsonb_agg(tablename order by tablename) from pg_tables where schemaname='public';")
        if not isinstance(names, list) or len(names) != 22 or any(not re.fullmatch('[a-z_]+', n) for n in names):
            raise HarnessFailure('exact public22 inventory')
        private = self.query("select coalesce(jsonb_agg(tablename order by tablename),'[]'::jsonb) from pg_tables where schemaname='monjez_private';")
        if not set(private).issubset(PRIVATE):
            raise HarnessFailure('unexpected private table')
        relations = [(n, 'public.' + n) for n in names] + [('private.' + n, 'monjez_private.' + n) for n in private]
        # One statement fixes a shared MVCC snapshot across all public/private tables.
        terms = ["'" + n + "',(select jsonb_build_object('count',count(*),'digest',md5(coalesce(string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),''))) from " + rel + ' t)' for n, rel in relations]
        return self.query('select jsonb_build_object(' + ','.join(terms) + ');')

    def state_snapshot(self):
        relations = self.snapshot()
        # The reused closure oracle checks the one permitted marker separately,
        # while requiring every other relation and Auth identity to stay exact.
        if getattr(self, '_closure_marker_checked_separately', False):
            relations.pop('private.owner_account_closures')
        return {'relations': relations, 'auth_identity_state': self.query(
            "select coalesce(jsonb_agg(jsonb_build_object('id',id,'deleted_at',deleted_at,'banned_until',banned_until) order by id),'[]'::jsonb) from auth.users;")}

    def closed_controls(self, a, b, sale, before):
        self._closure_marker_checked_separately = True
        legacy_before = {'relations': {k: v for k, v in before['relations'].items()
                          if k != 'private.owner_account_closures'},
                         'auth_identity_state': before['auth_identity_state']}
        try:
            return super().closed_controls(a, b, sale, legacy_before)
        finally:
            self._closure_marker_checked_separately = False

    def chain(self, expected, label):
        actual = self.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;')
        self.record(label, applied(expected, actual))

    def setup_oauth(self, actors):
        code, client = self.request('POST', '/auth/v1/admin/oauth/clients', {
            'redirect_uris': ['http://127.0.0.1:54325/test-oauth-callback'], 'client_type': 'public',
            'token_endpoint_auth_method': 'none', 'grant_types': ['authorization_code', 'refresh_token'],
            'client_name': 'B5 isolated composed'}, admin=True)
        self.record('genuine_oauth_client', code == 201 and isinstance(client.get('client_id'), str))
        self.client_id = client['client_id']
        for label, actor in actors.items():
            self.oauth_token(actor, 'initial_' + label, self.client_id)

    def price_function(self):
        paths = [p for p in Path('.tanstack').rglob('*') if p.is_file()] if Path('.tanstack').exists() else []
        paths += list(Path('.output/server').rglob('*.mjs'))
        found = []
        for p in paths:
            s = p.read_text(errors='replace')
            found += re.findall(r'["\']([a-f0-9]{40,64})["\']\s*:\s*\{[^}]{0,1000}?(?:resolvePaddlePrice)', s)
            found += re.findall(r'createServerRpc\(["\']([^"\']+)["\'],\s*[^,]+,\s*["\']resolvePaddlePrice["\']', s)
        ids = sorted(set(found))
        self.record('compiler_identifies_one_real_price_function', len(ids) == 1, count=len(ids))
        self.function_id = ids[0]

    def denied_state(self, actor, label, sale):
        digest = hashlib.sha256(actor['token'].encode()).hexdigest()
        before = self.state_snapshot()
        for name in ('current_tenant_id', 'get_tenant_today_estimate', 'create_sale_with_items'):
            self.live_token(actor, label + '_RPC_' + name)
            code, body = self.request('POST', '/rest/v1/rpc/' + name, sale if name == 'create_sale_with_items' else {}, token=actor['token'])
            self.record(label + '_named_RPC_' + name, explicit_inactive(code, body), status=code)
        for table in ('tenants', 'profiles', 'user_roles', 'products', 'customers', 'orders', 'order_items', 'payments', 'financial_audit_log'):
            code, body = self.request('GET', '/rest/v1/' + table + '?select=*', token=actor['token'])
            self.record(label + '_REST_' + table, explicit_inactive(code, body) or (code == 200 and body == []),
                        status=code, corroboration='same live token named42501/account_inactive RPC and pretransition positives')
        self.initialize(actor, label)
        for name in TOOLS:
            code, body = self.invoke(name, actor)
            self.record(label + '_MCP_' + name, account_tool_denial(code, body, name), status=code)
        self.live_token(actor, label + '_price')
        self.check_price(label + '_price_gate', actor['token'], 'account_inactive', 0)
        self.record(label + '_all25_relations_and_identity_unchanged', self.state_snapshot() == before)
        self.record(label + '_original_token_bytes_unchanged', hashlib.sha256(actor['token'].encode()).hexdigest() == digest)

    def ban(self, actor, label, sale, active):
        self.live_token(actor, label + '_before')
        self.initialize(actor, label + '_before')
        for name in TOOLS:
            code, body = self.invoke(name, actor)
            self.record(label + '_before_' + name, tool_success(code, body, name), status=code)
        self.check_price(label + '_before_price', actor['token'], 'pri_oc_app_dummy', 1)
        code, _ = self.request('PUT', '/auth/v1/admin/users/' + actor['uid'], {'ban_duration': '24h'}, admin=True)
        self.record(label + '_real_provider_ban', code == 200)
        self.denied_state(actor, label + '_old_token', sale)
        for suffix, path, payload in [
            ('new_password_login', '/auth/v1/token?grant_type=password', {'email': actor['email'], 'password': actor['password']}),
            ('old_session_refresh', '/auth/v1/token?grant_type=refresh_token', {'refresh_token': actor['refresh']})]:
            code, body = self.request('POST', path, payload)
            self.record(label + '_' + suffix + '_issuance_denied', auth_ban_denial(code, body), status=code)
        self.initialize(active, label + '_unaffected_owner')
        code, body = self.invoke('list_products', active)
        self.record(label + '_unaffected_positive', tool_success(code, body, 'list_products'))

    def permissions(self, a, b, staff):
        # Do not call historical46/47 run() wrappers or their empty-finance seed paths.
        self.sql("insert into public.platform_admins(user_id,note) values ('" + a['uid'] + "','B5 fixture');")
        ScannerProbe.positive(self, 'composed_admin_scanner_positive', a)
        ScannerProbe.positive(self, 'composed_service_scanner_positive', service=True)
        for label, actor in [('ordinary_owner', b), ('staff', staff)]:
            ScannerProbe.deny(self, 'composed_scanner_' + label, actor, a)
        ScannerProbe.deny(self, 'composed_scanner_trigger_spoof', b, a, trigger='cron')
        ScannerProbe.deny(self, 'composed_scanner_anonymous', None, a, message=None)
        rights = self.query("select jsonb_object_agg(attname,jsonb_build_object('insert',has_column_privilege('authenticated','public.tenants',attname,'INSERT'),'update',has_column_privilege('authenticated','public.tenants',attname,'UPDATE'))) from pg_attribute where attrelid='public.tenants'::regclass and attname in ('trial_ends_at','subscription_status','subscription_plan','paddle_customer_id','paddle_subscription_id');")
        self.record('all_five_protected_columns_no_client_write_grant', set(rights) == set(PROTECTED) and all(not any(v.values()) for v in rights.values()))
        for col, value in VALUES.items():
            before = self.state_snapshot()
            code, body = self.request('PATCH', '/rest/v1/tenants?id=eq.' + a['tenant'], {'name': 'MUST NOT PERSIST', col: value}, token=a['token'])
            self.record('entitlement_' + col + '_explicit_denial', explicit_denial(code, body), status=code)
            self.record('entitlement_' + col + '_atomic_invariance', self.state_snapshot() == before)
        code, rows = self.request('PATCH', '/rest/v1/tenants?id=eq.' + a['tenant'], {'name': 'B5 valid settings'}, token=a['token'])
        self.record('owner_settings_positive', code == 200 and len(rows) == 1 and rows[0]['name'] == 'B5 valid settings')
        before = self.state_snapshot()
        code, body = self.request('PATCH', '/rest/v1/tenants?id=eq.' + b['tenant'], {'name': 'MUST NOT PERSIST'}, token=a['token'])
        self.record('cross_tenant_settings_denied_with_own_positive', code == 200 and body == [])
        self.record('cross_tenant_settings_invariance', self.state_snapshot() == before)

    def run_composed(self, mode):
        self.mode = mode
        inv = inventory()
        self.chain(inv['original_versions'] if mode == 'upgrade' else inv['full_versions'], 'exact_initial_chain_' + mode)
        self.record('empty_disposable_fixture_initially', all(v == 0 for v in self.counts().values()))
        a, b = self.fixture('B5_A'), self.fixture('B5_B')
        staff = self.fixture('B5_staff_A', a['tenant'], True)
        banned = self.fixture('B5_future_banned')
        sale, product, order = self.financial_fixture(b)
        customer_ids = {}
        for label, actor in [('A', a), ('B', b)]:
            code, rows = self.request('POST', '/rest/v1/customers', {'tenant_id': actor['tenant'], 'name': 'B5 customer ' + label}, token=actor['token'])
            self.record(label + '_real_owned_customer', code == 201 and len(rows) == 1)
            customer_ids[label] = rows[0]['id']
        before_upgrade = self.state_snapshot()
        if mode == 'upgrade':
            code, body = self.request('POST', RPC, {}, token=b['token'])
            self.record('historical41_missing_closure_explicit_red', code == 404 and body.get('code') == 'PGRST202')
            self.record('baseline_attempt_does_not_change_history', self.state_snapshot() == before_upgrade)
            stack = Path(os.environ['RUNNER_TEMP']) / 'monjez-tanstack-route'
            for path in inv['all_paths']:
                shutil.copy2(ROOT / path, stack / 'supabase/migrations' / Path(path).name)
            with (Path(os.environ['RUNNER_TEMP']) / 'B5-upgrade-private.log').open('w') as log:
                result = subprocess.run(['supabase', '--workdir', str(stack), 'migration', 'up', '--local'], stdout=log, stderr=log, timeout=180)
            self.record('real_populated41_to50_migration', result.returncode == 0)
            after_upgrade = self.state_snapshot()
            self.record('all_original22_public_and_auth_identity_preserved',
                        after_upgrade['auth_identity_state'] == before_upgrade['auth_identity_state']
                        and all(after_upgrade['relations'][k] == v for k, v in before_upgrade['relations'].items()))
            for _ in range(60):
                code, body = self.request('POST', RPC, {}, token=staff['token'])
                if code == 403 and body.get('message') == 'owner_required': break
                if code != 404 or body.get('code') != 'PGRST202': raise HarnessFailure('unexpected schema readiness denial')
                time.sleep(.25)
            self.record('postgrest50_discovery_and_exact_staff_denial', code == 403 and body.get('message') == 'owner_required')
            (self.evidence_dir / 'populated-upgrade.json').write_text(json.dumps({'source': self.source, 'before': before_upgrade, 'after': after_upgrade}, indent=2) + '\n')
        self.chain(inv['full_versions'], 'exact_effective50_chain')
        snapshot = self.snapshot()
        self.record('all_three_new_private_tables_empty', all(snapshot['private.' + n]['count'] == 0 for n in PRIVATE))
        self.index_inventory()
        self.no_truncate()
        self.closure_catalog()
        private_rights = self.query("select jsonb_agg(jsonb_build_object('table',t.tablename,'role',r,'truncate',has_table_privilege(r,format('monjez_private.%I',t.tablename),'TRUNCATE'),'read',has_table_privilege(r,format('monjez_private.%I',t.tablename),'SELECT'))) from pg_tables t cross join unnest(array['anon','authenticated']) r where t.schemaname='monjez_private';")
        self.record('all_private_client_read_and_truncate_denied', len(private_rights) == 6 and all(not x['truncate'] and not x['read'] for x in private_rights))
        self.setup_oauth({'A': a, 'B': b, 'staff': staff, 'banned': banned})
        self.price_function()
        self.start()
        try:
            self.active_controls(a, b, 'composed_before')
            self.metadata_and_negatives(a)
            for label, actor in [('A', a), ('B', b)]:
                code, body = self.invoke('list_customers', actor)
                own = body.get('result', {}).get('structuredContent', {}).get('customers')
                self.record(label + '_populated_MCP_tenant_isolation', tool_success(code, body, 'list_customers') and len(own) == 1 and own[0]['id'] == customer_ids[label])
            self.check_price('active_A_price', a['token'], 'pri_oc_app_dummy', 1)
            self.check_price('active_B_price', b['token'], 'pri_oc_app_dummy', 1)
            self.check_price('anonymous_price', None, 'Unauthorized: No authorization header provided', 0)
            self.permissions(a, b, staff)
            self.sql("insert into public.platform_admins(user_id,note) values ('" + banned['uid'] + "','B5 banned admin fixture');")
            ScannerProbe.positive(self, 'future_banned_admin_scanner_positive', banned)
            self.ban(banned, 'owner_ban', sale, a)
            ScannerProbe.deny(self, 'banned_admin_scanner_explicit_inactive', banned, a, message='account_inactive')
            self.ban(staff, 'staff_ban', sale, a)
            # Staff was tested as forbidden before its ban via scanner; closure needs
            # an active staff positive to distinguish role rejection from inactivity.
            active_staff = self.fixture('B5_active_staff', a['tenant'], True)
            self.oauth_token(active_staff, 'active_staff', self.client_id)
            self.sql("insert into public.platform_admins(user_id,note) values ('" + b['uid'] + "','B5 closed admin fixture');")
            ScannerProbe.positive(self, 'future_closed_admin_scanner_positive', b)
            before_closure = self.state_snapshot()
            self.negative_requests(a, b, active_staff)
            closed = self.closed_controls(a, b, sale, before_closure)
            for label, actor in [('old', b), ('new', self.issued['B_after_closure'])]:
                self.live_token(actor, 'closed_price_' + label)
                self.check_price('closed_price_' + label, actor['token'], 'account_inactive', 0)
                ScannerProbe.deny(self, 'closed_admin_' + label + '_scanner_explicit_inactive', actor, a, message='account_inactive')
            # Private B tables and prior financial history are all in this invariant.
            self.record('closure_preserves_all25_relations_except_single_marker',
                all(self.snapshot()[k] == v for k, v in before_closure['relations'].items() if k != 'private.owner_account_closures')
                and self.snapshot()['private.owner_account_closures']['count'] == 1)
            self.check_price('active_peer_after_closure', a['token'], 'pri_oc_app_dummy', 1)
            for fault in ('database', 'transport', 'timeout'):
                path = self.runtime / 'app.fault'
                subprocess.run(['sudo', '-u', 'mcp-route', 'tee', str(path)], input=fault, text=True, capture_output=True, check=True)
                started = time.monotonic()
                try: self.check_price('unavailable_' + fault, a['token'], 'account_state_unavailable', 0)
                finally: subprocess.run(['sudo', 'rm', '-f', str(path)], check=True)
                if fault == 'timeout': self.record('state_timeout_is_bounded', 2 <= time.monotonic() - started < 10)
            self.record('faults_exercised_exact_state_boundary', self.state()['injected_faults'] == ['database', 'transport', 'timeout'])
            self.firewall_after('app')
            self.record('no_unstubbed_external_fetch', self.state()['external_blocked'] == 0)
            self.record('official_metrics_dummy_sink_exercised', self.state()['metrics_stub_calls'] > 0)
            self.chain(inv['full_versions'], 'exact50_at_finish')
            self.record('tracked_source_unchanged', subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0)
            report = {'source': self.source, 'mode': mode, 'checks': self.controls, 'passed': len(self.controls), 'failed': 0,
                      'before_closure': before_closure, 'after': self.state_snapshot(), 'closed_token_receipt': closed,
                      'process_containment': self.state(), 'firewall': self.firewall_observations,
                      'migration_versions': inv['full_versions'], 'original41': inv['original_versions'],
                      'scope': 'synthetic populated B50 real REST/RPC/OAuth/Nitro MCP+price; provider price response stubbed',
                      'integration_accepted': False, 'merge_approved': False}
            result = publish_result(self.evidence_dir, report, self.secrets + self.oauth_refresh_tokens)
            (self.evidence_dir / 'route-result.json').rename(self.evidence_dir / 'B5-result.json')
            if not result['evidence_no_credentials']: raise HarnessFailure('B5 evidence quarantine')
            print(json.dumps({'B5_mode': mode, 'passed': len(self.controls), 'source': self.source}))
        finally:
            self.stop()


def main():
    p = argparse.ArgumentParser()
    for name in ('status-file', 'evidence-dir'): p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--expected-source', required=True)
    p.add_argument('--mode', choices=('fresh', 'upgrade'), required=True)
    args = p.parse_args()
    probe = None
    try:
        probe = ComposedProbe(args.status_file, args.evidence_dir, args.expected_source)
        probe.run_composed(args.mode)
    except (HarnessFailure, RuntimeError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        args.evidence_dir.mkdir(exist_ok=True, parents=True)
        if probe and (probe.runtime / 'app.json').exists():
            state = probe.state()
            diagnostics = {'source': args.expected_source, 'external_blocked': state.get('external_blocked'),
                           'external_denials': state.get('external_denials', [])}
            (args.evidence_dir / 'blocked-transport.json').write_text(json.dumps(diagnostics, indent=2) + '\n')
        safe = str(error) if isinstance(error, HarnessFailure) else type(error).__name__
        result = {'source': args.expected_source, 'mode': args.mode, 'failed': True, 'reason': safe, 'integration_accepted': False}
        publish_result(args.evidence_dir, result, (probe.secrets + probe.oauth_refresh_tokens) if probe else [])
        (args.evidence_dir / 'route-result.json').rename(args.evidence_dir / 'B5-failure.json')
        print('B5_FAILED ' + safe)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
