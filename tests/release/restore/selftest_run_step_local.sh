#!/bin/bash
# Self-test for run_step_local.sh exit status (review fix #98, Graphify P2). Synthetic only: a throwaway git repository
# whose release-finance.yml carries a stub restore step; no database and no network. Like the helper itself it runs as
# root and recreates /tmp/monjez-c5sale, so do not run it while a real local restore run is in progress.
# usage: selftest_run_step_local.sh [HELPER]   (default: run_step_local.sh next to this file)
set -euo pipefail
HELPER=${1:-$(cd "$(dirname "$0")" && pwd)/run_step_local.sh}
T=$(mktemp -d); trap 'rm -rf "$T" /tmp/monjez-c5sale' EXIT
mk() { # $1 = repo dir, $2 = step body or "" for a workflow without the restore step
  git init -q "$1"; mkdir -p "$1/.github/workflows"
  if [ -n "$2" ]; then
    printf 'jobs:\n  suite:\n    steps:\n      - name: Logical backup and restore of the candidate database (stub)\n        run: |\n          %s\n' "$2"
  else
    printf 'jobs:\n  suite:\n    steps:\n      - name: Something else\n        run: echo other\n'
  fi > "$1/.github/workflows/release-finance.yml"
  git -C "$1" add -A; git -C "$1" -c user.name=t -c user.email=t@example.invalid commit -q -m stub
  git -C "$1" update-ref refs/remotes/origin/main HEAD
}
mk "$T/fail7" 'echo stub-step-ran; exit 7'
mk "$T/ok" 'echo stub-step-ran; exit 0'
mk "$T/nostep" ''
mk "$T/nomain" 'echo stub-step-ran; exit 0'; git -C "$T/nomain" update-ref -d refs/remotes/origin/main
mkdir -p "$T/src"
run() { # $1 case, $2 repo, $3 commit; prints "rc|ran|step_exit_line"
  local out rc=0; out=$("$HELPER" "$2" "$3" "$T/src" "$T/rt_$1" 2>&1) || rc=$?
  echo "$rc|$(grep -c '^stub-step-ran$' <<<"$out" || true)|$(grep '^STEP_EXIT=' <<<"$out" || true)"
}
ok=1; chk() { if [ "$2" = "$3" ]; then echo "$1 PASS ($2)"; else echo "$1 FAIL (got $2, want $3)"; ok=; fi; }
chk step_failure_reaches_caller           "$(run fail7  "$T/fail7"  HEAD)"            '7|1|STEP_EXIT=7'
chk step_success_exits_zero               "$(run ok     "$T/ok"     HEAD)"            '0|1|STEP_EXIT=0'
chk bad_commit_fails_before_step          "$(run badsha "$T/ok"     deadbeefdeadbeef)" '2|0|'
chk missing_restore_step_fails_before_run "$(run nostep "$T/nostep" HEAD | sed 's/^[1-9][0-9]*|/NZ|/')" 'NZ|0|'
chk repo_setup_failure_fails_before_step  "$(run nomain "$T/nomain" HEAD | sed 's/^[1-9][0-9]*|/NZ|/')" 'NZ|0|'
[ "$ok" ]
