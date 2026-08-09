#!/usr/bin/env bash
# Mongezz V2 — destructive end-to-end financial flow runner.
#
# This runner is intentionally restricted to the local/CI isolated Supabase
# stack. The Python preflight below MUST succeed before auth/session checks,
# dev-server probing, or execution of the write-capable flow.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

python3 "$HERE/sale-dashboard-close.py" --preflight-only

if [[ "${LOVABLE_BROWSER_AUTH_STATUS:-}" != "injected" ]]; then
  echo "LOVABLE_BROWSER_AUTH_STATUS=${LOVABLE_BROWSER_AUTH_STATUS:-unset}; provide an injected session for the isolated dev app." >&2
  exit 1
fi

if ! curl -sf -o /dev/null http://localhost:8080/; then
  echo "Isolated dev server not reachable at http://localhost:8080" >&2
  exit 1
fi

python3 "$HERE/sale-dashboard-close.py"
