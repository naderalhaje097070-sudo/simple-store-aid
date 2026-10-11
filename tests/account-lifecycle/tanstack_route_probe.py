"""Real built Nitro -> src/server.ts -> generated TanStack routes -> locked SDK.

Reuse PR62's real OAuth/PKCE fixtures, initialize sequence and strict tool oracle.
No application handlers are imported by this runner or by the Node preload.
"""
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.request

from mcp_probe import McpProbe, TOOLS, tool_success, account_tool_denial, protocol_body
from live_probe import HarnessFailure, FINANCE_TABLES
from tanstack_route_build import app_environment

APP = 'http://127.0.0.1:54325'
METADATA = '/.well-known/oauth-protected-resource'


def contains_credentials(text, secrets):
    return (any(secret in text for secret in secrets if secret)
            or re.search(r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}', text) is not None
            or re.search(r'sb_(?:secret|publishable)_[A-Za-z0-9_-]{8,}', text) is not None)


def exact_catalog(body):
    tools = body.get('result', {}).get('tools') if isinstance(body, dict) else None
    return (isinstance(tools, list) and len(tools) == 4
            and all(isinstance(tool, dict) for tool in tools)
            and {tool.get('name') for tool in tools} == set(TOOLS))


def lifecycle_accepted(observations):
    expected = [(actor, phase, name) for actor, phase in
                [('A', 'active'), ('B', 'active'), ('B', 'banned_old_jwt'), ('A', 'unaffected_active')]
                for name in TOOLS]
    return (len(observations) == 16
            and [(x.get('actor'), x.get('phase'), x.get('tool')) for x in observations] == expected
            and all(x.get('passed') is True for x in observations))


