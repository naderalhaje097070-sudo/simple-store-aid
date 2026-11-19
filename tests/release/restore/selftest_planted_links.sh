#!/bin/bash
# Defensive self-test for the restore step's file isolation (review fix #98, Strix HIGH on da33d39). LOCAL and
# synthetic only, with run_step_local.sh. Every path the pre-fix step touched as root inside the c5finance tree is
# pre-planted BY c5finance as a symlink to a root-owned canary, and c5finance's repository copy of the restore SQL is
# forged; the step must pass with real values and leave every canary, link and forgery exactly as planted.
#   plant  RT          run as PRE_STEP_HOOK (root): canary + c5finance plants; writes the baseline to RT/plants
#   verify RT LOG      after the step: canaries unchanged, links unchanged, no root-owned path in /tmp/monjez-c5sale,
#                      no leftover /tmp/monjez-restore.*, canary secret nowhere under RT, real fingerprint lines
set -euo pipefail
mode=$1; RT=$2; B=/tmp/monjez-c5sale; C=/var/tmp/monjez-restore-canary
links=("$B/restore-private" "$B/restore-status.json" "$B/restore-private-state.json"
       "$B/evidence/restore-guard" "$B/evidence/restore-n1-guard" "$B/evidence/restore-suite" "$B/evidence/restore-check.json")
snap() { stat -c '%n %U %G %a %Y %s' "$C" "$C/secret" "$C/dir" "$C/dir/keep"; sha256sum "$C/secret" "$C/dir/keep"; }
if [ "$mode" = plant ]; then
  rm -rf "${C:?}"; install -d -m 700 -o root -g root "$C" "$C/dir"
  printf 'CANARY_SECRET_%s\n' "$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')" > "$C/secret"; chmod 600 "$C/secret"
  echo keep > "$C/dir/keep"; chmod 600 "$C/dir/keep"
  sudo -u c5finance ln -s "$C/dir" "$B/restore-private"
  sudo -u c5finance ln -s "$C/secret" "$B/restore-status.json"
  sudo -u c5finance ln -s "$C/secret" "$B/restore-private-state.json"
  sudo -u c5finance ln -s "$C/dir" "$B/evidence/restore-guard"
  sudo -u c5finance ln -s "$C/dir" "$B/evidence/restore-n1-guard"
  sudo -u c5finance ln -s "$C/dir" "$B/evidence/restore-suite"
  sudo -u c5finance ln -s "$C/secret" "$B/evidence/restore-check.json"
  # c5finance's own repository copy of the restore SQL: a forged fingerprint and a link to the canary secret
  sudo -u c5finance sh -c "printf 'select 1;\n' > '$B/repo/tests/release/restore/fingerprint.sql'"
  sudo -u c5finance sh -c "rm -f '$B/repo/tests/release/restore/data_hash.sql' && ln -s '$C/secret' '$B/repo/tests/release/restore/data_hash.sql'"
  mkdir -p "$RT/plants"; snap > "$RT/plants/canary.before"
  for l in "${links[@]}"; do printf '%s -> %s\n' "$l" "$(readlink "$l")"; done > "$RT/plants/links.before"
  sha256sum "$B/repo/tests/release/restore/fingerprint.sql" > "$RT/plants/forged.before"
  readlink "$B/repo/tests/release/restore/data_hash.sql" >> "$RT/plants/forged.before"
  echo "PLANTED ${#links[@]} links, 2 forged repository SQL files, canary $C"
  exit 0
fi
LOG=$3; ok=1; r() { if [ "$2" = 1 ]; then echo "$1 PASS"; else echo "$1 FAIL"; ok=; fi; }
snap > "$RT/plants/canary.after"
for l in "${links[@]}"; do printf '%s -> %s\n' "$l" "$(readlink "$l" || echo MISSING)"; done > "$RT/plants/links.after"
{ sha256sum "$B/repo/tests/release/restore/fingerprint.sql"; readlink "$B/repo/tests/release/restore/data_hash.sql"; } > "$RT/plants/forged.after"
secret=$(cat "$C/secret")
r canary_owner_mode_mtime_content_unchanged "$(cmp -s "$RT/plants/canary.before" "$RT/plants/canary.after" && echo 1)"
r planted_links_left_as_planted "$(cmp -s "$RT/plants/links.before" "$RT/plants/links.after" && echo 1)"
r forged_repository_sql_left_as_planted "$(cmp -s "$RT/plants/forged.before" "$RT/plants/forged.after" && echo 1)"
r no_root_owned_path_in_c5finance_tree "$([ -z "$(find "$B" -xdev -user root -print -quit)" ] && echo 1)"
r no_leftover_private_layout "$(! compgen -G '/tmp/monjez-restore.*' > /dev/null && echo 1)"
r canary_secret_absent_from_runner_temp "$(! grep -rqF -- "$secret" "$RT" --exclude-dir=plants 2> /dev/null && echo 1)"
r step_passed_with_real_fingerprint "$(grep -q '^RELEASE_RESTORE_CHECK {"failed": \[\]' "$LOG" && grep -q '"fingerprint_lines": 344' "$LOG" && echo 1)"
r published_exactly_named_files "$(grep -q '"published": \["restore-check.json", "restore-guard.json", "restore-n1-guard.json", "restore-suite-controls.json"\]' "$LOG" && echo 1)"
rm -rf "${C:?}"
[ "$ok" ]
