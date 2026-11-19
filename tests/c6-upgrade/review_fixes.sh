#!/bin/bash
# Local only. Acceptance gate for the C6 apply files (review fixes 2026-11-19 and 2026-11-19b).
# Exit status: 0 only if every check passes; any FAIL or infrastructure error exits non-zero.
# usage: review_fixes.sh <main-worktree> <repo-root> <supabase-cli> <out-dir>
set -uo pipefail
W=$1; R=$2; export SB=$3; O=$4; rm -rf "$O"; mkdir -p "$O"
P=$R/docs/reviews/c6-apply; H=$R/tests/c6-upgrade; A=$O/apply_test; C=supabase_db_dahzkekdirrngnkcxinv
OLD_REVERT_REF=e32f92b   # the pre-fix revert, pinned (HEAD now holds the fixed one)
FAILS=0
pass() { echo "PASS $*"; }
fail() { echo "FAIL $*"; FAILS=$((FAILS + 1)); }
die() { echo "ABORT $*"; exit 2; }
check() { if eval "$2"; then pass "$1"; else fail "$1"; fi; }
sql() { docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -At -q "$@"; }
fp() { local o; o=$(sql < "$P/catalog_fingerprint.sql" | grep -E '\|on\|[0-9]+$') || return 1
       python3 -c "import sys,hashlib;t=sys.argv[1].rsplit('|',2);print(hashlib.md5(t[0].encode()).hexdigest(),'ledger='+t[2])" "$o"; }
ledger() { sql -c "select count(*) from supabase_migrations.schema_migrations"; }
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
# probe assertion: mode "nofraction-paths" = no sale path may accept a fraction on integer stock except the
# pre-existing legacy path (C0 defect, documented); mode "match" = every accepted sale's decrement == invoice
probe_assert() { python3 - "$O/frac_$1.json" "$2" <<'EOF' && pass "fractional $1: $2" || fail "fractional $1: $2"
import json,sys
d=json.load(open(sys.argv[1])); mode=sys.argv[2]; bad=[]
for k,v in d.items():
    if not isinstance(v,dict) or v['outcome']!='OK': continue
    if mode=='match' and not v['decrement_equals_invoice']: bad.append(k)
    if mode=='nofraction-paths' and not k.startswith('legacy'): bad.append(k+' (new path open on integer stock)')
print('   ', '; '.join(f"{k}: {v['outcome']}"+(f" inv {v['invoice_qty']} stock -{v['stock_decrement']:g} {v['stock_type']}" if v['outcome']=='OK' else '') for k,v in d.items() if isinstance(v,dict)))
if bad: print('   offending:', bad)
sys.exit(1 if bad else 0)
EOF
}

echo "== S0 build: fresh replica with ledger content, test apply files"
bash "$H/build_replica.sh" "$W" "$R" >/dev/null || die "replica"
python3 "$H/make_replica_ledger.py" "$R" "$O/replica_ledger_content.sql" "$O/expected_test.txt" || die "ledger content"
sql < "$O/replica_ledger_content.sql" >/dev/null || die "ledger content apply"
python3 "$H/harness.py" "$C" seed >/dev/null || die "seed"
bash "$P/build_apply_files.sh" "$R" "$O/expected_test.txt" "$A" >/dev/null || die "test build"
d=$(for f in C1.sql C5.sql C10.sql BUNDLE_C1_C10.sql BUNDLE_C1_C10_UNBLOCK.sql EMERGENCY_unblock_legacy_frontend_revert.sql; do diff "$P/$f" "$A/$f"; done | grep -E '^[<>]' | grep -vc 'LEDGER_CONTENT_MISMATCH')
check "test files differ from production files only in content-guard constants" '[ "$d" = 0 ]'
fp > "$O/fp_C0.txt" || die fp; check "C0 fingerprint captured" '[ -s "$O/fp_C0.txt" ]'
bat C0; cmpbat C0 bat_C0.json
probe C0; probe_assert C0 nofraction-paths

echo "== S1 guards (production files must refuse this replica; test files check order and content)"
expect_fail "production C1.sql refuses a database whose ledger content differs" LEDGER_CONTENT_MISMATCH "$P/C1.sql"
expect_fail "production bundle refuses it too" LEDGER_CONTENT_MISMATCH "$P/BUNDLE_C1_C10_UNBLOCK.sql"
expect_fail "C3 before C1/C2 refused" LEDGER_STATE_MISMATCH "$A/C3.sql"
sql -c "update supabase_migrations.schema_migrations set statements = array['tampered'] where version = '20260626142438'" || die tamper
expect_fail "same versions, one ledger row's content changed: refused" LEDGER_CONTENT_MISMATCH "$A/BUNDLE_C1_C10_UNBLOCK.sql"
sql < "$O/replica_ledger_content.sql" >/dev/null || die restore-ledger
sql -c "insert into supabase_migrations.schema_migrations(version) values ('29990101000000')" || die extra
expect_fail "one extra ledger version: refused" LEDGER_STATE_MISMATCH "$A/BUNDLE_C1_C10_UNBLOCK.sql"
sql -c "delete from supabase_migrations.schema_migrations where version = '29990101000000'" || die extra-del
check "ledger back to 52 and catalog == C0" '[ "$(ledger)" = 52 ] && [ "$(fp)" = "$(cat "$O/fp_C0.txt")" ]'
expect_fail "revert at C0 refused" REVERT_REFUSED "$A/EMERGENCY_unblock_legacy_frontend_revert.sql"

