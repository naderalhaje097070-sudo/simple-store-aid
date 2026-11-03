"""Explicit approved55 target: immutable54 baseline plus the admitted collection migration."""
import json
from pathlib import Path
import sys
from collection_identity import verify, BASE, MIGRATION, blob, git, check

def verify_source(root):
    root=Path(root)
    receipt=verify(root)
    expected={}
    for row in git(root,'ls-tree','-r','-z',BASE,'--','supabase/migrations').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,kind,sha=meta.decode().split()
            check(mode=='100644' and kind=='blob','Invalid original migration mode')
            expected[p.decode()]=sha
    check(len(expected)==54,'Original54 source count changed')
    manifest=json.loads((root/'tests/c5-collection/source.json').read_text())
    expected[MIGRATION]=manifest['additions'][MIGRATION]
    files=list((root/'supabase/migrations').iterdir())
    check({str(p.relative_to(root)) for p in files}==set(expected),'Unexpected migration entries')
    for p,sha in expected.items():
        check(blob((root/p).read_bytes())==sha,'Migration drift')
    versions=[Path(p).name.split('_',1)[0] for p in sorted(expected)]
    check(len(versions)==len(set(versions))==55,'Duplicate migration versions')
    return versions,{**receipt,'original54_migrations_preserved':True,'source_migrations_exact':55}

def verify_history(versions, observed):
    check(observed==versions,'Database history differs from approved55 target')

if __name__=='__main__':
    print(json.dumps(verify_source(Path(__file__).resolve().parents[2])[1]))
