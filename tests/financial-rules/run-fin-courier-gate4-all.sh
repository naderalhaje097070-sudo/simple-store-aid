#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST required}"
: "${PGPORT:?PGPORT required}"
: "${PGUSER:?PGUSER required}"
: "${PGDATABASE:?PGDATABASE required}"
: "${GATE4_UID:?GATE4_UID required}"
: "${GATE4_TID:?GATE4_TID required}"

EVIDENCE_DIR="${GATE4_EVIDENCE_DIR:-/tmp/fin-courier-gate4-backend}"
mkdir -p "$EVIDENCE_DIR"

PSQL=(psql -v ON_ERROR_STOP=1)
UID_ARG="'${GATE4_UID}'"
TID_ARG="'${GATE4_TID}'"

expect_red() {
  local name="$1"
  local sentinel="$2"
  shift 2
  local log="$EVIDENCE_DIR/${name}.log"

  set +e
  "$@" >"$log" 2>&1
  local rc=$?
  set -e
  cat "$log"

  if [[ $rc -eq 0 ]]; then
    echo "Gate 4 baseline mismatch: ${name} unexpectedly passed before implementation" >&2
    exit 1
  fi
  if ! grep -q "$sentinel" "$log"; then
    echo "Gate 4 ${name} failed for an unexpected harness/runtime reason" >&2
    exit 1
  fi
  echo "EXPECTED-RED OK: ${name} (${sentinel})"
}

require_green() {
  local name="$1"
  local sentinel="$2"
  shift 2
  local log="$EVIDENCE_DIR/${name}.log"

  set +e
  "$@" >"$log" 2>&1
  local rc=$?
  set -e
  cat "$log"

  if [[ $rc -ne 0 ]]; then
    echo "Gate 4 regression baseline failed: ${name}" >&2
    exit "$rc"
  fi
  if ! grep -q "$sentinel" "$log"; then
    echo "Gate 4 ${name} returned success without sentinel ${sentinel}" >&2
    exit 1
  fi
  echo "GREEN OK: ${name} (${sentinel})"
}

echo "============================================================"
echo "FIN-COURIER-001 Gate 4 consolidated backend safety net"
echo "tenant=${GATE4_TID}"
echo "============================================================"

# A + existing regression: unchanged T1–T15 must be GREEN while the first PR-A
# target remains RED for the named, approved missing contracts.
require_green \
  "01-core-regression-and-pr-a-red" \
  "PASS: existing T1-T15 are green and the new FIN-COURIER target is RED" \
  env GATE4_EXPECT=red GATE4_TENANT_ID="$GATE4_TID" GATE4_USER_ID="$GATE4_UID" \
  bash tests/financial-rules/run-fin-courier-gate4.sh

expect_red \
  "02-check-matrix" \
  "GATE4_CK_EXPECTED_RED" \
  "${PSQL[@]}" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-constraints.sql

expect_red \
  "03-create-aggregates" \
  "GATE4_CREATE_AGG_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-create-aggregates.sql

expect_red \
  "04-historical-preflight" \
  "GATE4_PREFLIGHT_EXPECTED_RED" \
  "${PSQL[@]}" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-preflight.sql

expect_red \
  "05-transition-matrix" \
  "GATE4_TRANSITION_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-transitions.sql

expect_red \
  "06-forced-atomicity" \
  "GATE4_ATOMICITY_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-atomicity.sql

expect_red \
  "07-retry-baseline" \
  "GATE4_RETRY_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-retry-baseline.sql

expect_red \
  "08-backward-compatibility" \
  "GATE4_COMPAT_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-compatibility.sql

expect_red \
  "09-reporting" \
  "GATE4_REPORT_EXPECTED_RED" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-reporting.sql

# Existing-safe baselines run BEFORE the concurrency shell. Every SQL suite above
# rolls back its transaction; the concurrency shell intentionally uses multiple
# sessions and may persist disposable rows once PR-A exists. Keeping close_day/
# snapshot baselines before it prevents future fixture contamination.
require_green \
  "10-returned-order-baseline" \
  "GATE4_RETURN_GREEN" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-return-baseline.sql

require_green \
  "11-f2-readmodel-snapshot" \
  "GATE4_F2_GREEN" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-readmodel-snapshot.sql

require_green \
  "12-rollback-endpoint" \
  "GATE4_ROLLBACK_GREEN" \
  "${PSQL[@]}" -v uid="$UID_ARG" -v tid="$TID_ARG" -f tests/financial-rules/fin-courier-gate4-rollback-contract.sql

# Concurrency runs last because it spans independent DB sessions and therefore
# cannot be wrapped by the single-session BEGIN/ROLLBACK pattern used above.
expect_red \
  "13-concurrency" \
  "GATE4_CONCURRENCY_EXPECTED_RED" \
  env GATE4_UID="$GATE4_UID" GATE4_TID="$GATE4_TID" \
  bash tests/financial-rules/fin-courier-gate4-concurrency.sh

echo "============================================================"
echo "GATE4_BACKEND_EVIDENCE_GREEN: all expected-RED and true-GREEN contracts behaved as classified"
echo "============================================================"
