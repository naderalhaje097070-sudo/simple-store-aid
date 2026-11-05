"""Pin the entire existing executable graph; admit only this journey harness."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g01-acceptance'))
from integrated_identity import REPOSITORY,check,git,protected,valid_path

BASE='d5c5566228f78c3b8f76e3aa721521244affd05a'
MANIFEST='tests/c5-journey/source.json'
CHANGES={'tests/g01-acceptance/capture.py'}
ADDITIONS={'tests/c5-journey/journey_identity.py','tests/c5-journey/test_identity.py',
    'tests/c5-journey/client.ts','tests/c5-journey/fixture.tsx','tests/c5-journey/index.html',
    'tests/c5-journey/build.mjs','tests/c5-journey/browser.py','tests/c5-journey/native.py',
    '.github/workflows/c5-journey.yml'}
FROZEN={'tests/g01-acceptance/integrated-source.json','tests/g01-acceptance/integrated-b-source.json'}

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()
def selected(path):return path!=MANIFEST and (protected(path) or path in FROZEN)

def inventory_delta(expected,observed):
    def public_path(p):
        return p if p.startswith(('src/','tests/','.github/','patches/')) else 'path_sha256:'+hashlib.sha256(p.encode()).hexdigest()
    return {'missing_count':len(expected-observed),'extra_count':len(observed-expected),
            'missing':[public_path(p) for p in sorted(expected-observed)[:8]],
            'extra':[public_path(p) for p in sorted(observed-expected)[:8]]}

def verify(root):
    root=Path(root);head=git(root,'rev-parse','HEAD').decode().strip()
    check(not os.environ.get('EXPECTED_SOURCE') or os.environ['EXPECTED_SOURCE']==head,'Journey source mismatch')
    check(git(root,'config','--get','remote.origin.url').decode().strip() in
          {f'https://github.com/{REPOSITORY}',f'https://github.com/{REPOSITORY}.git'},'Journey repository mismatch')
    check(subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE,'HEAD'],capture_output=True).returncode==0,'Journey base not ancestor')
    file=root/MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Journey manifest nonregular')
    raw=file.read_bytes();check(raw==git(root,'show','HEAD:'+MANIFEST),'Journey manifest uncommitted')
    m=json.loads(raw)
    check(type(m.get('schema_version')) is int and m['schema_version']==1 and m.get('base_source')==BASE
          and m.get('repository')==REPOSITORY and m.get('scope')=='C5-FULL-JOURNEY-01','Journey authority invalid')
    base={}
    for row in git(root,'ls-tree','-r','-z',BASE).split(bytes([0])):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split();p=p.decode()
            if selected(p):
                check(kind=='blob' and mode in {'100644','100755'},'Journey base mode invalid')
                base[p]=(sha,mode)
    changes,additions=m.get('changes'),m.get('additions')
    check(isinstance(changes,dict) and set(changes)==CHANGES,'Journey change scope invalid')
    for p,c in changes.items():
        check(isinstance(c,dict) and set(c)=={'before','after'} and c['before']==base[p][0],'Journey before identity invalid')
    check(isinstance(additions,dict) and set(additions)==ADDITIONS and not set(base)&set(additions),'Journey additions invalid')
    expected={**base,**{p:(c['after'],base[p][1]) for p,c in changes.items()},**{p:(sha,'100644') for p,sha in additions.items()}}
    check(all(valid_path(p) and isinstance(sha,str) and len(sha)==40 and all(c in '0123456789abcdef' for c in sha) for p,(sha,_) in expected.items()),'Journey path/blob invalid')
    paths={p.decode() for p in git(root,'ls-files','--cached','--others','--exclude-standard','-z').split(bytes([0])) if p}
    observed={p for p in paths if selected(p)}
    check(observed==set(expected),'Journey executable inventory changed:'+json.dumps(inventory_delta(set(expected),observed),separators=(',',':')))
    index={}
    for row in git(root,'ls-files','--stage','-z').split(bytes([0])):
        if row:
            meta,p=row.split(b'\t',1);mode,sha,stage=meta.decode().split()
            check(stage=='0','Journey unmerged index');index[p.decode()]=(sha,mode)
    expected[MANIFEST]=(blob(raw),'100644')
    reviewed={}
    for row in git(root,'ls-tree','-r','-z','HEAD').split(bytes([0])):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split();p=p.decode()
            if selected(p) or p==MANIFEST:
                check(kind=='blob','Journey HEAD nonblob');reviewed[p]=(sha,mode)
    check(reviewed==expected,'Journey reviewed HEAD differs from executed source')
    for p,(sha,mode) in expected.items():
        file=root/p
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Journey nonregular source: '+p)
        check(blob(file.read_bytes())==sha and index.get(p)==(sha,mode),'Journey source/index drift: '+p)
        check(('100755' if file.stat().st_mode & 0o111 else '100644')==mode,'Journey mode drift: '+p)
    check(len([p for p in base if p.startswith('supabase/migrations/') and p.endswith('.sql')])==55,'Journey migration count')
    return {'scope':'C5_full_journey_test_only_delta','source_sha':head,'base_source':BASE,
            'protected_blob_count':len(base)+len(additions),'migration_count':55,'all_integrated_blobs_match':True,
            'prior_manifests_unchanged':True,'reviewed_head_tree_match':True,'financial_acceptance':False,'integration_accepted':False}
