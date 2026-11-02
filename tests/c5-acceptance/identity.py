"""Explicit C5 test-only admission; prior source manifests/verifiers remain frozen."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'g01-acceptance'))
from integrated_identity import REPOSITORY, check, git, protected, valid_path

BASE = '836de635e2920480059f3d4dbbd00690c61c080a'
MANIFEST = 'tests/c5-acceptance/source.json'
CHANGES = {'tests/g01-acceptance/runtime.py', 'tests/g01-acceptance/capture.py',
           '.github/workflows/g01-runtime-retry.yml'}
ADDITIONS = {'tests/c5-acceptance/identity.py', 'tests/c5-acceptance/test_identity.py',
             'tests/c5-acceptance/target.py', 'tests/c5-acceptance/target.json',
             'tests/c5-acceptance/test_target.py'}
FROZEN = {
    'tests/g01-acceptance/integrated-source.json': 'b79640f400a32924f114e19ec51a728be94b6afd',
    'tests/g01-acceptance/integrated-b-source.json': 'f1e2a8cdce0aa02549716321af2a11cf433ab177',
    'tests/c-source/manifest.json': '828eb332e7ce0d6129993342414fb83fee6c02fe',
    'tests/c4-sale/source.json': '4b63f61f4b6529eca05177880a7bce9ddd107ed5',
    'tests/sec-dep-20261102/source.json': '252048a9245f090e07ce727e7fcda500505a82c7',
}


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def selected(path):
    return path != MANIFEST and protected(path)


def verify(root):
    root = Path(root)
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    check(not os.environ.get('EXPECTED_SOURCE') or os.environ['EXPECTED_SOURCE'] == head, 'C5 expected source mismatch')
    remote = git(root, 'config', '--get', 'remote.origin.url').decode().strip()
    check(remote in {f'https://github.com/{REPOSITORY}', f'https://github.com/{REPOSITORY}.git'}, 'C5 repository mismatch')
    file = root / MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'C5 manifest nonregular')
    data = file.read_bytes()
    check(data == git(root, 'show', 'HEAD:' + MANIFEST), 'C5 manifest not committed')
    m = json.loads(data)
    check(type(m.get('schema_version')) is int and m['schema_version'] == 1, 'C5 schema invalid')
    check(m.get('scope') == 'C5-G1-SCHEMA-01' and m.get('repository') == REPOSITORY
          and m.get('base_source') == BASE, 'C5 authority invalid')
    check(subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', BASE, 'HEAD'],
                         capture_output=True, timeout=15).returncode == 0, 'C5 base not ancestor')
    base = {}
    for row in git(root, 'ls-tree', '-r', '-z', BASE).split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            mode, kind, sha = meta.decode().split()
            path = path.decode()
            if selected(path):
                check(kind == 'blob' and mode in {'100644', '100755'}, 'C5 baseline mode invalid')
                base[path] = (sha, mode)
    check(isinstance(m.get('protected_blobs'), list), 'C5 snapshot invalid')
    expected = {}
    for row in m['protected_blobs']:
        check(isinstance(row, dict), 'C5 snapshot row invalid')
        p, sha, mode = row.get('path'), row.get('sha'), row.get('mode')
        check(valid_path(p) and selected(p) and p not in expected, 'C5 path invalid/duplicate')
        check(isinstance(sha, str) and len(sha) == 40 and all(c in '0123456789abcdef' for c in sha), 'C5 blob invalid')
        check(mode in {'100644', '100755'}, 'C5 mode invalid')
        expected[p] = (sha, mode)
    check(set(base) <= set(expected), 'C5 baseline paths lost')
    changed = {p for p in base if base[p] != expected[p]}
    added = set(expected) - set(base)
    check(changed <= CHANGES and added <= ADDITIONS, 'C5 undeclared change/addition')
    check(m.get('intentional_changes') == {p: {'before': base[p][0], 'after': expected[p][0],
                                              'mode': expected[p][1]} for p in sorted(changed)}, 'C5 changes provenance invalid')
    check(m.get('additions') == {p: expected[p][0] for p in sorted(added)}, 'C5 additions provenance invalid')
    sql = {p for p in base if p.startswith('supabase/migrations/') and p.endswith('.sql')}
    check(len(sql) == 54 and all(expected[p] == base[p] for p in sql), 'C5 migration identity changed')
    observed = {p.decode() for p in git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0') if p}
    check({p for p in observed if selected(p)} == set(expected), 'C5 protected path set changed')
    index = {}
    for row in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if row:
            meta, p = row.split(b'\t', 1)
            mode, sha, stage = meta.decode().split()
            check(stage == '0', 'C5 unmerged index')
            index[p.decode()] = (sha, mode)
    for p, value in {**expected, MANIFEST: (blob(data), '100644'),
                     **{p: (sha, '100644') for p, sha in FROZEN.items()}}.items():
        sha, mode = value
        file = root / p
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'C5 nonregular source: ' + p)
        check(blob(file.read_bytes()) == sha and index.get(p) == (sha, mode), 'C5 source/index changed: ' + p)
        check(('100755' if file.stat().st_mode & 0o111 else '100644') == mode, 'C5 worktree mode changed: ' + p)
    return {'scope': 'C5_G1_schema_and_test_source_only', 'head_sha': head, 'base_source': BASE,
            'protected_blob_count': len(expected), 'migration_count': 54,
            'frozen_A_B_C_C4_SEC_unchanged': True, 'all_integrated_blobs_match': True,
            'declared_changes': sorted(changed), 'declared_additions': sorted(added),
            'financial_acceptance': False, 'integration_accepted': False}
