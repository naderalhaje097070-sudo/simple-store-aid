"""C3 source admission: all prior executable/test/tool/config blobs stay exact."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / 'tests/c3-composition/source.json').read_text())
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert head == os.environ['EXPECTED_SOURCE']
assert subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], check=False).returncode == 0


def blob(path):
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


for entry in manifest['baseline']:
    assert blob(entry['path']) == entry['sha'], entry['path']
for path, expected in manifest['new_files'].items():
    assert blob(path) == expected, path
assert len(list((ROOT / 'supabase/migrations').glob('*.sql'))) == 54
assert (ROOT / manifest['migration']).read_bytes() == (ROOT / 'changes/c3-financial-composition/COMPOSITION.sql').read_bytes()
print('C3_EXACT_PRIOR_SOURCE_AND_51_SQL_PRESERVED_PLUS_TWO_ORIGINAL_AND_ONE_FORWARD')
