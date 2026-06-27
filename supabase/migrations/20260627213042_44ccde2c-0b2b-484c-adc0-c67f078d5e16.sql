
-- 1) Tables
CREATE TABLE public.security_scan_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  status text NOT NULL DEFAULT 'running',
  triggered_by text NOT NULL DEFAULT 'cron',
  new_count int NOT NULL DEFAULT 0,
  total_count int NOT NULL DEFAULT 0,
  error text
);
GRANT SELECT ON public.security_scan_runs TO authenticated;
GRANT ALL ON public.security_scan_runs TO service_role;
ALTER TABLE public.security_scan_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "platform admins read runs" ON public.security_scan_runs
  FOR SELECT TO authenticated USING (public.is_platform_admin());

CREATE TABLE public.security_scan_findings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanner text NOT NULL,
  level text NOT NULL CHECK (level IN ('error','warn','info')),
  name text NOT NULL,
  title text NOT NULL,
  detail text,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  fingerprint text NOT NULL UNIQUE,
  first_seen_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz,
  last_run_id uuid REFERENCES public.security_scan_runs(id) ON DELETE SET NULL
);
CREATE INDEX security_scan_findings_open_idx
  ON public.security_scan_findings (resolved_at, level);
GRANT SELECT ON public.security_scan_findings TO authenticated;
GRANT ALL ON public.security_scan_findings TO service_role;
ALTER TABLE public.security_scan_findings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "platform admins read findings" ON public.security_scan_findings
  FOR SELECT TO authenticated USING (public.is_platform_admin());

-- 2) Scan function (SECURITY DEFINER; self-guards by caller role)
CREATE OR REPLACE FUNCTION public.run_security_scan(p_triggered_by text DEFAULT 'manual')
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_run_id uuid;
  v_new int := 0;
  v_total int := 0;
  r record;
  v_fp text;
  v_caller_role text := current_setting('role', true);
