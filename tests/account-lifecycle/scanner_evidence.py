"""Fail-closed artifact sink: quarantine the entire batch before raising."""
import hashlib
import json
from pathlib import Path
import re
import shutil

PATTERN = re.compile(rb'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}|sb_(?:secret|publishable)_[A-Za-z0-9_-]{8,}')


class PublicationBlocked(RuntimeError):
    pass


def verify_publication(directory, quarantine, forbidden=()):
    directory, quarantine = Path(directory), Path(quarantine)
    if directory.resolve() == quarantine.resolve() or directory.resolve() in quarantine.resolve().parents:
        raise ValueError('quarantine must be outside the upload directory')
    records, blocked = [], False
    values = [v.encode() for v in forbidden if isinstance(v, str) and len(v) > 8]
    for path in sorted(directory.rglob('*')):
        if path.is_dir() and not path.is_symlink():
            continue
        if path.is_symlink() or not path.is_file():
            records.append({'file':str(path.relative_to(directory)), 'reason':'non-regular evidence'})
            blocked = True
            continue
        raw = path.read_bytes()
        unsafe = bool(PATTERN.search(raw)) or any(v in raw for v in values)
        records.append({'file':str(path.relative_to(directory)), 'sha256':hashlib.sha256(raw).hexdigest(),
                        'reason':'credential detected' if unsafe else 'batch quarantined'})
        blocked = blocked or unsafe
    if not blocked:
        return {'publication_allowed':True, 'files':len(records)}
    quarantine.parent.mkdir(parents=True, exist_ok=True)
    if quarantine.exists():
        raise ValueError('quarantine destination already exists')
    # Move the whole sink atomically on the same filesystem. The always-upload
    # step can now see only the safe receipt, even though this step fails.
    shutil.move(str(directory), str(quarantine))
    quarantine.chmod(0o700)
    directory.mkdir(mode=0o700)
    receipt = {'publication_allowed':False, 'reason':'evidence quarantined before failure', 'files':records}
    (directory/'publication-blocked.json').write_text(json.dumps(receipt,indent=2)+'\n')
    raise PublicationBlocked('AC01_EVIDENCE_QUARANTINED')
