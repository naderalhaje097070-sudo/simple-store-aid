"""Actual app MCP boundary; active failure never passes banned-account acceptance."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

from live_probe import Probe, HarnessFailure, FINANCE_TABLES

TOOLS = {'list_products': 'products', 'list_customers': 'customers',
         'list_recent_orders': 'orders', 'today_summary': 'summary'}


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
    # Empty table results need independent active controls and stored invariance.
    if name != 'today_summary' and tool_success(status, body, name):
        return body['result']['structuredContent'][TOOLS[name]] == []
    return (status == 200 and isinstance(body, dict) and isinstance(body.get('result'), dict)
            and body['result'].get('isError') is True
            and body['result'].get('content') == [{'type': 'text', 'text': 'account_inactive'}])


def protocol_body(raw):
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
                self.control('actual_app_locked_adapter_ready', ready and health.get('sdk_version') == '0.20.1')
                claims = json.loads(base64.urlsafe_b64decode(a['token'].split('.')[1] + '=='))
                issuer_matches = claims.get('iss') == health['source_derived_issuer']
                for label, actor in [('A', a), ('B', b)]:
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
                    for name in TOOLS:
                        status, body = self.invoke(name, b)
                        self.control('banned_old_jwt_' + name, account_tool_denial(status, body, name), status=status)
                        status, body = self.invoke(name, a)
                        self.control('unaffected_active_' + name, tool_success(status, body, name), status=status)
                    outcome = 'ENV_NATIVE_01_MCP_FOCUSED_GREEN'
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
                          'not_verified': ['nonempty financial data', 'full TanStack HTTP route/build', 'cloud OAuth deployment',
                                           'foreign nonempty MCP rows', 'concurrency', 'independent acceptance']}
                if not active_ok:
                    result['not_verified'] += ['committed-ban MCP denial', 'unaffected active MCP after ban']
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
