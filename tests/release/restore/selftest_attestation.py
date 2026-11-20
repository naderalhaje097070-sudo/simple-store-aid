#!/usr/bin/env python3
"""Defensive self-test for the restore attestation (review fix #98, Strix MEDIUM on 6c13bc2). Synthetic only: temporary
directories, no database, no privilege, no network. Each case follows the cleanup step's order with its production
code: the candidate's evidence tree is exported and imported into a fresh publication directory
(tests/release/evidence_import.py export | import; a rejected export leaves it empty and fails the step),
attestation.place, the real verify_publication, then attestation.verify. A case passes when the outcome is the expected one AND the runner-authored files are never
replaced by, merged with, or published from candidate content.

usage: python3 -I selftest_attestation.py
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'account-lifecycle'))
import attestation as A
from scanner_evidence import verify_publication, PublicationBlocked

SRC = 'a' * 40


def stage(att, source=SRC, extra=None, drop=None):
    att.mkdir()
    texts = {n: json.dumps({'controls': [{'name': n, 'passed': True}]}) + '\n' for n in A.FILES}
    texts['restore-check.json'] = json.dumps({'source': source, 'controls': [{'name': 'x', 'passed': True}]}) + '\n'
    if drop:
        texts.pop(drop)
    for n, t in texts.items():
        (att / n).write_text(t)
    lines = [hashlib.sha256(t.encode()).hexdigest() + '  ' + n for n, t in sorted(texts.items())]
    if extra:
        (att / extra).write_text('{}\n'); lines.append('0' * 64 + '  ' + extra)
    (att / A.SUMS).write_text('\n'.join(lines) + '\n')
    return {n: hashlib.sha256((att / n).read_bytes()).hexdigest() for n in os.listdir(att)}


FORGED = json.dumps({'source': SRC, 'controls': [{'name': 'forged_pass', 'passed': True}]}) + '\n'


def run(case):
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); ev, out, att = t / 'evidence', t / 'release-evidence', t / 'restore-attestation'
        ev.mkdir(); (ev / 'financial-result.json').write_text('{"financial_acceptance": true}\n')
        trusted = None
        if case == 'restore_stopped_early':
            att.mkdir()   # the restore step creates the directory first and stops before writing (e.g. tamper not rolled back)
        elif case not in ('no_restore_step_clean', 'no_restore_step_planted'):
            trusted = stage(att, **({'source': 'b' * 40} if case == 'source_mismatch' else
                                    {'extra': 'unexpected.json'} if case == 'staged_unexpected_name' else
                                    {'drop': 'restore-guard.json'} if case == 'staged_missing_file' else {}))
        if case in ('planted_restore_dir', 'no_restore_step_planted'):
            (ev / 'restore').mkdir(); (ev / 'restore' / 'restore-check.json').write_text(FORGED)
        if case == 'planted_top_level_name':
            (ev / 'restore-check.json').write_text(FORGED)
        if case == 'planted_nested_name':
            (ev / 'a' / 'b').mkdir(parents=True); (ev / 'a' / 'b' / 'restore-guard.json').write_text(FORGED)
        if case == 'planted_restore_symlink':
            (t / 'elsewhere').mkdir(); os.symlink(t / 'elsewhere', ev / 'restore')
        tool = str(HERE.parent / 'evidence_import.py')                      # the cleanup step's import boundary
        exp = subprocess.Popen([sys.executable, '-I', tool, 'export', str(ev)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        imp = subprocess.run([sys.executable, '-I', tool, 'import', str(out)], stdin=exp.stdout, capture_output=True)
        exp.stdout.close(); import_ok = exp.wait() == 0 and imp.returncode == 0
        if not import_ok:
            shutil.rmtree(out, ignore_errors=True); out.mkdir()
        placed = A.place(out, att)
        if case == 'overwritten_after_placement':
            (out / 'restore' / 'restore-check.json').write_text(FORGED)
        blocked = False
        try:
            verify_publication(out, t / 'quarantine', [])
        except PublicationBlocked:
            blocked = True
        status, found = A.verify(out, att, SRC)
        pub = out / 'restore'
        # invariants: the staged files are unchanged, and never merged into a candidate-occupied directory
        staged_intact = trusted is None or {n: hashlib.sha256((att / n).read_bytes()).hexdigest() for n in os.listdir(att)} == trusted
        no_merge = not (found and pub.is_dir() and not pub.is_symlink() and (pub / A.SUMS).exists())
        published_ok = status != 'verified' or all((pub / n).read_bytes() == (att / n).read_bytes() for n in list(A.FILES) + [A.SUMS])
        publish_allowed = import_ok and (not blocked) and status in ('verified', 'absent') and not found
        return status, found, placed['placed'], publish_allowed, staged_intact and no_merge and published_ok


EXPECT = {   # case: (status, collisions?, placed, publication allowed)
    'good': ('verified', False, True, True),
    'planted_restore_dir': ('MISMATCH', True, False, False),
    'planted_top_level_name': ('MISMATCH', True, False, False),
    'planted_nested_name': ('MISMATCH', True, False, False),
    'planted_restore_symlink': ('verified', False, True, False),   # the import refuses the link: empty publication, step fails
    'overwritten_after_placement': ('MISMATCH', False, True, False),
    'source_mismatch': ('MISMATCH', False, True, False),
    'staged_unexpected_name': ('MISMATCH', False, False, False),
    'staged_missing_file': ('MISMATCH', False, False, False),
    'no_restore_step_clean': ('absent', False, False, True),
    'restore_stopped_early': ('absent', False, False, True),
    'no_restore_step_planted': ('MISMATCH', True, False, False),
}
ok = True
for case, (st, coll, pl, allowed) in EXPECT.items():
    status, found, placed, publish_allowed, invariants = run(case)
    good = status == st and bool(found) == coll and placed == pl and publish_allowed == allowed and invariants
    ok &= good
    print(f"{case} {'PASS' if good else 'FAIL'} (status={status} collisions={found} placed={placed} "
          f"publication_allowed={publish_allowed} runner_files_never_replaced={invariants})")
sys.exit(0 if ok else 1)
