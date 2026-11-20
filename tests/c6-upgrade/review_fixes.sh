#!/bin/bash
# Local only. Acceptance gate for the C6 apply files (review fixes 2026-11-19, -19b, -19c).
# Self-test of the gate's own logic: gate_selftest.sh.
# Exit status: 0 only if every check passes; any FAIL or infrastructure error exits non-zero.
# usage: review_fixes.sh <main-worktree> <repo-root> <supabase-cli> <out-dir>
set -uo pipefail
W=$1; R=$2; export SB=$3; O=$4
P=$R/docs/reviews/c6-apply; H=$R/tests/c6-upgrade; A=$O/apply_test; C=supabase_db_dahzkekdirrngnkcxinv
OLD_REVERT_REF=e32f92b   # the pre-fix revert, pinned (HEAD now holds the fixed one)
# Transport fix (#99): e32f92b is not in the integration branch's history, so the pre-fix revert is carried as a
# LOCAL TEST FIXTURE with its original bytes (git blob 09c3ce91, sha256 below), never as an apply file. It is only
# ever executed inside the BEGIN ... ROLLBACK below, against this script's own local replica container ($C).
OLD_REVERT_FIXTURE=$H/fixtures/old_emergency_revert_e32f92b.sql.fixture
OLD_REVERT_SHA256=f357c099a3a67b0f454ebe02188eabfd62d29fe6ec1d9f10f099a61867ab0aae
. "$H/gate_lib.sh"
new_outdir "$O"           # review fix 2026-11-19c: a new directory per run; nothing is deleted

echo "== S0 build: fresh replica with ledger content, test apply files"
bash "$H/build_replica.sh" "$W" "$R" >/dev/null || die "replica"
python3 "$H/make_replica_ledger.py" "$R" "$O/replica_ledger_content.sql" "$O/expected_test.txt" || die "ledger content"
sql < "$O/replica_ledger_content.sql" >/dev/null || die "ledger content apply"
python3 "$H/harness.py" "$C" seed >/dev/null || die "seed"
bash "$P/build_apply_files.sh" "$R" "$O/expected_test.txt" "$A" >/dev/null || die "test build"
d=$(for f in C1.sql C5.sql C10.sql BUNDLE_C1_C10.sql BUNDLE_C1_C10_UNBLOCK.sql EMERGENCY_unblock_legacy_frontend_revert.sql; do diff "$P/$f" "$A/$f"; done | grep -E '^[<>]' | grep -vc 'LEDGER_CONTENT_MISMATCH')
check "test files differ from production files only in content-guard constants" '[ "$d" = 0 ]'
pre_json() { sql < "$1" | grep '^{' ; }
check "test pre-check on C0: versions_ok and content_ok true" 'pre_json "$A/PRECHECK_target_ledger_read.sql" | grep -q "\"ledger_versions_ok\" : true, \"ledger_content_ok\" : true"'
check "production pre-check on the replica: versions_ok true, content_ok FALSE" 'pre_json "$P/PRECHECK_target_ledger_read.sql" | grep -q "\"ledger_versions_ok\" : true, \"ledger_content_ok\" : false"'
fp_capture FP0; echo "$FP0" > "$O/fp_C0.txt"; pass "C0 fingerprint captured ($FP0)"
bat C0; cmpbat C0 bat_C0.json
probe C0; probe_assert C0 pre

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
check "ledger back to 52" '[ "$(ledger)" = 52 ]'
fp_same "catalog == C0 after the guard tests" "$FP0"
expect_fail "revert at C0 refused" REVERT_REFUSED "$A/EMERGENCY_unblock_legacy_frontend_revert.sql"

echo "== S2 real failure inside the bundle at C3 (an open transaction holds products 9 s)"
docker exec "$C" psql -U postgres -q -c "begin; select 1 from public.products limit 1 for update; select pg_sleep(9); rollback;" >/dev/null 2>&1 &
sleep 1
expect_fail "bundle fails on the C3 lock" "lock timeout" "$A/BUNDLE_C1_C10_UNBLOCK.sql"
wait
fp_same "catalog == C0 exactly after the C3 failure (C1 rolled back too)" "$FP0"
bat after_c3_fail; cmpbat after_c3_fail bat_C0.json
probe after_c3_fail; probe_assert after_c3_fail pre

