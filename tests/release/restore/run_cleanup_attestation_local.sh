#!/bin/bash
# Local emulation of the cleanup step's publication part (C6/C7 plan 2.2; review fixes #98: Strix MEDIUM on 6c13bc2
# and Strix review 4 on bed1035). It runs the SAME production code as the cleanup step, in the same order:
#   tests/release/collect_evidence.sh   (c5finance exports its evidence, no link following; the runner imports it
#                                        into a fresh directory; forbidden values; restore attestation placement)
#   verify_publication                  (with the forbidden values collected above)
#   attestation.verify, and the evidence-import verdict
# Prints RELEASE_CLEANUP_ATTESTATION and exits non-zero exactly when the cleanup step would fail on these checks.
# Not reproduced: the firewall, docker and private-file receipts of the cleanup step.
# usage: run_cleanup_attestation_local.sh RUNNER_TEMP EXPECTED_SOURCE    (run as the runner, from its checkout)
set -euo pipefail
RT=$1; SRC=$2; out="$RT/release-evidence"
export RUNNER_TEMP="$RT"
tests/release/collect_evidence.sh "$out" "$RT/restore-attestation"
SRC="$SRC" python3 - <<'PY'
import json, os, sys
from pathlib import Path
root = Path(os.environ['RUNNER_TEMP']); out = root / 'release-evidence'
sys.path.insert(0, 'tests/account-lifecycle'); sys.path.insert(0, 'tests/release/restore')
from scanner_evidence import verify_publication, PublicationBlocked
from attestation import verify
imported = json.loads((root / 'evidence-import.json').read_text())
blocked = None
try:
    verify_publication(out, root / 'release-private-quarantine', json.loads((root / 'publication-forbidden.json').read_text()))
except PublicationBlocked as e:
    blocked = str(e)
status, collisions = verify(out, root / 'restore-attestation', os.environ['SRC'])
r = {'evidence_import_ok': imported['ok'], 'publication_blocked': blocked, 'restore_attestation': status,
     'restore_name_collisions': collisions,
     'published': sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file())}
print('RELEASE_CLEANUP_ATTESTATION ' + json.dumps(r))
sys.exit(0 if imported['ok'] and blocked is None and not collisions and status in ('verified', 'absent') else 1)
PY
