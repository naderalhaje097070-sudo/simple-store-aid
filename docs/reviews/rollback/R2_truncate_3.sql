BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
DO $pre$ BEGIN
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version IN ('20261013221918','20261020210549','20261021080927','20261021132651','20261021134621','20261021140746')) THEN RAISE EXCEPTION 'ROLLBACK_ORDER_VIOLATION: undo later stages first'; END IF;
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN ('20261013120223')) <> 1 THEN RAISE EXCEPTION 'STAGE_NOT_APPLIED: nothing to undo'; END IF;
  IF NOT EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261107214500') THEN RAISE EXCEPTION 'EMAIL_HOTFIX_MISSING'; END IF;
END $pre$;
-- Undo 20261013120223: restores the pre-update TRUNCATE grants exactly (authenticated on 21 tables, not anon).
GRANT TRUNCATE ON TABLE public.couriers, public.customers, public.day_closes, public.email_send_log, public.email_send_state, public.email_unsubscribe_tokens, public.expenses, public.financial_audit_log, public.order_items, public.orders, public.payments, public.platform_admin_audit_log, public.platform_admins, public.products, public.profiles, public.security_scan_findings, public.security_scan_runs, public.subscriptions, public.suppressed_emails, public.tenants, public.user_roles TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT TRUNCATE ON TABLES TO authenticated;
DO $led$ DECLARE n int; BEGIN
  DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261013120223');
  GET DIAGNOSTICS n = ROW_COUNT; IF n <> 1 THEN RAISE EXCEPTION 'LEDGER_DELETE_COUNT % <> 1', n; END IF;
END $led$;
COMMIT;
