-- Fresh-database prerequisite for migration 20260626191523.
-- That migration creates policies, indexes, and logging functions against this
-- table before the later idempotent hardening migration recreates its grants.
CREATE TABLE IF NOT EXISTS public.platform_admin_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

REVOKE ALL ON public.platform_admin_audit_log FROM PUBLIC;
REVOKE ALL ON public.platform_admin_audit_log FROM anon;
GRANT SELECT ON public.platform_admin_audit_log TO authenticated;
GRANT ALL ON public.platform_admin_audit_log TO service_role;

ALTER TABLE public.platform_admin_audit_log ENABLE ROW LEVEL SECURITY;