class TanStackRouteProbe(McpProbe):
    def __init__(self, *args):
        # The credential-free OS/redirect preflight precedes even Probe reading keys.
        runtime = Path(os.environ['RUNNER_TEMP']) / 'route-runtime'
        state = json.loads((runtime / 'preflight.json').read_text())
        firewall = json.loads((runtime.parent / 'route-firewall.json').read_text())
        if not (state.get('guard_ready') is True and state.get('native_redirect_rejected') is True
                and state.get('redirect_manual') is True and state.get('uid') == firewall.get('uid')
                and firewall.get('ipv4_reject_packets', 0) > 0 and firewall.get('ipv6_rule_installed') is True):
            raise HarnessFailure('credential-free containment preflight missing')
        super().__init__(*args)
        self.runtime, self.firewall = runtime, firewall
        self.observations = []
        self.headers = {}
        self.extra_headers = {}
        self.failure_stage = 'startup'
        self.oauth_refresh_tokens = []
        self.firewall_observations = []
        self.readiness = []

    def request(self, method, path, *args, **kwargs):
        status, body = super().request(method, path, *args, **kwargs)
        if path == '/auth/v1/oauth/token' and isinstance(body, dict) and body.get('refresh_token'):
            self.oauth_refresh_tokens.append(body['refresh_token'])
        return status, body

    def http(self, method, path, payload=None, token=None, extra=None):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'MCP-Protocol-Version': '2025-03-26', **(extra or {})}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(APP + path, method=method, headers=headers,
            data=json.dumps(payload).encode() if payload is not None else None)
        try:
            response = self.opener.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        except (urllib.error.URLError, TimeoutError) as error:
            raise HarnessFailure('actual route transport failure') from error
        with response:
            raw = response.read()
            self.headers = dict(response.headers)
            self.mcp_session_id_present = bool(response.headers.get('Mcp-Session-Id'))
            try:
                body = protocol_body(raw)
            except (ValueError, UnicodeError):
                body = {'non_json_error': True}
            self.last_body = body
            return response.status, body

    def initialize(self, actor, label):
        super().initialize(actor, label)
        self.control('exact_four_unique_tools_' + label, exact_catalog(self.last_body))

    def local_mcp(self, method, payload=None, token=None):
        return self.http(method, '/mcp', payload, token, self.extra_headers)

    def state(self, label='app'):
        return json.loads((self.runtime / (label + '.json')).read_text())

    def rejected_packets(self):
        output = subprocess.run(['sudo', 'iptables', '-nvxL', 'MCP_ROUTE'],
                                capture_output=True, text=True, check=True).stdout
        rows = [int(line.split()[0]) for line in output.splitlines() if 'REJECT' in line]
        if len(rows) != 1:
            raise HarnessFailure('UID firewall counter missing')
        output6 = subprocess.run(['sudo', 'ip6tables', '-nvxL', 'OUTPUT'],
                                 capture_output=True, text=True, check=True).stdout
        rows6 = [int(line.split()[0]) for line in output6.splitlines()
                 if 'REJECT' in line and f"owner UID match {self.firewall['uid']} " in line]
        if len(rows6) != 1:
            raise HarnessFailure('UID IPv6 firewall counter missing')
        return {'ipv4': rows[0], 'ipv6': rows6[0]}

    def firewall_after(self, label):
        end = self.rejected_packets()
        observation = {'process': label, 'baseline_after_canary_before_bundle': self.firewall_baseline,
                       'end': end, 'unexpected_reject_packets': {
                           key: end[key] - self.firewall_baseline[key] for key in end}}
        self.firewall_observations.append(observation)
        self.control(label + '_no_native_outbound_attempts', end == self.firewall_baseline)

    def start(self, label='app', conflict=False):
        env = app_environment(self.anon)
        allowed = ('MONGEZZ_DEPLOY_TARGET', 'CI_ISOLATED_SUPABASE', 'SUPABASE_URL', 'VITE_SUPABASE_URL',
                   'SUPABASE_PUBLISHABLE_KEY', 'VITE_SUPABASE_PUBLISHABLE_KEY',
                   'SUPABASE_PROJECT_ID', 'VITE_SUPABASE_PROJECT_ID')
        server_env = {k: env[k] for k in allowed}
        if conflict:
            server_env['SUPABASE_PROJECT_ID'] = server_env['VITE_SUPABASE_PROJECT_ID'] = 'route-conflict'
        server_env.update(NITRO_HOST='127.0.0.1', NITRO_PORT='54325',
                          MCP_ROUTE_STATE=str(self.runtime / (label + '.json')),
                          MCP_ROUTE_RELEASE=str(self.runtime.parent / ('route-release-' + label)))
        release = Path(server_env['MCP_ROUTE_RELEASE'])
        release.unlink(missing_ok=True)
        self.log = (Path(os.environ['RUNNER_TEMP']) / ('route-' + label + '-private.log')).open('w')
        command = ['sudo', '-u', 'mcp-route', 'env', '-i', 'PATH=/usr/bin:/bin']
        command += [k + '=' + v for k, v in server_env.items()]
        command += [shutil.which('node'), '--import', str(Path('tests/account-lifecycle/tanstack_route_guard.mjs').resolve()),
                    str(Path('.output/server/index.mjs').resolve())]
        self.process = subprocess.Popen(command, stdout=self.log, stderr=self.log)
        for _ in range(80):
            if (self.runtime / (label + '.json')).exists() and self.state(label).get('guard_ready') is True:
                self.firewall_baseline = self.rejected_packets()
                release.write_text('release actual bundle\n')
                break
            if self.process.poll() is not None:
                raise HarnessFailure('actual process containment failed')
            time.sleep(.1)
        else:
            raise HarnessFailure('actual preload not ready before bundle')
        for _ in range(80):
            if self.process.poll() is not None:
                raise HarnessFailure('built application process failed')
            try:
                status, _ = self.http('GET', METADATA)
                self.readiness.append({'process': label, 'status': status})
                if (conflict and status == 500) or (not conflict and status == 200):
                    return
                if not conflict and status >= 500:
                    self.failure_stage = 'built_metadata_http_500'
                    raise HarnessFailure('Actual built application metadata failed')
            except HarnessFailure:
                if self.failure_stage == 'built_metadata_http_500':
                    raise
                pass
            time.sleep(.25)
        raise HarnessFailure('built route did not become ready')

    def stop(self):
        # sudo forwards TERM to its child; UID kill also covers failed startup.
        subprocess.run(['sudo', 'pkill', '-TERM', '-u', 'mcp-route'], capture_output=True)
        if getattr(self, 'process', None):
            self.process.wait(timeout=10)
        if getattr(self, 'log', None):
            self.log.close()

    def phase(self, actor, label, phase, banned=False):
        for name in TOOLS:
            status, body = self.invoke(name, actor)
            passed = account_tool_denial(status, body, name) if banned else tool_success(status, body, name)
            self.observations.append({'actor': label, 'phase': phase, 'tool': name,
                                      'status': status, 'passed': passed,
                                      'isError': body.get('result', {}).get('isError') if isinstance(body, dict) else None,
                                      'expected_account_inactive': passed if banned else False})
        self.control(label + '_' + phase + '_four_tools', all(x['passed'] for x in self.observations[-4:]))

    def metadata_and_negatives(self, actor):
        self.failure_stage = 'metadata_authentication'
        status, metadata = self.http('GET', METADATA)
        self.control('actual_metadata_local_resource_and_issuer', status == 200
                     and metadata.get('resource') == APP + '/mcp'
                     and metadata.get('authorization_servers') == [self.base + '/auth/v1'])
        payload = {'jsonrpc': '2.0', 'id': 9, 'method': 'tools/list', 'params': {}}
        for label, token in [('missing', None), ('malformed', 'invalid-local-test-token'),
                             ('oauth_client_claim_absent', actor['session_token'])]:
            status, body = self.http('POST', '/mcp', payload, token)
            challenge = next((v for k, v in self.headers.items() if k.lower() == 'www-authenticate'), '')
            self.control('actual_route_' + label + '_auth_denied', status == 401
                         and body == {'error': 'unauthorized'} and challenge.startswith('Bearer ')
                         and f'resource_metadata="{APP}{METADATA}"' in challenge
                         and (label == 'missing' or 'error="invalid_token"' in challenge), status=status)
        # The generated adapter trusts first X-Forwarded-Host for advertised resource;
        # its options do not enable forwarded proto. Neither is an issuer input.
        for label, headers in [('host', {'Host': 'hostile.example'}),
                              ('forwarded', {'X-Forwarded-Host': 'forwarded.example, ignored.example',
                                             'X-Forwarded-Proto': 'https',
                                             'Forwarded': 'host=other.example;proto=https'})]:
            status, metadata = self.http('GET', METADATA, extra=headers)
            self.control(label + '_issuer_stays_trusted', status == 200
                         and metadata.get('authorization_servers') == [self.base + '/auth/v1'])
            self.extra_headers = headers
            self.initialize(actor, 'hostile_' + label)
            self.extra_headers = {}
        self.control('headers_no_remote_jwks_or_discovery', self.state()['external_blocked'] == 0)

    def run_route(self):
        before, initial, versions = None, self.counts(), []
        self.control('fresh_empty_disposable_stack', all(v == 0 for v in initial.values()))
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        self.control('exact_43_migrations', len(files) == 43 and versions == [p.name.split('_')[0] for p in files])
        build = json.loads((self.evidence_dir / 'build.json').read_text())
        self.control('actual_built_app_contract', build['source_sha'] == self.source and build['exit_code'] == 0
                     and all(build['compiled_contract_markers'].values()) and build['tracked_source_unchanged'])
        accepted, failure = False, None
        try:
            a, b = self.fixture('route_A'), self.fixture('route_B')
            self.control('distinct_tenants', a['tenant'] != b['tenant'] and a['uid'] != b['uid'])
            status, client = self.request('POST', '/auth/v1/admin/oauth/clients', {
                'redirect_uris': [APP + '/test-oauth-callback'], 'client_type': 'public',
                'token_endpoint_auth_method': 'none', 'grant_types': ['authorization_code', 'refresh_token'],
                'client_name': 'isolated-tanstack-route'}, admin=True)
            self.control('oauth_client_registered', status == 201 and bool(client.get('client_id')))
            for label, actor in [('A', a), ('B', b)]:
                self.oauth_token(actor, label, client['client_id'])
            before = self.snapshot()
            self.start()
            self.control('guard_in_actual_node_process', self.state()['guard_ready'] is True
                         and self.state()['uid'] == self.firewall['uid'])
            self.metadata_and_negatives(a)
            for label, actor in [('A', a), ('B', b)]:
                self.failure_stage = 'initialize_' + label
                self.initialize(actor, label)
            self.failure_stage = 'active_A'
            self.phase(a, 'A', 'active')
            self.failure_stage = 'active_B'
            self.phase(b, 'B', 'active')
            self.failure_stage = 'ban_B'
            old_b = b['token']
            status, _ = self.request('PUT', '/auth/v1/admin/users/' + b['uid'], {'ban_duration': '24h'}, admin=True)
            self.control('ban_saved', status == 200)
            self.control('ban_persisted_sql', self.sql("select (banned_until>now())::text from auth.users where id='" + b['uid'] + "';") == 'true')
            self.control('same_preban_B_token', b['token'] == old_b)
            self.failure_stage = 'banned_B'
            self.phase(b, 'B', 'banned_old_jwt', banned=True)
            self.failure_stage = 'unaffected_A'
            self.phase(a, 'A', 'unaffected_active')
            health = self.state()
            self.control('local_jwks_used', health['downstream'].get('jwks', 0) > 0)
            self.control('no_unexpected_outbound', health['external_blocked'] == 0)
            self.firewall_after('app')
            self.stop()
            self.failure_stage = 'runtime_build_conflict'
            self.start('conflict', conflict=True)
            status, _ = self.http('POST', '/mcp', {'jsonrpc': '2.0', 'id': 12, 'method': 'tools/list'}, a['token'])
            conflict = self.state('conflict')
            self.control('runtime_build_conflict_fail_closed', status == 500
                         and conflict['runtime_conflict_errors'] > 0 and conflict['downstream'] == {}
                         and conflict['external_blocked'] == 0, status=status)
            self.firewall_after('conflict')
            self.control('exact_order_and_explicit_results', lifecycle_accepted(self.observations))
            accepted = True
        except (HarnessFailure, OSError, ValueError, KeyError, subprocess.SubprocessError):
            # Only allowlisted stage escapes; no exception/JWT/HTTP body serialization.
            failure = self.failure_stage
        finally:
            self.stop()
            after, final = self.snapshot(), self.counts()
            preserved = before is not None and after == before
            empty = all(final[t] == 0 for t in FINANCE_TABLES)
            clean = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0
            accepted = accepted and preserved and empty and clean
            self.controls += [{'name': 'public_22_fingerprints_unchanged', 'passed': preserved},
                              {'name': 'financial_7_empty', 'passed': empty},
                              {'name': 'tracked_source_unchanged', 'passed': clean}]
            result = {'source_sha': self.source, 'full_local_route_accepted': accepted,
                      'integration_accepted': False, 'failure_stage': failure,
                      'actual_path': 'HTTP -> Nitro node-server -> src/server.ts -> generated TanStack /mcp -> SDK 0.20.1 -> local Supabase',
                      'checks': self.controls, 'observations': self.observations,
                      'migration_versions': versions, 'initial_counts': initial, 'final_counts': final,
                      'history_before': before, 'history_after': after,
                      'runtime': self.state() if (self.runtime / 'app.json').exists() else None,
                      'conflict_runtime': self.state('conflict') if (self.runtime / 'conflict.json').exists() else None,
                      'firewall': self.firewall,
                      'firewall_observations': self.firewall_observations,
                      'readiness_http': self.readiness,
                      'not_verified': ['Cloudflare runtime', 'production', 'nonempty financial isolation',
                                       'concurrency', 'broader integration acceptance']}
            # Check private output before publishing evidence. Known credentials never
            # reach the artifact; a leak changes acceptance and is reported as a bool.
            secrets = [self.anon, self.admin, *self.oauth_refresh_tokens]
            for actor in [locals().get('a'), locals().get('b')]:
                if actor:
                    secrets += [actor[k] for k in ('token', 'session_token', 'refresh', 'password') if k in actor]
            private_paths = list(Path(os.environ['RUNNER_TEMP']).glob('route-*-private.log'))
            log_leak = any(contains_credentials(p.read_text(), secrets) for p in private_paths)
            artifact_leak = contains_credentials(json.dumps(result), secrets) or any(
                contains_credentials(p.read_text(), secrets) for p in self.evidence_dir.glob('*.json'))
            result['private_logs_no_known_credentials'] = not log_leak
            result['evidence_no_credentials'] = not artifact_leak
            result['full_local_route_accepted'] = accepted and not log_leak and not artifact_leak
            (self.evidence_dir / 'route-result.json').write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps({'full_local_route_accepted': result['full_local_route_accepted'], 'failure_stage': failure,
                              'checks': len(self.controls)}))
        return 0 if result['full_local_route_accepted'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status-file', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(TanStackRouteProbe(args.status_file, args.evidence_dir, args.expected_source).run_route())
    except (HarnessFailure, OSError, ValueError, subprocess.SubprocessError):
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'route-harness-failure.json').write_text(json.dumps({
            'full_local_route_accepted': False, 'integration_accepted': False, 'failure_stage': 'preflight_or_baseline'}) + '\n')
        print('ROUTE_HARNESS_FAILURE: sanitized evidence retained')
        raise SystemExit(2)
