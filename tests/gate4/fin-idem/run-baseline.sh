#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PGHOST:-}" ]]; then
  echo "FIN_IDEM_G4_HARNESS_FAIL: PGHOST not set" >&2
  exit 1
fi

read -r TID OWNER < <(psql -At -F' ' -c \
  "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;")

if [[ -z "${TID:-}" || -z "${OWNER:-}" ]]; then
  echo "FIN_IDEM_G4_HARNESS_FAIL: no tenant/owner fixture" >&2
  exit 1
fi

psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v uid="'$OWNER'" \
  -f "$HERE/baseline_duplicate.sql" \
  2>&1 | tee /tmp/fin-idem-g4-baseline.log

grep -Fq "FIN_IDEM_G4_E1_EXPECTED_RED" /tmp/fin-idem-g4-baseline.log || {
  echo "FIN_IDEM_G4_HARNESS_FAIL: baseline duplicate sentinel missing" >&2
  exit 1
}

echo "FIN_IDEM_G4_BASELINE_EXPECTED_RED_CONFIRMED"
