BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
DO $pre$ BEGIN
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version IN ('20261020210549','20261021080927','20261021132651','20261021134621','20261021140746')) THEN RAISE EXCEPTION 'ROLLBACK_ORDER_VIOLATION: undo later stages first'; END IF;
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN ('20261013221918')) <> 1 THEN RAISE EXCEPTION 'STAGE_NOT_APPLIED: nothing to undo'; END IF;
  IF NOT EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261107214500') THEN RAISE EXCEPTION 'EMAIL_HOTFIX_MISSING'; END IF;
END $pre$;
-- Undo 20261013221918. owner_account_closures table and rows are KEPT (closure no longer enforced after this).
CREATE OR REPLACE FUNCTION monjez_private.actor_is_active()
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = ''
AS $guard$
  SELECT EXISTS (
    SELECT 1 FROM auth.users u
    WHERE u.id = (SELECT auth.uid()) AND u.deleted_at IS NULL
      AND (u.banned_until IS NULL OR u.banned_until <= statement_timestamp())
  );
$guard$;
DROP FUNCTION IF EXISTS public.close_owner_account();
DO $led$ DECLARE n int; BEGIN
  DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261013221918');
  GET DIAGNOSTICS n = ROW_COUNT; IF n <> 1 THEN RAISE EXCEPTION 'LEDGER_DELETE_COUNT % <> 1', n; END IF;
END $led$;
COMMIT;
