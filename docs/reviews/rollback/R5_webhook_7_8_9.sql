BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
-- Undo 20261021132651/134621/140746. Receipts and bindings tables and their rows are KEPT.
DROP FUNCTION IF EXISTS public.apply_subscription_webhook(text,text,text,timestamptz,jsonb);
DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261021132651','20261021134621','20261021140746');
COMMIT;
