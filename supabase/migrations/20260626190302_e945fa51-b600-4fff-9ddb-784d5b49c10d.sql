-- Revoke EXECUTE from authenticated on internal-only SECURITY DEFINER helpers
-- that are never called directly by the client (only invoked from within other
-- SECURITY DEFINER functions, which run as their owner and don't need the
-- caller to hold EXECUTE).
REVOKE EXECUTE ON FUNCTION public._assert_owner(uuid) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public._assert_platform_admin() FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public._assert_staff(uuid) FROM PUBLIC, anon, authenticated;