#!/bin/bash
# Evidence collection for the release-finance cleanup step, the SAME code in CI and in the local emulation
# (review fix for PR #98, Strix review 4, CWE-59: the cleanup merge read the candidate-owned evidence tree as root).
#
# Run as the runner, from the runner's own checkout, with OUT not existing yet:
#   1. forbidden values for the publication check: the stack keys from the runner's own status copy
#      (RUNNER_TEMP/status-private.json), and the actor secrets from c5finance's private-state.json, read AS c5finance
#      with no link following (evidence_import.py readjson)
#   2. the candidate's evidence: exported AS c5finance (evidence_import.py export, no-follow at every level, only real
#      directories and regular files) and imported by the runner into the fresh OUT (evidence_import.py import)
#   3. the restore attestation placed into OUT (tests/release/restore/attestation.py place)
# Root reads nothing of the candidate's. Any rejection or failure leaves OUT empty, is recorded in
# RUNNER_TEMP/evidence-import.json and must fail the cleanup step (it asserts 'ok').
# usage: collect_evidence.sh OUT ATT   (RUNNER_TEMP set)
set -uo pipefail
out=$1; att=$2; ws=$PWD; tool="$ws/tests/release/evidence_import.py"; src=/tmp/monjez-c5sale
res="$RUNNER_TEMP/evidence-import.json"; err="$RUNNER_TEMP/evidence-import-stderr.txt"; forb="$RUNNER_TEMP/publication-forbidden.json"
if [[ -e "$out" || -L "$out" ]]; then echo "RELEASE_EVIDENCE_OUT_EXISTS"; exit 2; fi
as_c5() { sudo -u c5finance env -i PATH="$PATH" PYTHONDONTWRITEBYTECODE=1 python -I - "$@" < "$tool"; }
: > "$err"
python - "$forb" <<'PY'   # stack keys: the runner's own copy, never the candidate's
import json, os, sys
from pathlib import Path
p = Path(os.environ['RUNNER_TEMP']) / 'status-private.json'
d = json.loads(p.read_text()) if p.is_file() and not p.is_symlink() else {}
Path(sys.argv[1]).write_text(json.dumps([v for k, v in d.items() if 'KEY' in k or 'PASSWORD' in k]))
PY
state_rc=0; export_rc=0; import_rc=0; have_user=1
id c5finance > /dev/null 2>&1 || have_user=0
if [[ $have_user == 1 ]]; then
  as_c5 readjson "$src/private-state.json" > "$RUNNER_TEMP/private-state-copy.json" 2>> "$err" || state_rc=$?
  as_c5 export "$src/evidence" 2>> "$err" | python -I "$tool" import "$out" > "$RUNNER_TEMP/evidence-import-receipt.json" 2>> "$err"
  st=("${PIPESTATUS[@]}"); export_rc=${st[0]}; import_rc=${st[1]}
else   # failed before the confined identity existed: there is no candidate evidence or state
  echo '{}' > "$RUNNER_TEMP/private-state-copy.json"; mkdir -m 700 "$out"; echo '{"files": 0}' > "$RUNNER_TEMP/evidence-import-receipt.json"
fi
ok=0; [[ $state_rc == 0 && $export_rc == 0 && $import_rc == 0 ]] && ok=1
if [[ $ok != 1 ]]; then rm -rf "${out:?}"; mkdir -m 700 "$out"; fi   # nothing of a rejected export is kept
python - "$forb" "$res" "$ok" "$state_rc" "$export_rc" "$import_rc" "$have_user" <<'PY'
import json, os, sys
from pathlib import Path
forb, res, ok, state_rc, export_rc, import_rc, have_user = sys.argv[1:]
rt = Path(os.environ['RUNNER_TEMP'])
try:
    state = json.loads((rt / 'private-state-copy.json').read_text() or '{}')
except ValueError:
    state = {}
values = json.loads(Path(forb).read_text())
values += [v for a in (state.get('actors') or {}).values() if isinstance(a, dict)
           for k, v in a.items() if k in ('token', 'refresh', 'password', 'email')]
Path(forb).write_text(json.dumps(values))
(rt / 'private-state-copy.json').unlink()
notes = []
for line in (rt / 'evidence-import-stderr.txt').read_text().splitlines():
    try:
        notes.append(json.loads(line))
    except ValueError:
        notes.append({'stderr': line[:300]})
try:
    receipt = json.loads((rt / 'evidence-import-receipt.json').read_text() or '{}')
except ValueError:
    receipt = {}
r = {'ok': ok == '1', 'confined_identity_present': have_user == '1', 'private_state_exit': int(state_rc),
     'export_exit': int(export_rc), 'import_exit': int(import_rc), 'imported': receipt if ok == '1' else None,
     'rejections': notes, 'forbidden_values': len(values)}
Path(res).write_text(json.dumps(r) + '\n')
print('RELEASE_EVIDENCE_IMPORT ' + json.dumps({k: v for k, v in r.items()}))
PY
rm -f "$RUNNER_TEMP/evidence-import-receipt.json"
python tests/release/restore/attestation.py place "$out" "$att"
