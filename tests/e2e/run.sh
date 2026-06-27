#!/usr/bin/env bash
# Mongezz V2 — End-to-end financial flow runner.
# Requires:
#   - Dev server on http://localhost:8080
#   - LOVABLE_BROWSER_* and PG* env vars present
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

if [[ -z "${PGHOST:-}" ]]; then
  echo "PGHOST not set — run inside Lovable sandbox." >&2; exit 1
fi
if [[ "${LOVABLE_BROWSER_AUTH_STATUS:-}" != "injected" ]]; then
  echo "LOVABLE_BROWSER_AUTH_STATUS=${LOVABLE_BROWSER_AUTH_STATUS:-unset}; sign in via preview first." >&2; exit 1
fi
if ! curl -sf -o /dev/null http://localhost:8080/; then
  echo "Dev server not reachable at http://localhost:8080" >&2; exit 1
fi

python "$HERE/sale-dashboard-close.py"
