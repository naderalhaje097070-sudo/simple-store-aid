-- C7 final fence: invalidate the current attempt number before any resume decision (STOP_RESUME.md §3a).
-- Run as postgres by the approved writer, in its own committed transaction. Under the same advisory lock as every
-- fenced attempt: a request still running finishes first; a request that arrives later sees the new number and
-- is refused with STALE_REQUEST before F1. Record the returned number; only an attempt file for that number may run.
BEGIN;
SELECT pg_advisory_xact_lock(7202611201);
UPDATE monjez_private.c7_final_fence SET attempt = attempt + 1 RETURNING attempt AS current_attempt;
COMMIT;
