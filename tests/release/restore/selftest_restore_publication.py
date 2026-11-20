#!/usr/bin/env python3
"""Self-test for the restore step's final control block (review fix #98, Strix HIGH on da33d39).

Synthetic only: no database, no network, no privilege. It extracts the step's own Python control block from the
committed workflow text, then runs it on synthetic runner-owned inputs in temporary directories, once per case:

  good                     every input consistent      -> exit 0, exactly the 4 named files + their sha256 list staged
  layout_writable          c5finance can write R        -> private_layout_not_writable_by_c5finance fails, exit != 0
  layout_wrong_owner       R/in not root-owned          -> same control fails
  secret_in_verdict        a restore stack key appears in a published verdict  -> publication control fails, nothing published
  actor_email_in_verdict   a restored-suite actor email appears in a verdict   -> publication control fails, nothing published
  extra_file_in_pub        an unexpected file already in the publication dir   -> publication control fails
  no_status                no restore status (no forbidden list to check)       -> publication control fails (fail closed)

usage: python3 -I selftest_restore_publication.py [WORKFLOW_YML]
"""
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

import yaml

wf = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[3] / '.github/workflows/release-finance.yml')
step = [s for s in yaml.safe_load(wf.read_text())['jobs']['suite']['steps'] if s.get('name', '').startswith('Logical backup and restore')]
assert len(step) == 1, 'restore step not found'
run = step[0]['run']
code = run.split("python3 - <<'PY'\n", 1)[1].split('\nPY\n', 1)[0]

KEY = 'synthetic-anon-key-' + 'k' * 40
EMAIL = 'restored-actor-synthetic@example.invalid'
CORE = ['real_hook_single_stored_collection', 'parallel_fresh_key_exactly_one_effect', 'keyed_only_acl_and_existing_ledger_rls',
        'settlement_retry_no_second_cash', 'concurrent_same_sale_key_exactly_one_effect', 'concurrent_collection_cannot_exceed_total',
        'lost_reply_first_commit_persisted_once', 'previously_authorized_staff_banned']
NAMED = ['restore-attestation.sha256', 'restore-check.json', 'restore-guard.json', 'restore-n1-guard.json', 'restore-suite-controls.json']


def inputs(w, case):
    fp = [f'rel|public.t{i}|{i:032x}' for i in range(120)]
    data = [f'public.t{i}|{i}|{i:032x}' for i in range(30)] + ['supabase_migrations.schema_migrations|61|' + 'a' * 32]
    tam = data[:-1] + ['supabase_migrations.schema_migrations|61|' + 'b' * 32]
    files = {'src.fp': fp, 'tgt.fp': fp, 'n1.fp': fp[:-5] + ['rel|public.extra|x'], 'src.data': data, 'tgt.data': data,
             'after_tamper.data': data, 'tamper.data': tam, 'identity.txt': ['c5finance'],
             'layout.txt': ['runnerx 711', 'root c5finance 750', 'c5finance c5finance 700']}
    if case == 'layout_writable':
        files['layout.txt'] = files['layout.txt'] + ['R_WRITABLE_BY_C5FINANCE']
    if case == 'layout_wrong_owner':
        files['layout.txt'] = ['runnerx 711', 'c5finance c5finance 750', 'c5finance c5finance 700']
    for n, lines in files.items():
        (w / n).write_text('\n'.join(lines) + '\n')
    guard = {'controls': [{'name': 'baseline_no_violations', 'passed': True}]}
    n1 = {'controls': [{'name': 'baseline_no_violations', 'passed': False}]}
    rows = [{'name': n, 'passed': True} for n in CORE]
    if case == 'secret_in_verdict':
        rows.append({'name': 'leaky ' + KEY, 'passed': True})
    if case == 'actor_email_in_verdict':
        rows.append({'name': 'actor ' + EMAIL, 'passed': True})
    (w / 'restore-guard.json').write_text(json.dumps(guard))
    (w / 'restore-n1-guard.json').write_text(json.dumps(n1))
    (w / 'suite-result.json').write_text(json.dumps({'financial_acceptance': True, 'controls': rows}))
    if case != 'no_status':
        (w / 'status-tgt-private.json').write_text(json.dumps({'ANON_KEY': KEY, 'SERVICE_ROLE_KEY': 'synthetic-service-' + 's' * 40,
                                                                'API_URL': 'http://127.0.0.1:54321'}))
    (w / 'restore-private-state.json').write_text(json.dumps({'actors': {'owner': {'email': EMAIL, 'token': 'synthetic-token-' + 't' * 30}}}))


def run_case(case):
    with tempfile.TemporaryDirectory() as t:
        w, pub = Path(t) / 'work', Path(t) / 'pub'
        w.mkdir(); pub.mkdir()
        inputs(w, case)
        if case == 'extra_file_in_pub':
            (pub / 'unexpected.json').write_text('{}\n')
        env = dict(os.environ, WORK=str(w), ATT=str(pub), EXPECTED_SOURCE='c' * 40, N1_RESTORE='0', N1_GUARD='1', OK_RESTORE='0', OK_GUARD='0',
                   SUITE_EXIT='0', RUNNER_USER='runnerx')
        r = subprocess.run([sys.executable, '-I', '-c', code], env=env, capture_output=True, text=True)
        line = next((l for l in r.stdout.splitlines() if l.startswith('RELEASE_RESTORE_CHECK ')), '')
        if r.returncode and not line:
            print(r.stderr[-800:])
        result = json.loads(line.split(' ', 1)[1]) if line else {}
        published = sorted(p.name for p in pub.iterdir())
        texts = ''.join((pub / n).read_text() for n in published)
        if case == 'good':   # the digest list matches the staged files, and the check carries the tested source
            sums = dict(l.split('  ', 1)[::-1] for l in (pub / 'restore-attestation.sha256').read_text().splitlines())
            assert sorted(sums) == NAMED[1:] and all(hashlib.sha256((pub / n).read_bytes()).hexdigest() == h for n, h in sums.items())
            assert json.loads((pub / 'restore-check.json').read_text())['source'] == 'c' * 40
        return r.returncode, result.get('failed'), published, (KEY in texts or EMAIL in texts)


expect = {
    'good': (0, [], NAMED),
    'layout_writable': ('nonzero', ['private_layout_not_writable_by_c5finance'], NAMED),
    'layout_wrong_owner': ('nonzero', ['private_layout_not_writable_by_c5finance'], NAMED),
    'secret_in_verdict': ('nonzero', ['published_restore_evidence_named_and_secret_free'], []),
    'actor_email_in_verdict': ('nonzero', ['published_restore_evidence_named_and_secret_free'], []),
    'extra_file_in_pub': ('nonzero', ['published_restore_evidence_named_and_secret_free'], sorted(NAMED + ['unexpected.json'])),
    'no_status': ('nonzero', ['published_restore_evidence_named_and_secret_free'], []),
}
ok = True
for case, (rc_want, failed_want, pub_want) in expect.items():
    rc, failed, published, leaked = run_case(case)
    good = (rc == 0 if rc_want == 0 else rc != 0) and failed == failed_want and published == pub_want and not leaked
    ok &= good
    print(f"{case} {'PASS' if good else 'FAIL'} (exit={rc} failed={failed} published={published} private_value_published={leaked})")
sys.exit(0 if ok else 1)
