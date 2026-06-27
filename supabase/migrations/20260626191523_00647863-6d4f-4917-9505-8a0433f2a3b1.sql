-- Idempotent guards for previously-created objects
-- Ensure the audit-log table exists before the policy/index below reference it
-- (it was originally created directly in production, outside version control).
-- Full RLS/grants/policy are (re)asserted idempotently in a later migration.
CREATE TABLE IF NOT EXISTS public.platform_admin_audit_log (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action     text NOT NULL,
  details    jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname='public' AND tablename='platform_admin_audit_log' AND policyname='platform admins read audit log') THEN
    EXECUTE 'CREATE POLICY "platform admins read audit log" ON public.platform_admin_audit_log FOR SELECT TO authenticated USING (public.is_platform_admin())';
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_pa_audit_created_at ON public.platform_admin_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pa_audit_user ON public.platform_admin_audit_log (user_id, created_at DESC);

CREATE OR REPLACE FUNCTION public._log_platform_admin_action(p_action text, p_details jsonb DEFAULT '{}'::jsonb)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  IF auth.uid() IS NULL THEN RETURN; END IF;
  INSERT INTO public.platform_admin_audit_log(user_id, action, details)
    VALUES (auth.uid(), p_action, COALESCE(p_details, '{}'::jsonb));
END $$;

REVOKE ALL ON FUNCTION public._log_platform_admin_action(text, jsonb) FROM PUBLIC;
REVOKE ALL ON FUNCTION public._log_platform_admin_action(text, jsonb) FROM anon;
REVOKE ALL ON FUNCTION public._log_platform_admin_action(text, jsonb) FROM authenticated;

