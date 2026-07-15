#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PGHOST:-}" ]]; then
  echo "PGHOST not set" >&2
  exit 1
fi

read -r TID OWNER < <(psql -At -F' ' -c \
  "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;")
STAFF_A="$(psql -Atc "SELECT id::text FROM auth.users WHERE email='employee.a@mongezz.test' LIMIT 1;")"
STAFF_B="$(psql -Atc "SELECT id::text FROM auth.users WHERE email='employee.b@mongezz.test' LIMIT 1;")"

if [[ -z "${TID:-}" || -z "${OWNER:-}" || -z "${STAFF_A:-}" || -z "${STAFF_B:-}" ]]; then
  echo "Missing employee-account test fixtures" >&2
  exit 1
fi

psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v owner="'$OWNER'" \
  -v staff_a="'$STAFF_A'" \
  -v staff_b="'$STAFF_B'" \
  -f "$HERE/rules.sql"
