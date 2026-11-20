"""Restore attestation placement and re-verification for the release-finance cleanup step (C6/C7 plan 2.2).

Review fix for PR #98, Strix MEDIUM on 6c13bc2 (CWE-345): the restore step's runner-authored verification files
must not be replaceable by the candidate's evidence tree, which the cleanup step merges into the same publication
directory. The restore step therefore stages them in the runner-only $RUNNER_TEMP/restore-attestation (with
restore-attestation.sha256), and this module, run by the runner from its own checkout:

  place(out, att)            AFTER the candidate's evidence is merged into out: records every candidate entry that
                             occupies a reserved name (out/restore, or any of the attestation file names anywhere),
                             and only if there is none copies the staged attestation to out/restore with exclusive,
                             no-follow creation. A collision is never overwritten or merged.
  verify(out, att, source)   AFTER the publication check: 'verified' when there is no collision, the staged and the
                             published files have exactly the attested names and digests, and the attested source is
                             the tested commit; 'absent' when no attestation was staged and nothing occupies its
                             place (jobs without the restore step, or a restore step that stopped early); otherwise
                             'MISMATCH'. The cleanup step fails on anything but 'verified' or 'absent'.
"""
import hashlib
import json
import os
from pathlib import Path

DIR = 'restore'
FILES = ('restore-check.json', 'restore-guard.json', 'restore-n1-guard.json', 'restore-suite-controls.json')
SUMS = 'restore-attestation.sha256'
RESERVED = set(FILES) | {SUMS}
COLLISIONS = 'restore-collisions.json'


def collisions(out):
    found = []
    for top, dirs, files in os.walk(out, followlinks=False):
        for name in dirs + files:
            rel = os.path.relpath(os.path.join(top, name), out)
            if rel == DIR or name in RESERVED:
                found.append(rel)
    return sorted(found)


def sums(att):
    p = Path(att) / SUMS
    if not p.is_file() or p.is_symlink():
        return None
    rows = {}
    for line in p.read_text().splitlines():
        digest, _, name = line.partition('  ')
        if name in rows or name not in FILES or len(digest) != 64:
            return {}
        rows[name] = digest
    return rows if set(rows) == set(FILES) else {}


def _write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)


def place(out, att):
    out, att = Path(out), Path(att)
    found = collisions(out)
    (out.parent / COLLISIONS).write_text(json.dumps(found) + '\n')   # runner-only, outside the publication
    rows = sums(att)
    if found or not rows:
        return {'placed': False, 'collisions': found}
    os.mkdir(out / DIR, 0o700)
    for name in list(FILES) + [SUMS]:
        _write_new(out / DIR / name, (att / name).read_bytes())
    return {'placed': True, 'collisions': found}


def _matches(d, rows):
    if not d.is_dir() or d.is_symlink() or sorted(p.name for p in d.iterdir()) != sorted(list(rows) + [SUMS]):
        return False
    return all((d / n).is_file() and not (d / n).is_symlink()
               and hashlib.sha256((d / n).read_bytes()).hexdigest() == h for n, h in rows.items())


def verify(out, att, source):
    out, att = Path(out), Path(att)
    recorded = out.parent / COLLISIONS
    found = sorted(set(json.loads(recorded.read_text()) if recorded.exists() else ['collision record missing'])
                   | set(c for c in collisions(out) if c != DIR and not c.startswith(DIR + os.sep)))
    pub = out / DIR
    rows = sums(att)
    if rows is None:
        return ('absent' if not found and not os.path.lexists(pub) else 'MISMATCH'), found
    try:
        src_ok = json.loads((att / FILES[0]).read_text()).get('source') == source
    except (OSError, ValueError):
        src_ok = False
    ok = (bool(rows) and not found and src_ok and _matches(att, rows) and _matches(pub, rows)
          and (pub / SUMS).read_bytes() == (att / SUMS).read_bytes())
    return ('verified' if ok else 'MISMATCH'), found


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'place':
        print('RELEASE_RESTORE_ATTESTATION_PLACE ' + json.dumps(place(sys.argv[2], sys.argv[3])))
    else:
        raise SystemExit('usage: attestation.py place OUT ATT')
