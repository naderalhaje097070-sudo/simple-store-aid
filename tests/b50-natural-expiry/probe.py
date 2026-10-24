"""Current B50 adapter for the unchanged genuine real-time token-expiry contract.

Copies only historical run_expiry orchestration; inherited cryptography, timing,
challenge, peer and no-refresh oracles remain the historical implementation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from natural_expiry_probe import NaturalExpiryProbe, TTL, WAIT_MARGIN, expiry_accepted
from live_probe import HarnessFailure, FINANCE_TABLES
from tanstack_route_probe import APP, contains_credentials, publish_result
sys.path.insert(0, str(ROOT / 'tests/b5-lifecycle'))
from inventory import inventory, applied

PRIVATE = ('owner_account_closures', 'billing_tenant_bindings', 'billing_webhook_receipts')


class B50NaturalExpiryProbe(NaturalExpiryProbe):
    def extra_snapshot(self):
        rows = {}
        for name in PRIVATE:
            rows[name] = self.query("select jsonb_build_object('count',count(*),'digest',md5(coalesce(string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),''))) from monjez_private." + name + " t;")
        auth = self.query("select coalesce(jsonb_agg(jsonb_build_object('id',id,'deleted_at',deleted_at,'banned_until',banned_until) order by id),'[]'::jsonb) from auth.users;")
        return {'private_relations': rows, 'auth_identity_links': auth}

    def run_expiry(self):
        accepted, before, failure, a, b, old, initial = False, None, None, None, None, None, self.counts()
        extra_before = None
        self.control('fresh_empty_stack', all(v == 0 for v in initial.values()))
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        inv = inventory()
        self.control('fixedB50_and_original41_source', inv['identity']['migration_count'] == 50)
        self.control('exact_effective50_migrations', applied(inv['full_versions'], versions))
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
            extra_before = self.extra_snapshot()
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
            extra_after = self.extra_snapshot()
            invariants = {'private3_and_auth_identity_links_unchanged': extra_before is not None and extra_before == extra_after,
                          'public_22_fingerprints_unchanged': before is not None and before == after,
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
                'actual_path': 'HTTP -> Nitro node-server -> src/server.ts -> generated TanStack /mcp -> mcp-js0.20.1 wrapper -> local Supabase',
                'schema_scope': 'fixedB50_original41_anchor', 'private_auth_before': extra_before, 'private_auth_after': extra_after,
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
        raise SystemExit(B50NaturalExpiryProbe(args.status_file, args.evidence_dir, args.expected_source).run_expiry())
    except (HarnessFailure, OSError, ValueError, subprocess.SubprocessError):
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        (args.evidence_dir / 'expiry-harness-failure.json').write_text(json.dumps({
            'natural_expiry_accepted': False, 'integration_accepted': False, 'failure_stage': 'preflight_or_baseline'}) + '\n')
        print('NATURAL_EXPIRY_HARNESS_FAILURE: sanitized evidence retained')
        raise SystemExit(2)
