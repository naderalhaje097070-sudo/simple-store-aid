"""Bounded qs evidence; reuse the previously reviewed command/audit recorder."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

spec = importlib.util.spec_from_file_location('hono_evidence', 'tests/g0-hono/verify.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
evidence.OUT = Path('evidence/g0-qs')
evidence.OUT.mkdir(parents=True, exist_ok=True)
evidence.TARGETS = {'GHSA-x5fp-wj9c-mxmx', 'GHSA-4mjr-xmp4-gh2g'}
BASE = '15710d48301e4130ece09c733b1f102ade20501f'


def contracts(baseline=False):
    result = evidence.command('contracts', ['node', '--test', '--test-reporter=tap',
                                           'tests/g0-qs/qs-contract.test.cjs'])
    text = result.stdout.decode()
    failed = re.findall(r'^not ok \d+ - (.*)$', text, re.M)
    expected = {
        'GHSA-x5fp-wj9c-mxmx: bracket comma group cannot bypass strict limit',
        'GHSA-4mjr-xmp4-gh2g: parse/stringify preserves data with plainObjects',
        'GHSA-4mjr-xmp4-gh2g: parse/stringify preserves data with allowPrototypes',
    }
    version = subprocess.check_output(['node', '-p', 'require("qs/package.json").version']).decode().strip()
    evidence.save('contracts-summary.json', {'source': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
        'version': version, 'baseline_control': baseline, 'exit_code': result.returncode,
        'failed_tests': failed, 'tap_totals': re.findall(r'^# (?:tests|pass|fail|skipped) \d+$', text, re.M)})
    counts = dict(re.findall(r'^# (tests|pass|fail|skipped) (\d+)$', text, re.M))
    assert counts.get('skipped') == '0' and int(counts['tests']) > 3, text
    if baseline:
        assert counts['fail'] == '3' and int(counts['pass']) == int(counts['tests']) - 3, text
        assert version == '6.15.3' and result.returncode != 0 and set(failed) == expected, text
        assert 'obj.constructor.isBuffer is not a function' in text
        assert 'Missing expected exception (RangeError)' in text
    else:
        assert version == '6.16.0' and result.returncode == 0 and not failed, text


def graph():
    before = evidence.jsonc(evidence.git_file(BASE, 'bun.lock'))
    after = evidence.jsonc(Path('bun.lock').read_bytes())
    changed = sorted(k for k in before['packages'].keys() | after['packages'].keys()
                     if before['packages'].get(k) != after['packages'].get(k))
    assert changed == ['qs'], changed
    old, new = before['packages'].pop('qs'), after['packages'].pop('qs')
    assert old[0] == 'qs@6.15.3' and new[0] == 'qs@6.16.0'
    assert after['overrides'].pop('qs') == '6.16.0'
    assert before == after, 'Unrelated dependency graph change'
    manifest = json.loads(Path('package.json').read_text())
    for key in ['overrides', 'resolutions']:
        assert manifest[key].pop('qs') == '6.16.0'
    assert manifest == json.loads(evidence.git_file(BASE, 'package.json'))
    assert Path('bunfig.toml').read_bytes() == evidence.git_file(BASE, 'bunfig.toml')
    evidence.save('graph.json', {'base': BASE, 'changed_packages': changed, 'old': old, 'new': new,
                              'hono_and_all_other_records_unchanged': True})
    for package in ['qs', 'express', 'body-parser', '@modelcontextprotocol/sdk']:
        data = json.loads((Path('node_modules') / package / 'package.json').read_text())
        evidence.save(package.replace('/', '_').replace('@', '') + '-installed.json', data)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'baseline':
        contracts(True)
    elif mode == 'contracts':
        contracts()
    elif mode == 'graph':
        graph()
    elif mode == 'audit':
        evidence.audit()
    else:
        raise ValueError(mode)