BEGIN
  -- Allow only: service_role, supabase_admin (cron), or platform admins
  IF current_user NOT IN ('service_role','supabase_admin','postgres')
     AND NOT public.is_platform_admin() THEN
    RAISE EXCEPTION 'forbidden';
  END IF;

  INSERT INTO public.security_scan_runs(started_at, status, triggered_by)
  VALUES (now(), 'running', p_triggered_by)
  RETURNING id INTO v_run_id;

  -- Check 1: public tables without RLS
  FOR r IN
    SELECT c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r' AND NOT c.relrowsecurity
  LOOP
    v_fp := 'rls_disabled:' || r.table_name;
    INSERT INTO public.security_scan_findings(scanner, level, name, title, detail, metadata, fingerprint, last_run_id)
    VALUES ('internal_rls_check','error','rls_disabled','RLS غير مفعّل',
            'الجدول public.' || r.table_name || ' بدون Row Level Security',
            jsonb_build_object('table', r.table_name), v_fp, v_run_id)
    ON CONFLICT (fingerprint) DO UPDATE
      SET last_seen_at = now(), resolved_at = NULL, last_run_id = v_run_id;
    v_total := v_total + 1;
  END LOOP;

  -- Check 2: public tables with RLS enabled but zero policies
  FOR r IN
    SELECT c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity
      AND NOT EXISTS (SELECT 1 FROM pg_policy pol WHERE pol.polrelid = c.oid)
  LOOP
    v_fp := 'rls_no_policy:' || r.table_name;
    INSERT INTO public.security_scan_findings(scanner, level, name, title, detail, metadata, fingerprint, last_run_id)
    VALUES ('internal_rls_check','warn','rls_no_policy','RLS مفعّل بدون سياسات',
            'public.' || r.table_name || ' بدون أي policy — كل الوصول محجوب.',
            jsonb_build_object('table', r.table_name), v_fp, v_run_id)
    ON CONFLICT (fingerprint) DO UPDATE
      SET last_seen_at = now(), resolved_at = NULL, last_run_id = v_run_id;
    v_total := v_total + 1;
  END LOOP;

  -- Check 3: SECURITY DEFINER functions executable by anon or PUBLIC
  FOR r IN
    SELECT p.proname,
           CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE rol.rolname END AS grantee_name
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    CROSS JOIN LATERAL aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
    LEFT JOIN pg_roles rol ON rol.oid = a.grantee
    WHERE n.nspname = 'public'
      AND p.prosecdef = true
      AND a.privilege_type = 'EXECUTE'
      AND (a.grantee = 0 OR rol.rolname = 'anon')
      AND p.proname NOT IN ('has_role','is_platform_admin')
  LOOP
    v_fp := 'sec_definer_public_exec:' || r.proname || ':' || r.grantee_name;
    INSERT INTO public.security_scan_findings(scanner, level, name, title, detail, metadata, fingerprint, last_run_id)
    VALUES ('internal_rls_check','error','sec_definer_public_exec',
            'دالة SECURITY DEFINER مكشوفة',
            'public.' || r.proname || ' قابلة للتنفيذ من ' || r.grantee_name,
            jsonb_build_object('function', r.proname, 'grantee', r.grantee_name),
            v_fp, v_run_id)
    ON CONFLICT (fingerprint) DO UPDATE
      SET last_seen_at = now(), resolved_at = NULL, last_run_id = v_run_id;
    v_total := v_total + 1;
  END LOOP;

  -- Check 4: public tables granted SELECT to anon without an anon policy (data leak risk)
  FOR r IN
    SELECT c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public' AND c.relkind = 'r'
      AND has_table_privilege('anon', c.oid, 'SELECT')
      AND NOT EXISTS (
        SELECT 1 FROM pg_policy pol
        WHERE pol.polrelid = c.oid
          AND ('anon' = ANY (SELECT rolname FROM pg_roles WHERE oid = ANY (coalesce(pol.polroles, '{0}'::oid[])))
               OR 0 = ANY (coalesce(pol.polroles, '{0}'::oid[])))
      )
  LOOP
    v_fp := 'anon_select_no_policy:' || r.table_name;
    INSERT INTO public.security_scan_findings(scanner, level, name, title, detail, metadata, fingerprint, last_run_id)
    VALUES ('internal_rls_check','warn','anon_select_no_policy',
            'صلاحية SELECT لـ anon بدون policy مطابقة',
            'public.' || r.table_name || ' معطى لها GRANT SELECT لـ anon لكن لا يوجد policy لـ anon — قد يكون مقصودًا أو خطأ.',
            jsonb_build_object('table', r.table_name), v_fp, v_run_id)
    ON CONFLICT (fingerprint) DO UPDATE
      SET last_seen_at = now(), resolved_at = NULL, last_run_id = v_run_id;
    v_total := v_total + 1;
  END LOOP;

  -- Mark resolved any open finding not seen in this run
  UPDATE public.security_scan_findings
  SET resolved_at = now()
  WHERE resolved_at IS NULL
    AND (last_run_id IS DISTINCT FROM v_run_id);

  SELECT count(*) INTO v_new
  FROM public.security_scan_findings
  WHERE last_run_id = v_run_id AND first_seen_at = last_seen_at;

  UPDATE public.security_scan_runs
  SET finished_at = now(), status = 'success', new_count = v_new, total_count = v_total
  WHERE id = v_run_id;

  RETURN jsonb_build_object('run_id', v_run_id, 'new_count', v_new, 'total_count', v_total);
END;
$$;

REVOKE EXECUTE ON FUNCTION public.run_security_scan(text) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.run_security_scan(text) TO authenticated, service_role;

-- 3) pg_cron: weekly Sunday 01:00 UTC (03:00 Africa/Tripoli)
CREATE EXTENSION IF NOT EXISTS pg_cron;

DO $$ BEGIN
  PERFORM cron.unschedule('mongezz-weekly-security-scan');
EXCEPTION WHEN OTHERS THEN NULL; END $$;

SELECT cron.schedule(
  'mongezz-weekly-security-scan',
  '0 1 * * 0',
  $cron$ SELECT public.run_security_scan('cron'); $cron$
);
