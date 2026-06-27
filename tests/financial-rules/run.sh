#!/usr/bin/env bash
# Mongezz V2 — Financial rules regression runner.
# Auto-picks the first tenant + its owner and runs tests/financial-rules/rules.sql.
# Requires PG* env vars (psql) pointing at the project DB.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PGHOST:-}" ]]; then
  echo "PGHOST not set — cannot reach DB. Run inside the Lovable sandbox or export PG* envs." >&2
  exit 1
fi

read -r TID UID < <(psql -At -F' ' -c \
  "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;")

if [[ -z "${TID:-}" || -z "${UID:-}" ]]; then
  echo "No tenant with an owner found — seed one tenant before running tests." >&2
  exit 1
fi

echo "→ Using tenant=$TID owner=$UID"
psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v uid="'$UID'" \
  -f "$HERE/rules.sql"
