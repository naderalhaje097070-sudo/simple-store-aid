-- B2 / AC-01: invoker authorization before scanner side effects.
BEGIN;
CREATE OR REPLACE FUNCTION public.run_security_scan(p_triggered_by text DEFAULT 'manual'::text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog', 'pg_temp'
AS $function$
DECLARE
  v_run_id uuid;
  v_new int := 0;
  v_total int := 0;
  r record;
  v_fp text;
  v_caller_role text := current_setting('role', true);
BEGIN
  PERFORM monjez_private.assert_active_actor();
  -- SECURITY DEFINER changes current_user to the function owner. Authorize the
  -- connection role instead, preserving the existing trusted service/cron boundary.
  IF (
    v_caller_role IN ('service_role', 'supabase_admin')
    OR (v_caller_role = 'none' AND session_user IN ('postgres', 'supabase_admin'))
    OR (v_caller_role = 'authenticated' AND public.is_platform_admin())
  ) IS DISTINCT FROM true THEN
    RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'forbidden_platform_admin';
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
$function$;
COMMIT;
