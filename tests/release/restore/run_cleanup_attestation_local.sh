#!/bin/bash
# Local emulation of the cleanup step's attestation part (C6/C7 plan 2.2, review fix #98 Strix MEDIUM), on the real
# artifacts of a run_step_local.sh run: the c5finance evidence tree /tmp/monjez-c5sale/evidence and the staged
# RT/restore-attestation. Same order as the cleanup step: cp -a merge, attestation.py place, verify_publication
# (forbidden list from the restore target status), attestation.verify. Prints RELEASE_CLEANUP_ATTESTATION and exits
# non-zero exactly when the cleanup step would fail on it. Not reproduced: firewall, docker and private-file checks.
# usage: run_cleanup_attestation_local.sh RUNNER_TEMP EXPECTED_SOURCE    (run from the runner's checkout)
set -euo pipefail
RT=$1; SRC=$2; out="$RT/release-evidence"
[ -e "$out" ] && { echo "publication directory exists: $out" >&2; exit 2; }
mkdir -p "$out"
if [[ -d /tmp/monjez-c5sale/evidence ]]; then
  sudo cp -a /tmp/monjez-c5sale/evidence/. "$out/"
  sudo chown -R "$(id -un):$(id -gn)" "$out"
fi
python3 tests/release/restore/attestation.py place "$out" "$RT/restore-attestation"
RT="$RT" SRC="$SRC" python3 - <<'PY'
import json, os, sys
from pathlib import Path
root = Path(os.environ['RT']); out = root / 'release-evidence'
sys.path.insert(0, 'tests/account-lifecycle'); sys.path.insert(0, 'tests/release/restore')
from scanner_evidence import verify_publication, PublicationBlocked
from attestation import verify
blocked = None
try:
    verify_publication(out, root / 'release-private-quarantine', [])
except PublicationBlocked as e:
    blocked = str(e)
status, collisions = verify(out, root / 'restore-attestation', os.environ['SRC'])
r = {'publication_blocked': blocked, 'restore_attestation': status, 'restore_name_collisions': collisions,
     'published_restore': sorted(p.name for p in (out / 'restore').iterdir()) if (out / 'restore').is_dir() else None}
print('RELEASE_CLEANUP_ATTESTATION ' + json.dumps(r))
sys.exit(0 if blocked is None and not collisions and status in ('verified', 'absent') else 1)
PY
