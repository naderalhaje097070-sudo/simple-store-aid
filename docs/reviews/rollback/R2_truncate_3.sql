BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
-- Undo 20261013120223: restores the pre-update TRUNCATE grants exactly (authenticated on 21 tables, not anon).
GRANT TRUNCATE ON TABLE public.couriers, public.customers, public.day_closes, public.email_send_log, public.email_send_state, public.email_unsubscribe_tokens, public.expenses, public.financial_audit_log, public.order_items, public.orders, public.payments, public.platform_admin_audit_log, public.platform_admins, public.products, public.profiles, public.security_scan_findings, public.security_scan_runs, public.subscriptions, public.suppressed_emails, public.tenants, public.user_roles TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT TRUNCATE ON TABLES TO authenticated;
DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261013120223');
COMMIT;
