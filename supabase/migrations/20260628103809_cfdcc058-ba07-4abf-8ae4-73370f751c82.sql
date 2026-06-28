-- Revoke unnecessary DELETE grants. The app performs ALL deletions through
-- SECURITY DEFINER RPCs (delete_order_with_restore_stock, delete_product_safe,
-- __test_force_delete_e2e_order, etc.). No client code calls .delete() directly.
-- This closes a pre-existing hardening gap without changing any app logic.

REVOKE DELETE ON public.orders                   FROM anon, authenticated;
REVOKE DELETE ON public.order_items              FROM anon, authenticated;
REVOKE DELETE ON public.payments                 FROM anon, authenticated;
REVOKE DELETE ON public.products                 FROM anon, authenticated;
REVOKE DELETE ON public.customers                FROM anon, authenticated;
REVOKE DELETE ON public.couriers                 FROM anon, authenticated;
REVOKE DELETE ON public.expenses                 FROM anon, authenticated;
REVOKE DELETE ON public.day_closes               FROM anon, authenticated;
REVOKE DELETE ON public.tenants                  FROM anon, authenticated;
REVOKE DELETE ON public.profiles                 FROM anon, authenticated;
REVOKE DELETE ON public.user_roles               FROM anon, authenticated;
REVOKE DELETE ON public.platform_admins          FROM anon, authenticated;
REVOKE DELETE ON public.subscriptions            FROM anon, authenticated;
REVOKE DELETE ON public.security_scan_findings   FROM anon, authenticated;
REVOKE DELETE ON public.security_scan_runs       FROM anon, authenticated;
REVOKE DELETE ON public.financial_audit_log      FROM anon, authenticated;
REVOKE DELETE ON public.platform_admin_audit_log FROM anon, authenticated;