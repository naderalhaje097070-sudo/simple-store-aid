#!/bin/bash
# Defensive self-test for the cleanup step's evidence import boundary (review fix #98, Strix review 4 on bed1035).
# LOCAL and synthetic only, run as root (the local runner identity) from the runner's checkout. It drives the
# PRODUCTION script tests/release/collect_evidence.sh on the production path /tmp/monjez-c5sale, which each case
# recreates with synthetic c5finance-owned content. The only "host" target is a synthetic root-only canary created and
# removed by this test (/var/tmp/monjez-import-canary); no real host file is read or linked.
# A case passes when the import verdict is the expected one and the canary's secret appears nowhere in RUNNER_TEMP.
# Part 2 feeds malformed tar streams straight into `evidence_import.py import`.
# usage: tests/release/selftest_evidence_import.sh   (destroys and recreates /tmp/monjez-c5sale)
set -euo pipefail
ws=$PWD; B=/tmp/monjez-c5sale; C=/var/tmp/monjez-import-canary; T=$(mktemp -d); ok=1
trap 'rm -rf "${T:?}" "${C:?}"' EXIT
id c5finance > /dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin c5finance
rm -rf "${C:?}"; install -d -m 700 -o root -g root "$C"
secret="CANARY_IMPORT_$(head -c 12 /dev/urandom | od -An -tx1 | tr -d ' \n')"
printf '%s\n' "$secret" > "$C/secret"; chmod 600 "$C/secret"; mkdir -m 700 "$C/dir"; cp "$C/secret" "$C/dir/inner"
as_c5() { sudo -u c5finance sh -c "$1"; }
fresh() {   # the layout the job builds: c5finance-owned tree, evidence dir, a private state with an actor secret
  rm -rf "${B:?}"; install -d -m 711 -o c5finance -g c5finance "$B"; install -d -m 700 -o c5finance -g c5finance "$B/evidence"
  as_c5 "mkdir -p '$B/evidence/sub dir/deeper' && printf '{\"ok\": true}\n' > '$B/evidence/financial-result.json' \
         && printf 'x\n' > '$B/evidence/sub dir/deeper/notes é.txt' \
         && printf '{\"actors\": {\"owner\": {\"email\": \"synthetic-actor@example.invalid\", \"token\": \"synthetic-token-tttttttttttttttt\"}}}\n' > '$B/private-state.json'"
}
run() {   # $1 case name; prints "ok|export|import|state|files|forbidden" from the real script's receipt
  local rt="$T/rt_$1"; mkdir -m 700 "$rt"
  printf '{"ANON_KEY": "synthetic-anon-key-kkkkkkkkkkkkkkkk", "API_URL": "http://127.0.0.1:54321"}\n' > "$rt/status-private.json"
  (cd "$ws" && RUNNER_TEMP="$rt" tests/release/collect_evidence.sh "$rt/release-evidence" "$rt/restore-attestation" > "$rt/log" 2>&1) || true
  python3 - "$rt" <<'PY'
import json, sys
from pathlib import Path
rt = Path(sys.argv[1]); r = json.loads((rt / 'evidence-import.json').read_text())
files = sorted(str(p.relative_to(rt / 'release-evidence')) for p in (rt / 'release-evidence').rglob('*') if p.is_file())
print('%s|%s|%s|%s|%s|%s' % (r['ok'], r['export_exit'], r['import_exit'], r['private_state_exit'], ','.join(files), r['forbidden_values']))
PY
}
chk() {   # $1 case, $2 got, $3 want (glob)
  local leak=0; grep -rqF -- "$secret" "$T" 2> /dev/null && leak=1
  if [[ "$2" == $3 && $leak == 0 ]]; then echo "$1 PASS ($2)"; else echo "$1 FAIL (got $2, want $3, canary_secret_found=$leak)"; ok=; fi
}
GOOD='True|0|0|0|financial-result.json,sub dir/deeper/notes é.txt|3'
fresh; chk good_regular_tree "$(run good)" "$GOOD"
fresh; as_c5 "rm -rf '$B/evidence' && ln -s '$C/dir' '$B/evidence'"; chk evidence_root_is_link_to_root_only_dir "$(run root_link)" 'False|3|*|0||*'
fresh; as_c5 "ln -s '$C/secret' '$B/evidence/stolen.json'"; chk nested_link_to_root_only_file "$(run nested_link)" 'False|3|*|0||*'
fresh; as_c5 "printf 'own\n' > '$B/own.txt' && ln -s '$B/own.txt' '$B/evidence/sub dir/own-link'"; chk nested_link_to_candidate_file "$(run own_link)" 'False|3|*|0||*'
fresh; as_c5 "ln -s '$C/dir' '$B/evidence/sub dir/dirlink'"; chk nested_dir_link "$(run dir_link)" 'False|3|*|0||*'
fresh; as_c5 "mkfifo '$B/evidence/pipe'"; chk fifo_in_evidence "$(run fifo)" 'False|3|*|0||*'
fresh; if as_c5 "ln '$C/secret' '$B/evidence/hard.json'" 2> /dev/null; then chk hardlink_to_root_only_file "$(run hard)" 'False|3|*|0||*'
       else echo "hardlink_to_root_only_file PASS (not creatable by c5finance: fs.protected_hardlinks=$(cat /proc/sys/fs/protected_hardlinks))"; fi
