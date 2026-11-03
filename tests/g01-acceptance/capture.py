"""Keep actual command failures, publish bounded noncredential receipts only."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('kind', choices=['frozen', 'audit', 'lint', 'identity'])
args = parser.parse_args()
root = Path(os.environ['RUNNER_TEMP'])
out = root/'g01-evidence'
out.mkdir(exist_ok=True)
receipt = {'source_sha': os.environ['EXPECTED_SOURCE'], 'kind': args.kind}
if args.kind == 'identity':
    if Path('tests/c5-collection/source.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/c5-collection').resolve()))
        from collection_identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/c5-finance/source.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/c5-finance').resolve()))
        from identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/c5-acceptance/source.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/c5-acceptance').resolve()))
        from identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/sec-dep-20261102/source.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/sec-dep-20261102').resolve()))
        from sec_identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/c4-sale/source.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/c4-sale').resolve()))
        from identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/c-source/manifest.json').exists():
        import sys
        sys.path.insert(0, str(Path('tests/c-source').resolve()))
        from c_identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    if Path('tests/g01-acceptance/integrated-source.json').exists():
        from integrated_identity import verify
        receipt.update(verify(Path.cwd()))
        (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt));raise SystemExit(0)
    manifest = json.loads(Path('tests/g01-acceptance/source54.json').read_text())
    overrides_file = Path('tests/g01-acceptance/g1-source-overrides.json')
    overrides = json.loads(overrides_file.read_text()) if overrides_file.exists() else {}
    assert set(overrides) <= {'.github/workflows/sec-env-gate4-probe.yml', 'PROJECT_STATE.md', 'TASKS.md', 'DECISIONS.md'}, 'Unexpected original-source override'
    matched = []
    changed = []
    for item in manifest['base_blobs']:
        p = Path(item['path']); data = p.read_bytes()
        digest = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if digest != item['git_blob_sha']:
            assert item['path'] in overrides and digest == overrides[item['path']], 'Unexpected source mutation: '+item['path']
            changed.append({'path':item['path'],'original':item['git_blob_sha'],'approved':digest})
        matched.append(digest == overrides.get(item['path'],item['git_blob_sha']))
    receipt.update(base_source=manifest['source_sha'], base_blob_count=len(matched),
                   all_base_blobs_unchanged=not changed, all_original_application_blobs_unchanged=True,
                   approved_base_changes=changed,
                   migration_count=len(list(Path('supabase/migrations').glob('*.sql'))))
    (out/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert len(matched) == 383 and all(matched)
    assert len(list(Path('supabase/migrations').glob('*.sql'))) == 41
    print(json.dumps(receipt));raise SystemExit(0)

commands = {'frozen':['bun','install','--frozen-lockfile'],
            'audit':['bun','audit','--json'],
            'lint':['bunx','--no-install','eslint','.','--format','json']}
private = root/('g01-'+args.kind+'-private.log')
with private.open('wb') as log:
    result = subprocess.run(commands[args.kind],stdout=log,stderr=subprocess.STDOUT,timeout=240)
data = private.read_bytes()
receipt.update(command=commands[args.kind], exit_code=result.returncode,
               stdout_sha256=hashlib.sha256(data).hexdigest(),
               bun_version=subprocess.run(['bun','--version'],capture_output=True,text=True,check=True).stdout.strip(),
               node_version=subprocess.run(['node','--version'],capture_output=True,text=True,check=True).stdout.strip())
if args.kind == 'audit':
    text = data.decode(errors='replace')
    start = text.find('{')
    audit = json.JSONDecoder().raw_decode(text[start:])[0] if start >= 0 else None
    if not isinstance(audit,dict):raise RuntimeError('Audit did not produce structured result')
    counts = Counter()
    records = []
    for key,value in audit.get('advisories',{}).items():
        counts[value['severity']]+=1
        records.append({k:value[k] for k in ['id','module_name','severity','title','url','vulnerable_versions','patched_versions'] if k in value})
    if not records and all(isinstance(value,list) for value in audit.values()):
        for name,values in audit.items():
            for value in values:
                counts[value['severity']]+=1
                records.append({'module_name':name,**{k:value[k] for k in ['id','severity','title','url','vulnerable_versions'] if k in value}})
    if not records and 'vulnerabilities' in audit:
        for name,value in audit['vulnerabilities'].items():
            counts[value['severity']]+=1
            records.append({'module_name':name,'severity':value['severity'],'via':value.get('via'),'range':value.get('range')})
    receipt.update(severity_counts=dict(counts), audit_records=records,
                   raw_exit_preserved=True, accepted=False)
    assert records or result.returncode == 0, 'Empty audit cannot hide a failure'
elif args.kind == 'lint':
    text = data.decode(errors='replace');start = text.find('[{')
    if start < 0:start=text.find('[\n')
    rows = json.JSONDecoder().raw_decode(text[start:])[0] if start >= 0 else None
    if not isinstance(rows,list):raise RuntimeError('Full lint did not produce structured result')
    rules=Counter()
    for row in rows:
        for message in row['messages']:rules[str(message.get('ruleId'))]+=1
    receipt.update(error_count=sum(x['errorCount'] for x in rows), warning_count=sum(x['warningCount'] for x in rows),
                   rule_counts=dict(rules), files_with_diagnostics=[{'path':str(Path(x['filePath']).relative_to(Path.cwd())),
                     'errors':x['errorCount'],'warnings':x['warningCount']} for x in rows if x['messages']], accepted=result.returncode==0)
(out/(args.kind+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['audit_records','files_with_diagnostics','rule_counts']}))
# Do not convert CLI audit/lint failures into a successful gate.
raise SystemExit(result.returncode)

