#!/usr/bin/env bash
# Mongezz V2 — financial rules regression runner.
# Restricted to the isolated local Supabase database used by CI.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

block() {
  echo "SEC_ENV_FINANCIAL_RUNNER_BLOCKED: $1" >&2
  exit 2
}

if [[ "${CI_ISOLATED_SUPABASE:-}" != "1" ]]; then
  block "CI_ISOLATED_SUPABASE must equal 1"
fi

case "${PGHOST:-}" in
  127.0.0.1|localhost) ;;
  *) block "PGHOST must be loopback" ;;
esac

case "${PGHOSTADDR:-}" in
  ""|127.0.0.1|::1) ;;
  *) block "PGHOSTADDR must be unset or loopback" ;;
esac

if [[ -n "${PGSERVICE:-}" || -n "${PGSERVICEFILE:-}" ]]; then
  block "PGSERVICE and PGSERVICEFILE are not allowed"
fi

[[ "${PGPORT:-}" == "54322" ]] || block "PGPORT must equal 54322"
[[ "${PGUSER:-}" == "postgres" ]] || block "PGUSER must equal postgres"
[[ "${PGDATABASE:-}" == "postgres" ]] || block "PGDATABASE must equal postgres"

if [[ "${1:-}" == "--preflight-only" ]]; then
  echo "SEC_ENV_FINANCIAL_RUNNER_PREFLIGHT_OK: isolated PostgreSQL target verified"
  exit 0
fi

PSQL_BASE=(
  psql -X
  -h "$PGHOST"
  -p "$PGPORT"
  -U "$PGUSER"
  -d "$PGDATABASE"
)

run_psql() {
  env \
    -u PGHOST \
    -u PGHOSTADDR \
    -u PGPORT \
    -u PGUSER \
    -u PGDATABASE \
    -u PGSERVICE \
    -u PGSERVICEFILE \
    -u PSQLRC \
    "${PSQL_BASE[@]}" "$@"
}

read -r TID OWNER < <(
  run_psql -At -F' ' -c \
    "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;"
)

if [[ -z "${TID:-}" || -z "${OWNER:-}" ]]; then
  echo "No tenant with an owner found — seed one isolated tenant before running tests." >&2
  exit 1
fi

echo "→ Using isolated tenant=$TID owner=$OWNER"
run_psql -v ON_ERROR_STOP=1 \
  -v tid="'$TID'" \
  -v uid="'$OWNER'" \
  -f "$HERE/rules.sql"
