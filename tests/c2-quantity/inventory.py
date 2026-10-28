"""Verify explicit C2 delta before disposable credentials are read."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
manifest = json.loads((ROOT / 'tests/c2-quantity/source.json').read_text())
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
assert head == os.environ['EXPECTED_SOURCE']
assert subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], check=False).returncode == 0

def blob(path):
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

for entry in manifest['baseline']:
    expected = manifest['intentional_changes'].get(entry['path'], entry['sha'])
    assert blob(entry['path']) == expected, entry['path']
for path, expected in manifest['new_files'].items():
    assert blob(path) == expected, path
assert len(list((ROOT / 'supabase/migrations').glob('*.sql'))) == 51
assert (ROOT / manifest['migration']).read_bytes() == (ROOT / 'changes/c2-fractional-quantity/QUANTITY.sql').read_bytes()
print('C2_SOURCE_388_PRESERVED_EXCEPT_FOUR_EXPLICIT_CHANGES_AND_ONE_NEW_MIGRATION')