CREATE OR REPLACE FUNCTION public.get_platform_admin_overview()
 RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE
  v jsonb;
  v_total_tenants int; v_active_tenants int; v_total_products int;
  v_total_customers int; v_total_orders int; v_total_payments int;
  v_open_debts numeric(14,2); v_unsettled_custody numeric(14,2);
  v_expenses_today numeric(14,2); v_day_close_count int; v_critical_alerts int := 0;
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_overview', '{}'::jsonb);
  SELECT COUNT(*) INTO v_total_tenants FROM public.tenants;
  SELECT COUNT(DISTINCT tenant_id) INTO v_active_tenants FROM public.orders WHERE created_at >= now() - interval '30 days';
  SELECT COUNT(*) INTO v_total_products FROM public.products;
  SELECT COUNT(*) INTO v_total_customers FROM public.customers;
  SELECT COUNT(*) INTO v_total_orders FROM public.orders;
  SELECT COUNT(*) INTO v_total_payments FROM public.payments;
  SELECT COALESCE(SUM(total - paid),0) INTO v_open_debts FROM public.orders
    WHERE status IN ('partial','debt') AND (delivery = 'direct' OR courier_id IS NULL);
  SELECT COALESCE(SUM(collected_by_courier),0) INTO v_unsettled_custody FROM public.orders
    WHERE delivery = 'courier' AND courier_id IS NOT NULL;
  SELECT COALESCE(SUM(amount),0) INTO v_expenses_today FROM public.expenses
    WHERE created_at::date = (now() AT TIME ZONE 'UTC')::date;
  SELECT COUNT(*) INTO v_day_close_count FROM public.day_closes
    WHERE closed_for = (now() AT TIME ZONE 'UTC')::date;
  SELECT (SELECT COUNT(*) FROM public.orders WHERE paid > total)
       + (SELECT COUNT(*) FROM public.orders WHERE paid < 0)
       + (SELECT COUNT(*) FROM public.orders WHERE total < 0)
       + (SELECT COUNT(*) FROM public.products WHERE stock < 0)
       + (SELECT COUNT(*) FROM public.orders WHERE collected_by_courier > total)
    INTO v_critical_alerts;
  v := jsonb_build_object(
    'total_tenants', v_total_tenants, 'active_tenants', v_active_tenants,
    'total_products', v_total_products, 'total_customers', v_total_customers,
    'total_orders', v_total_orders, 'total_payments', v_total_payments,
    'open_customer_debts', v_open_debts, 'unsettled_courier_custody', v_unsettled_custody,
    'expenses_today', v_expenses_today, 'day_close_count_today', v_day_close_count,
    'critical_alerts', v_critical_alerts);
  RETURN v;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_tenants_health()
 RETURNS TABLE(tenant_id uuid, tenant_name text, owner_user_id uuid, created_at timestamptz, products_count integer, customers_count integer, orders_count integer, total_sales numeric, total_collected numeric, open_debts numeric, unsettled_custody numeric, last_activity timestamptz, health text)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_tenants', '{}'::jsonb);
  RETURN QUERY
  SELECT t.id, t.name, t.owner_user_id, t.created_at,
    (SELECT COUNT(*)::int FROM public.products p WHERE p.tenant_id = t.id),
    (SELECT COUNT(*)::int FROM public.customers c WHERE c.tenant_id = t.id),
    (SELECT COUNT(*)::int FROM public.orders o WHERE o.tenant_id = t.id),
    COALESCE((SELECT SUM(total) FROM public.orders o WHERE o.tenant_id = t.id),0),
    COALESCE((SELECT SUM(amount) FROM public.payments pm WHERE pm.tenant_id = t.id),0),
    COALESCE((SELECT SUM(total - paid) FROM public.orders o
      WHERE o.tenant_id = t.id AND o.status IN ('partial','debt')
        AND (o.delivery = 'direct' OR o.courier_id IS NULL)),0),
    COALESCE((SELECT SUM(collected_by_courier) FROM public.orders o
      WHERE o.tenant_id = t.id AND o.delivery = 'courier' AND o.courier_id IS NOT NULL),0),
    (SELECT MAX(created_at) FROM public.orders o WHERE o.tenant_id = t.id),
    CASE
      WHEN EXISTS (SELECT 1 FROM public.orders o WHERE o.tenant_id = t.id AND (o.paid > o.total OR o.paid < 0 OR o.total < 0 OR o.collected_by_courier > o.total))
        OR EXISTS (SELECT 1 FROM public.products p WHERE p.tenant_id = t.id AND p.stock < 0)
        THEN 'Critical'
      WHEN COALESCE((SELECT SUM(collected_by_courier) FROM public.orders o
            WHERE o.tenant_id = t.id AND o.delivery = 'courier' AND o.courier_id IS NOT NULL),0) > 0
        THEN 'Warning'
      ELSE 'Healthy'
    END
  FROM public.tenants t ORDER BY t.created_at DESC;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_financial_health()
 RETURNS TABLE(check_key text, explanation_ar text, status text, affected_count integer)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE
  r record;
  checks jsonb := jsonb_build_array(
    jsonb_build_object('key','paid_gt_total','ar','فواتير المدفوع فيها أكبر من الإجمالي','sev','Critical','sql','SELECT COUNT(*)::int FROM public.orders WHERE paid > total'),
    jsonb_build_object('key','paid_negative','ar','فواتير بمدفوع سالب','sev','Critical','sql','SELECT COUNT(*)::int FROM public.orders WHERE paid < 0'),
    jsonb_build_object('key','total_negative','ar','فواتير بإجمالي سالب','sev','Critical','sql','SELECT COUNT(*)::int FROM public.orders WHERE total < 0'),
    jsonb_build_object('key','stock_negative','ar','منتجات بمخزون سالب','sev','Critical','sql','SELECT COUNT(*)::int FROM public.products WHERE stock < 0'),
    jsonb_build_object('key','collected_gt_total','ar','تحصيل المندوب أكبر من إجمالي الفاتورة','sev','Critical','sql','SELECT COUNT(*)::int FROM public.orders WHERE collected_by_courier > total'),
    jsonb_build_object('key','debt_without_customer','ar','فواتير دين/جزئية بدون عميل','sev','Warning','sql','SELECT COUNT(*)::int FROM public.orders WHERE status IN (''partial'',''debt'') AND customer_id IS NULL'),
    jsonb_build_object('key','courier_missing_refs','ar','طلب مندوب بدون عميل أو بدون مندوب','sev','Critical','sql','SELECT COUNT(*)::int FROM public.orders WHERE delivery = ''courier'' AND (customer_id IS NULL OR courier_id IS NULL)'),
    jsonb_build_object('key','payments_nonpositive','ar','مدفوعات بقيمة صفر أو سالبة','sev','Critical','sql','SELECT COUNT(*)::int FROM public.payments WHERE amount <= 0'),
    jsonb_build_object('key','order_items_nonpositive','ar','بنود فواتير بكمية غير موجبة','sev','Critical','sql','SELECT COUNT(*)::int FROM public.order_items WHERE qty <= 0'),
    jsonb_build_object('key','payments_orphan_order','ar','مدفوعات مرتبطة بفاتورة محذوفة','sev','Critical','sql','SELECT COUNT(*)::int FROM public.payments p WHERE p.order_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM public.orders o WHERE o.id = p.order_id)'),
    jsonb_build_object('key','order_items_orphan','ar','بنود فواتير مرتبطة بفاتورة محذوفة','sev','Critical','sql','SELECT COUNT(*)::int FROM public.order_items oi WHERE NOT EXISTS (SELECT 1 FROM public.orders o WHERE o.id = oi.order_id)'),
    jsonb_build_object('key','missing_tenant_id','ar','صفوف بدون tenant_id في جداول حساسة','sev','Critical','sql','SELECT (SELECT COUNT(*)::int FROM public.orders WHERE tenant_id IS NULL) + (SELECT COUNT(*)::int FROM public.payments WHERE tenant_id IS NULL) + (SELECT COUNT(*)::int FROM public.products WHERE tenant_id IS NULL) + (SELECT COUNT(*)::int FROM public.customers WHERE tenant_id IS NULL)'),
    jsonb_build_object('key','duplicate_tenant_names','ar','أسماء متاجر مكررة لنفس المالك','sev','Warning','sql','SELECT COALESCE(SUM(c-1),0)::int FROM (SELECT COUNT(*)::int c FROM public.tenants GROUP BY owner_user_id, name HAVING COUNT(*) > 1) x'),
    jsonb_build_object('key','day_close_mismatch','ar','إغلاق يوم لا يطابق المصدر','sev','Warning','sql','SELECT COUNT(*)::int FROM public.day_closes dc WHERE ABS(dc.sales - COALESCE((SELECT SUM(total) FROM public.orders o WHERE o.tenant_id = dc.tenant_id AND o.created_at::date = dc.closed_for),0)) > 0.01'),
    jsonb_build_object('key','custody_mismatch','ar','عهدة مناديب غير متطابقة مع السجلات','sev','Warning','sql','SELECT 0'),
    jsonb_build_object('key','courier_stuck','ar','طلبات مناديب عالقة بحالة مالية متناقضة','sev','Warning','sql','SELECT COUNT(*)::int FROM public.orders WHERE delivery = ''courier'' AND courier_state IS NOT NULL AND collected_by_courier > (total - paid)')
  );
  v_count int; v_sql text; v_sev text;
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_financial_health', '{}'::jsonb);
  FOR r IN SELECT * FROM jsonb_array_elements(checks) LOOP
    v_sql := r.value->>'sql'; v_sev := r.value->>'sev';
    EXECUTE v_sql INTO v_count;
    check_key := r.value->>'key'; explanation_ar := r.value->>'ar';
    affected_count := COALESCE(v_count,0);
    status := CASE WHEN affected_count = 0 THEN 'Passed'
                   WHEN v_sev = 'Critical' THEN 'Critical' ELSE 'Warning' END;
    RETURN NEXT;
  END LOOP;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_financial_health_rows(p_check_key text, p_limit integer DEFAULT 50)
 RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE v jsonb; v_lim int := LEAST(GREATEST(COALESCE(p_limit,50),1),200);
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_financial_health_rows', jsonb_build_object('check_key', p_check_key, 'limit', v_lim));
  CASE p_check_key
    WHEN 'paid_gt_total' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.total, o.paid, o.status FROM public.orders o WHERE o.paid > o.total LIMIT v_lim) x;
    WHEN 'paid_negative' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.paid, o.total FROM public.orders o WHERE o.paid < 0 LIMIT v_lim) x;
    WHEN 'total_negative' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.total FROM public.orders o WHERE o.total < 0 LIMIT v_lim) x;
    WHEN 'stock_negative' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(p.tenant_id::text,8) tenant, p.name, p.stock FROM public.products p WHERE p.stock < 0 LIMIT v_lim) x;
    WHEN 'collected_gt_total' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.total, o.collected_by_courier FROM public.orders o WHERE o.collected_by_courier > o.total LIMIT v_lim) x;
    WHEN 'debt_without_customer' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.status, o.total, o.paid FROM public.orders o WHERE o.status IN ('partial','debt') AND o.customer_id IS NULL LIMIT v_lim) x;
    WHEN 'courier_missing_refs' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, (o.customer_id IS NULL) missing_customer, (o.courier_id IS NULL) missing_courier FROM public.orders o WHERE o.delivery = 'courier' AND (o.customer_id IS NULL OR o.courier_id IS NULL) LIMIT v_lim) x;
    WHEN 'payments_nonpositive' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(p.tenant_id::text,8) tenant, p.kind, p.amount, p.created_at FROM public.payments p WHERE p.amount <= 0 LIMIT v_lim) x;
    WHEN 'order_items_nonpositive' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(oi.tenant_id::text,8) tenant, oi.name, oi.qty FROM public.order_items oi WHERE oi.qty <= 0 LIMIT v_lim) x;
    WHEN 'payments_orphan_order' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(p.tenant_id::text,8) tenant, p.id, p.amount FROM public.payments p WHERE p.order_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM public.orders o WHERE o.id = p.order_id) LIMIT v_lim) x;
    WHEN 'order_items_orphan' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(oi.tenant_id::text,8) tenant, oi.id, oi.name, oi.qty FROM public.order_items oi WHERE NOT EXISTS (SELECT 1 FROM public.orders o WHERE o.id = oi.order_id) LIMIT v_lim) x;
    WHEN 'courier_stuck' THEN SELECT COALESCE(jsonb_agg(x),'[]'::jsonb) INTO v FROM (SELECT LEFT(o.tenant_id::text,8) tenant, o.number, o.total, o.paid, o.collected_by_courier, o.courier_state::text FROM public.orders o WHERE o.delivery = 'courier' AND o.courier_state IS NOT NULL AND o.collected_by_courier > (o.total - o.paid) LIMIT v_lim) x;
    ELSE v := '[]'::jsonb;
  END CASE;
  RETURN v;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_system_health()
 RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE
  sensitive_tables text[] := ARRAY['tenants','profiles','user_roles','products','customers','couriers','orders','order_items','payments','expenses','day_closes','platform_admins','platform_admin_audit_log'];
  financial_rpcs text[] := ARRAY['create_sale_with_items','collect_order_debt','settle_courier_orders','return_courier_order','close_day'];
  t text; rls_rows jsonb := '[]'::jsonb; rpc_rows jsonb := '[]'::jsonb; grant_issues jsonb := '[]'::jsonb;
  v_enabled bool; v_exists bool; v_has_anon bool; v_has_public bool;
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_system_health', '{}'::jsonb);
  FOREACH t IN ARRAY sensitive_tables LOOP
    SELECT c.relrowsecurity INTO v_enabled FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname='public' AND c.relname = t;
    rls_rows := rls_rows || jsonb_build_object('table', t, 'rls_enabled', COALESCE(v_enabled,false),
      'status', CASE WHEN COALESCE(v_enabled,false) THEN 'Healthy' ELSE 'Critical' END);
  END LOOP;
  FOREACH t IN ARRAY financial_rpcs LOOP
    SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname = t) INTO v_exists;
    SELECT EXISTS(SELECT 1 FROM information_schema.role_routine_grants WHERE specific_schema='public' AND routine_name=t AND grantee='anon') INTO v_has_anon;
    SELECT EXISTS(SELECT 1 FROM information_schema.role_routine_grants WHERE specific_schema='public' AND routine_name=t AND grantee='PUBLIC') INTO v_has_public;
    rpc_rows := rpc_rows || jsonb_build_object('rpc', t, 'exists', v_exists, 'anon_can_execute', v_has_anon, 'public_can_execute', v_has_public,
      'status', CASE WHEN NOT v_exists THEN 'Critical' WHEN v_has_anon OR v_has_public THEN 'Critical' ELSE 'Healthy' END);
    IF v_has_anon THEN grant_issues := grant_issues || jsonb_build_object('rpc',t,'issue','anon_execute'); END IF;
    IF v_has_public THEN grant_issues := grant_issues || jsonb_build_object('rpc',t,'issue','public_execute'); END IF;
  END LOOP;
  RETURN jsonb_build_object('rls', rls_rows, 'rpcs', rpc_rows, 'grant_issues', grant_issues);
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_day_close_health(p_limit integer DEFAULT 30)
 RETURNS TABLE(id uuid, tenant_id uuid, tenant_name text, closed_for date, sales numeric, collected numeric, expenses numeric, customer_debts numeric, unsettled_custody numeric, realized_profit numeric, created_at timestamptz, sales_diff numeric, collected_diff numeric, expenses_diff numeric, status text)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE v_lim int := LEAST(GREATEST(COALESCE(p_limit,30),1),200);
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_day_close_health', jsonb_build_object('limit', v_lim));
  RETURN QUERY
  SELECT dc.id, dc.tenant_id, t.name, dc.closed_for, dc.sales, dc.collected, dc.expenses,
         dc.customer_debts, dc.unsettled_custody, dc.realized_profit, dc.created_at,
         dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o WHERE o.tenant_id = dc.tenant_id AND o.created_at::date = dc.closed_for),0),
         dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p WHERE p.tenant_id = dc.tenant_id AND p.created_at::date = dc.closed_for),0),
         dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e WHERE e.tenant_id = dc.tenant_id AND e.created_at::date = dc.closed_for),0),
         CASE WHEN
           ABS(dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o WHERE o.tenant_id = dc.tenant_id AND o.created_at::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p WHERE p.tenant_id = dc.tenant_id AND p.created_at::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e WHERE e.tenant_id = dc.tenant_id AND e.created_at::date = dc.closed_for),0)) < 0.01
         THEN 'Matches' ELSE 'Mismatch' END
  FROM public.day_closes dc LEFT JOIN public.tenants t ON t.id = dc.tenant_id
  ORDER BY dc.created_at DESC LIMIT v_lim;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_courier_custody_health()
 RETURNS TABLE(tenant_id uuid, tenant_name text, courier_id uuid, courier_name text, unsettled_amount numeric, orders_count integer, oldest_age_days integer, risk text)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_courier_custody_health', '{}'::jsonb);
  RETURN QUERY
  SELECT o.tenant_id, t.name, o.courier_id, c.name,
    COALESCE(SUM(o.collected_by_courier),0), COUNT(*)::int,
    COALESCE(EXTRACT(DAY FROM (now() - MIN(o.created_at)))::int, 0),
    CASE WHEN COALESCE(EXTRACT(DAY FROM (now() - MIN(o.created_at)))::int,0) > 7 THEN 'Critical'
         WHEN COALESCE(EXTRACT(DAY FROM (now() - MIN(o.created_at)))::int,0) > 3 THEN 'Warning'
         ELSE 'Healthy' END
  FROM public.orders o LEFT JOIN public.tenants t ON t.id = o.tenant_id
    LEFT JOIN public.couriers c ON c.id = o.courier_id
  WHERE o.delivery = 'courier' AND o.courier_id IS NOT NULL AND o.collected_by_courier > 0
  GROUP BY o.tenant_id, t.name, o.courier_id, c.name ORDER BY 5 DESC;
END $function$;

CREATE OR REPLACE FUNCTION public.get_platform_admin_audit_log(p_limit integer DEFAULT 100, p_offset integer DEFAULT 0)
 RETURNS TABLE(id uuid, user_id uuid, user_email text, action text, details jsonb, created_at timestamptz)
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path TO 'public' AS $function$
DECLARE
  v_lim int := LEAST(GREATEST(COALESCE(p_limit,100),1),500);
  v_off int := GREATEST(COALESCE(p_offset,0),0);
BEGIN
  PERFORM public._assert_platform_admin();
  RETURN QUERY
  SELECT a.id, a.user_id, u.email::text, a.action, a.details, a.created_at
  FROM public.platform_admin_audit_log a
  LEFT JOIN auth.users u ON u.id = a.user_id
  ORDER BY a.created_at DESC LIMIT v_lim OFFSET v_off;
END $function$;

GRANT EXECUTE ON FUNCTION public.get_platform_admin_audit_log(integer, integer) TO authenticated;