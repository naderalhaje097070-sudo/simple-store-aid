"""MONJEZ release gate: one source-identity check for every financial workflow.

Replaces the chained per-stage byte manifests. It protects what must not move:

  A. the tested commit is exactly the commit being judged (EXPECTED_SOURCE);
  B. the checkout is clean (no unmerged, modified or untracked files);
  C. every migration already on the base branch (origin/main) is present and
     byte-identical, and every new migration sorts after the newest base
     migration, except the explicitly pinned legacy-order files below.

Which other files changed is reported against the base for human review; the
behavioural, financial and security suites prove what the change does.

Two modes:
  checkout  read the working tree (push workflows, local runs);
  objects   read only git objects of --head (pull_request_target: the gate
            itself comes from the base branch and never executes PR code).
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

REPOSITORY = 'naderalhaje097070-sudo/simple-store-aid'
MIGRATIONS = 'supabase/migrations/'
NAME = re.compile(r'supabase/migrations/([0-9]{14})_[A-Za-z0-9_-]+\.sql')
# Added in October with August timestamps (audit finding F7). Allowed out of
# order only with these exact bytes; once they are on the base branch this
# exception is never consulted again.
LEGACY_ORDER = {
    'supabase/migrations/20260815170000_fin_courier_pr_a.sql': '1e6654acdad1591229df91b77981de264612d738',
    'supabase/migrations/20260815171000_fin_idem_sale_create.sql': 'c6a97b4af3b43fc7d6ed2e5b67890aeed77f79d7',
}


# Files that define acceptance itself. A PR changing any of them could make the
# required checks pass vacuously (pull_request runs the PR's own copy), so the
# trusted gate blocks such PRs until the owner adds GOVERNANCE_LABEL.
GOVERNANCE_PATTERNS = (
    '.github/workflows/',
    'tests/release/',
    'tests/c5-collection/native.py',
    'tests/c4-sale/native.py',
    'tests/c5-journey/native.py',
    'tests/c5-journey/browser.py',
    'tests/c5-journey/profit_contract.py',
)
GOVERNANCE_LABEL = 'governance-change-approved'


class GateFailure(Exception):
    pass


def check(ok, message):
    if not ok:
        raise GateFailure(message)


def git(root, *args):
    r = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=60)
    check(r.returncode == 0, 'git ' + args[0] + ' failed')
    return r.stdout


def tree(root, ref, prefix=MIGRATIONS):
    """{path: (mode, kind, blob)} for ref under prefix."""
    out = {}
    for row in git(root, 'ls-tree', '-r', '-z', ref, '--', prefix).split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            mode, kind, sha = meta.decode().split()
            out[path.decode()] = (mode, kind, sha)
    return out


def verify_migrations(root, head='HEAD', base='origin/main', legacy=None):
    """Return the sorted migration versions of head after checks A-C(migrations)."""
    legacy = LEGACY_ORDER if legacy is None else legacy
    for ref, label in ((base, 'Base'), (head, 'Head')):
        r = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '--quiet', ref + '^{commit}'],
                           capture_output=True, timeout=60)
        check(r.returncode == 0, label + ' reference unavailable: ' + ref)
    base_files, head_files = tree(root, base), tree(root, head)
    check(base_files, 'Base migrations unavailable')
    for path, entry in head_files.items():
        check(NAME.fullmatch(path), 'Invalid migration name: ' + path)
        check(entry[:2] == ('100644', 'blob'), 'Invalid migration mode: ' + path)
    for path, entry in base_files.items():
        check(path in head_files, 'Base migration removed or renamed: ' + path)
        check(head_files[path][2] == entry[2], 'Base migration changed: ' + path)
    newest = max(NAME.fullmatch(p).group(1) for p in base_files)
    for path in sorted(set(head_files) - set(base_files)):
        if NAME.fullmatch(path).group(1) > newest:
            continue
        check(legacy.get(path) == head_files[path][2], 'New migration out of order: ' + path)
    versions = [NAME.fullmatch(p).group(1) for p in sorted(head_files)]
    check(len(versions) == len(set(versions)), 'Duplicate migration version')
    return versions


def verify_checkout(root):
    """Working tree must equal HEAD exactly, including migration files on disk."""
    check(not git(root, 'status', '--porcelain', '--untracked-files=all').strip(), 'Checkout not clean')
    on_disk = {str(p.relative_to(root)) for p in (Path(root) / MIGRATIONS).iterdir()}
    check(on_disk == set(tree(root, 'HEAD')), 'Migration directory differs from HEAD')
    for path in on_disk:
        check((Path(root) / path).is_file() and not (Path(root) / path).is_symlink(), 'Nonregular migration: ' + path)


def governance_changes(root, base, head):
    out = git(root, 'diff', '--name-only', '-z', base + '...' + head).split(b'\0')
    return sorted(p.decode() for p in out if p and p.decode().startswith(GOVERNANCE_PATTERNS))


def verify_governance(root, base, head, approved):
    """Fail if acceptance-defining files change without explicit owner approval."""
    changed = governance_changes(root, base, head)
    check(not changed or approved, 'Acceptance-defining files changed without approval label '
          + GOVERNANCE_LABEL + ': ' + ', '.join(changed[:20]))
    return changed


def verify(root, head='HEAD', base='origin/main', mode='checkout', expected=None):
    root = Path(root)
    head_sha = git(root, 'rev-parse', '--verify', head + '^{commit}').decode().strip()
    expected = expected if expected is not None else os.environ.get('EXPECTED_SOURCE')
    check(expected, 'EXPECTED_SOURCE required')
    check(expected == head_sha, 'Tested commit differs from expected source')
    url = git(root, 'config', '--get', 'remote.origin.url').decode().strip()
    check(url in {f'https://github.com/{REPOSITORY}', f'https://github.com/{REPOSITORY}.git'}, 'Repository mismatch')
    if mode == 'checkout':
        check(git(root, 'rev-parse', 'HEAD').decode().strip() == head_sha, 'Checkout is not the tested commit')
        verify_checkout(root)
    versions = verify_migrations(root, head_sha, base)
    base_sha = git(root, 'rev-parse', '--verify', base + '^{commit}').decode().strip()
    changed = git(root, 'diff', '--name-only', '-z', base_sha + '...' + head_sha).split(b'\0')
    changed = sorted(p.decode() for p in changed if p)
    sensitive = [p for p in changed if p.startswith(('.github/', 'tests/release/', MIGRATIONS))]
    return {'scope': 'release_gate_v1', 'source_sha': head_sha, 'base_sha': base_sha, 'mode': mode,
            'migration_count': len(versions), 'base_migrations_preserved': True,
            'changed_file_count': len(changed), 'review_sensitive_paths': sensitive}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--base', default='origin/main')
    parser.add_argument('--mode', choices=['checkout', 'objects'], default='checkout')
    parser.add_argument('--governance', action='store_true',
                        help='also block acceptance-defining changes unless GATE_GOVERNANCE_APPROVED=true')
    args = parser.parse_args(argv)
    try:
        receipt = verify(args.root, args.head, args.base, args.mode)
        if args.governance:
            approved = os.environ.get('GATE_GOVERNANCE_APPROVED') == 'true'
            receipt['governance_changes'] = verify_governance(args.root, args.base, args.head, approved)
            receipt['governance_approved'] = approved
    except GateFailure as error:
        print('RELEASE_GATE_FAILED ' + json.dumps({'reason': str(error)}))
        return 1
    print('RELEASE_GATE_PASSED ' + json.dumps(receipt))
    return 0


if __name__ == '__main__':
    sys.exit(main())
