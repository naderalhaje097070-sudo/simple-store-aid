"""Reuse raw command/audit recorder; DOMPurify graph and every-copy evidence."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

spec = importlib.util.spec_from_file_location('hono_evidence', 'tests/g0-hono/verify.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
evidence.OUT = Path('evidence/g0-dompurify')
evidence.OUT.mkdir(parents=True, exist_ok=True)
evidence.TARGETS = {'GHSA-c2j3-45gr-mqc4', 'GHSA-55q2-fjhq-7xh7', 'GHSA-6688-9rhm-gjv2'}
BASE = '5623a6ea09101dfa97f36909a66d8ea3a81956f4'


def graph():
    before = evidence.jsonc(evidence.git_file(BASE, 'bun.lock'))
    after = evidence.jsonc(Path('bun.lock').read_bytes())
    changed = sorted(k for k in before['packages'].keys() | after['packages'].keys()
                     if before['packages'].get(k) != after['packages'].get(k))
    assert changed == ['dompurify'], changed
    old, new = before['packages'].pop('dompurify'), after['packages'].pop('dompurify')
    assert old[0] == 'dompurify@3.4.11' and new[0] == 'dompurify@3.4.16'
    assert after['overrides'].pop('dompurify') == '3.4.16'
    assert before == after, 'Unrelated graph changes'
    manifest = json.loads(Path('package.json').read_text())
    for key in ['overrides', 'resolutions']:
        assert manifest[key].pop('dompurify') == '3.4.16'
    assert manifest == json.loads(evidence.git_file(BASE, 'package.json'))
    assert Path('bunfig.toml').read_bytes() == evidence.git_file(BASE, 'bunfig.toml')
    evidence.save('graph.json', {'base': BASE, 'changed_packages': changed, 'old': old,
                                'new': new, 'every_other_record_unchanged': True})


def installed():
    result = evidence.command('resolve-parent', ['node', '--input-type=module', '-e', '''
import {createRequire} from 'node:module';
const require=createRequire(process.cwd()+'/package.json');
const parent=require.resolve('jspdf/package.json');
const own=require.resolve('dompurify');
const child=createRequire(parent).resolve('dompurify');
console.log(JSON.stringify({parent,own,child,manifest:require('jspdf/package.json')}));
if(own!==child)process.exitCode=1;
'''])
    assert result.returncode == 0
    parent = json.loads(result.stdout)
    assert parent['manifest']['version'] == '4.2.1'
    assert parent['manifest']['optionalDependencies']['dompurify'] == '^3.3.1'
    found = []
    for path in Path('node_modules').rglob('dompurify/package.json'):
        data = json.loads(path.read_text())
        assert data['name'] == 'dompurify'
        found.append({'path': str(path), 'resolved': str(path.resolve()), 'version': data['version']})
    assert found and all(x['version'] == sys.argv[2] for x in found), found
    evidence.save('installed-copies.json', {'copies': found, 'parent': parent,
        'optional_dependency_absence_is_failure': True})
    for name in ['dompurify', 'jspdf']:
        evidence.save(name+'-installed.json', json.loads((Path('node_modules')/name/'package.json').read_text()))


def guards():
    original = Path('bun.lock').read_text()
    source = Path('tests/unit/dependency-security.test.ts').read_text()
    cases = {
        'patched': original,
        'old': original.replace('dompurify@3.4.16', 'dompurify@3.4.11'),
        'prerelease': original.replace('dompurify@3.4.16', 'dompurify@3.4.16-rc.1'),
        'major4': original.replace('dompurify@3.4.16', 'dompurify@4.0.0'),
        'nested-old': original.replace('"packages": {', '"packages": {\n "fixture/dompurify": ["dompurify@3.4.11", "", {}],', 1),
        'missing': original.replace('dompurify@3.4.16', 'fixture@3.4.16'),
        'hono-old': original.replace('hono@4.13.7', 'hono@4.13.6'),
        'qs-old': original.replace('qs@6.16.0', 'qs@6.15.3'),
    }
    results = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        test = root/'tests/unit/dependency-security.test.ts'
        test.parent.mkdir(parents=True)
        test.write_text(source)
        for name, lock in cases.items():
            (root/'bun.lock').write_text(lock)
            result = evidence.command('guard-'+name, ['bun', 'test', str(test)])
            results.append({'case': name, 'exit_code': result.returncode})
            assert (result.returncode == 0) == (name == 'patched'), results
    evidence.save('guard-mutations.json', results)


if __name__ == '__main__':
    {'graph': graph, 'installed': installed, 'guards': guards, 'audit': evidence.audit}[sys.argv[1]]()
