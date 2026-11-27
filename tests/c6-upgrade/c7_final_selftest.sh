#!/usr/bin/env bash
# C7 final (F1 = 20261120140000, F2 = 20261120150000) self-test. LOCAL ONLY, synthetic data, never production.
#
# Lab data version (fixed, all from this repository):
#   - Supabase CLI 2.101.0, image supabase/postgres:17.6.1.106 (checked)
#   - schema: the 50 main migrations at 1c5276f, then 20261107214500 from 183dc50,
#     docs/reviews/c6-apply/replica_drift.sql and replica_ledger_set.sql (the production replica, as in
#     tests/c6-upgrade/build_replica.sh)
#   - ledger: tests/c6-upgrade/make_replica_ledger.py = production's 52 versions; 47 with the repository text
#     (md5 equal to production), 5 local placeholders (md5 differs), so the TEST expected file differs from
#     production only in those 5 md5 values
#   - rows: tests/c6-upgrade/harness.py seed (synthetic owners A/B, staff A, products, sales, courier orders,
#     settlement, collection, expense, day close)
#
# Proves, on that lab:
#   T1 wrong baseline refused with no change: (a) at 52 (before C6) -> LEDGER_STATE_MISMATCH;
#      (b) the committed production-constant bundle at the lab's 62 -> LEDGER_CONTENT_MISMATCH
#   T2 failure injected between F1 and F2 -> whole transaction rolled back: ledger 62, catalog and row hashes
#      identical to the post-C6 capture
#   T3 success: 64 rows, version fingerprint a6ca7170... (base-independent), test-constant VERIFY all true,
#      only the three function definitions change in the catalog, rows unchanged, function ACLs unchanged
#   T4 rerun refused with no change
#   T5 C6 checkpoint verifier (VERIFY_C6_CHECKPOINT.sql): false at 52 and at 64, true at 62 with lab constants,
#      false only on ledger_content_ok with production constants on the lab
#   T6 the checkpoint verifier rejects a missing object and changed privileges, including a column-level
#      SELECT grant to anon (mutations rolled back, unchanged)
# The test build differs from the committed files only in ledger guard constant lines (checked).
#
# usage: c7_final_selftest.sh <repo-root> <supabase-cli> <out-dir>
set -euo pipefail
umask 077
R=$(cd "$1" && pwd); SB=$2; OUT=$3; mkdir -p "$OUT"
test "$("$SB" --version)" = 2.101.0
W=$(mktemp -d); ID=monjez-c7final-selftest; DB=supabase_db_$ID
EXT=realtime,storage,imgproxy,inbucket,mailpit,meta,studio,edge-runtime,functions,analytics,vector,supavisor,pooler
cleanup() { "$SB" --workdir "$W/stack" stop --no-backup >/dev/null 2>&1 || true; rm -rf -- "$W"; }
trap cleanup EXIT
log() { echo "$*" | tee -a "$OUT/selftest.txt"; }
q() { docker exec -i "$DB" psql -X -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq "$@"; }
capture() {
  q -f - < "$R/tests/release/restore/fingerprint.sql" > "$W/$1.catalog"
  q -f - < "$R/tests/release/restore/data_hash.sql" > "$W/$1.data"
  q -c "select version||' '||md5(array_to_string(statements, E'\n')) from supabase_migrations.schema_migrations order by version" > "$W/$1.ledger"
  q -c "select p.oid::regprocedure||' '||coalesce(p.proacl::text,'NULL') from pg_proc p where p.proname in ('update_courier_outcome_v2','settle_courier_orders','close_day') and p.pronamespace='public'::regnamespace order by 1" > "$W/$1.acl"
  test -s "$W/$1.catalog" && test -s "$W/$1.data"
}
same() { diff -u "$W/$1.catalog" "$W/$2.catalog" && diff -u "$W/$1.data" "$W/$2.data" && diff -u "$W/$1.ledger" "$W/$2.ledger"; }
refuse() {  # refuse <expected error> <sql file>
  if q -f - < "$2" > "$W/refuse.out" 2> "$W/refuse.err"; then log "FAIL expected refusal $1"; return 1; fi
  grep -F "$1" "$W/refuse.err" | head -1 | tee -a "$OUT/selftest.txt"
}
fingerprint() {
  q -c "select count(*)||' '||md5(coalesce(string_agg(version, ',' ORDER BY version), ''))||' '||md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) from supabase_migrations.schema_migrations"
}
nonguard() { grep -vE "LEDGER_(STATE|CONTENT)_MISMATCH|^-- C7 final read-only verification" "$1"; }
ckpt() {  # ckpt <verify file> [mutation sql]: run the checkpoint verifier, optionally after a mutation in the SAME
          # transaction, which is then rolled back by the verifier's own final rollback
  if [ -n "${2:-}" ]; then { printf 'begin;\n%s\n' "$2"; grep -v '^begin transaction read only;$' "$1"; } | q -f -; else q -f - < "$1"; fi
}
ckpt_expect() {  # ckpt_expect <label> <json> <ok true|false> [failed name ...]
  python3 - "$@" <<'PY' | tee -a "$OUT/selftest.txt"
import json, sys
label, raw, ok, names = sys.argv[1], sys.argv[2], sys.argv[3] == 'true', sys.argv[4:]
v = json.loads(raw)
assert v['checks'] == 37 and isinstance(v['ok'], bool) and v['ok'] is ok, v
missing = [n for n in names if n not in v['failed']]
assert not missing, (missing, v['failed'])
print(f"PASS {label}: ok={str(v['ok']).lower()}, failed={v['failed']}")
PY
}

