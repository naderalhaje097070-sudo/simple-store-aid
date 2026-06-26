
-- Tighten EXECUTE on SECURITY DEFINER helpers and the audit-log RPC.
-- Internal helpers are used only inside RLS policies / other SECURITY DEFINER
-- functions, so signed-in users do not need direct EXECUTE.
REVOKE EXECUTE ON FUNCTION public.has_role(uuid, uuid, public.app_role) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.has_owner_role(uuid, uuid) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.has_staff_or_owner_role(uuid, uuid) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.current_tenant_id() FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.is_platform_admin() FROM PUBLIC, anon, authenticated;

-- The audit-log RPC had PUBLIC + anon EXECUTE leftover; restrict to authenticated only
-- (it self-checks via _assert_platform_admin).
REVOKE EXECUTE ON FUNCTION public.get_platform_admin_audit_log(integer, integer) FROM PUBLIC, anon;
