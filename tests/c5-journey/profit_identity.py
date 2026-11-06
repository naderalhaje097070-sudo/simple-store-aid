"""Admit only the adopted profit delta; freeze the entire reviewed55 source."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'g01-acceptance'))
from integrated_identity import REPOSITORY, check, git, protected, valid_path
from journey_identity import inventory_delta

BASE='f2967cfbc0cf46fb09a5f4fc0c454f38f3f51a66'
MANIFEST='tests/c5-journey/profit-source.json'
MIGRATION='supabase/migrations/20261106145346_c5_day_close_profit_report.sql'
CHANGES={'src/lib/db.ts','src/features/shared/AppContext.ts','src/routes/_authenticated/app.tsx',
         'src/routes/_authenticated/platform-admin.tsx','src/features/reports/ProfitScreen.tsx',
         'src/integrations/supabase/types.ts','tests/g01-acceptance/capture.py',
         'tests/c5-journey/native.py','tests/c5-journey/browser.py','.github/workflows/c5-journey.yml',
         'tests/c5-collection/history.cjs','tests/app-financial-read/build.mjs',
         'tests/app-financial-read/replay.mjs','tests/day-close-clock/replay.mjs',
         'tests/c5-journey/build.mjs','tests/c5-collection/native.py','tests/c4-sale/native.py',
         '.github/workflows/integration-verification.yml'}
ADDITIONS={MIGRATION,'src/lib/day-close-report.ts','tests/c5-journey/profit_identity.py',
           'tests/c5-journey/test_profit_identity.py','tests/c5-journey/profit-report.test.ts',
           'tests/c5-journey/profit_contract.py','tests/c5-journey/profit-types.cjs',
           'tests/c5-journey/profit-history.cjs','tests/release/gate.py','tests/release/test_gate.py',
           'tests/release/target.py','tests/release/upgrade.py','.github/workflows/release-finance.yml',
           '.github/workflows/release-gate-trusted.yml'}
FROZEN={'tests/g01-acceptance/integrated-source.json','tests/g01-acceptance/integrated-b-source.json'}

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def selected(path):return path!=MANIFEST and (protected(path) or path in FROZEN)

def baseline(root):
    base={}
    for row in git(root,'ls-tree','-r','-z',BASE).split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split();p=p.decode()
            if selected(p):
                check(kind=='blob' and mode in {'100644','100755'},'Profit baseline mode invalid')
                base[p]=(sha,mode)
    return base

def manifest(root,base):
    file=root/MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Profit manifest nonregular')
    raw=file.read_bytes();check(raw==git(root,'show','HEAD:'+MANIFEST),'Profit manifest uncommitted')
    m=json.loads(raw)
    check(type(m.get('schema_version')) is int and m['schema_version']==1 and m.get('base_source')==BASE
          and m.get('repository')==REPOSITORY and m.get('scope')=='C5-PROFIT-CONTRACT-IMPLEMENT-01','Profit authority invalid')
    changes,additions=m.get('changes'),m.get('additions')
    check(isinstance(changes,dict) and set(changes)==CHANGES,'Profit change scope invalid')
    for p,c in changes.items():
        check(p in base and isinstance(c,dict) and set(c)=={'before','after'} and c['before']==base[p][0], 'Profit before identity invalid')
    check(isinstance(additions,dict) and set(additions)==ADDITIONS and not set(base)&set(additions),'Profit addition scope invalid')
    expected={**base,**{p:(c['after'],base[p][1]) for p,c in changes.items()},**{p:(sha,'100644') for p,sha in additions.items()}}
    check(all(valid_path(p) and isinstance(sha,str) and re.fullmatch('[0-9a-f]{40}',sha) for p,(sha,_) in expected.items()),'Profit path/blob invalid')
    return raw,expected

def verify_migrations(root):
    root=Path(root);base=baseline(root);_,expected=manifest(root,base)
    old={p:v for p,v in base.items() if p.startswith('supabase/migrations/') and p.endswith('.sql')}
    check(len(old)==55,'Profit original55 migration count')
    sql={p:v for p,v in expected.items() if p.startswith('supabase/migrations/') and p.endswith('.sql')}
    check(len(sql)==56 and all(sql.get(p)==v for p,v in old.items()) and set(sql)-set(old)=={MIGRATION},'Profit original55 SQL changed')
    directory=root/'supabase/migrations'
    check(directory.exists() and stat.S_ISDIR(directory.lstat().st_mode),'Profit migration directory nonregular')
    check({str(p.relative_to(root)) for p in directory.iterdir()}==set(sql),'Profit migration entries changed')
    for p,(sha,mode) in sql.items():
        file=root/p
        check(re.fullmatch(r'supabase/migrations/[0-9]{14}_[A-Za-z0-9_-]+\.sql',p) and mode=='100644','Profit SQL name/mode invalid')
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode) and not file.stat().st_mode & 0o111,'Profit SQL nonregular')
        check(blob(file.read_bytes())==sha,'Profit SQL drift')
    versions=[Path(p).name.split('_',1)[0] for p in sorted(sql)]
    check(len(versions)==len(set(versions))==56 and Path(MIGRATION).name.split('_',1)[0]==versions[-1],'Profit SQL version invalid')
    return versions

def verify_history(versions,observed,seed55=False):
    check(observed==(versions[:-1] if seed55 else versions),'Database history differs from exact profit target')

def verify(root):
    root=Path(root);head=git(root,'rev-parse','HEAD').decode().strip()
    check(not os.environ.get('EXPECTED_SOURCE') or os.environ['EXPECTED_SOURCE']==head,'Profit source mismatch')
    check(git(root,'config','--get','remote.origin.url').decode().strip() in
          {f'https://github.com/{REPOSITORY}',f'https://github.com/{REPOSITORY}.git'},'Profit repository mismatch')
    check(subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE,'HEAD'],capture_output=True,timeout=15).returncode==0,'Profit base not ancestor')
    base=baseline(root);raw,expected=manifest(root,base)
    paths={p.decode() for p in git(root,'ls-files','--cached','--others','--exclude-standard','-z').split(b'\0') if p}
    observed={p for p in paths if selected(p)}
    check(observed==set(expected),'Profit executable inventory changed:'+json.dumps(inventory_delta(set(expected),observed),separators=(',',':')))
    index={}
    for row in git(root,'ls-files','--stage','-z').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,sha,stage=meta.decode().split()
            check(stage=='0','Profit unmerged index');index[p.decode()]=(sha,mode)
    expected[MANIFEST]=(blob(raw),'100644');reviewed={}
    for row in git(root,'ls-tree','-r','-z','HEAD').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split();p=p.decode()
            if selected(p) or p==MANIFEST:
                check(kind=='blob','Profit HEAD nonblob');reviewed[p]=(sha,mode)
    check(reviewed==expected,'Profit reviewed HEAD differs from source')
    for p,(sha,mode) in expected.items():
        file=root/p
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Profit nonregular source: '+p)
        check(blob(file.read_bytes())==sha and index.get(p)==(sha,mode),'Profit source/index drift: '+p)
        check(('100755' if file.stat().st_mode & 0o111 else '100644')==mode,'Profit mode drift: '+p)
    verify_migrations(root)
    return {'scope':'adopted_profit_contract_exact_delta','source_sha':head,'base_source':BASE,
            'protected_blob_count':len(expected),'migration_count':56,'original55_unchanged':True,
            'prior_manifests_unchanged':True,'reviewed_head_tree_match':True,
            'financial_acceptance':False,'integration_accepted':False}