: > "$OUT/selftest.txt"
log "C7 final self-test, repo HEAD $(git -C "$R" rev-parse HEAD), $(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$W/stack"; "$SB" --workdir "$W/stack" init > /dev/null
sed -i "s/^project_id = .*/project_id = \"$ID\"/" "$W/stack/supabase/config.toml"
git -C "$R" archive 1c5276fae77cb71f49d868fe71d17d84c5d3c6b3 supabase/migrations | tar -x -C "$W/stack"
test "$(ls "$W/stack/supabase/migrations"/*.sql | wc -l)" -eq 50
"$SB" --workdir "$W/stack" start -x "$EXT" > "$W/start.log" 2>&1 || { grep -Ei 'error|fail' "$W/start.log" | head; exit 1; }
img=$(docker inspect --format '{{.Config.Image}}' "$DB"); case "$img" in *supabase/postgres:17.6.1.106) ;; *) exit 1 ;; esac
log "stack: CLI 2.101.0, $img"
E=$(git -C "$R" ls-tree --name-only 183dc50 supabase/migrations/ | grep 20261107214500)
git -C "$R" show "183dc50:$E" | q -f -
q -f - < "$R/docs/reviews/c6-apply/replica_drift.sql"
q -f - < "$R/docs/reviews/c6-apply/replica_ledger_set.sql"
python3 "$R/tests/c6-upgrade/make_replica_ledger.py" "$R" "$W/fixture.sql" "$W/c0.expected" > /dev/null
q -f - < "$W/fixture.sql"
python3 "$R/tests/c6-upgrade/harness.py" "$DB" seed > /dev/null
diff -u <(sort "$W/c0.expected") <(q -c "select version||' '||md5(array_to_string(statements, E'\n')) from supabase_migrations.schema_migrations order by version")
log "C0 lab ledger: $(fingerprint)"
capture c0

# Test builds with the lab's expected ledger; they must differ from the committed files only in guard constants.
bash "$R/docs/reviews/c6-apply/build_apply_files.sh" "$R" "$W/c0.expected" "$W/c6test" > /dev/null
bash "$R/docs/reviews/c7-final/build_c7_final.sh" "$R" "$W/c0.expected" "$W/c7test" | tee -a "$OUT/selftest.txt"
cmp <(nonguard "$W/c6test/BUNDLE_C1_C10.sql") <(nonguard "$R/docs/reviews/c6-apply/BUNDLE_C1_C10.sql")
cmp <(nonguard "$W/c7test/BUNDLE_C7_FINAL.sql") <(nonguard "$R/docs/reviews/c7-final/BUNDLE_C7_FINAL.sql")
cmp <(grep -vE "^-- C6 checkpoint|'ledger_content_ok'" "$W/c7test/VERIFY_C6_CHECKPOINT.sql") <(grep -vE "^-- C6 checkpoint|'ledger_content_ok'" "$R/docs/reviews/c7-final/VERIFY_C6_CHECKPOINT.sql")
log "PASS test builds equal committed files except ledger guard constants"
T7=$W/c7test/BUNDLE_C7_FINAL.sql

