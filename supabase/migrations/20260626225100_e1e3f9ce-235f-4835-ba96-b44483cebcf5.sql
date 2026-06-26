-- Restore EXECUTE on RLS helper functions to authenticated.
-- These SECURITY DEFINER helpers are invoked by RLS policies on every table read/write;
-- without EXECUTE, all policy checks fail with "permission denied for function".
-- Safe: each function only reads its own scoped row (profiles by auth.uid(), user_roles by user+tenant).
GRANT EXECUTE ON FUNCTION public.current_tenant_id() TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_role(uuid, uuid, public.app_role) TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_owner_role(uuid, uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_staff_or_owner_role(uuid, uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION public.is_platform_admin() TO authenticated;