#!/bin/bash
# C7 final fence: wrap BUNDLE_C7_FINAL.sql for one attempt number. The bundle body between its BEGIN; and COMMIT;
# is copied unchanged; the wrapper adds, inside the same transaction and before F1, the advisory lock and the
# attempt-number check. usage: make_attempt.sh <attempt> <bundle.sql> > attempt_<n>.sql
# For production the bundle must be the committed docs/reviews/c7-final/BUNDLE_C7_FINAL.sql (sha256 in SHA256SUMS);
# the header line records that sha256. A retry never re-sends an old attempt file: after make_advance.sh and a
# confirmed FENCE_READ.sql, generate a new wrapper for the confirmed number around the same pinned bundle.
# READ COMMITTED is set at BEGIN, so each statement after the lock wait reads the committed fence number.
set -euo pipefail
N=$1; B=$2
[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "attempt must be a positive integer" >&2; exit 2; }
test "$(grep -c '^BEGIN;$' "$B")" -ge 1 && test "$(tail -n 1 "$B")" = "COMMIT;"
first=$(grep -n '^BEGIN;$' "$B" | head -1 | cut -d: -f1)
echo "-- C7 final fenced attempt $N of BUNDLE_C7_FINAL.sql (sha256 $(sha256sum < "$B" | cut -c1-64)). Review-only candidate."
echo "BEGIN ISOLATION LEVEL READ COMMITTED;"
echo "SELECT pg_advisory_xact_lock(7202611201);"
echo "DO \$fence\$ BEGIN"
echo "  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;"
echo "  IF current_setting('transaction_isolation') <> 'read committed' THEN RAISE EXCEPTION 'FENCE_REQUIRES_READ_COMMITTED'; END IF;"
echo "  IF to_regclass('monjez_private.c7_final_fence') IS NULL THEN RAISE EXCEPTION 'FENCE_MISSING'; END IF;"
echo "  IF (SELECT attempt FROM monjez_private.c7_final_fence) IS DISTINCT FROM $N THEN RAISE EXCEPTION 'STALE_REQUEST attempt $N'; END IF;"
echo "END \$fence\$;"
sed -n "$((first + 1)),\$p" "$B"
