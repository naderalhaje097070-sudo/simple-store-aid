#!/usr/bin/env bash
# C7 final late-request fence self-test (docs/reviews/c7-final/fence, LATE_REQUEST_FENCE.md option B).
# LOCAL ONLY, synthetic data, never production. Same lab data version as c7_final_selftest.sh.
#
# Proves, at the 62-row checkpoint:
#   T7a an attempt whose number was invalidated (FENCE_ADVANCE) is refused with STALE_REQUEST before F1: unchanged
#   T7b a future attempt number is refused the same way
#   T7c a request that arrives while a resume holds the lock waits, then is refused once the resume commits the
#       new number (the late-request case Codex reproduced through a TCP proxy)
#   T7d the current attempt number applies F1/F2: 64, VERIFY_C7_FINAL (lab constants) all true
#   T7e a repeat of the current attempt at 64 is refused by the ledger guard: unchanged
#   T7f after FENCE_DROP any attempt is refused with FENCE_MISSING: unchanged
#   T7g invalidation is compare-and-set: repeating it is a no-op, a delayed old copy is refused (FENCE_UNEXPECTED)
#   T7h with the session default at REPEATABLE READ the attempt still reads the committed number after the lock
#       wait (pinned READ COMMITTED) and is refused; red-check: the previous unpinned wrapper passes the fence check
#       on a stale snapshot (its transaction is rolled back here)
#   T7i FENCE_DROP is refused at 62; a late FENCE_SETUP is refused at 64 after the drop; FENCE_DROP is idempotent
#   and no client role (anon, authenticated, service_role) has any privilege on the fence table
# usage: c7_final_fence_selftest.sh <repo-root> <supabase-cli> <out-dir>
set -euo pipefail
umask 077
R=$(cd "$1" && pwd); SB=$2; OUT=$3; mkdir -p "$OUT"
test "$("$SB" --version)" = 2.101.0
W=$(mktemp -d); ID=monjez-c7final-fence; DB=supabase_db_$ID
EXT=realtime,storage,imgproxy,inbucket,mailpit,meta,studio,edge-runtime,functions,analytics,vector,supavisor,pooler
F=$R/docs/reviews/c7-final/fence
cleanup() { "$SB" --workdir "$W/stack" stop --no-backup >/dev/null 2>&1 || true; rm -rf -- "$W"; }
trap cleanup EXIT
log() { echo "$*" | tee -a "$OUT/fence_selftest.txt"; }
q() { docker exec -i "$DB" psql -X -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq "$@"; }
fingerprint() {
  q -c "select count(*)||' '||md5(coalesce(string_agg(version, ',' ORDER BY version), ''))||' '||md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) from supabase_migrations.schema_migrations"
}
state() {  # ledger fingerprint + row hashes outside the fence table
  echo "$(fingerprint)"; q -f - < "$R/tests/release/restore/data_hash.sql" | grep -v '^monjez_private.c7_final_fence|'
}
refuse() {  # refuse <expected error> <sql file>
  if q -f - < "$2" > "$W/refuse.out" 2> "$W/refuse.err"; then log "FAIL expected refusal $1"; return 1; fi
  grep -F "$1" "$W/refuse.err" | head -1 | sed 's/^psql:<stdin>:[0-9]*: //' | tee -a "$OUT/fence_selftest.txt"
}
attempt() { "$F/make_attempt.sh" "$1" "$W/c7test/BUNDLE_C7_FINAL.sql" > "$W/attempt_$1.sql"; echo "$W/attempt_$1.sql"; }
advance() { "$F/make_advance.sh" "$1" > "$W/advance_$1.sql"; echo "$W/advance_$1.sql"; }
current() { q -f - < "$F/FENCE_READ.sql" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["current_attempt"])'; }
hold_advance() {  # hold_advance <from> <to>: a resume that holds the lock 4s, then commits the compare-and-set
  docker exec -i "$DB" psql -X -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq > "$W/hold.out" 2>&1 <<SQL &
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT pg_advisory_xact_lock(7202611201);
UPDATE monjez_private.c7_final_fence SET attempt = $2 WHERE attempt = $1;
SELECT pg_sleep(4);
COMMIT;
SQL
  HOLD=$!
  for i in $(seq 1 40); do
    [ "$(q -c "select count(*) from pg_locks where locktype = 'advisory' and granted")" -ge 1 ] && break; sleep 0.2
  done
}
qrr() { docker exec -i -e PGOPTIONS='-c default_transaction_isolation=repeatable\ read' "$DB" psql -X -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq "$@"; }

