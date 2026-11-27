-- C7 final fence: remove the fence only after VERIFY_C7_FINAL.sql is literally true at 64 (STOP_RESUME.md §4).
-- Refused unless the ledger is exactly the 64-version set. Idempotent (DROP ... IF EXISTS): on a lost reply, run it
-- again and confirm with FENCE_READ.sql that fence_exists=false. A late attempt is then refused (FENCE_MISSING, and
-- the ledger guard at 64); a late FENCE_SETUP.sql is refused (FENCE_SETUP_NOT_AT_62).
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT pg_advisory_xact_lock(7202611201);
DO $drop$ BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations)
     <> 'a6ca71705682237fc4bc6b93c4f782b5' THEN RAISE EXCEPTION 'FENCE_DROP_NOT_AT_64'; END IF;
END $drop$;
DROP TABLE IF EXISTS monjez_private.c7_final_fence;
COMMIT;
