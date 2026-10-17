"""Bounded evidence with unmodified child exits; no findings suppressed."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

spec = importlib.util.spec_from_file_location('existing_evidence', 'tests/g0-hono/verify.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
evidence.OUT = Path('evidence/g0-esbuild')
evidence.OUT.mkdir(parents=True, exist_ok=True)
evidence.TARGETS = {'GHSA-g7r4-m6w7-qqqr'}
BASE = '1b7a1a016f793c49d6b60f513c3241bb687681f3'


def security(baseline=False):
    result = evidence.command('security', ['node', '--test', '--test-reporter=tap', 'tests/g0-esbuild/security.test.cjs'])
    text = result.stdout.decode('utf-8')
    counts = dict(re.findall(r'^# (tests|pass|fail|skipped) (\d+)$', text, re.M))
    failed = re.findall(r'^not ok \d+ - (.*)$', text, re.M)
    rows = json.loads((evidence.OUT/'security-observations.json').read_text(encoding='utf-8'))
    evidence.save('security-summary.json', {'baseline': baseline, 'exit_code': result.returncode, 'counts': counts, 'failed': failed, 'identity': rows[0]})
    assert counts.get('tests') == '5' and counts.get('skipped') == '0' and len(rows) == 3, text
    if baseline:
        assert rows[0]['platform'] == 'win32' and rows[0]['version'] == '0.27.7'
        assert result.returncode == 1 and counts['fail'] == '2' and len(failed) == 2 and all(x.startswith('security-') for x in failed), text
        assert all(r['status'] == 200 and r['body'] == 'outside-web-root-dummy-marker' for r in rows[1:]), rows
    else:
        assert rows[0]['version'] == '0.28.1' and result.returncode == 0 and counts['fail'] == '0', text
        assert all(r['status'] in (400, 404) and 'outside-web-root-dummy-marker' not in r['body'] for r in rows[1:]), rows


if __name__ == '__main__':
    {'baseline': lambda: security(True), 'security': security, 'audit': evidence.audit}[sys.argv[1]]()
