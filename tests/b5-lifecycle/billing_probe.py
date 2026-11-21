"""Candidate63 adapter for the unchanged APP-02 signed-webhook contract (B5 billing job, fresh full chain).

The historical WebhookProbe pins a 50-file source whose last three files are the webhook migrations.
This adapter replaces only that source/chain expectation with the reviewed candidate63 ledger; every
signed-route, SQL, authorization and invariance case is the inherited WebhookProbe implementation.
The populated 47->50 'before' phase is not part of this job's matrix and is refused here.

Reference body (B5 post-merge run 44798187106): the historical probe compares the live
apply_subscription_webhook body with the B4 fixture changes/b4-app02/WEBHOOK_ERRORS.sql, which equals the
October migration 20261021140746. The candidate ledger redefines the function in the reviewed C-PADDLE-01
migration 20261110130000, changing only the tenant row lock. This adapter binds the expected body to that
manifest-pinned final definition and refuses any delta from the B4 fixture other than the exact reviewed one.
Every other security_catalog assertion is the historical one, unchanged.
"""
import difflib
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from webhook_persistence_probe import WebhookProbe, PRIVATE
from live_probe import HarnessFailure, FINANCE_TABLES
from write_harness_guard import _psql_command, _psql_env

WEBHOOK = ('_webhook_persistence_01.sql', '_webhook_bootstrap_01.sql', '_webhook_errors_01.sql')


RPC_SIGNATURE = 'public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'
B4_REFERENCE = 'changes/b4-app02/WEBHOOK_ERRORS.sql'
OCTOBER_DEFINITION = 'supabase/migrations/20261021140746_webhook_errors_01.sql'
FINAL_DEFINITION = 'supabase/migrations/20261110130000_paddle_webhook_no_key_update_01.sql'
# The exact reviewed C-PADDLE-01 delta from the B4 fixture body, as unified-diff lines (n=0).
REVIEWED_DELTA = (
    '-  SELECT * INTO v_tenant FROM public.tenants WHERE id=v_tenant_id FOR UPDATE;',
    '+  -- FOR NO KEY UPDATE: still excludes every other writer of this tenant row, but no longer',
    '+  -- waits on the FK KEY SHARE locks held by concurrent sales/collections of the same tenant.',
    '+  -- The UPDATE below changes only non-key columns, so it needs no stronger lock.',
    '+  SELECT * INTO v_tenant FROM public.tenants WHERE id=v_tenant_id FOR NO KEY UPDATE;',
)


def function_body(text):
    parts = text.split('$function$')
    if len(parts) != 3:
        raise HarnessFailure('reference definition shape')
    return parts[1]


def body_delta(reference, final):
    return tuple(l for l in difflib.unified_diff(reference.splitlines(), final.splitlines(), lineterm='', n=0)
                 if l[:1] in '+-' and not l.startswith(('+++', '---')))


def reviewed_final_body(root=ROOT):
    """The expected live body: the last ledger definition of the RPC, pinned by blob, with the exact reviewed delta."""
    ledger = json.loads((root / 'tests/g01-acceptance/candidate-63-source.json').read_text())['migration_ledger']
    marker = 'FUNCTION public.apply_subscription_webhook('
    definers = [x for x in ledger if marker in (root / x['path']).read_text()]
    if not definers or definers[-1]['path'] != FINAL_DEFINITION:
        raise HarnessFailure('final RPC definition is not the reviewed C-PADDLE-01 migration')
    final_bytes = (root / FINAL_DEFINITION).read_bytes()
    if blob(final_bytes) != definers[-1]['sha']:
        raise HarnessFailure('final RPC definition differs from the manifest-pinned blob')
    reference = function_body((root / B4_REFERENCE).read_text())
    if reference != function_body((root / OCTOBER_DEFINITION).read_text()):
        raise HarnessFailure('B4 reference no longer equals the October definition')
    final = function_body(final_bytes.decode())
    if body_delta(reference, final) != REVIEWED_DELTA:
        raise HarnessFailure('final RPC body differs from the B4 reference by more than the reviewed delta')
    return final


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
    def security_catalog(self):
        # Same catalog read and the same assertions as WebhookProbe.security_catalog, except that the expected
        # body is the manifest-pinned final ledger definition (see the module docstring).
        sig = RPC_SIGNATURE
        data = self.query("""select jsonb_build_object(
          'body',(select prosrc from pg_proc where oid='""" + sig + """'::regprocedure),
          'definer',(select prosecdef from pg_proc where oid='""" + sig + """'::regprocedure),
          'settings',(select proconfig from pg_proc where oid='""" + sig + """'::regprocedure),
          'execute',(select jsonb_object_agg(r,has_function_privilege(r,'""" + sig + """','EXECUTE')) from unnest(array['anon','authenticated','service_role']) r),
          'public_execute',(select exists(select 1 from pg_proc p,lateral aclexplode(p.proacl) a where p.oid='""" + sig + """'::regprocedure and a.grantee=0 and a.privilege_type='EXECUTE')),
          'private',(select jsonb_agg(jsonb_build_object('name',c.relname,'rls',c.relrowsecurity,'auth',has_table_privilege('authenticated',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE'),'anon',has_table_privilege('anon',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE'),'service_truncate',has_table_privilege('service_role',c.oid,'TRUNCATE'),'service_delete',has_table_privilege('service_role',c.oid,'DELETE'))) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='monjez_private' and c.relname in ('billing_tenant_bindings','billing_webhook_receipts'))
        );""")
        try:
            expected = reviewed_final_body()
            reference_ok = True
        except HarnessFailure:
            expected, reference_ok = None, False
        self.control('final_RPC_reference_is_pinned_ledger_definition_with_exact_reviewed_delta', reference_ok)
        self.control('final_RPC_actual_body_matches_reviewed_ledger_definition', data['body'] == expected)
        self.control('application_errors_never_use_serialization_SQLSTATE', "ERRCODE='40001'" not in data['body'] and data['body'].count("ERRCODE='P0001'") >= 10)
        self.control('new_RPC_security_invoker_and_pinned_path', data['definer'] is False and 'search_path=pg_catalog, pg_temp' in data['settings'])
        self.control('new_RPC_explicit_service_only', data['execute'] == {'anon': False, 'authenticated': False, 'service_role': True} and data['public_execute'] is False)
        self.control('new_private_tables_RLS_no_client_or_destructive_service_grants', len(data['private']) == 2 and all(t['rls'] and not any(t[k] for k in ('auth', 'anon', 'service_truncate', 'service_delete')) for t in data['private']))
        for role in ('anon', 'authenticated'):
            for table in PRIVATE:
                sql = 'BEGIN; SET LOCAL ROLE ' + role + '; SELECT count(*) FROM monjez_private.' + table + '; ROLLBACK;'
                run = subprocess.run(_psql_command(self.config, '-Atq', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose'), input=sql, text=True, capture_output=True, env=_psql_env(self.config), timeout=20)
                self.control(role + '_' + table + '_actual_private_denial', run.returncode != 0 and '42501' in run.stderr)
        (self.evidence_dir / 'billing-security-catalog.json').write_text(json.dumps(data, indent=2) + '\n')

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
