#!/usr/bin/env bash
# FIN-COURIER-001 — Gate 4 isolated runner.
#
# Runs the existing T1–T15 regression suite first. Only when the baseline stays
# green does it execute the reviewed FIN-COURIER target-contract probes.
# Before PR-A implementation, the second command is expected to exit non-zero
# because the approved v2 RPC contract does not exist yet.
#
# Requires PG* environment variables pointing to an isolated test database.
# Never run this script against production.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PGHOST:-}" ]]; then
  echo "PGHOST not set — Gate 4 requires an isolated database." >&2
  exit 1
fi

read -r TID OWNER < <(psql -At -F' ' -c \
  "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;")

if [[ -z "${TID:-}" || -z "${OWNER:-}" ]]; then
  echo "No tenant with an owner found — seed one isolated tenant before running Gate 4." >&2
  exit 1
fi

echo "→ Gate 4 isolated tenant=$TID owner=$OWNER"
echo "→ Step 1/2: existing financial regression T1–T15 must remain green"
psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v uid="'$OWNER'" \
  -f "$HERE/rules.sql"

echo "→ Step 2/2: FIN-COURIER target contract probes"
psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v uid="'$OWNER'" \
  -f "$HERE/fin-courier-gate4-contract.sql"