: > "$OUT/fence_selftest.txt"
log "C7 final fence self-test, repo HEAD $(git -C "$R" rev-parse HEAD), $(date -u +%Y-%m-%dT%H:%M:%SZ)"
mkdir -p "$W/stack"; "$SB" --workdir "$W/stack" init > /dev/null
sed -i "s/^project_id = .*/project_id = \"$ID\"/" "$W/stack/supabase/config.toml"
git -C "$R" archive 1c5276fae77cb71f49d868fe71d17d84c5d3c6b3 supabase/migrations | tar -x -C "$W/stack"
"$SB" --workdir "$W/stack" start -x "$EXT" > "$W/start.log" 2>&1 || { grep -Ei 'error|fail' "$W/start.log" | head; exit 1; }
img=$(docker inspect --format '{{.Config.Image}}' "$DB"); case "$img" in *supabase/postgres:17.6.1.106) ;; *) exit 1 ;; esac
E=$(git -C "$R" ls-tree --name-only 183dc50 supabase/migrations/ | grep 20261107214500)
git -C "$R" show "183dc50:$E" | q -f -
q -f - < "$R/docs/reviews/c6-apply/replica_drift.sql"; q -f - < "$R/docs/reviews/c6-apply/replica_ledger_set.sql"
python3 "$R/tests/c6-upgrade/make_replica_ledger.py" "$R" "$W/fixture.sql" "$W/c0.expected" > /dev/null
q -f - < "$W/fixture.sql"; python3 "$R/tests/c6-upgrade/harness.py" "$DB" seed > /dev/null
bash "$R/docs/reviews/c6-apply/build_apply_files.sh" "$R" "$W/c0.expected" "$W/c6test" > /dev/null
bash "$R/docs/reviews/c7-final/build_c7_final.sh" "$R" "$W/c0.expected" "$W/c7test" > /dev/null
q -f - < "$W/c6test/BUNDLE_C1_C10.sql" > /dev/null 2>&1
test "$(q -f - < "$W/c7test/VERIFY_C6_CHECKPOINT.sql" | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["ok"])')" = True
log "at 62 with the C6 checkpoint ok: $(fingerprint)"

log "T7i(a): FENCE_DROP before F (at 62)"
refuse "FENCE_DROP_NOT_AT_64" "$F/FENCE_DROP.sql"
q -f - < "$F/FENCE_SETUP.sql" > /dev/null
log "fence created: $(q -f - < "$F/FENCE_READ.sql")"
refuse "FENCE_ALREADY_EXISTS" "$F/FENCE_SETUP.sql"
privs=$(q -c "select bool_or(has_table_privilege(r, 'monjez_private.c7_final_fence', p)) from unnest(array['anon','authenticated','service_role']) r, unnest(array['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']) p")
test "$privs" = f; log "PASS no client role has any privilege on the fence table; a second setup is refused"
state > "$W/s62"

log "T7a: invalidate attempt 1 (1 -> 2), then attempt 1 arrives"
q -f - < "$(advance 1)" > /dev/null; test "$(current)" = 2
refuse "STALE_REQUEST attempt 1" "$(attempt 1)"
state > "$W/t7a"; diff "$W/s62" "$W/t7a"; log "PASS T7a refused before F1, ledger and rows unchanged"

log "T7g: the same invalidation again, then a delayed copy after a later invalidation"
q -f - < "$W/advance_1.sql" > /dev/null 2> "$W/adv.err"; grep -q FENCE_ALREADY_ADVANCED "$W/adv.err"; test "$(current)" = 2
log "PASS T7g(a) repeat of 1 -> 2 is a no-op (FENCE_ALREADY_ADVANCED), current still 2"

log "T7b: a future attempt number"
refuse "STALE_REQUEST attempt 3" "$(attempt 3)"
state > "$W/t7b"; diff "$W/s62" "$W/t7b"; log "PASS T7b refused, unchanged"

log "T7c+T7h: attempt 2 (session default REPEATABLE READ) arrives while a resume holds the lock and commits 2 -> 3"
A2=$(attempt 2)
hold_advance 2 3
start=$(date +%s.%N)
if qrr -f - < "$A2" > "$W/refuse.out" 2> "$W/refuse.err"; then log "FAIL attempt 2 was not refused"; exit 1; fi
grep -F "STALE_REQUEST attempt 2" "$W/refuse.err" | head -1 | sed 's/^psql:<stdin>:[0-9]*: //' | tee -a "$OUT/fence_selftest.txt"
waited=$(python3 -c "print(round($(date +%s.%N) - $start, 1))")
wait "$HOLD"; python3 -c "import sys; sys.exit(0 if $waited >= 2 else 1)"
test "$(current)" = 3
state > "$W/t7c"; diff "$W/s62" "$W/t7c"
log "PASS T7c/T7h waited ${waited}s on the lock under a REPEATABLE READ default, read the committed number, refused; unchanged"