log "T1a: C7 final test bundle at 52 (before C6)"
refuse "LEDGER_STATE_MISMATCH before 20261120140000" "$T7"
capture t1a; same c0 t1a; log "PASS T1a refused, catalog/rows/ledger unchanged"
ckpt_expect "T5a checkpoint at 52 (before C6)" "$(ckpt "$W/c7test/VERIFY_C6_CHECKPOINT.sql")" false ledger_rows_ok keyed_sale_exists legacy_sale_authenticated_withdrawn report_view_is_view

q -f - < "$W/c6test/BUNDLE_C1_C10.sql"
log "after C6 (test bundle): $(fingerprint)"
capture c6
test "$(q -f - < "$W/c7test/VERIFY_C7_FINAL.sql" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["ledger_rows_ok"])')" = False
log "PASS VERIFY at 62 reports ledger_rows_ok false"
ckpt_expect "T5b checkpoint at 62, lab constants (positive control)" "$(ckpt "$W/c7test/VERIFY_C6_CHECKPOINT.sql")" true
ckpt_expect "T5c checkpoint at 62, production constants on the lab" "$(ckpt "$R/docs/reviews/c7-final/VERIFY_C6_CHECKPOINT.sql")" false ledger_content_ok
V=$W/c7test/VERIFY_C6_CHECKPOINT.sql
ckpt_expect "T6a missing object (report view dropped)" "$(ckpt "$V" 'drop view public.day_close_profit_report;')" false report_view_is_view report_view_authenticated_select
ckpt_expect "T6b legacy sale re-granted to authenticated" "$(ckpt "$V" 'grant execute on function public.create_sale_with_items(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb) to authenticated;')" false legacy_sale_authenticated_withdrawn
ckpt_expect "T6c keyed sale revoked from authenticated" "$(ckpt "$V" 'revoke execute on function public.create_sale_with_items_idempotent(uuid,uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state) from authenticated;')" false keyed_sale_authenticated_execute
ckpt_expect "T6d legacy collection granted to anon" "$(ckpt "$V" 'grant execute on function public.collect_order_debt(uuid,numeric,public.payment_method) to anon;')" false legacy_collection_anon_withdrawn
ckpt_expect "T6e keyed collection dropped (missing object)" "$(ckpt "$V" 'drop function public.collect_order_debt_idempotent(uuid,uuid,numeric,public.payment_method);')" false keyed_collection_exists keyed_collection_authenticated_execute keyed_collection_anon_withdrawn keyed_collection_public_withdrawn
ckpt_expect "T6f column-level SELECT granted to anon on the report view" "$(ckpt "$V" 'grant select (id) on public.day_close_profit_report to anon;')" false report_view_anon_no_select
capture t6; same c6 t6; log "PASS T6 mutations rolled back: catalog/rows/ledger identical to after C6"

log "T1b: committed production-constant BUNDLE_C7_FINAL.sql at the lab's 62"
refuse "LEDGER_CONTENT_MISMATCH before 20261120140000" "$R/docs/reviews/c7-final/BUNDLE_C7_FINAL.sql"
capture t1b; same c6 t1b; log "PASS T1b refused, catalog/rows/ledger unchanged"

log "T2: failure injected between F1 and F2"
awk '/^-- stage C7F.2$/{print "DO $$ BEGIN RAISE EXCEPTION '"'"'INJECTED_BETWEEN_F1_F2'"'"'; END $$;"} {print}' "$T7" > "$W/c7fail.sql"
test "$(grep -c INJECTED_BETWEEN_F1_F2 "$W/c7fail.sql")" = 1
refuse INJECTED_BETWEEN_F1_F2 "$W/c7fail.sql"
capture t2; same c6 t2; log "PASS T2 rolled back to 62: $(fingerprint)"

