#!/bin/bash
# Shared functions of the C6 acceptance gate (review fix 2026-11-19c). Sourced by review_fixes.sh and
# gate_selftest.sh. Requires: C (container), P (production apply dir), H (tests dir), R (repo), O (out dir).
FAILS=${FAILS:-0}
pass() { echo "PASS $*"; }
fail() { echo "FAIL $*"; FAILS=$((FAILS + 1)); }
die() { echo "ABORT $*"; exit 2; }
check() { if eval "$2"; then pass "$1"; else fail "$1"; fi; }
sql() { docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -At -q "$@"; }
ledger() { sql -c "select count(*) from supabase_migrations.schema_migrations"; }

# Output directory: must not exist yet. Never deletes anything the operator passed in.
new_outdir() { [ -n "$1" ] || die "no output directory given"; [ -e "$1" ] && die "output directory already exists: $1 (use a new one per run)"; mkdir -p "$1" || die "cannot create $1"; }

# Catalog fingerprint. Prints "md5 ledger=N"; returns non-zero (and prints nothing) if it cannot be captured.
fp() { local o; o=$(sql < "$P/catalog_fingerprint.sql" 2>/dev/null | grep -E '\|on\|[0-9]+$') || return 1
       [ -n "$o" ] || return 1
       python3 -c "import sys,hashlib;t=sys.argv[1].rsplit('|',2);print(hashlib.md5(t[0].encode()).hexdigest(),'ledger='+t[2])" "$o"; }
# fp_capture VAR: capture into VAR, or ABORT. A failed capture can never be compared (equal or different).
fp_capture() { local v; v=$(fp) && [ -n "$v" ] || die "catalog fingerprint could not be captured ($1)"; printf -v "$1" '%s' "$v"; }
fp_same()   { local now; fp_capture now; if [ "$now" = "$2" ]; then pass "$1 ($now)"; else fail "$1: $now != $2"; fi; }
fp_differs() { local now; fp_capture now; if [ "$now" != "$2" ]; then pass "$1"; else fail "$1: unchanged $now"; fi; }

expect_fail() { # label, error pattern, sql file
  local out rc; out=$(sql < "$3" 2>&1); rc=$?
  if [ $rc -ne 0 ] && grep -q "$2" <<<"$out"; then pass "$1 ($(grep -o "$2[A-Z_]*" <<<"$out" | head -1))"; else fail "$1: rc=$rc $(tail -1 <<<"$out")"; fi; }
apply_ok() { local out; out=$(sql < "$2" 2>&1) && pass "$1" || fail "$1: $(tail -1 <<<"$out")"; }
bat() { python3 "$H/harness.py" "$C" battery > "$O/bat_$1.json" || die "battery $1"; }
cmpbat() { python3 - "$O/bat_$1.json" "$R/docs/reviews/c6-evidence/$2" <<'EOF' && pass "battery $1 == recorded $2" || fail "battery $1 != recorded $2"
import json,sys
a,b=json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))
d=[k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
print('   diff:', d[:6]) if d else None
sys.exit(1 if d else 0)
EOF
}
probe() { python3 "$H/fractional_probe.py" "$C" "$1" > "$O/frac_$1.json" || die "probe $1"; }
# probe_assert STATE CLASS: every path x qty cell must equal the pinned expectation (probe_expect.py)
probe_assert() { local out; out=$(python3 "$H/probe_expect.py" "$O/frac_$1.json" "$2" 2>&1)
  if [ $? -eq 0 ]; then pass "fractional $1 == pinned '$2' (9 cells)"; else fail "fractional $1 != pinned '$2'"; echo "$out"; fi; }