echo "== S2 real failure inside the bundle at C3 (an open transaction holds products 9 s)"
docker exec "$C" psql -U postgres -q -c "begin; select 1 from public.products limit 1 for update; select pg_sleep(9); rollback;" >/dev/null 2>&1 &
sleep 1
expect_fail "bundle fails on the C3 lock" "lock timeout" "$A/BUNDLE_C1_C10_UNBLOCK.sql"
wait
check "catalog == C0 exactly after the C3 failure (C1 rolled back too)" '[ "$(fp)" = "$(cat "$O/fp_C0.txt")" ]'
bat after_c3_fail; cmpbat after_c3_fail bat_C0.json
probe after_c3_fail; probe_assert after_c3_fail nofraction-paths

for point in B.1:C2 B.4:C5; do
  after=${point%%:*}; before=${point##*:}
  echo "== S3 injected failure after stage $after (before $before)"
  awk -v s="-- stage $after" '{print} $0==s{f=1} f&&/^\$stage\$;$/{print "DO $x$ BEGIN RAISE EXCEPTION '"'"'INJECTED_BEFORE_'"$before"''"'"'; END $x$;"; f=0}' "$A/BUNDLE_C1_C10_UNBLOCK.sql" > "$O/inject_$before.sql"
  check "one injection point before $before" '[ "$(grep -c INJECTED_BEFORE_'"$before"' "$O/inject_'"$before"'.sql")" = 1 ]'
  expect_fail "bundle stops before $before" "INJECTED_BEFORE_$before" "$O/inject_$before.sql"
  check "catalog == C0 exactly after the stop before $before" '[ "$(fp)" = "$(cat "$O/fp_C0.txt")" ]'
  bat "stop_before_$before"; cmpbat "stop_before_$before" bat_C0.json
done

echo "== S4 old revert (pinned $OLD_REVERT_REF) if run while stuck after C2, versus the fixed revert"
git -C "$R" show "$OLD_REVERT_REF:docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql" > "$O/old_revert.sql" || die old-revert
check "pinned old revert is the pre-fix file (no REVERT_REFUSED guard)" '! grep -q REVERT_REFUSED "$O/old_revert.sql"'
out=$(docker exec -i "$C" psql -U postgres -At -q -v ON_ERROR_STOP=1 <<EOF 2>&1
begin;
$(cat "$A/C1.sql")
$(cat "$A/C2.sql")
$(sed 's/^begin;$//; s/^commit;$//' "$O/old_revert.sql")
select 'legacy_collect=' || has_function_privilege('authenticated','public.collect_order_debt(uuid,numeric,payment_method)','EXECUTE')
    || ' new_collect_exists=' || (to_regprocedure('public.collect_order_debt_idempotent(uuid,uuid,numeric,payment_method)') is not null);
rollback;
EOF
)
echo "   old revert at C2: $(grep legacy_collect <<<"$out")"
check "old revert at C2 leaves no collection path (defect reproduced)" 'grep -q "legacy_collect=false new_collect_exists=false" <<<"$out"'
out=$(docker exec -i "$C" psql -U postgres -At -q -v ON_ERROR_STOP=1 <<EOF 2>&1
begin;
$(cat "$A/C1.sql")
$(cat "$A/C2.sql")
$(cat "$A/EMERGENCY_unblock_legacy_frontend_revert.sql")
rollback;
EOF
)
check "fixed revert at C2 refused" 'grep -q REVERT_REFUSED <<<"$out"'
check "ledger 52 after the rolled-back S4" '[ "$(ledger)" = 52 ]'

echo "== S5 full bundle with unblock, then revert"
apply_ok "bundle C1..C10 + unblock committed" "$A/BUNDLE_C1_C10_UNBLOCK.sql"
check "ledger 62" '[ "$(ledger)" = 62 ]'
check "sanity: catalog differs from C0" '[ "$(fp)" != "$(cat "$O/fp_C0.txt")" ]'
bat bundle_unblocked; cmpbat bundle_unblocked bat_unblocked.json
probe bundle_unblocked; probe_assert bundle_unblocked match
expect_fail "bundle rerun refused" LEDGER_STATE_MISMATCH "$A/BUNDLE_C1_C10_UNBLOCK.sql"
apply_ok "revert at C10" "$A/EMERGENCY_unblock_legacy_frontend_revert.sql"
bat C10_reverted; cmpbat C10_reverted bat_C10.json
probe C10_reverted; probe_assert C10_reverted match
check "after revert the legacy sale path is denied" 'python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if all(v[\"outcome\"]==\"DENIED\" for k,v in d.items() if k.startswith(\"legacy\")) else 1)" "$O/frac_C10_reverted.json"'

echo "== RESULT: $FAILS failure(s)"
[ "$FAILS" = 0 ] || exit 1