fresh; as_c5 "rm -f '$B/private-state.json' && ln -s '$C/secret' '$B/private-state.json'"; chk private_state_is_link "$(run state_link)" 'False|0|0|3||*'
fresh; as_c5 "rm -rf '$B/evidence'"; chk evidence_absent "$(run absent)" 'True|0|0|0||3'
fresh; rm -f "$B/private-state.json"; chk no_private_state "$(run no_state)" 'True|0|0|0|financial-result.json,sub dir/deeper/notes é.txt|1'
# Part 2: hostile streams straight into the runner's import (never produced by the export, which refuses them)
python3 - "$ws/tests/release/evidence_import.py" "$T" <<'PY' || ok=
import io, subprocess, sys, tarfile
tool, T = sys.argv[1], sys.argv[2]
def stream(members):
    b = io.BytesIO()
    with tarfile.open(fileobj=b, mode='w', format=tarfile.PAX_FORMAT) as tf:
        for name, kind in members:
            i = tarfile.TarInfo(name)
            if kind == 'dir': i.type = tarfile.DIRTYPE; tf.addfile(i)
            elif kind == 'sym': i.type = tarfile.SYMTYPE; i.linkname = '/var/tmp/monjez-import-canary/secret'; tf.addfile(i)
            elif kind == 'hard': i.type = tarfile.LNKTYPE; i.linkname = 'a.json'; tf.addfile(i)
            else: data = b'{}\n'; i.size = len(data); tf.addfile(i, io.BytesIO(data))
    return b.getvalue()
cases = {'absolute_name': [('/etc/x.json', 'file')], 'parent_traversal': [('../x.json', 'file')],
         'dot_component': [('a/./b.json', 'file')], 'symlink_member': [('l', 'sym')], 'hardlink_member': [('a.json', 'file'), ('h', 'hard')],
         'duplicate_name': [('a.json', 'file'), ('a.json', 'file')], 'orphan_file': [('nodir/a.json', 'file')],
         'file_then_dir_same_name': [('a', 'file'), ('a', 'dir')]}
bad = 0
for n, members in cases.items():
    dest = f'{T}/imp_{n}'
    r = subprocess.run([sys.executable, '-I', tool, 'import', dest], input=stream(members), capture_output=True)
    good = r.returncode == 4
    print(f"import_rejects_{n} {'PASS' if good else 'FAIL'} (exit={r.returncode})"); bad += not good
r = subprocess.run([sys.executable, '-I', tool, 'import', f'{T}/imp_good'], input=stream([('d', 'dir'), ('d/a.json', 'file')]), capture_output=True)
print(f"import_accepts_plain_tree {'PASS' if r.returncode == 0 else 'FAIL'} (exit={r.returncode})"); bad += r.returncode != 0
import os; os.mkdir(f'{T}/imp_exists')
r = subprocess.run([sys.executable, '-I', tool, 'import', f'{T}/imp_exists'], input=stream([('a.json', 'file')]), capture_output=True)
print(f"import_refuses_existing_destination {'PASS' if r.returncode != 0 else 'FAIL'} (exit={r.returncode})"); bad += r.returncode == 0
sys.exit(1 if bad else 0)
PY
rm -rf "${B:?}"
[ "$ok" ]