q -f - < "$W/advance_1.sql" > /dev/null 2> "$W/adv.err" && { log "FAIL delayed 1 -> 2 accepted"; exit 1; }
grep -F "FENCE_UNEXPECTED" "$W/adv.err" | head -1 | sed 's/^psql:<stdin>:[0-9]*: //' | tee -a "$OUT/fence_selftest.txt"
test "$(current)" = 3; log "PASS T7g(b) delayed copy of 1 -> 2 after 2 -> 3 refused, current still 3"

log "red-check T7h: the previous unpinned wrapper (BEGIN; without isolation) under REPEATABLE READ, rolled back"
python3 - "$(attempt 3)" "$W/old_attempt_3.sql" <<'PY'
import sys
src = open(sys.argv[1]).read().splitlines()
out = [l for l in src if 'transaction_isolation' not in l]
out = ['BEGIN;' if l == 'BEGIN ISOLATION LEVEL READ COMMITTED;' else l for l in out]
i = max(k for k, l in enumerate(out) if l == 'COMMIT;')
out[i] = 'ROLLBACK;'
j = next(k for k, l in enumerate(out) if l.startswith('END $fence$;'))
out.insert(j + 1, "DO $r$ BEGIN RAISE NOTICE 'RED_PASSED_FENCE_CHECK'; END $r$;")
open(sys.argv[2], 'w').write('\n'.join(out) + '\n')
PY
hold_advance 3 4
qrr -f - < "$W/old_attempt_3.sql" > "$W/red.out" 2> "$W/red.err" || true
wait "$HOLD"
if grep -q RED_PASSED_FENCE_CHECK "$W/red.err"; then
  log "RED-CHECK: the unpinned wrapper for attempt 3 passed the fence check although 3 -> 4 committed first (stale snapshot); rolled back"
else
  log "RED-CHECK: the unpinned wrapper did not pass the fence check here: $(grep -E 'ERROR' "$W/red.err" | head -1)"
fi
test "$(current)" = 4
state > "$W/t7hr"; diff "$W/s62" "$W/t7hr"; log "PASS red-check left ledger and rows unchanged; current 4"

log "T7d: the current attempt (4) applies F1/F2"
q -f - < "$(attempt 4)" > /dev/null
test "$(fingerprint | cut -d' ' -f1,2)" = "64 a6ca71705682237fc4bc6b93c4f782b5"
q -f - < "$W/c7test/VERIFY_C7_FINAL.sql" > "$OUT/fence_verify_c7.json"
python3 - "$OUT/fence_verify_c7.json" <<'PY' | tee -a "$OUT/fence_selftest.txt"
import json, sys
v = json.load(open(sys.argv[1]))
flat = {k: v[k] for k in v if k.endswith('_ok')}
fns = {f'{n}.{k}': x for n, d in v['functions'].items() for k, x in d.items()}
bad = [k for k, x in {**flat, **fns}.items() if x is not True]
assert v['ledger_rows'] == 64 and not bad, bad
print(f'PASS T7d 64 rows; VERIFY_C7_FINAL (lab constants): {len(flat)} ledger and {len(fns)} function checks true')
PY
state > "$W/s64"

log "T7e: the same attempt again at 64"
refuse "LEDGER_STATE_MISMATCH before 20261120140000" "$W/attempt_4.sql"
state > "$W/t7e"; diff "$W/s64" "$W/t7e"; log "PASS T7e refused by the ledger guard, unchanged"

log "T7f/T7i: FENCE_DROP (twice), then a late attempt and a late setup"
q -f - < "$F/FENCE_DROP.sql" > /dev/null
q -f - < "$F/FENCE_DROP.sql" > /dev/null
log "fence after two drops: $(q -f - < "$F/FENCE_READ.sql")"
refuse "FENCE_MISSING" "$W/attempt_4.sql"
refuse "FENCE_SETUP_NOT_AT_62" "$F/FENCE_SETUP.sql"
test "$(q -c "select to_regclass('monjez_private.c7_final_fence') is null")" = t
state > "$W/t7f"; diff "$W/s64" "$W/t7f"; log "PASS T7f/T7i drop is idempotent; late attempt FENCE_MISSING; late setup refused, fence not recreated; unchanged"
log "ALL PASS"