log "T3: C7 final test bundle at 62"
q -f - < "$T7"
log "after C7 final: $(fingerprint)"
test "$(fingerprint | cut -d' ' -f1,2)" = "64 a6ca71705682237fc4bc6b93c4f782b5"
q -f - < "$W/c7test/VERIFY_C7_FINAL.sql" > "$OUT/verify_test_constants.json"
python3 - "$OUT/verify_test_constants.json" <<'PY' | tee -a "$OUT/selftest.txt"
import json, sys
v = json.load(open(sys.argv[1]))
flat = {k: v[k] for k in v if k.endswith('_ok')}
fns = {f'{n}.{k}': x for n, d in v['functions'].items() for k, x in d.items()}
bad = [k for k, x in {**flat, **fns}.items() if x is not True]
assert v['ledger_rows'] == 64 and not bad, bad
print(f'PASS VERIFY (test constants): {len(flat)} ledger checks and {len(fns)} function checks true')
PY
q -f - < "$R/docs/reviews/c7-final/VERIFY_C7_FINAL.sql" > "$OUT/verify_production_constants.json"
python3 - "$OUT/verify_production_constants.json" <<'PY' | tee -a "$OUT/selftest.txt"
import json, sys
v = json.load(open(sys.argv[1]))
fns = [x for d in v['functions'].values() for x in d.values()]
assert v['ledger_content_ok'] is False and v['ledger_versions_ok'] and v['ledger_rows_ok'] and all(fns)
print('PASS VERIFY (production constants) on the lab: content false (5 placeholder rows), versions, rows and all function checks true')
PY
capture c7
diff "$W/c6.data" "$W/c7.data" > "$OUT/data_diff_c6_c7.txt" || true
diff "$W/c6.acl" "$W/c7.acl" > "$OUT/acl_diff_c6_c7.txt" || true
diff "$W/c6.catalog" "$W/c7.catalog" > "$OUT/catalog_diff_c6_c7.txt" || true
cp "$W/c7.acl" "$OUT/function_acl_after.txt"
other_data=$(grep -E '^[<>]' "$OUT/data_diff_c6_c7.txt" | grep -vc '^[<>] supabase_migrations\.schema_migrations|' || true)
acl_lines=$(grep -cE '^[<>]' "$OUT/acl_diff_c6_c7.txt" || true)
cat_lines=$(grep -cE '^[<>]' "$OUT/catalog_diff_c6_c7.txt" || true)
other_cat=$(grep -E '^[<>]' "$OUT/catalog_diff_c6_c7.txt" | grep -vcE '(update_courier_outcome_v2|settle_courier_orders|close_day)\(' || true)
log "c6->c7: data lines outside the ledger changed: $other_data; function ACL lines changed: $acl_lines; catalog lines changed: $cat_lines (outside the three functions: $other_cat)"
grep -E '^[<>]' "$OUT/catalog_diff_c6_c7.txt" | cut -c1-80 | tee -a "$OUT/selftest.txt" || true
test "$other_data" = 0 && test "$acl_lines" = 0 && test "$other_cat" = 0 && test "$cat_lines" -gt 0
log "PASS T3 only the three function definitions changed; rows outside the ledger and function ACLs unchanged"
ckpt_expect "T5d checkpoint at 64 (after F)" "$(ckpt "$W/c7test/VERIFY_C6_CHECKPOINT.sql")" false ledger_rows_ok

log "T4: rerun at 64"
refuse "LEDGER_STATE_MISMATCH before 20261120140000" "$T7"
capture t4; same c7 t4; log "PASS T4 refused, unchanged"
cp "$W/c0.expected" "$OUT/lab_c0_expected_ledger.txt"
for s in c0 c6 c7; do sha256sum "$W/$s.catalog" "$W/$s.data" | awk -v s=$s '{print s, $1, $2}' | sed "s#$W/##"; done | tee -a "$OUT/selftest.txt"
log "ALL PASS"
