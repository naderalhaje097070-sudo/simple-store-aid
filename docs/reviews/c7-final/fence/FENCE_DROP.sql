-- C7 final fence: remove the fence only after VERIFY_C7_FINAL.sql is literally true at 64 (STOP_RESUME.md §4).
-- Under the advisory lock. A request that arrives afterwards is refused by FENCE_MISSING, and by the ledger guard at 64.
BEGIN;
SELECT pg_advisory_xact_lock(7202611201);
DROP TABLE monjez_private.c7_final_fence;
COMMIT;
