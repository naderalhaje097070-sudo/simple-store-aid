-- C7 final late-request fence (LATE_REQUEST_FENCE.md, option B). Review-only candidate; not approved for any target.
-- Run once, as postgres, by the approved writer, in its own committed transaction, AFTER BUNDLE_C1_C10.sql and
-- VERIFY_C6_CHECKPOINT.sql (ok=true) and BEFORE the first fenced F attempt. Temporary object outside the migration
-- ledger: dropped by FENCE_DROP.sql after VERIFY_C7_FINAL.sql is literally true. No client role can read or write it.
BEGIN;
DO $setup$ BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF to_regclass('monjez_private.c7_final_fence') IS NOT NULL THEN RAISE EXCEPTION 'FENCE_ALREADY_EXISTS'; END IF;
END $setup$;
SELECT pg_advisory_xact_lock(7202611201);
CREATE TABLE monjez_private.c7_final_fence (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  attempt integer NOT NULL CHECK (attempt >= 1)
);
REVOKE ALL ON TABLE monjez_private.c7_final_fence FROM PUBLIC, anon, authenticated, service_role;
INSERT INTO monjez_private.c7_final_fence (attempt) VALUES (1);
COMMIT;
