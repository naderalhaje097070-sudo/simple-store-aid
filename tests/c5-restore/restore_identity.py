"""Owner-authorized bounded collection delta; prior54 migrations and all other source stay exact."""
import json
import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'g01-acceptance'))
from integrated_identity import REPOSITORY, check, git, protected, valid_path
prior_spec = importlib.util.spec_from_file_location('c5_frozen_guard', Path(__file__).resolve().parents[1] / 'c5-acceptance/identity.py')
prior = importlib.util.module_from_spec(prior_spec)
prior_spec.loader.exec_module(prior)
blob, PRIOR_FROZEN = prior.blob, prior.FROZEN

BASE = 'be0f128f82e23da094ddce56d3f06dabef018dc9'
MANIFEST = 'tests/c5-restore/source.json'
CHANGES = {'tests/g01-acceptance/capture.py'}
ADDITIONS = {'tests/c5-restore/restore_identity.py','tests/c5-restore/test_identity.py','tests/c5-restore/restore.py','.github/workflows/c5-restore.yml'}

FROZEN = {**PRIOR_FROZEN, 'tests/c5-acceptance/source.json': 'b70c7cf72d39f995df1a570046f3a106b68db9e6', 'tests/c5-collection/source.json': '2483c1c05cec0f40dbbf22a77dec492f7c83ca3f', 'tests/c5-collection/collection_identity.py': 'b751ad12071edeae0eafd1e4d238e185242a7cfe'}


def selected(path):
    return path != MANIFEST and protected(path)


def verify(root):
    root = Path(root)
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    check(not os.environ.get('EXPECTED_SOURCE') or os.environ['EXPECTED_SOURCE'] == head, 'Finance source mismatch')
    check(git(root, 'config', '--get', 'remote.origin.url').decode().strip()
          in {f'https://github.com/{REPOSITORY}', f'https://github.com/{REPOSITORY}.git'}, 'Finance repository mismatch')
    check(subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE,'HEAD'],
                         capture_output=True,timeout=15).returncode == 0, 'Finance base not ancestor')
    file = root / MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'Finance manifest nonregular')
    data = file.read_bytes()
    check(data == git(root, 'show', 'HEAD:' + MANIFEST), 'Finance manifest uncommitted')
    m = json.loads(data)
    check(type(m.get('schema_version')) is int and m['schema_version'] == 1
          and m.get('base_source') == BASE and m.get('repository') == REPOSITORY
          and m.get('scope') == 'C5-RESTORE-01', 'Finance authority invalid')
    base = {}
    for row in git(root,'ls-tree','-r','-z',BASE).split(b'\0'):
        if row:
            meta,p = row.split(b'\t',1)
            mode,kind,sha = meta.decode().split();p=p.decode()
            if selected(p):
                check(kind == 'blob' and mode in {'100644','100755'}, 'Finance baseline mode invalid')
                base[p] = (sha,mode)
    changes, additions = m.get('changes'),m.get('additions')
    check(isinstance(changes,dict) and set(changes)==CHANGES, 'Collection change scope invalid')
    for p, change in changes.items():
        check(isinstance(change,dict) and set(change)=={'before','after'}
              and change['before']==base[p][0], 'Collection change provenance invalid')
    check(isinstance(additions,dict) and set(additions)==ADDITIONS and not (set(base)&set(additions)), 'Collection additions invalid')
    expected = {**base, **{p:(c['after'],base[p][1]) for p,c in changes.items()},
                **{p:(sha,'100644') for p,sha in additions.items()}}
    check(all(valid_path(p) and isinstance(sha,str) and len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
              for p,(sha,_) in expected.items()), 'Finance blob/path invalid')
    observed = {p.decode() for p in git(root,'ls-files','--cached','--others','--exclude-standard','-z').split(b'\0') if p}
    check({p for p in observed if selected(p)} == set(expected), 'Finance protected path set changed')
    index = {}
    for row in git(root,'ls-files','--stage','-z').split(b'\0'):
        if row:
            meta,p=row.split(b'\t',1);mode,sha,stage=meta.decode().split()
            check(stage=='0','Finance unmerged index');index[p.decode()]=(sha,mode)
    expected.update({MANIFEST:(blob(data),'100644'),**{p:(sha,'100644') for p,sha in FROZEN.items()}})
    for p,(sha,mode) in expected.items():
        file=root/p
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode),'Finance nonregular source: '+p)
        check(blob(file.read_bytes())==sha and index.get(p)==(sha,mode),'Finance source/index drift: '+p)
        check(('100755' if file.stat().st_mode & 0o111 else '100644')==mode,'Finance mode drift: '+p)
    sql={p for p in base if p.startswith('supabase/migrations/') and p.endswith('.sql')}
    check(len(sql)==55,'Finance migration inventory invalid')
    return {'scope':'C5_restore_test_only_delta','source_sha':head,'base_source':BASE,
            'protected_blob_count':len(base)+len(additions),'migration_count':55,
            'all_integrated_blobs_match':True,'prior_manifests_unchanged':True,
            'financial_acceptance':False,'integration_accepted':False}
