BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
DO $pre$ BEGIN
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN ('20261021132651','20261021134621','20261021140746')) <> 3 THEN RAISE EXCEPTION 'STAGE_NOT_APPLIED: nothing to undo'; END IF;
  IF NOT EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261107214500') THEN RAISE EXCEPTION 'EMAIL_HOTFIX_MISSING'; END IF;
END $pre$;
-- Undo 20261021132651/134621/140746. Receipts and bindings tables and their rows are KEPT.
DROP FUNCTION IF EXISTS public.apply_subscription_webhook(text,text,text,timestamptz,jsonb);
DO $led$ DECLARE n int; BEGIN
  DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261021132651','20261021134621','20261021140746');
  GET DIAGNOSTICS n = ROW_COUNT; IF n <> 3 THEN RAISE EXCEPTION 'LEDGER_DELETE_COUNT % <> 3', n; END IF;
END $led$;
COMMIT;
