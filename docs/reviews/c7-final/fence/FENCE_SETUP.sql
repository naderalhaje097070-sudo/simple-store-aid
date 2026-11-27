-- C7 final late-request fence (LATE_REQUEST_FENCE.md, option B). Review-only candidate; not approved for any target.
-- Run once, as postgres, by the approved writer, AFTER BUNDLE_C1_C10.sql and VERIFY_C6_CHECKPOINT.sql (ok=true) and
-- BEFORE the first fenced F attempt. Temporary object outside the migration ledger, dropped by FENCE_DROP.sql.
-- Lost reply: never re-run blindly; run FENCE_READ.sql. fence_exists=true with current_attempt=1 means it committed.
-- A copy that arrives late is refused: if the fence exists (FENCE_ALREADY_EXISTS), or if the ledger is no longer
-- exactly the 62-version set (FENCE_SETUP_NOT_AT_62), e.g. after F was applied and the fence dropped at 64.
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT pg_advisory_xact_lock(7202611201);
DO $setup$ BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF current_setting('transaction_isolation') <> 'read committed' THEN RAISE EXCEPTION 'FENCE_REQUIRES_READ_COMMITTED'; END IF;
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations)
     <> '8eec91642011d297ca5504cebda430ef' THEN RAISE EXCEPTION 'FENCE_SETUP_NOT_AT_62'; END IF;
  IF to_regclass('monjez_private.c7_final_fence') IS NOT NULL THEN RAISE EXCEPTION 'FENCE_ALREADY_EXISTS'; END IF;
END $setup$;
CREATE TABLE monjez_private.c7_final_fence (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  attempt integer NOT NULL CHECK (attempt >= 1)
);
REVOKE ALL ON TABLE monjez_private.c7_final_fence FROM PUBLIC, anon, authenticated, service_role;
INSERT INTO monjez_private.c7_final_fence (attempt) VALUES (1);
COMMIT;
