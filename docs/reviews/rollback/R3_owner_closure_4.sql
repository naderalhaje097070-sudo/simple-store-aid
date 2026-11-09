BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
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
DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261013221918');
COMMIT;
