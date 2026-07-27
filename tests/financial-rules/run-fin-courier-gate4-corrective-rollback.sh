#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST required}"
: "${PGPORT:?PGPORT required}"
: "${PGUSER:?PGUSER required}"
: "${PGDATABASE:?PGDATABASE required}"
: "${GATE4_UID:?GATE4_UID required}"
: "${GATE4_TID:?GATE4_TID required}"
: "${GATE4_CORRECTIVE_ROLLBACK_SQL:?path to future forward-only corrective rollback SQL required}"

if [[ ! -f "$GATE4_CORRECTIVE_ROLLBACK_SQL" ]]; then
  echo "Corrective rollback SQL does not exist: $GATE4_CORRECTIVE_ROLLBACK_SQL" >&2
  exit 2
fi

echo "== Apply future forward-only FIN-COURIER corrective rollback =="
psql -v ON_ERROR_STOP=1 -f "$GATE4_CORRECTIVE_ROLLBACK_SQL"

echo "== H1: pre-change T1-T15 baseline must pass again =="
psql -v ON_ERROR_STOP=1 \
  -v tid="'${GATE4_TID}'" \
  -v uid="'${GATE4_UID}'" \
  -f tests/financial-rules/rules.sql

echo "== H1/H2/H3: rollback endpoint must match frozen fingerprint =="
psql -v ON_ERROR_STOP=1 \
  -v tid="'${GATE4_TID}'" \
  -v uid="'${GATE4_UID}'" \
  -f tests/financial-rules/fin-courier-gate4-rollback-contract.sql \
  | tee /tmp/fin-courier-gate4-corrective-rollback.log

grep -q "GATE4_ROLLBACK_GREEN" /tmp/fin-courier-gate4-corrective-rollback.log

echo "GATE4_CORRECTIVE_ROLLBACK_GREEN: corrective migration restored the frozen pre-change contract"
