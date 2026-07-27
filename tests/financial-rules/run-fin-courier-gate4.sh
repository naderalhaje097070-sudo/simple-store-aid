#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST required}"
: "${PGPORT:?PGPORT required}"
: "${PGUSER:?PGUSER required}"
: "${PGDATABASE:?PGDATABASE required}"

MODE="${GATE4_EXPECT:-red}"
if [[ "$MODE" != "red" && "$MODE" != "green" ]]; then
  echo "GATE4_EXPECT must be red or green" >&2
  exit 2
fi

TENANT_ID="${GATE4_TENANT_ID:-$(psql -Atq -c "select id from public.tenants order by created_at limit 1")}" 
USER_ID="${GATE4_USER_ID:-$(psql -Atq -c "select owner_user_id from public.tenants where id='${TENANT_ID}' limit 1")}" 

if [[ -z "$TENANT_ID" || -z "$USER_ID" ]]; then
  echo "Gate 4 runner requires a seeded tenant and owner" >&2
  exit 2
fi

echo "== Gate 4 baseline: existing T1-T15 must remain green =="
psql -v ON_ERROR_STOP=1 \
  -v tid="'${TENANT_ID}'" \
  -v uid="'${USER_ID}'" \
  -f tests/financial-rules/rules.sql

echo "== Gate 4 target: FIN-COURIER PR-A contract =="
set +e
psql -v ON_ERROR_STOP=1 \
  -v tid="'${TENANT_ID}'" \
  -v uid="'${USER_ID}'" \
  -f tests/financial-rules/fin-courier-gate4-pr-a.sql \
  > /tmp/fin-courier-gate4-pr-a.log 2>&1
RC=$?
set -e
cat /tmp/fin-courier-gate4-pr-a.log

if [[ "$MODE" == "red" ]]; then
  if [[ $RC -eq 0 ]]; then
    echo "Gate 4 baseline mismatch: target contract unexpectedly passed before implementation" >&2
    exit 1
  fi
  if ! grep -q "GATE4_EXPECTED_RED" /tmp/fin-courier-gate4-pr-a.log; then
    echo "Gate 4 probe failed for an unexpected harness/runtime reason" >&2
    exit 1
  fi
  echo "PASS: existing T1-T15 are green and the new FIN-COURIER target is RED for recorded contract gaps"
  exit 0
fi

if [[ $RC -ne 0 ]]; then
  echo "Gate 4 target remains red after implementation" >&2
  exit "$RC"
fi
if ! grep -q "GATE4_GREEN" /tmp/fin-courier-gate4-pr-a.log; then
  echo "Gate 4 target returned success without the GREEN sentinel" >&2
  exit 1
fi

echo "PASS: existing T1-T15 and FIN-COURIER Gate 4 PR-A target are green"
