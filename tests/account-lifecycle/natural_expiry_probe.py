"""L13 genuine local OAuth token, unchanged wall clock, full HTTP route.

Only new fixture/login/code-exchange calls and read-only user operations are allowed.
Reuse the real PR63 application process, PKCE, snapshots and evidence quarantine.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from live_probe import HarnessFailure, FINANCE_TABLES
from mcp_probe import TOOLS, tool_success
from tanstack_route_probe import TanStackRouteProbe, APP, METADATA, contains_credentials, publish_result

TTL = 180
POSTGREST_SKEW = 30
WAIT_MARGIN = 5
PATHS = ['rest', 'rpc', 'initialize', *TOOLS]
PHASES = [('B', 'before'), ('B', 'expired'), ('A', 'fresh'), ('B', 'new'), ('B', 'old_again')]


def expired_rest(status, body):
    return (status == 401 and isinstance(body, dict) and body.get('code') == 'PGRST303'
            and body.get('message') == 'JWT expired')


def expired_mcp(status, body, challenge, crypto):
    # SDK's public response intentionally collapses JWT failures. Require the exact
    # challenge plus independent SAME-token signature/identity/time evidence.
    return (status == 401 and body == {'error': 'unauthorized'}
            and 'error="invalid_token"' in challenge
            and f'resource_metadata="{APP}{METADATA}"' in challenge
            and crypto.get('signature_verified') is True and crypto.get('identity_verified') is True
            and crypto.get('expired') is True and crypto.get('error_code') == 'ERR_JWT_EXPIRED')


def expiry_accepted(observations, timing, continuity):
    leeway = timing.get('max_verifier_leeway')
    if type(leeway) is not int or not POSTGREST_SKEW <= leeway <= 120:
        return False
    expected = [(actor, phase, path) for actor, phase in PHASES for path in PATHS]
    if (len(observations) != len(expected)
            or [(x.get('actor'), x.get('phase'), x.get('path')) for x in observations] != expected
            or not all(x.get('passed') is True for x in observations)
            or not all(continuity.get(k) is True for k in ['accounts_active', 'old_session_exists',
                'no_auto_refresh', 'same_old_token', 'new_token_distinct'])):
        return False
    if (not isinstance(timing.get('iat'), int) or not isinstance(timing.get('exp'), int)
            or timing['exp'] - timing['iat'] != TTL
            or timing.get('positive_finished', float('inf')) >= timing['exp']
            or timing.get('negative_started', 0) <= timing['exp'] + leeway
            or timing.get('real_wait_seconds', 0) < timing['exp'] + leeway - timing['positive_finished']
            or timing.get('monotonic_wait_seconds', 0) < timing['real_wait_seconds'] - 2
            or timing.get('clock_drift_seconds', float('inf')) > 2):
        return False
    for x in observations:
        negative = x['phase'] in ('expired', 'old_again')
        if x.get('token_role') != ('old_B' if x['actor'] == 'B' and x['phase'] != 'new' else 'fresh_' + x['actor']):
            return False
        if negative:
            if (x.get('status') != 401 or x.get('expiration_proven') is not True
                    or x.get('checked_at', 0) <= timing['exp'] + leeway
                    or x.get('same_old_token') is not True):
                return False
        elif x.get('status') != 200 or x.get('checked_at', float('inf')) >= x.get('token_exp', 0):
            return False
    return True


class NaturalExpiryProbe(TanStackRouteProbe):
    def __init__(self, *args):
        super().__init__(*args)
        self.observations, self.timing, self.continuity = [], {}, {}
        self.all_secrets = [self.anon, self.admin]
        self.flow_counts = {'password': 0, 'authorization_code': 0, 'refresh_token': 0}
        self.crypto_receipts = []
        self.old_digest = None
        contract = json.loads((self.evidence_dir / 'expiry-contract.json').read_text())
        self.leeway = max(POSTGREST_SKEW, contract['sdk_clock_tolerance_seconds'])
        self.sdk_leeway = contract['sdk_clock_tolerance_seconds']

    def request(self, method, path, payload=None, token=None, admin=False):
        if (method in ('DELETE', 'PUT') or 'logout' in path
                or isinstance(payload, dict) and ('ban_duration' in payload or 'grant_type' in payload
                    and payload['grant_type'] not in ('authorization_code', 'password'))
                or 'grant_type=refresh_token' in path):
            raise HarnessFailure('expiry fixture forbids revocation or refresh')
        if path == '/auth/v1/oauth/token':
            self.flow_counts['authorization_code'] += 1
        elif path == '/auth/v1/token?grant_type=password':
            self.flow_counts['password'] += 1
        status, body = super().request(method, path, payload, token, admin)
        if isinstance(body, dict):
            self.all_secrets.extend(value for key, value in body.items()
                                   if 'token' in key and isinstance(value, str))
        if isinstance(payload, dict):
            self.all_secrets.extend(payload[key] for key in ('password', 'code', 'code_verifier') if key in payload)
        return status, body

    def verify(self, actor, label):
        receipt = subprocess.run(['node', 'tests/account-lifecycle/natural_expiry_crypto.mjs'],
            input=json.dumps({'token': actor['token'], 'uid': actor['uid'], 'client_id': self.client,
                              'clock_tolerance': self.sdk_leeway}),
            capture_output=True, text=True, timeout=20, check=True)
        value = json.loads(receipt.stdout)
        self.control('crypto_' + label, value.get('signature_verified') is True
                     and value.get('identity_verified') is True and isinstance(value.get('iat'), int)
                     and isinstance(value.get('exp'), int) and value['exp'] - value['iat'] == TTL)
        # Treat session ID as untrusted until UUID parsing and verified signature.
        value['session_id'] = str(uuid.UUID(value['session_id']))
        self.crypto_receipts.append({k: v for k, v in value.items() if k not in ('digest', 'session_id')})
        return value

    def active_state(self, a, b, session):
        active = self.sql("select count(*) from auth.users where id in ('" + a['uid'] + "','" + b['uid']
                          + "') and deleted_at is null and (banned_until is null or banned_until<=now());") == '2'
        exists = self.sql("select count(*) from auth.sessions where id='" + session + "' and user_id='"
                          + b['uid'] + "' and (not_after is null or not_after>now());") == '1'
        return active, exists

    def positive(self, actor, label, phase, crypto):
        self.control(label + '_' + phase + '_unexpired', crypto.get('time_valid') is True and time.time() < crypto['exp'])
        status, user = self.request('GET', '/auth/v1/user', token=actor['token'])
        self.control(label + '_' + phase + '_provider_identity', status == 200 and user.get('id') == actor['uid'])
        self.initialize(actor, label + '_' + phase)
        self.batch(actor, label, phase, crypto, negative=False)

    def batch(self, actor, label, phase, crypto, negative=True):
        token = actor['token']
        role = 'old_B' if label == 'B' and phase != 'new' else 'fresh_' + label
        for path in PATHS:
            checked = time.time()
            same = hashlib.sha256(token.encode()).hexdigest() == self.old_digest
            if negative and (not same or checked <= crypto['exp'] + self.leeway):
                raise HarnessFailure('expired replay timing or token identity invalid')
            challenge, reason = '', None
            if path == 'rest':
                status, body = self.own_rows(actor, 'tenants')
                passed = expired_rest(status, body) if negative else (status == 200 and body == [{'id': actor['tenant']}])
                reason = body.get('message') if isinstance(body, dict) and expired_rest(status, body) else None
            elif path == 'rpc':
                status, body = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=token)
                passed = expired_rest(status, body) if negative else (status == 200 and isinstance(body, dict) and 'sales' in body)
                reason = body.get('message') if isinstance(body, dict) and expired_rest(status, body) else None
            else:
                downstream_before = dict(self.state()['downstream'])
                if path == 'initialize':
                    status, body = self.local_mcp('POST', {'jsonrpc': '2.0', 'id': 11, 'method': 'initialize',
                        'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
                                   'clientInfo': {'name': 'natural-expiry', 'version': '1.0.0'}}}, token)
                    successful = (status == 200 and isinstance(body, dict) and body.get('id') == 11
                                  and body.get('result', {}).get('serverInfo', {}).get('name') == 'mongezz-mcp')
                else:
                    status, body = self.invoke(path, actor)
                    successful = tool_success(status, body, path)
                challenge = next((v for k, v in self.headers.items() if k.lower() == 'www-authenticate'), '')
                passed = expired_mcp(status, body, challenge, crypto) if negative else successful
                if negative:
                    downstream_after = self.state()['downstream']
                    no_user_or_tool_access = all(downstream_after.get(key, 0) == downstream_before.get(key, 0)
                                                for key in ('rest', 'user', 'other_local'))
                    passed = passed and no_user_or_tool_access
                reason = 'invalid_token+verified_exp' if negative and passed else None
            if not negative:
                passed = passed and checked < crypto['exp']
            self.observations.append({'actor': label, 'phase': phase, 'path': path, 'token_role': role,
                'checked_at': checked, 'token_exp': crypto['exp'], 'status': status, 'passed': passed,
                'expiration_proven': negative and passed, 'same_old_token': same,
                'reason': reason, 'no_user_or_tool_access': no_user_or_tool_access
                    if negative and path not in ('rest', 'rpc') else None})
        self.control(label + '_' + phase + '_seven_paths', all(x['passed'] for x in self.observations[-len(PATHS):]))

    def fresh_oauth(self, actor, label):
        status, session = self.request('POST', '/auth/v1/token?grant_type=password',
                                       {'email': actor['email'], 'password': actor['password']})
        self.control('fresh_password_' + label, status == 200 and isinstance(session.get('access_token'), str))
        fresh = {**actor, 'token': session['access_token']}
        self.oauth_token(fresh, label, self.client)
        return fresh

    def run_expiry(self):
        accepted, before, failure, a, b, old, initial = False, None, None, None, None, None, self.counts()
        self.control('fresh_empty_stack', all(v == 0 for v in initial.values()))
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        self.control('exact_43_migrations', len(files) == 43 and versions == [p.name.split('_')[0] for p in files])
        build = json.loads((self.evidence_dir / 'build.json').read_text())
        self.control('actual_built_app', build['source_sha'] == self.source and build['exit_code'] == 0
                     and all(build['compiled_contract_markers'].values()) and build['tracked_source_unchanged']
                     and build['standalone_copy_hashes_match'])
        self.control('pinned_live_provider_versions', any('gotrue:v2.188.1' in x for x in build['runtime_images'])
                     and any('postgrest:v14.10' in x for x in build['runtime_images']))
        try:
            self.failure_stage = 'fixtures'
            a, b = self.fixture('expiry_A'), self.fixture('expiry_B')
            self.control('distinct_tenants', a['tenant'] != b['tenant'] and a['uid'] != b['uid'])
            status, client = self.request('POST', '/auth/v1/admin/oauth/clients', {
                'redirect_uris': [APP + '/test-oauth-callback'], 'client_type': 'public',
                'token_endpoint_auth_method': 'none', 'grant_types': ['authorization_code', 'refresh_token'],
                'client_name': 'isolated-natural-expiry'}, admin=True)
            self.control('oauth_client_registered', status == 201 and bool(client.get('client_id')))
            self.client = client['client_id']
            self.start()
            self.failure_stage = 'B_before'
            self.oauth_token(b, 'B_initial', self.client)
            old = dict(b)
            self.old_digest = hashlib.sha256(old['token'].encode()).hexdigest()
            crypto = self.verify(old, 'B_before')
            self.control('old_provider_token_is_valid', crypto.get('time_valid') is True)
            before = self.snapshot()
            active, exists = self.active_state(a, b, crypto['session_id'])
            self.control('initial_active_users_and_session', active and exists)
            self.positive(old, 'B', 'before', crypto)
            self.timing.update(iat=crypto['iat'], exp=crypto['exp'], positive_finished=time.time(),
                               max_verifier_leeway=self.leeway, wait_margin=WAIT_MARGIN)
            self.control('enough_validity_for_positives', self.timing['positive_finished'] < crypto['exp'])
            self.failure_stage = 'natural_wall_time_wait'
            target = crypto['exp'] + self.leeway + WAIT_MARGIN
            wall, mono = time.time(), time.monotonic()
            if not 0 < target - wall < TTL + self.leeway + WAIT_MARGIN:
                raise HarnessFailure('natural wait outside fixed budget')
            # No clock/exp changes. CI runs asynchronously while real time passes.
            # Bounded 30-second chunks keep cancellation responsive.
            while time.time() < target:
                time.sleep(min(30, target - time.time()))
            elapsed, elapsed_mono = time.time() - wall, time.monotonic() - mono
            self.timing.update(real_wait_seconds=elapsed, monotonic_wait_seconds=elapsed_mono,
                               clock_drift_seconds=abs(elapsed - elapsed_mono), negative_started=time.time())
            self.control('real_time_elapsed_without_clock_shift', abs(elapsed - elapsed_mono) <= 2
                         and time.time() > crypto['exp'] + self.leeway)
            self.failure_stage = 'B_expired'
            expired = self.verify(old, 'B_expired')
            self.control('same_signed_token_now_expired', expired['digest'] == self.old_digest
                         and expired.get('expired') is True and expired.get('time_valid') is False)
            self.batch(old, 'B', 'expired', expired)
            self.failure_stage = 'fresh_A'
            fresh_a = self.fresh_oauth(a, 'A_fresh')
            self.positive(fresh_a, 'A', 'fresh', self.verify(fresh_a, 'A_fresh'))
            self.failure_stage = 'new_B'
            fresh_b = self.fresh_oauth(b, 'B_new')
            self.positive(fresh_b, 'B', 'new', self.verify(fresh_b, 'B_new'))
            self.failure_stage = 'old_B_again'
            still_expired = self.verify(old, 'B_old_again')
            self.batch(old, 'B', 'old_again', still_expired)
            active, exists = self.active_state(a, b, crypto['session_id'])
            self.continuity = {'accounts_active': active, 'old_session_exists': exists,
                'no_auto_refresh': self.flow_counts == {'password': 4, 'authorization_code': 3, 'refresh_token': 0},
                'same_old_token': hashlib.sha256(old['token'].encode()).hexdigest() == self.old_digest,
                'new_token_distinct': hashlib.sha256(fresh_b['token'].encode()).hexdigest() != self.old_digest}
            self.control('active_identity_session_and_token_continuity', all(self.continuity.values()))
            self.control('ordered_natural_expiry_oracle', expiry_accepted(self.observations, self.timing, self.continuity))
            self.control('no_external_fetch_attempts', self.state()['external_blocked'] == 0)
            self.firewall_after('app')
            accepted = True
        except (HarnessFailure, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
            failure = self.failure_stage
        finally:
            self.stop()
            after, final = self.snapshot(), self.counts()
            invariants = {'public_22_fingerprints_unchanged': before is not None and before == after,
                          'financial_7_empty': all(final[t] == 0 for t in FINANCE_TABLES),
                          'tracked_source_unchanged': subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0}
            self.controls.extend({'name': k, 'passed': v} for k, v in invariants.items())
            accepted = accepted and all(invariants.values())
            secrets = self.all_secrets + self.oauth_refresh_tokens
            for actor in [a, b, old]:
                if actor:
                    secrets += [actor[k] for k in ('token', 'session_token', 'refresh', 'password') if k in actor]
            logs = list(Path(os.environ['RUNNER_TEMP']).glob('route-*-private.log'))
            no_log_leak = not any(contains_credentials(p.read_text(errors='replace'), secrets) for p in logs)
            result = {'source_sha': self.source, 'natural_expiry_accepted': accepted and no_log_leak,
                'integration_accepted': False, 'failure_stage': failure,
                'actual_path': 'HTTP -> Nitro node-server -> src/server.ts -> generated TanStack /mcp -> SDK0.20.1 -> local Supabase',
                'ttl_seconds': TTL, 'timing': self.timing, 'continuity': self.continuity,
                'crypto_receipts': self.crypto_receipts, 'observations': self.observations, 'checks': self.controls,
                'flow_counts': self.flow_counts, 'history_before': before, 'history_after': after,
                'initial_counts': initial, 'final_counts': final, 'migration_versions': versions,
                'runtime': self.state() if (self.runtime / 'app.json').exists() else None,
                'firewall_observations': self.firewall_observations, 'private_logs_no_known_credentials': no_log_leak,
                'not_verified': ['Cloudflare/production', 'nonempty financial or foreign payloads',
                    'concurrency', 'refresh policy', 'complete L13/lifecycle/isolation acceptance']}
            result = publish_result(self.evidence_dir, result, secrets)
            result['natural_expiry_accepted'] = result.get('natural_expiry_accepted', False) and result.get('evidence_no_credentials') is True
            (self.evidence_dir / 'expiry-result.json').write_text(json.dumps(result, indent=2) + '\n')
            (self.evidence_dir / 'route-result.json').unlink(missing_ok=True)
            print(json.dumps({'natural_expiry_accepted': result['natural_expiry_accepted'],
                              'failure_stage': result['failure_stage'], 'checks': len(self.controls)}))
        return 0 if result['natural_expiry_accepted'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status-file', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(NaturalExpiryProbe(args.status_file, args.evidence_dir, args.expected_source).run_expiry())
    except (HarnessFailure, OSError, ValueError, subprocess.SubprocessError):
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'expiry-harness-failure.json').write_text(json.dumps({
            'natural_expiry_accepted': False, 'integration_accepted': False, 'failure_stage': 'preflight_or_baseline'}) + '\n')
        print('NATURAL_EXPIRY_HARNESS_FAILURE: sanitized evidence retained')
        raise SystemExit(2)
