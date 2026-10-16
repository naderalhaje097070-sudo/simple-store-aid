"""Bounded adapter evidence; real command exits and native Windows conditions."""
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
evidence.OUT = Path('evidence/g0-node-server')
evidence.OUT.mkdir(parents=True, exist_ok=True)
evidence.TARGETS = {'GHSA-frvp-7c67-39w9'}
BASE = '5cbf198d88b0f091a30371676fb09abf92903dc8'


def contracts(baseline=False):
    result = evidence.command('contracts', ['node', '--test', '--test-reporter=tap', 'tests/g0-node-server/contracts.test.cjs'])
    text = result.stdout.decode()
    failed = re.findall(r'^not ok \d+ - (.*)$', text, re.M)
    counts = dict(re.findall(r'^# (tests|pass|fail|skipped) (\d+)$', text, re.M))
    observations = json.loads((evidence.OUT/'http-observations.json').read_text())
    security = [x for x in observations if 'case' in x]
    assert len(security) == 2 and counts.get('skipped') == '0', text
    evidence.save('contracts-summary.json', {'baseline_control': baseline, 'exit_code': result.returncode,
        'counts': counts, 'failed_tests': failed, 'native_platform': observations[0]['platform'],
        'version': observations[0]['version']})
    if baseline:
        assert observations[0]['platform'] == 'win32' and observations[0]['version'] == '1.19.14'
        assert result.returncode == 1 and len(failed) == 2 and counts['fail'] == '2', text
        assert all(x.startswith('encoded-backslash-') for x in failed), failed
        assert all(x['status'] == 200 and x['body'] == 'protected-marker' and x['middlewareCalls'] == 0 for x in security)
    else:
        assert result.returncode == 0 and not failed, text
        assert observations[0]['version'] == '1.19.15'
        assert all(x['status'] == 404 and x['middlewareCalls'] == 0 and 'protected-marker' not in x['body'] for x in security)


def installed():
    lock = evidence.jsonc(Path('bun.lock').read_bytes())
    expected = sys.argv[2]
    locked = [{'path': k, 'record': v} for k,v in lock['packages'].items() if v[0].startswith('@hono/node-server@')]
    assert locked and all(x['record'][0] == '@hono/node-server@'+expected for x in locked), locked
    physical = []
    for p in Path('node_modules').rglob('@hono/node-server/package.json'):
        obj = json.loads(p.read_text())
        physical.append({'path': str(p.resolve()), 'version': obj['version'], 'engines': obj.get('engines')})
    assert physical and all(x['version'] == expected for x in physical), physical
    # Current graph is one copy; refuse to silently leave a new copy unexercised.
    assert len(locked) == len(physical) == 1, (locked, physical)
    sdk = json.loads(Path('node_modules/@modelcontextprotocol/sdk/package.json').read_text())
    assert sdk['version'] == '1.31.0'
    result = evidence.command('installed-parent-ranges', ['node', '-e', r'''
const fs=require('node:fs'),semver=require('semver');
const lock=JSON.parse(fs.readFileSync('bun.lock','utf8').replace(/,\s*([}\]])/g,'$1'));
const rows=[];for(const [name,v] of Object.entries(lock.packages))for(const kind of ['dependencies','optionalDependencies','peerDependencies']){
 const range=v[2][kind]?.['@hono/node-server'];if(range){if(!semver.satisfies('1.19.15',range))throw Error('Parent incompatible '+name);rows.push({name,kind,range});}}
if(!rows.length)throw Error('Missing parent');
const adapter=JSON.parse(fs.readFileSync('node_modules/@hono/node-server/package.json','utf8'));
const hono=JSON.parse(fs.readFileSync('node_modules/hono/package.json','utf8'));
if(!semver.satisfies(process.version,adapter.engines.node)||!semver.satisfies(hono.version,adapter.peerDependencies.hono))throw Error('Engines/peer mismatch');
console.log(JSON.stringify({rows,node:process.version,hono:hono.version,engines:adapter.engines,peer:adapter.peerDependencies},null,2));
'''])
    assert result.returncode == 0, result.stderr.decode()
    evidence.save('installed-copies.json', {'locked': locked, 'physical': physical, 'sdk': sdk['version'], 'parent_checks': json.loads(result.stdout)})
    for name in ['@hono/node-server', '@modelcontextprotocol/sdk']:
        root = Path('node_modules')/name
        evidence.save(name.replace('@','').replace('/','_')+'-manifest.json',json.loads((root/'package.json').read_text()))
    imports=[]
    for p in Path('node_modules/@modelcontextprotocol/sdk/dist').rglob('*.js'):
        data=p.read_text()
        if '@hono/node-server' in data: imports.append({'path':str(p),'imports':re.findall(r'''["'](@hono/node-server[^"']*)["']''',data)})
    assert imports, 'SDK adapter consumption must be observed'
    evidence.save('sdk-adapter-imports.json',imports)


