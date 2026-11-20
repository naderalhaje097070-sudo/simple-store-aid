"""Actual app MCP boundary; active failure never passes banned-account acceptance."""
import argparse
import base64
import json
import hashlib
import re
import secrets
import urllib.parse
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

from live_probe import Probe, HarnessFailure, FINANCE_TABLES

TOOLS = {'list_products': 'products', 'list_customers': 'customers',
         'list_recent_orders': 'orders', 'today_summary': 'summary'}


def safe_authorization_id(value):
    # Auth's public AuthorizationID is SecureAlphanumeric(32), not its DB UUID.
    # Reject any path/query delimiters before inserting it into a local API path.
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9]{32}', value) is not None


def tool_success(status, body, name):
    if status != 200 or name not in TOOLS or not isinstance(body, dict):
        return False
    result = body.get('result')
    if body.get('error') is not None or not isinstance(result, dict) or result.get('isError'):
        return False
    structured = result.get('structuredContent')
    if not isinstance(structured, dict) or TOOLS[name] not in structured:
        return False
    value = structured[TOOLS[name]]
    return (isinstance(value, dict) and 'sales' in value) if name == 'today_summary' else isinstance(value, list)


def account_tool_denial(status, body, name):
    # Empty fixtures make empty RLS results indistinguishable from successful reads.
    # Only an explicit expected account denial proves the requested tool rejection.
    return (status == 200 and isinstance(body, dict) and isinstance(body.get('result'), dict)
            and body['result'].get('isError') is True
            and body['result'].get('content') == [{'type': 'text', 'text': 'account_inactive'}])


def protocol_body(raw):
    if not raw:
        return None
    text = raw.decode('utf8')
    if text.startswith('event:') or text.startswith('data:'):
        data = [line[6:] for line in text.splitlines() if line.startswith('data: ')]
        if len(data) != 1:
            raise HarnessFailure('MCP SSE shape')
        return json.loads(data[0])
    return json.loads(text)


