#!/bin/bash
# C7 final fence: invalidate attempt N by moving the fence from exactly N to N+1 (compare-and-set), under the same
# advisory lock as every attempt, in READ COMMITTED. Repeating the same file is harmless:
#   current = N    -> becomes N+1
#   current = N+1  -> no change (this invalidation already committed)
#   anything else  -> FENCE_UNEXPECTED, no change (e.g. a delayed copy after a later invalidation)
# A request for attempt N that is still running finishes first; one that arrives later sees N+1 and is refused
# (STALE_REQUEST) before F1. After it returns, or on a lost reply, confirm with FENCE_READ.sql that
# current_attempt = N+1 (re-running this same file is safe), then generate the attempt file for N+1 only.
# usage: make_advance.sh <N> > advance_<N>_to_<N+1>.sql
set -euo pipefail
N=$1
[[ "$N" =~ ^[1-9][0-9]*$ ]] || { echo "attempt must be a positive integer" >&2; exit 2; }
M=$((N + 1))
cat <<SQL
-- C7 final fence: invalidate attempt $N (move $N -> $M). Review-only candidate.
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT pg_advisory_xact_lock(7202611201);
DO \$advance\$
DECLARE cur integer;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF current_setting('transaction_isolation') <> 'read committed' THEN RAISE EXCEPTION 'FENCE_REQUIRES_READ_COMMITTED'; END IF;
  IF to_regclass('monjez_private.c7_final_fence') IS NULL THEN RAISE EXCEPTION 'FENCE_MISSING'; END IF;
  SELECT attempt INTO cur FROM monjez_private.c7_final_fence;
  IF cur = $N THEN
    UPDATE monjez_private.c7_final_fence SET attempt = $M WHERE attempt = $N;
  ELSIF cur = $M THEN
    RAISE NOTICE 'FENCE_ALREADY_ADVANCED to $M';
  ELSE
    RAISE EXCEPTION 'FENCE_UNEXPECTED current % (expected $N or $M)', cur;
  END IF;
END \$advance\$;
COMMIT;
SQL
