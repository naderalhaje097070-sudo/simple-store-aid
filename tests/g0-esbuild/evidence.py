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


def graph():
    before = evidence.jsonc(evidence.git_file(BASE, 'bun.lock'))
    after = evidence.jsonc(Path('bun.lock').read_bytes())
    changed = sorted(k for k in before['packages'].keys() | after['packages'].keys() if before['packages'].get(k) != after['packages'].get(k))
    assert len(changed) == 27 and all(k == 'esbuild' or k.startswith('@esbuild/') for k in changed), changed
    for k in changed:
        assert before['packages'].pop(k)[0] == k+'@0.27.7'
        assert after['packages'].pop(k)[0] == k+'@0.28.1'
    assert after['overrides'].pop('esbuild') == '0.28.1' and before == after, 'Unrelated graph change'
    manifest = json.loads(Path('package.json').read_text(encoding='utf-8'))
    for key in ['overrides', 'resolutions']: assert manifest[key].pop('esbuild') == '0.28.1'
    assert manifest == json.loads(evidence.git_file(BASE, 'package.json'))
    assert Path('bunfig.toml').read_bytes() == evidence.git_file(BASE, 'bunfig.toml')
    evidence.save('graph.json', {'base': BASE, 'changed': changed, 'all_other_records_identical': True,
                  'lock_sha256': hashlib.sha256(Path('bun.lock').read_bytes()).hexdigest()})


def installed():
    import zipfile
    copies = []
    for directory, _, files in os.walk('node_modules'):
        if 'package.json' not in files: continue
        p = Path(directory)/'package.json'
        if not (str(Path(directory).name) == 'esbuild' or str(Path(directory).parent.name) == '@esbuild'): continue
        m = json.loads(p.read_text(encoding='utf-8'))
        copies.append({'path': str(p.resolve()), 'name': m['name'], 'version': m['version']})
    assert copies and all(x['version'] == '0.28.1' for x in copies), copies
    assert sum(x['name'] == 'esbuild' for x in copies) == 1, copies
    with zipfile.ZipFile('docs/g0-esbuild/preparation-failed.zip') as z:
        inventory = json.loads(z.read('baseline-files.json'))
    hashes = []
    for rel, item in inventory.items():
        p = Path('node_modules/@lovable.dev/mcp-js')/rel
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == item['sha256'], rel
        hashes.append({'path': rel, 'sha256': actual})
    result = evidence.command('resolved-parent-versions', ['node', '-e', r'''
const fs=require('node:fs'),path=require('node:path'),{createRequire}=require('node:module'),semver=require('semver');
const lock=JSON.parse(fs.readFileSync('bun.lock','utf8').replace(/,\s*([}\]])/g,'$1'));
const rows=[];
for(const [name,v] of Object.entries(lock.packages))for(const kind of ['dependencies','optionalDependencies','peerDependencies']){
 const range=v[2][kind]?.esbuild;if(!range)continue;
 const r=createRequire(path.resolve('node_modules',name,'package.json'));
 const resolved=r('esbuild');if(resolved.version!=='0.28.1')throw Error('Wrong actual resolved copy');
 const accepted=semver.satisfies(resolved.version,range);
 if(accepted!==(name!=='@lovable.dev/mcp-js'))throw Error('Unexpected parent range compatibility');
 rows.push({name,kind,range,accepted,version:resolved.version,resolved:r.resolve('esbuild')});
}
if(rows.length!==3)throw Error('Unexpected consumers');
const esbuild=require('esbuild');if(esbuild.version!=='0.28.1')throw Error('Wrong wrapper');
const mcp=JSON.parse(fs.readFileSync('node_modules/@lovable.dev/mcp-js/package.json'));
const sdk=JSON.parse(fs.readFileSync('node_modules/@modelcontextprotocol/sdk/package.json'));
if(mcp.version!=='0.20.1'||sdk.version!=='1.31.0')throw Error('Unapproved parent change');
console.log(JSON.stringify({node:process.version,platform:process.platform,rows,mcp:mcp.version,sdk:sdk.version},null,2));
'''])
    assert result.returncode == 0, result.stderr.decode('utf-8')
    evidence.save('installed.json', {'copies': copies, 'official_mcp_files': hashes, 'consumers': json.loads(result.stdout)})
    binary_path = ('node_modules/@esbuild/win32-x64/esbuild.exe' if sys.platform == 'win32'
                   else 'node_modules/@esbuild/linux-x64/bin/esbuild')
    binary = evidence.command('native-binary-version', [binary_path, '--version'])
    assert binary.returncode == 0 and binary.stdout.strip() == b'0.28.1'



def compatibility():
    result = evidence.command('compatibility', ['node', '--test', '--test-reporter=tap', 'tests/g0-esbuild/compatibility.test.mjs'])
    assert result.returncode == 0, result.stdout.decode('utf-8')+result.stderr.decode('utf-8')


def guards():
    import tempfile
    original = Path('bun.lock').read_text(encoding='utf-8')
    source = Path('tests/unit/dependency-security.test.ts').read_text(encoding='utf-8')
    cases = {'patched': original,
        'old': original.replace('esbuild@0.28.1', 'esbuild@0.27.7'),
        'prerelease': original.replace('esbuild@0.28.1', 'esbuild@0.28.1-rc.1'),
        'missing': original.replace('esbuild@0.28.1', 'fixture@0.28.1'),
        'nested-old': original.replace('"packages": {', '"packages": {\n"fixture/esbuild": ["esbuild@0.27.7", "", {}],', 1),
        'old-platform': original.replace('@esbuild/win32-x64@0.28.1', '@esbuild/win32-x64@0.27.7'),
        'hono-old': original.replace('hono@4.13.7', 'hono@4.13.6'),
        'qs-old': original.replace('qs@6.16.0', 'qs@6.15.3'),
        'dompurify-old': original.replace('dompurify@3.4.16', 'dompurify@3.4.15'),
        'babel-old': original.replace('@babel/core@7.29.7', '@babel/core@7.29.0'),
        'node-server-old': original.replace('@hono/node-server@1.19.15', '@hono/node-server@1.19.14')}
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); test = root/'tests/unit/dependency-security.test.ts'
        test.parent.mkdir(parents=True); test.write_text(source, encoding='utf-8')
        for name, lock in cases.items():
            (root/'bun.lock').write_text(lock, encoding='utf-8')
            result = evidence.command('guard-'+name, ['bun', 'test', str(test)])
            rows.append({'case': name, 'exit_code': result.returncode})
            assert (result.returncode == 0) == (name == 'patched'), rows
    evidence.save('guard-controls.json', rows)


def audit():
    try:
        evidence.audit()
    except SystemExit as actual:
        current = json.loads((evidence.OUT/'audit-summary.json').read_text(encoding='utf-8'))
        before = json.loads(Path('docs/g0-node-server/audit-summary.json').read_text(encoding='utf-8'))
        old, new = set(before['all_reported_ids']), set(current['all_reported_ids'])
        evidence.save('audit-delta.json', {'before': sorted(old), 'after': sorted(new), 'removed': sorted(old-new), 'new': sorted(new-old), 'actual_exit_code': actual.code})
        assert old-new == evidence.TARGETS and not new-old, 'Unexpected advisory delta'
        raise


if __name__ == '__main__':
    {'baseline': lambda: security(True), 'security': security, 'graph': graph, 'installed': installed,
     'compatibility': compatibility, 'guards': guards, 'audit': audit}[sys.argv[1]]()
