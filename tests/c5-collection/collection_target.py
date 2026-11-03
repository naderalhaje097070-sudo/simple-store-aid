"""Explicit approved55 target: immutable54 baseline plus the admitted collection migration."""
import json
from pathlib import Path
import re
import stat
import sys
from collection_identity import BASE, MIGRATION, MANIFEST, REPOSITORY, blob, git, check

def verify_files(root, expected):
    root=Path(root)
    directory=root/'supabase/migrations'
    check(directory.exists() and stat.S_ISDIR(directory.lstat().st_mode),'Nonregular migration directory')
    check({str(p.relative_to(root)) for p in directory.iterdir()}==set(expected),'Unexpected migration entries')
    for p,sha in expected.items():
        file=root/p
        check(re.fullmatch(r'supabase/migrations/[0-9]{14}_[A-Za-z0-9_-]+\.sql',p),'Invalid migration name')
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode) and not file.stat().st_mode & 0o111,'Nonregular migration file')
        check(blob(file.read_bytes())==sha,'Migration drift')
    versions=[Path(p).name.split('_',1)[0] for p in sorted(expected)]
    check(len(versions)==len(set(versions))==55,'Duplicate migration versions')
    return versions

def verify_source(root):
    root=Path(root)
    # The workflow checks the complete executable source before credentials.
    # This runtime contract, like the prior54 target, checks migration bytes and
    # database history. Installer/build runtime artifacts are not migration input.
    expected={}
    for row in git(root,'ls-tree','-r','-z',BASE,'--','supabase/migrations').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split()
            check(mode=='100644' and kind=='blob','Invalid original migration mode')
            expected[p.decode()]=sha
    check(len(expected)==54,'Original54 source count changed')
    file=root/MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Nonregular target manifest')
    raw=file.read_bytes()
    check(raw==git(root,'show','HEAD:'+MANIFEST),'Uncommitted target manifest')
    manifest=json.loads(raw)
    check(manifest.get('base_source')==BASE and manifest.get('repository')==REPOSITORY
          and manifest.get('scope')=='C5-COLLECTION-RETRY-01','Invalid target authority')
    expected[MIGRATION]=manifest['additions'][MIGRATION]
    versions=verify_files(root,expected)
    return versions,{'base_source':BASE,'target_manifest_blob':blob(raw),
                     'original54_migrations_preserved':True,'source_migrations_exact':55,
                     'financial_acceptance':False,'integration_accepted':False}

def verify_history(versions, observed):
    check(observed==versions,'Database history differs from approved55 target')

if __name__=='__main__':
    print(json.dumps(verify_source(Path(__file__).resolve().parents[2])[1]))
