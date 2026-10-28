-- SEC-TRUNCATE-01: app-public tables only; no row operation or provider change.
-- CLI2.101.0 creates the migration filename before this exact SQL is published.
BEGIN;

DO $scope$
BEGIN
  IF current_user <> 'postgres' THEN
    RAISE EXCEPTION 'SEC_TRUNCATE_MIGRATION_CREATOR_MISMATCH';
  END IF;
  -- Per-schema defaults cannot subtract a global/inherited client grant.
  -- Stop rather than changing defaults outside public or provider memberships.
  IF EXISTS (
    SELECT 1
    FROM pg_default_acl d
    CROSS JOIN LATERAL aclexplode(d.defaclacl) a
    WHERE d.defaclrole = 'postgres'::regrole
      AND d.defaclnamespace = 0 AND d.defaclobjtype = 'r'
      AND a.privilege_type = 'TRUNCATE'
      AND CASE WHEN a.grantee = 0 THEN true ELSE
        a.grantee IN ('anon'::regrole, 'authenticated'::regrole)
        OR pg_has_role('anon', a.grantee, 'USAGE')
        OR pg_has_role('authenticated', a.grantee, 'USAGE') END
  ) THEN
    RAISE EXCEPTION 'SEC_TRUNCATE_UNSCOPED_GLOBAL_DEFAULT_GRANT';
  END IF;
END
$scope$;

REVOKE TRUNCATE ON TABLE
  public.couriers,
  public.customers,
  public.day_closes,
  public.email_send_log,
  public.email_send_state,
  public.email_unsubscribe_tokens,
  public.expenses,
  public.financial_audit_log,
  public.order_items,
  public.orders,
  public.payments,
  public.platform_admin_audit_log,
  public.platform_admins,
  public.products,
  public.profiles,
  public.security_scan_findings,
  public.security_scan_runs,
  public.subscriptions,
  public.suppressed_emails,
  public.tenant_counters,
  public.tenants,
  public.user_roles
FROM anon, authenticated, PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
  REVOKE TRUNCATE ON TABLES FROM anon, authenticated, PUBLIC;

COMMIT;