for point in B.1:C2 B.4:C5; do
  after=${point%%:*}; before=${point##*:}
  echo "== S3 injected failure after stage $after (before $before)"
  awk -v s="-- stage $after" '{print} $0==s{f=1} f&&/^\$stage\$;$/{print "DO $x$ BEGIN RAISE EXCEPTION '"'"'INJECTED_BEFORE_'"$before"''"'"'; END $x$;"; f=0}' "$A/BUNDLE_C1_C10_UNBLOCK.sql" > "$O/inject_$before.sql"
  check "one injection point before $before" '[ "$(grep -c INJECTED_BEFORE_'"$before"' "$O/inject_'"$before"'.sql")" = 1 ]'
  expect_fail "bundle stops before $before" "INJECTED_BEFORE_$before" "$O/inject_$before.sql"
  fp_same "catalog == C0 exactly after the stop before $before" "$FP0"
  probe "stop_before_$before"; probe_assert "stop_before_$before" pre
  bat "stop_before_$before"; cmpbat "stop_before_$before" bat_C0.json
done

echo "== S4 old revert (pinned $OLD_REVERT_REF) if run while stuck after C2, versus the fixed revert"
[ "$(sha256sum < "$OLD_REVERT_FIXTURE" | cut -c1-64)" = "$OLD_REVERT_SHA256" ] || die "old-revert fixture digest"
cp "$OLD_REVERT_FIXTURE" "$O/old_revert.sql" || die old-revert
if git -C "$R" cat-file -e "$OLD_REVERT_REF:docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql" 2> /dev/null; then
  check "fixture bytes equal the pinned commit's file" 'git -C "$R" show "$OLD_REVERT_REF:docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql" | cmp -s - "$O/old_revert.sql"'
fi
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
check "test pre-check after the bundle: false, 10 C6 versions present" 'pre_json "$A/PRECHECK_target_ledger_read.sql" | grep -q "\"ledger_versions_ok\" : false, \"ledger_content_ok\" : false, \"c6_versions_present\" : 10"'
fp_differs "catalog differs from C0 after the bundle (capture checked)" "$FP0"
bat bundle_unblocked; cmpbat bundle_unblocked bat_unblocked.json
probe bundle_unblocked; probe_assert bundle_unblocked after_unblock
expect_fail "bundle rerun refused" LEDGER_STATE_MISMATCH "$A/BUNDLE_C1_C10_UNBLOCK.sql"
apply_ok "revert at C10" "$A/EMERGENCY_unblock_legacy_frontend_revert.sql"
bat C10_reverted; cmpbat C10_reverted bat_C10.json
probe C10_reverted; probe_assert C10_reverted after_revert

echo "== S6 live negative controls on the real database (the pinned check must FAIL, then pass again)"
P1=$(python3 -c "import json;print(json.load(open('/tmp/c6_seed.json'))['p1'])")
S0=$(sql -c "select stock from public.products where id = '$P1'") || die "stock read"
sql -c "update public.products set stock = 0 where id = '$P1'" >/dev/null || die "stock zero"
probe live_refused
python3 "$H/probe_expect.py" "$O/frac_live_refused.json" after_revert >/dev/null; rc=$?
check "an expected sale really REFUSED (stock 0) makes the pinned check fail (exit $rc)" '[ $rc = 1 ] && grep -q "\"REFUSED\"" "$O/frac_live_refused.json"'
sql -c "update public.products set stock = $S0 where id = '$P1'" >/dev/null || die "stock restore"
sql -c "revoke execute on function public.create_sale_with_items_idempotent(uuid,uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state) from authenticated" >/dev/null || die revoke
probe live_denied
python3 "$H/probe_expect.py" "$O/frac_live_denied.json" after_revert >/dev/null; rc=$?
check "an expected sale DENIED makes the pinned check fail (exit $rc)" '[ $rc = 1 ]'
sql -c "grant execute on function public.create_sale_with_items_idempotent(uuid,uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state) to authenticated" >/dev/null || die regrant
probe live_restored; probe_assert live_restored after_revert
bat live_restored; cmpbat live_restored bat_C10.json

echo "== RESULT: $FAILS failure(s)"
[ "$FAILS" = 0 ] || exit 1