class McpProbe(Probe):
    def snapshot(self):
        tables = self.query("select jsonb_agg(tablename order by tablename) from pg_tables where schemaname='public';")
        if not isinstance(tables, list) or len(tables) != 22:
            raise HarnessFailure('MCP public surface mismatch')
        return {t: self.query("select to_jsonb(md5(coalesce(jsonb_agg(to_jsonb(t) order by to_jsonb(t)::text)::text,'[]'))) from public." + t + ' t;') for t in tables}

    def local_mcp(self, method, payload=None, token=None):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'MCP-Protocol-Version': '2025-03-26'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        path = '/test-health' if method == 'GET' else '/mcp'
        req = urllib.request.Request('http://127.0.0.1:54325' + path, method=method, headers=headers,
                                     data=json.dumps(payload).encode() if payload is not None else None)
        try:
            with self.opener.open(req, timeout=15) as response:
                self.mcp_session_id_present = bool(response.headers.get('Mcp-Session-Id'))
                return response.status, protocol_body(response.read())
        except urllib.error.HTTPError as error:
            raw = error.read()
            try:
                body = protocol_body(raw)
            except (ValueError, UnicodeError):
                body = {'non_json_error': True}
            return error.code, body
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise HarnessFailure('MCP transport or response failure') from exc

    def oauth_token(self, actor, label, client_id):
        # Genuine local OAuth code/PKCE exchange. Never mint/modify a JWT or relax SDK policy.
        callback = 'http://127.0.0.1:54325/test-oauth-callback'
        verifier = secrets.token_urlsafe(48)
        state = secrets.token_urlsafe(24)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        query = urllib.parse.urlencode({'client_id': client_id, 'redirect_uri': callback,
                                       'response_type': 'code', 'scope': 'openid email profile',
                                       'state': state, 'code_challenge': challenge,
                                       'code_challenge_method': 'S256'})
        request = urllib.request.Request(self.base + '/auth/v1/oauth/authorize?' + query,
                                         headers={'apikey': self.anon})
        # NoRedirect captures the provider Location without ever following it.
        try:
            with self.opener.open(request, timeout=15):
                raise HarnessFailure('OAuth authorize must return redirect')
        except urllib.error.HTTPError as error:
            location = urllib.parse.urlparse(error.headers.get('Location', ''))
            params = urllib.parse.parse_qs(location.query)
            self.control('oauth_authorize_' + label, error.code == 302
                         and location.scheme == 'http' and location.netloc == '127.0.0.1:3000'
                         and location.path == '/oauth/consent'
                         and len(params.get('authorization_id', [])) == 1)
            authorization_id = params['authorization_id'][0]
            self.control('oauth_authorization_id_format_' + label,
                         safe_authorization_id(authorization_id))
        status, details = self.request('GET', '/auth/v1/oauth/authorizations/' + authorization_id,
                                       token=actor['token'])
        if isinstance(details, dict) and isinstance(details.get('redirect_url'), str):
            # Auth2.188.1 OAuthServerGetAuthorization auto-approves an existing
            # consent and returns the SAME ConsentResponse shape. The common
            # callback/state/code/PKCE/client checks below remain mandatory.
            self.control('oauth_existing_consent_' + label, status == 200)
            approved = details
        else:
            self.control('oauth_details_' + label, status == 200
                         and details.get('client', {}).get('id') == client_id)
            status, approved = self.request('POST', '/auth/v1/oauth/authorizations/' + authorization_id + '/consent',
                                            {'action': 'approve'}, token=actor['token'])
        redirect = urllib.parse.urlparse(approved.get('redirect_url', ''))
        params = urllib.parse.parse_qs(redirect.query)
        self.control('oauth_consent_' + label, status == 200
                     and redirect.scheme == 'http' and redirect.netloc == '127.0.0.1:54325'
                     and redirect.path == '/test-oauth-callback'
                     and params.get('state') == [state] and len(params.get('code', [])) == 1)
        status, token = self.request('POST', '/auth/v1/oauth/token', {
            'grant_type': 'authorization_code', 'code': params['code'][0],
            'redirect_uri': callback, 'client_id': client_id, 'code_verifier': verifier})
        self.control('oauth_exchange_' + label, status == 200 and isinstance(token.get('access_token'), str))
        actor['session_token'] = actor['token']
        actor['token'] = token['access_token']
        claims = json.loads(base64.urlsafe_b64decode(actor['token'].split('.')[1] + '=='))
        self.control('oauth_bound_claims_' + label, claims.get('sub') == actor['uid']
                     and claims.get('client_id') == client_id
                     and claims.get('iss') == self.base + '/auth/v1'
                     and claims.get('aud') == 'authenticated')

    def initialize(self, actor, label):
        status, body = self.local_mcp('POST', {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
            'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
                       'clientInfo': {'name': 'monjez-local-lifecycle', 'version': '1.0.0'}}}, actor['token'])
        result = body.get('result', {}) if isinstance(body, dict) else {}
        self.control('mcp_initialize_' + label, status == 200 and body.get('id') == 1
                     and result.get('protocolVersion') == '2025-03-26'
                     and result.get('serverInfo', {}).get('name') == 'mongezz-mcp'
                     and isinstance(result.get('capabilities', {}).get('tools'), dict), status=status)
        # Locked SDK0.20.1 creates a transport per request with sessionIdGenerator undefined.
        self.control('mcp_stateless_session_' + label, not self.mcp_session_id_present)
        status, body = self.local_mcp('POST', {'jsonrpc': '2.0', 'method': 'notifications/initialized'}, actor['token'])
        self.control('mcp_initialized_' + label, status == 202 and body is None, status=status)
        status, body = self.local_mcp('POST', {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/list', 'params': {}}, actor['token'])
        result = body.get('result', {}) if isinstance(body, dict) else {}
        self.control('mcp_catalog_' + label, status == 200
                     and {tool.get('name') for tool in result.get('tools', [])} == set(TOOLS), status=status)

    def invoke(self, name, actor):
        return self.local_mcp('POST', {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
                                      'params': {'name': name, 'arguments': {}}}, actor['token'])

    def run_mcp(self):
        initial = self.counts()
        self.control('fresh_empty_disposable_stack', all(v == 0 for v in initial.values()))
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        self.control('exact_final_43_migrations', len(files) == 43 and versions == [p.name.split('_')[0] for p in files])
        a, b = self.fixture('mcp_owner_A'), self.fixture('mcp_owner_B')
        self.control('distinct_actor_tenants', a['tenant'] != b['tenant'] and a['uid'] != b['uid'])
        status, client = self.request('POST', '/auth/v1/admin/oauth/clients', {
            'redirect_uris': ['http://127.0.0.1:54325/test-oauth-callback'],
            'client_type': 'public', 'token_endpoint_auth_method': 'none',
            'grant_types': ['authorization_code', 'refresh_token'], 'client_name': 'isolated-mcp-probe'}, admin=True)
        self.control('local_oauth_client_registered', status == 201 and isinstance(client.get('client_id'), str))
        for label, actor in [('A', a), ('B', b)]:
            self.oauth_token(actor, label, client['client_id'])
        for label, actor in [('A', a), ('B', b)]:
            status, user = self.request('GET', '/auth/v1/user', token=actor['token'])
            self.control('auth_provider_verified_' + label, status == 200 and user.get('id') == actor['uid'], status=status)
            status, rows = self.own_rows(actor, 'tenants')
            self.control('direct_active_own_tenant_' + label, status == 200 and len(rows) == 1 and rows[0]['id'] == actor['tenant'], status=status)
            status, summary = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=actor['token'])
            self.control('direct_active_summary_' + label, status == 200 and isinstance(summary, dict) and 'sales' in summary, status=status)
        before = self.snapshot()
        server_status = Path(os.environ['RUNNER_TEMP']) / 'mcp-test-public-status.json'
        server_status.write_text(json.dumps({'API_URL': self.base, 'ANON_KEY': self.anon}))
        server_status.chmod(0o600)
        env = dict(os.environ, MCP_TEST_STATUS_FILE=str(server_status))
        log = Path(os.environ['RUNNER_TEMP']) / 'mcp-server-private.log'
        outcome, reason = 'ENV_NATIVE_01_MCP_HARNESS_FAILURE', None
        observed, health = [], None
        with log.open('w') as output:
            process = subprocess.Popen(['bun', 'tests/account-lifecycle/mcp_server.mjs'], env=env, stdout=output, stderr=output)
            try:
                ready = False
                for _ in range(80):
                    if process.poll() is not None:
                        raise HarnessFailure('MCP server startup failed')
                    try:
                        status, health = self.local_mcp('GET')
                        ready = status == 200 and health.get('ready') is True
                    except HarnessFailure:
                        pass
                    if ready:
                        break
                    time.sleep(0.25)
                self.control('actual_app_locked_adapter_ready', ready and isinstance(health, dict)
                             and health.get('sdk_version') == '0.20.1')
                self.control('pinned_local_oauth_configuration',
                             health.get('source_derived_issuer') == self.base + '/auth/v1'
                             and health.get('source_jwks_uri') == self.base + '/auth/v1/.well-known/jwks.json'
                             and health.get('oauth_client_claim_required') is True
                             and health.get('session_mode') == 'stateless')
                claims = json.loads(base64.urlsafe_b64decode(a['token'].split('.')[1] + '=='))
                issuer_matches = claims.get('iss') == health['source_derived_issuer']
                for label, actor in [('A', a), ('B', b)]:
                    self.initialize(actor, label)
                    for name in TOOLS:
                        status, body = self.invoke(name, actor)
                        passed = tool_success(status, body, name)
                        observed.append({'actor': label, 'tool': name, 'phase': 'active',
                                         'status': status, 'passed': passed,
                                         'jsonrpc_error': isinstance(body, dict) and body.get('error') is not None})
                _, health = self.local_mcp('GET')
                active_ok = all(x['passed'] for x in observed)
                # Preserve all four actual tool observations, then stop before bans
                # if authentication/setup is unhealthy. HTTP401 is not lifecycle proof.
                if not active_ok:
                    outcome = 'ENV_NATIVE_01_MCP_ACTIVE_CONTROL_BLOCKED'
                    reason = 'source_issuer_does_not_match_local_auth' if not issuer_matches else 'actual_mcp_active_control_failed'
                else:
                    if health['blocked_issuer_requests'] or health['blocked_other_requests'] or health['sdk_exceptions']:
                        raise HarnessFailure('MCP active path attempted external network or raised')
                    status, _ = self.request('PUT', '/auth/v1/admin/users/' + b['uid'], {'ban_duration': '24h'}, admin=True)
                    self.control('committed_ban_saved', status == 200)
                    self.control('committed_ban_verified', self.sql("select (banned_until>now())::text from auth.users where id='" + b['uid'] + "';") == 'true')
                    negatives_ok = True
                    for name in TOOLS:
                        status, body = self.invoke(name, b)
                        denied = account_tool_denial(status, body, name)
                        negatives_ok = negatives_ok and denied
                        empty_filtered = (name != 'today_summary' and tool_success(status, body, name)
                                          and body['result']['structuredContent'][TOOLS[name]] == [])
                        observed.append({'actor': 'B', 'tool': name, 'phase': 'banned_old_jwt',
                                         'status': status, 'passed': denied,
                                         'empty_result_only': empty_filtered,
                                         'expected_account_inactive': denied})
                    # Complete all B old-token denials before testing A, in owner-requested order.
                    for name in TOOLS:
                        status, body = self.invoke(name, a)
                        passed = tool_success(status, body, name)
                        observed.append({'actor': 'A', 'tool': name, 'phase': 'unaffected_active',
                                         'status': status, 'passed': passed})
                        self.control('unaffected_active_' + name, passed, status=status)
                    outcome = 'ENV_NATIVE_01_MCP_FOCUSED_GREEN' if negatives_ok else 'ENV_NATIVE_01_MCP_EXPLICIT_BAN_DENIAL_UNPROVEN'
                    if not negatives_ok:
                        reason = 'empty_finance_results_do_not_prove_explicit_tool_rejection'
                _, health = self.local_mcp('GET')
                self.control('no_outbound_or_sdk_failure', not any(health[k] for k in
                             ['blocked_issuer_requests', 'blocked_other_requests', 'sdk_exceptions']))
                self.control('mcp_stored_no_effect', self.snapshot() == before)
                final = self.counts()
                self.control('all_financial_tables_empty', all(final[t] == 0 for t in FINANCE_TABLES))
                self.control('tracked_source_unchanged', subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0)
                result = {'source_sha': self.source, 'outcome': outcome, 'reason': reason,
                          'mcp_accepted': outcome == 'ENV_NATIVE_01_MCP_FOCUSED_GREEN',
                          'integration_accepted': False, 'active_observations': observed,
                          'issuer_matches_actual_local_token': issuer_matches,
                          'runtime': health, 'checks': self.controls, 'migration_versions': versions,
                          'initial_counts': initial, 'final_counts': final,
                          'history_before': before, 'history_after': self.snapshot(),
                          'not_verified': ['nonempty financial data', 'full TanStack HTTP route', 'cloud OAuth deployment',
                                           'foreign nonempty MCP rows', 'concurrency', 'independent acceptance']}
                if not active_ok:
                    result['not_verified'] += ['committed-ban MCP denial', 'unaffected active MCP after ban']
                elif outcome != 'ENV_NATIVE_01_MCP_FOCUSED_GREEN':
                    result['not_verified'] += ['explicit rejection of all four tools for banned old JWT']
                (self.evidence_dir / 'mcp-result.json').write_text(json.dumps(result, indent=2) + '\n')
                print(json.dumps({'outcome': outcome, 'checks_passed': len(self.controls), 'mcp_accepted': result['mcp_accepted']}))
                return 0 if result['mcp_accepted'] else 2
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=5)
                server_status.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status-file', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(McpProbe(args.status_file, args.evidence_dir, args.expected_source).run_mcp())
    except (HarnessFailure, OSError, ValueError, subprocess.SubprocessError) as error:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        # Never serialize transport exceptions, JWTs or process output.
        (args.evidence_dir / 'mcp-harness-failure.json').write_text(json.dumps({'outcome': 'ENV_NATIVE_01_MCP_HARNESS_FAILURE', 'mcp_accepted': False, 'integration_accepted': False}) + '\n')
        print('ENV_NATIVE_01_MCP_HARNESS_FAILURE: sanitized evidence retained')
        raise SystemExit(2)


