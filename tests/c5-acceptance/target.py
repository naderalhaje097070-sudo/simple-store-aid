"""Pinned source bytes plus actual local migration history; no financial acceptance."""
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess

BASE = '836de635e2920480059f3d4dbbd00690c61c080a'
REPOSITORY = 'naderalhaje097070-sudo/simple-store-aid'
MANIFEST = 'tests/c5-acceptance/target.json'
ARCHIVE = 'tests/g01-acceptance/integrated-source.json'
ARCHIVE_SHA = 'b79640f400a32924f114e19ec51a728be94b6afd'


class TargetError(RuntimeError):
    pass


def require(passed, reason):
    if not passed:
        raise TargetError(reason)


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], timeout=15)


def baseline(root):
    rows = []
    for entry in git(root, 'ls-tree', '-r', '-z', BASE, '--', 'supabase/migrations').split(b'\0'):
        if not entry:
            continue
        meta, path = entry.split(b'\t', 1)
        mode, kind, sha = meta.decode().split()
        require(kind == 'blob' and mode == '100644', 'invalid baseline migration mode')
        rows.append({'path': path.decode(), 'sha': sha, 'mode': mode})
    archive = git(root, 'show', BASE + ':' + ARCHIVE)
    require(blob(archive) == ARCHIVE_SHA, 'original41 archive changed')
    return sorted(rows, key=lambda row: row['path']), json.loads(archive)['original54_migrations']


def verify_files(root, manifest, expected, original):
    require(isinstance(manifest, dict) and type(manifest.get('schema_version')) is int
            and manifest['schema_version'] == 1, 'invalid target manifest schema')
    require(manifest.get('base_source') == BASE and manifest.get('repository') == REPOSITORY
            and manifest.get('scope') == 'C5-G1-SCHEMA-01', 'invalid target authority')
    require(len(expected) == 54 and manifest.get('migrations') == expected,
            'target differs from pinned54 source')
    names = [row['path'] for row in expected]
    require(len(set(names)) == 54 and names == sorted(names), 'invalid migration path set')
    require(all(re.fullmatch(r'supabase/migrations/[0-9]{14}_[A-Za-z0-9_-]+\.sql', p)
                for p in names), 'invalid migration filename')
    versions = [Path(p).name.split('_', 1)[0] for p in names]
    require(len(set(versions)) == 54, 'duplicate migration version')
    expected_map = {row['path']: row['sha'] for row in expected}
    require(len(original) == 41 and all(expected_map.get(p) == sha for p, sha in original.items()),
            'original41 migration identity lost')
    directory = Path(root) / 'supabase/migrations'
    require(directory.exists() and stat.S_ISDIR(directory.lstat().st_mode), 'nonregular migration directory')
    require({p.name for p in directory.iterdir()} == {Path(p).name for p in names},
            'unexpected or missing migration entry')
    for row in expected:
        file = Path(root) / row['path']
        require(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'nonregular migration file')
        require(row['mode'] == '100644' and not file.stat().st_mode & 0o111, 'migration mode changed')
        require(blob(file.read_bytes()) == row['sha'], 'migration bytes changed')
    return versions


def verify_history(versions, observed):
    require(isinstance(observed, list) and all(type(v) is str for v in observed),
            'invalid database history result')
    require(observed == versions, 'database history differs from pinned54 source')


def verify_source(root):
    root = Path(root)
    file = root / MANIFEST
    require(file.exists() and stat.S_ISREG(file.lstat().st_mode), 'nonregular target manifest')
    data = file.read_bytes()
    require(data == git(root, 'show', 'HEAD:' + MANIFEST), 'uncommitted target manifest')
    expected, original = baseline(root)
    versions = verify_files(root, json.loads(data), expected, original)
    return versions, {'base_source': BASE, 'target_manifest_blob': blob(data),
                      'source_migrations_exact': 54, 'original_migrations_preserved': 41,
                      'financial_acceptance': False, 'integration_accepted': False}


if __name__ == '__main__':
    _, receipt = verify_source(Path(__file__).resolve().parents[2])
    print(json.dumps(receipt))
