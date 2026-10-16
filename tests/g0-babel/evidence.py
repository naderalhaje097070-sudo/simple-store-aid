"""Record actual Babel graphs, parent ranges, transforms and supported audit exit."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

spec = importlib.util.spec_from_file_location('hono_evidence', 'tests/g0-hono/verify.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
evidence.OUT = Path('evidence/g0-babel')
evidence.OUT.mkdir(parents=True, exist_ok=True)
evidence.TARGETS = {'GHSA-4x5r-pxfx-6jf8'}
BASE = '86d5a87bc8b38c1bd0c173a0fb28987c0291dfa0'


def contracts(baseline=False):
    result = evidence.command('contracts', ['node', '--test', '--test-reporter=tap', 'tests/g0-babel/contracts.test.cjs'])
    text = result.stdout.decode()
    failed = re.findall(r'^not ok \d+ - (.*)$', text, re.M)
    counts = dict(re.findall(r'^# (tests|pass|fail|skipped) (\d+)$', text, re.M))
    observations = json.loads((evidence.OUT/'map-observations.json').read_text())
    assert observations and counts.get('skipped') == '0'
    evidence.save('contracts-summary.json', {'baseline_control': baseline, 'exit_code': result.returncode,
        'counts': counts, 'failed_tests': failed, 'versions': sorted({x['version'] for x in observations})})
    if baseline:
        assert result.returncode == 1 and len(failed) == 2 and counts['fail'] == '2', text
        assert all('7.29.0:' in x and ('outside-relative' in x or 'outside-absolute' in x) for x in failed), failed
        assert all(x['containsMarker'] == x['kind'].startswith('outside')
                   for x in observations if x['version'] == '7.29.0' and x['kind'].startswith('outside'))
        assert any(x['version'] == '7.29.7' for x in observations)
    else:
        assert result.returncode == 0 and not failed
        assert all(x['version'] == '7.29.7' for x in observations)


def installed():
    result = evidence.command('installed', ['node', '--input-type=module', '-e', r'''
import fs from 'node:fs';import path from 'node:path';import{createRequire}from'node:module';
const req=createRequire(process.cwd()+'/package.json');const semver=req('semver');
const text=fs.readFileSync('bun.lock','utf8').replace(/,\s*([}\]])/g,'$1');const lock=JSON.parse(text);
const rows=[];
for(const[name,entry]of Object.entries(lock.packages))for(const kind of['dependencies','optionalDependencies','peerDependencies']){
 const range=entry[2][kind]?.['@babel/core'];if(range){if(!semver.satisfies('7.29.7',range))throw Error('Parent range incompatible '+name);rows.push({parent:name,package:entry[0],kind,range});}}
const copies=[];
for(const parent of['@vitejs/plugin-react','babel-dead-code-elimination','workbox-build','@tanstack/router-plugin','@tanstack/start-plugin-core']){
 const manifestPath=path.resolve('node_modules',parent,'package.json');const manifest=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
 const from=createRequire(manifestPath);const entry=from.resolve('@babel/core');
 copies.push({parent,parentVersion:manifest.version,entry,coreVersion:from('@babel/core').version});}
console.log(JSON.stringify({parentDeclarations:rows,resolvedParents:copies},null,2));
'''])
    assert result.returncode == 0, result.stderr.decode()
    data = json.loads(result.stdout)
    found = []
    for p in Path('node_modules').rglob('@babel/core/package.json'):
        obj = json.loads(p.read_text())
        found.append({'path': str(p), 'version': obj['version']})
    assert found and all(x['version'] in sys.argv[2].split(',') for x in found), found
    data['physical_copies'] = found
    evidence.save('installed-copies.json', data)


def graph():
    before = evidence.jsonc(evidence.git_file(BASE, 'bun.lock'))
    after = evidence.jsonc(Path('bun.lock').read_bytes())
    changed = sorted(k for k in before['packages'].keys() | after['packages'].keys()
                     if before['packages'].get(k) != after['packages'].get(k))
    assert changed and '@babel/core' in changed
    assert after['overrides'].pop('@babel/core') == '7.29.7'
    assert {k:v for k,v in before.items() if k!='packages'} == {k:v for k,v in after.items() if k!='packages'}
    # Approved generator diff must be enumerated exactly before adoption.
    allowed = json.loads(Path('docs/g0-babel/approved-graph-delta.json').read_text())
    assert changed == allowed['changed_paths'], changed
    assert all(after['packages'].get(k) == v for k,v in allowed['after_records'].items())
    assert all(before['packages'].get(k) == v for k,v in allowed['before_records'].items())
    manifest = json.loads(Path('package.json').read_text())
    for key in ['overrides','resolutions']:assert manifest[key].pop('@babel/core') == '7.29.7'
    assert manifest == json.loads(evidence.git_file(BASE, 'package.json'))
    assert Path('bunfig.toml').read_bytes() == evidence.git_file(BASE, 'bunfig.toml')
    old_safe = {v[0] for v in before['packages'].values() if v[0].startswith('@babel/core@') and v[0]!='@babel/core@7.29.0'}
    new_cores = {v[0] for v in after['packages'].values() if v[0].startswith('@babel/core@')}
    assert old_safe <= new_cores and new_cores == {'@babel/core@7.29.7'}
    evidence.save('graph.json', {'base': BASE, 'changed_paths': changed, 'safe_versions_not_downgraded': True,
                               'new_core_versions': sorted(new_cores), 'approved_delta_exact': True})


def guards():
    original = Path('bun.lock').read_text()
    source = Path('tests/unit/dependency-security.test.ts').read_text()
    cases = {'patched': original,
        'old': original.replace('@babel/core@7.29.7','@babel/core@7.29.0'),
        'prerelease': original.replace('@babel/core@7.29.7','@babel/core@7.29.7-rc.1'),
        'major8': original.replace('@babel/core@7.29.7','@babel/core@8.0.0'),
        'nested-old': original.replace('"packages": {','"packages": {\n "fixture/core": ["@babel/core@7.29.0", "", {}],',1),
        'missing': original.replace('@babel/core@7.29.7','fixture@7.29.7'),
        'hono-old': original.replace('hono@4.13.7','hono@4.13.6'),
        'qs-old': original.replace('qs@6.16.0','qs@6.15.3'),
        'dompurify-old': original.replace('dompurify@3.4.16','dompurify@3.4.15')}
    rows=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);test=root/'tests/unit/dependency-security.test.ts';test.parent.mkdir(parents=True);test.write_text(source)
        for name,lock in cases.items():
            (root/'bun.lock').write_text(lock)
            r=evidence.command('guard-'+name,['bun','test',str(test)])
            rows.append({'case':name,'exit_code':r.returncode});assert (r.returncode==0)==(name=='patched'),rows
    evidence.save('guard-mutations.json',rows)


if __name__ == '__main__':
    mode=sys.argv[1]
    if mode=='baseline':contracts(True)
    elif mode=='contracts':contracts()
    else:{'installed':installed,'graph':graph,'guards':guards,'audit':evidence.audit}[mode]()
