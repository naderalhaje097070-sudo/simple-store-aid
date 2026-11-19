#!/bin/bash
# Local only. Tests for the C6 review fixes (2026-11-19) on a fresh production replica.
# usage: review_fixes.sh <main-worktree> <repo-root> <supabase-cli> <out-dir>
set -uo pipefail
W=$1; R=$2; export SB=$3; O=$4; mkdir -p "$O"
A=$R/docs/reviews/c6-apply; H=$R/tests/c6-upgrade
C=supabase_db_dahzkekdirrngnkcxinv
sql() { docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -At -q "$@"; }
fp() { sql < "$A/catalog_fingerprint.sql" | grep -E '\|on\|[0-9]+$' | python3 -c "import sys,hashlib;t=sys.stdin.read().rsplit('|',2);print(hashlib.md5(t[0].encode()).hexdigest(), 'ledger='+t[2].strip())"; }
ledger() { sql -c "select count(*) from supabase_migrations.schema_migrations"; }
expect_fail() { # label, pattern, file
  local out; out=$(sql < "$3" 2>&1); if [ $? -ne 0 ] && grep -q "$2" <<<"$out"; then echo "PASS $1: $(grep -o "$2[^\"]*" <<<"$out" | head -1 | cut -c1-90)"; else echo "FAIL $1: $(tail -1 <<<"$out")"; fi; }
bat() { python3 "$H/harness.py" "$C" battery > "$O/bat_$1.json"; }
cmpbat() { python3 - "$O/bat_$1.json" "$R/docs/reviews/c6-evidence/$2" "$1" "$2" <<'EOF'
import json,sys
a,b=json.load(open(sys.argv[1])),json.load(open(sys.argv[2]))
d=[k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]
print(('PASS' if not d else 'FAIL'), f'battery {sys.argv[3]} == recorded {sys.argv[4]}', '' if not d else d[:5])
EOF
}
fresh() { bash "$H/build_replica.sh" "$W" "$R" >/dev/null && python3 "$H/harness.py" "$C" seed >/dev/null && echo "fresh replica + seed: ledger $(ledger)"; }

echo "== T1 preconditions on a fresh replica (C0)"
fresh
expect_fail "C3 before C1/C2 refused" LEDGER_STATE_MISMATCH "$A/C3.sql"
expect_fail "bundle before C1 refused" LEDGER_STATE_MISMATCH "$A/BUNDLE_C2_C10_UNBLOCK.sql"
echo "ledger after refusals: $(ledger) (expect 52)"
python3 "$H/fractional_probe.py" "$C" C0 > "$O/frac_C0.json"
sql < "$A/C1.sql" && echo "C1 applied: ledger $(ledger) (expect 53)"
expect_fail "C1 rerun refused" "LEDGER_STATE_MISMATCH" "$A/C1.sql"
fp > "$O/fp_C1.txt"; bat C1; cmpbat C1 bat_C1.json
python3 "$H/fractional_probe.py" "$C" C1 > "$O/frac_C1.json"
expect_fail "revert at C1 refused" REVERT_REFUSED "$A/EMERGENCY_unblock_legacy_frontend_revert.sql"

echo "== T2 real failure inside the bundle at C3 (an open transaction holds products 9 s)"
docker exec "$C" psql -U postgres -q -c "begin; select 1 from public.products limit 1 for update; select pg_sleep(9); rollback;" >/dev/null 2>&1 &
sleep 1
expect_fail "bundle fails on C3 lock" "lock timeout" "$A/BUNDLE_C2_C10_UNBLOCK.sql"
wait
[ -s "$O/fp_C1.txt" ] && [ "$(fp)" = "$(cat "$O/fp_C1.txt")" ] && echo "PASS catalog == C1 exactly, $(fp | cut -d' ' -f2)" || echo "FAIL catalog differs from C1"
bat after_c3_fail; cmpbat after_c3_fail bat_C1.json
python3 "$H/fractional_probe.py" "$C" after_c3_fail > "$O/frac_after_c3_fail.json"

echo "== T3 injected failure inside the bundle after C4, before C5 (stall before C5)"
awk '{print} /^-- stage B.4$/{f=1} f&&/^\$stage\$;$/{print "DO $x$ BEGIN RAISE EXCEPTION '"'"'INJECTED_BEFORE_C5'"'"'; END $x$;"; f=0}' "$A/BUNDLE_C2_C10_UNBLOCK.sql" > "$O/bundle_inject_before_c5.sql"
grep -c INJECTED_BEFORE_C5 "$O/bundle_inject_before_c5.sql" | sed 's/^/injection points: /'
expect_fail "bundle stops before C5" INJECTED_BEFORE_C5 "$O/bundle_inject_before_c5.sql"
[ -s "$O/fp_C1.txt" ] && [ "$(fp)" = "$(cat "$O/fp_C1.txt")" ] && echo "PASS catalog == C1 exactly, $(fp | cut -d' ' -f2)" || echo "FAIL catalog differs from C1"
bat after_c5_stall; cmpbat after_c5_stall bat_C1.json

echo "== T4 the old (pre-fix) revert, if run while stuck after C2: shows the defect"
git -C "$R" show HEAD:docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql > "$O/old_revert.sql"
docker exec -i "$C" psql -U postgres -q -At <<EOF 2>&1 | grep -v '^$' | tail -2
begin;
$(cat "$A/C2.sql")
$(sed 's/^begin;$//; s/^commit;$//' "$O/old_revert.sql")
select 'old revert at C2: legacy collect EXECUTE=' || has_function_privilege('authenticated','public.collect_order_debt(uuid,numeric,payment_method)','EXECUTE')
       || ', new collect exists=' || (to_regprocedure('public.collect_order_debt_idempotent(uuid,uuid,numeric,payment_method)') is not null);
rollback;
EOF
docker exec -i "$C" psql -U postgres -q <<EOF 2>&1 | grep -E 'REVERT_REFUSED|ERROR' | head -1 | sed 's/^/new revert at C2: /'
begin;
$(cat "$A/C2.sql")
$(cat "$A/EMERGENCY_unblock_legacy_frontend_revert.sql")
rollback;
EOF
echo "ledger after T4 (rolled back): $(ledger) (expect 53)"

echo "== T5 full bundle with unblock"
sql < "$A/BUNDLE_C2_C10_UNBLOCK.sql" && echo "bundle committed: ledger $(ledger) (expect 62)"
[ "$(fp)" != "$(cat "$O/fp_C1.txt")" ] && echo "PASS sanity: catalog after bundle differs from C1" || echo "FAIL sanity: fingerprint did not change"
bat bundle_unblocked; cmpbat bundle_unblocked bat_unblocked.json
python3 "$H/fractional_probe.py" "$C" C10_unblocked > "$O/frac_C10_unblocked.json"
expect_fail "bundle rerun refused" LEDGER_STATE_MISMATCH "$A/BUNDLE_C2_C10_UNBLOCK.sql"
sql < "$A/EMERGENCY_unblock_legacy_frontend_revert.sql" && echo "revert at C10 applied"
bat C10_reverted; cmpbat C10_reverted bat_C10.json
python3 "$H/fractional_probe.py" "$C" C10_reverted > "$O/frac_C10_reverted.json"
for f in "$O"/frac_*.json; do python3 - "$f" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
row=[]
for k,v in d.items():
    if not isinstance(v,dict): continue
    o=v['outcome']
    if o=='OK': o+=f"(inv {v['invoice_qty']}, stock -{v['stock_decrement']:g}, {'MATCH' if v['decrement_equals_invoice'] else 'MISMATCH'}, {v['stock_type']})"
    row.append(f"{k}: {o}")
print(d['state'], '| ' + ' ; '.join(row))
EOF
done