def graph():
    before = evidence.jsonc(evidence.git_file(BASE, 'bun.lock'))
    after = evidence.jsonc(Path('bun.lock').read_bytes())
    changed = sorted(k for k in before['packages'].keys() | after['packages'].keys() if before['packages'].get(k) != after['packages'].get(k))
    assert changed == ['@hono/node-server'], changed
    old,new = before['packages'].pop('@hono/node-server'),after['packages'].pop('@hono/node-server')
    assert old[0] == '@hono/node-server@1.19.14' and new[0] == '@hono/node-server@1.19.15'
    assert after['overrides'].pop('@hono/node-server') == '1.19.15'
    assert before == after, 'Unrelated generated graph change'
    manifest=json.loads(Path('package.json').read_text())
    for key in ['overrides','resolutions']: assert manifest[key].pop('@hono/node-server') == '1.19.15'
    assert manifest == json.loads(evidence.git_file(BASE,'package.json'))
    assert Path('bunfig.toml').read_bytes() == evidence.git_file(BASE,'bunfig.toml')
    evidence.save('graph.json',{'base':BASE,'changed_paths':changed,'old':old,'new':new,'all_other_records_identical':True})


def guards():
    original=Path('bun.lock').read_text()
    source=Path('tests/unit/dependency-security.test.ts').read_text()
    cases={'patched':original,
        'old':original.replace('@hono/node-server@1.19.15','@hono/node-server@1.19.14'),
        'prerelease':original.replace('@hono/node-server@1.19.15','@hono/node-server@1.19.15-rc.1'),
        'unreviewed-major':original.replace('@hono/node-server@1.19.15','@hono/node-server@2.0.5'),
        'nested-old':original.replace('"packages": {','"packages": {\n "fixture/node-server": ["@hono/node-server@1.19.14", "", {}],',1),
        'missing':original.replace('@hono/node-server@1.19.15','fixture@1.19.15'),
        'hono-old':original.replace('hono@4.13.7','hono@4.13.6'),
        'qs-old':original.replace('qs@6.16.0','qs@6.15.3'),
        'dompurify-old':original.replace('dompurify@3.4.16','dompurify@3.4.15'),
        'babel-old':original.replace('@babel/core@7.29.7','@babel/core@7.29.0')}
    rows=[]
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);test=root/'tests/unit/dependency-security.test.ts';test.parent.mkdir(parents=True);test.write_text(source)
        for name,lock in cases.items():
            (root/'bun.lock').write_text(lock)
            result=evidence.command('guard-'+name,['bun','test',str(test)])
            rows.append({'case':name,'exit_code':result.returncode});assert (result.returncode==0)==(name=='patched'),rows
    evidence.save('guard-mutations.json',rows)


if __name__ == '__main__':
    mode=sys.argv[1]
    if mode=='baseline': contracts(True)
    elif mode=='contracts': contracts()
    else: {'installed':installed,'graph':graph,'guards':guards,'audit':evidence.audit}[mode]()
