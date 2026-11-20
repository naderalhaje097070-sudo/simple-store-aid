"""Candidate63 adapter for the unchanged APP-02 signed-webhook contract (B5 billing job, fresh full chain).

The historical WebhookProbe pins a 50-file source whose last three files are the webhook migrations.
This adapter replaces only that source/chain expectation with the reviewed candidate63 ledger; every
signed-route, SQL, authorization and invariance case is the inherited WebhookProbe implementation.
The populated 47->50 'before' phase is not part of this job's matrix and is refused here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from webhook_persistence_probe import WebhookProbe
from live_probe import HarnessFailure, FINANCE_TABLES

WEBHOOK = ('_webhook_persistence_01.sql', '_webhook_bootstrap_01.sql', '_webhook_errors_01.sql')


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def candidate_source(root=ROOT):
    """Disk migrations equal the reviewed candidate ledger by name and blob; B50 is an exact ordered subsequence of it."""
    ledger = json.loads((root / 'tests/g01-acceptance/candidate-63-source.json').read_text())['migration_ledger']
    b50 = sorted(json.loads((root / 'tests/g01-acceptance/integrated-b-source.json').read_text())['integrated_migrations'])
    disk = sorted((root / 'supabase/migrations').glob('*.sql'))
    exact = (len(ledger) == 63 and [x['path'] for x in ledger] == ['supabase/migrations/' + p.name for p in disk]
             and all(blob(p.read_bytes()) == x['sha'] for p, x in zip(disk, ledger))
             and [x['path'] for x in ledger if x['path'] in set(b50)] == b50
             and all(b50[47 + i].endswith(s) for i, s in enumerate(WEBHOOK)))
    return exact, [p.name.split('_')[0] for p in disk]


class CandidateWebhookProbe(WebhookProbe):
    def run(self, phase, state):
        if phase != 'after' or state.exists():
            raise HarnessFailure('candidate63 billing adapter supports the fresh full chain only')
        exact, expected = candidate_source()
        self.control('source_exact63_candidate_migrations', exact)
        versions = self.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;')
        self.control('native_exact_chain_after', versions == expected)
        self.control('financial_empty_at_start', all(self.counts()[t] == 0 for t in FINANCE_TABLES))
        actors = self.seed(state)
        legacy = {'event': self.make_legacy(actors['legacy'], 9000), 'display': self.make_legacy(actors['legacy_order'], 9001)}
        self.sequence = 20000
        self.run_cases(actors, legacy)
        self.control('financial_tables_remain_empty', all(self.counts()[t] == 0 for t in FINANCE_TABLES))
        self.control('tracked_source_unchanged', subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0)
        report = {'source': self.source, 'baseline_source': None, 'phase': phase, 'passed': len(self.controls), 'failed': 0,
                  'checks': self.controls, 'postgres_version': self.query('select to_jsonb(version());'),
                  'schema_versions': versions, 'fingerprints': self.snapshot(),
                  'scope': 'synthetic signed callbacks through actual route/SDK with local real SQL only; candidate63 fresh chain',
                  'provider_calls': False, 'B4_runtime_accepted': True, 'package_B_accepted': False, 'merge_approved': False}
        (self.evidence_dir / ('webhook-' + phase + '.json')).write_text(json.dumps(report, indent=2) + '\n')
        print('APP02_RECEIPT ' + json.dumps({k: v for k, v in report.items() if k not in ('checks', 'fingerprints', 'schema_versions')}))


def main():
    p = argparse.ArgumentParser()
    for n in ('status-file', 'evidence-dir', 'private-state'):
        p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--expected-source', required=True)
    p.add_argument('--phase', choices=('after',), required=True)
    args = p.parse_args()
    try:
        probe = CandidateWebhookProbe(args.status_file, args.evidence_dir, args.expected_source)
        probe.status_file = args.status_file
        probe.run(args.phase, args.private_state)
    except (HarnessFailure, ValueError, OSError, subprocess.SubprocessError) as e:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        reason = str(e) if isinstance(e, HarnessFailure) else type(e).__name__
        (args.evidence_dir / 'failure.json').write_text(json.dumps({'source': args.expected_source, 'phase': args.phase, 'failure': reason}))
        print('APP02_HARNESS_FAILURE ' + reason)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
