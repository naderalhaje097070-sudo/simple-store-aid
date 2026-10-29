"""C3+SEC source admission; original B verifier and its assertions remain unchanged."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'g01-acceptance'))
from integrated_identity import IdentityError, REPOSITORY, check, git, protected, valid_path

MANIFEST = 'tests/c-source/manifest.json'
C_BASE = '5b6da796008de10dd429bb53cafdab365b108686'
FROZEN = {'tests/g01-acceptance/integrated-source.json': 'b79640f400a32924f114e19ec51a728be94b6afd',
          'tests/g01-acceptance/integrated-b-source.json': 'f1e2a8cdce0aa02549716321af2a11cf433ab177'}
ALLOWED_CHANGES = {'package.json', 'bun.lock', 'tests/unit/dependency-security.test.ts',
                   'tests/g01-acceptance/capture.py', '.github/workflows/integration-verification.yml'}
ALLOWED_ADDITIONS = {'tests/c-source/c_identity.py', 'tests/c-source/test_identity.py',
                     'tests/sec-dep-20261029/regressions.cjs', 'tests/sec-dep-20261029/serde-child.cjs',
                     '.github/workflows/sec-dep-20261029.yml'}


def c_protected(path):
    return path != MANIFEST and protected(path)


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def verify(root):
    root = Path(root)
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    check(not os.environ.get('EXPECTED_SOURCE') or os.environ['EXPECTED_SOURCE'] == head, 'C expected source mismatch')
    remote = git(root, 'config', '--get', 'remote.origin.url').decode().strip()
    check(remote in (f'https://github.com/{REPOSITORY}', f'https://github.com/{REPOSITORY}.git'), 'C repository remote mismatch')
    file = root / MANIFEST
    check(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'Nonregular C manifest')
    data = file.read_bytes()
    check(data == git(root, 'show', f'HEAD:{MANIFEST}'), 'Uncommitted C manifest')
    m = json.loads(data)
    check(isinstance(m, dict), 'Invalid C manifest object')
    check(type(m.get('schema_version')) is int and m['schema_version'] == 1, 'Invalid C schema')
    check(m.get('scope') == 'SEC-DEP-20261029' and m.get('repository') == REPOSITORY, 'Invalid C scope/repository')
    check(m.get('base_source') == C_BASE, 'Invalid fixed C baseline')
    status = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', C_BASE, 'HEAD'], capture_output=True, timeout=15)
    check(status.returncode == 0, 'C baseline not ancestor')
    base = {}
    for row in git(root, 'ls-tree', '-r', '-z', C_BASE).split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            mode, kind, sha = meta.decode().split()
            p = path.decode()
            if c_protected(p):
                check(kind == 'blob' and mode in ('100644', '100755'), 'Invalid C baseline mode')
                base[p] = (sha, mode)
    check(isinstance(m.get('protected_blobs'), list), 'Invalid C snapshot list')
    expected = {}
    for item in m['protected_blobs']:
        check(isinstance(item, dict), 'Invalid C entry')
        p, sha, mode = item.get('path'), item.get('sha'), item.get('mode')
        check(valid_path(p) and c_protected(p), 'Invalid C protected path')
        check(p not in expected, 'Duplicate C protected path')
        check(isinstance(sha, str) and len(sha) == 40 and all(c in '0123456789abcdef' for c in sha), 'Invalid C blob')
        check(mode in ('100644', '100755'), 'Invalid C mode')
        expected[p] = (sha, mode)
    check(bool(expected) and set(base) <= set(expected), 'C baseline paths lost')
    changed = {p for p in base if base[p] != expected[p]}
    added = set(expected) - set(base)
    check(changed <= ALLOWED_CHANGES and added <= ALLOWED_ADDITIONS, 'Undeclared C change/addition boundary')
    declared = m.get('intentional_changes')
    check(isinstance(declared, dict) and set(declared) == changed, 'C change inventory differs')
    for p in changed:
        check(declared[p] == {'before': base[p][0], 'after': expected[p][0], 'mode': expected[p][1]}, 'C change provenance mismatch')
    check(m.get('additions') == {p: expected[p][0] for p in sorted(added)}, 'C additions differ')
    sql = {p: v for p, v in base.items() if p.startswith('supabase/migrations/') and p.endswith('.sql')}
    check(len(sql) == 54 and all(expected.get(p) == v for p, v in sql.items()), 'Applied C54 SQL identity/mode changed')
    observed = {p.decode() for p in git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split(b'\0') if p}
    check({p for p in observed if c_protected(p)} == set(expected), 'C protected path set changed')
    index = {}
    for row in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if row:
            meta, p = row.split(b'\t', 1)
            mode, sha, stage = meta.decode().split()
            check(stage == '0', 'C unmerged index')
            index[p.decode()] = (sha, mode)
    all_expected = {**expected, MANIFEST: (blob(data), '100644'), **{p: (sha, '100644') for p, sha in FROZEN.items()}}
    for p, (sha, mode) in all_expected.items():
        file = root / p
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), f'Nonregular C source/manifest: {p}')
        check(blob(file.read_bytes()) == sha, f'Unreviewed C source/frozen manifest mutation: {p}')
        check(index.get(p) == (sha, mode), f'C tracked index/mode changed: {p}')
        actual_mode = '100755' if file.stat().st_mode & 0o111 else '100644'
        check(actual_mode == mode, f'C worktree mode changed: {p}')
    return {'scope': 'C3_plus_SEC_DEP_source_identity_only', 'base_source': C_BASE, 'head_sha': head,
            'protected_blob_count': len(expected), 'all_integrated_blobs_match': True,
            'migration_count': 54, 'frozen_A_B_unchanged': True,
            'declared_changes': sorted(changed), 'declared_additions': sorted(added),
            'financial_acceptance': False, 'integration_accepted': False}
