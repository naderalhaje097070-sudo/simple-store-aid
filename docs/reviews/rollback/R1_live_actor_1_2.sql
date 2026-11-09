BEGIN;
SET LOCAL lock_timeout = '5s';
DO $g$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ROLLBACK_REQUIRES_POSTGRES'; END IF; END $g$;
DO $pre$ BEGIN
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version IN ('20261013120223','20261013221918','20261020210549','20261021080927','20261021132651','20261021134621','20261021140746')) THEN RAISE EXCEPTION 'ROLLBACK_ORDER_VIOLATION: undo later stages first'; END IF;
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN ('20261010223557','20261010225012')) <> 2 THEN RAISE EXCEPTION 'STAGE_NOT_APPLIED: nothing to undo'; END IF;
  IF NOT EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261107214500') THEN RAISE EXCEPTION 'EMAIL_HOTFIX_MISSING'; END IF;
END $pre$;
-- Undo 20261010223557 + 20261010225012: 33 functions restored to the exact production definitions captured before the change;
-- the 22 RESTRICTIVE policies dropped. Schema monjez_private, its functions and tables are KEPT (unused, no data loss).
CREATE OR REPLACE FUNCTION public._assert_owner(_tid uuid)
 RETURNS void
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
BEGIN
  IF _tid IS NULL OR _tid <> public.current_tenant_id() THEN
    RAISE EXCEPTION 'forbidden_tenant';
  END IF;
  IF NOT public.has_owner_role(auth.uid(), _tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
END $function$;
CREATE OR REPLACE FUNCTION public._assert_platform_admin()
 RETURNS void
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
BEGIN
  IF NOT public.is_platform_admin() THEN
    RAISE EXCEPTION 'forbidden_platform_admin';
  END IF;
END $function$;
CREATE OR REPLACE FUNCTION public._assert_staff(_tid uuid)
 RETURNS void
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
BEGIN
  IF _tid IS NULL OR _tid <> public.current_tenant_id() THEN
    RAISE EXCEPTION 'forbidden_tenant';
  END IF;
  IF NOT public.has_staff_or_owner_role(auth.uid(), _tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
END $function$;
CREATE OR REPLACE FUNCTION public.close_day(p_note text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_tz text := public.current_tenant_timezone();
  v_today date := (now() AT TIME ZONE v_tz)::date;
  v_sales numeric(12,2) := 0;
  v_collected numeric(12,2) := 0;
  v_expenses numeric(12,2) := 0;
  v_customer_debts numeric(12,2) := 0;
  v_unsettled_custody numeric(12,2) := 0;
  v_realized_profit numeric(12,2) := 0;
BEGIN
  PERFORM public._assert_owner(v_tenant);

  SELECT COALESCE(SUM(total), 0) INTO v_sales
    FROM public.orders
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_collected
    FROM public.payments
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(amount), 0) INTO v_expenses
    FROM public.expenses
   WHERE tenant_id = v_tenant
     AND (created_at AT TIME ZONE v_tz)::date = v_today;

  SELECT COALESCE(SUM(
    CASE
      WHEN courier_state = 'returned' THEN 0
      WHEN delivery = 'direct' OR courier_id IS NULL THEN GREATEST(total - paid, 0)
      WHEN delivery = 'courier' AND courier_state = 'delivered_none' THEN total
      WHEN delivery = 'courier' AND courier_state = 'delivered_partial' THEN GREATEST(total - collected_by_courier, 0)
      ELSE 0
    END), 0) INTO v_customer_debts
    FROM public.orders
   WHERE tenant_id = v_tenant AND status IN ('partial','debt');

  SELECT COALESCE(SUM(collected_by_courier), 0) INTO v_unsettled_custody
    FROM public.orders
   WHERE tenant_id = v_tenant AND delivery = 'courier' AND courier_id IS NOT NULL;

  SELECT COALESCE(SUM(
    CASE WHEN o.total > 0
      THEN (p.amount / o.total) *
           (SELECT COALESCE(SUM((oi.unit_price - oi.unit_cost) * oi.qty),0)
              FROM public.order_items oi WHERE oi.order_id = o.id)
      ELSE 0 END
  ), 0) INTO v_realized_profit
  FROM public.payments p
  JOIN public.orders o ON o.id = p.order_id
  WHERE p.tenant_id = v_tenant
    AND (p.created_at AT TIME ZONE v_tz)::date = v_today
    AND p.order_id IS NOT NULL;

  INSERT INTO public.day_closes(
    tenant_id, closed_for, sales, collected, expenses,
    realized_profit, customer_debts, unsettled_custody, note, created_by
  ) VALUES (
    v_tenant, v_today, v_sales, v_collected, v_expenses,
    v_realized_profit, v_customer_debts, v_unsettled_custody, p_note, v_uid
  )
  ON CONFLICT (tenant_id, closed_for) DO UPDATE SET
    sales = EXCLUDED.sales,
    collected = EXCLUDED.collected,
    expenses = EXCLUDED.expenses,
    realized_profit = EXCLUDED.realized_profit,
    customer_debts = EXCLUDED.customer_debts,
    unsettled_custody = EXCLUDED.unsettled_custody,
    note = EXCLUDED.note;

  RETURN jsonb_build_object(
    'success', true, 'sales', v_sales, 'collected', v_collected, 'expenses', v_expenses,
    'realized_profit', v_realized_profit, 'customer_debts', v_customer_debts,
    'unsettled_custody', v_unsettled_custody
  );
END $function$;
CREATE OR REPLACE FUNCTION public.collect_order_debt(p_order_id uuid, p_amount numeric, p_method payment_method)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_uid uuid := auth.uid();
  v_order public.orders%ROWTYPE;
  v_remaining numeric(12,2);
  v_new_paid numeric(12,2);
  v_status order_status;
BEGIN
  IF p_amount IS NULL OR p_amount <= 0 THEN
    RAISE EXCEPTION 'invalid_amount';
  END IF;
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.courier_state = 'returned' THEN
    RAISE EXCEPTION 'cannot_collect_returned_order';
  END IF;

  IF v_order.delivery = 'courier' AND v_order.courier_id IS NOT NULL THEN
    IF COALESCE(v_order.collected_by_courier, 0) > 0
       OR v_order.courier_state IN ('pending','delivered_partial','delivered_full') THEN
      RAISE EXCEPTION 'settle_courier_first';
    END IF;
  END IF;

  v_remaining := v_order.total - v_order.paid;
  IF p_amount > v_remaining THEN
    RAISE EXCEPTION 'amount_exceeds_remaining';
  END IF;
  v_new_paid := v_order.paid + p_amount;
  v_status := CASE
    WHEN v_new_paid >= v_order.total THEN 'paid'::order_status
    WHEN v_new_paid > 0 THEN 'partial'::order_status
    ELSE 'debt'::order_status
  END;
  UPDATE public.orders SET paid = v_new_paid, status = v_status WHERE id = p_order_id;
  INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, created_by)
    VALUES (v_order.tenant_id, 'debt_collection', p_method, p_amount, p_order_id, v_order.customer_id, v_uid);

  RETURN jsonb_build_object('success', true, 'new_paid', v_new_paid, 'status', v_status);
END $function$;
CREATE OR REPLACE FUNCTION public.create_sale_with_items(p_customer_id uuid, p_delivery delivery_kind, p_courier_id uuid, p_paid numeric, p_method payment_method, p_items jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid    uuid := auth.uid();
  v_total  numeric(12,2) := 0;
  v_status order_status;
  v_order  public.orders%ROWTYPE;
  v_tnum   int;
  v_item   jsonb;
  v_pid    uuid;
  v_qty    numeric(12,2);
  v_prod   public.products%ROWTYPE;
  v_order_paid          numeric(12,2);
  v_order_collected     numeric(12,2);
  v_order_courier_state courier_state;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN RAISE EXCEPTION 'invalid_paid'; END IF;
  IF p_delivery = 'courier' AND (p_courier_id IS NULL OR p_customer_id IS NULL) THEN
    RAISE EXCEPTION 'courier_requires_customer_and_courier';
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0 THEN RAISE EXCEPTION 'invalid_item'; END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_found'; END IF;
    IF NOT v_prod.is_active THEN RAISE EXCEPTION 'product_inactive: %', v_prod.name; END IF;
    IF v_prod.stock < v_qty THEN RAISE EXCEPTION 'insufficient_stock: %', v_prod.name; END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN RAISE EXCEPTION 'paid_exceeds_total'; END IF;
  IF p_delivery = 'direct' AND p_paid < v_total AND p_customer_id IS NULL THEN
    RAISE EXCEPTION 'customer_required_for_debt';
  END IF;

  IF p_delivery = 'courier' THEN
    v_order_paid := 0;
    v_order_collected := p_paid;
    v_order_courier_state := CASE
      WHEN p_paid = 0 THEN 'pending'::courier_state
      WHEN p_paid >= v_total THEN 'delivered_full'::courier_state
      ELSE 'delivered_partial'::courier_state END;
    v_status := 'debt'::order_status;
  ELSE
    v_order_paid := p_paid;
    v_order_collected := 0;
    v_order_courier_state := NULL;
    v_status := CASE
      WHEN p_paid >= v_total THEN 'paid'::order_status
      WHEN p_paid > 0 THEN 'partial'::order_status
      ELSE 'debt'::order_status END;
  END IF;

  v_tnum := public.next_order_number(v_tenant);

  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by, tenant_number
  ) VALUES (
    v_tenant, p_customer_id, v_total, v_order_paid, v_status, p_delivery, p_courier_id,
    v_order_courier_state, v_order_collected, v_uid, v_tnum
  ) RETURNING * INTO v_order;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    v_pid := (v_item->>'productId')::uuid;
    v_qty := (v_item->>'qty')::numeric;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid;
    INSERT INTO public.order_items(tenant_id, order_id, product_id, name, qty, unit_price, unit_cost)
      VALUES (v_tenant, v_order.id, v_pid, v_prod.name, v_qty, v_prod.price, v_prod.cost);
    UPDATE public.products SET stock = stock - v_qty WHERE id = v_pid;
  END LOOP;

  IF p_delivery = 'direct' AND p_paid > 0 THEN
    INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, created_by)
      VALUES (v_tenant, 'sale', p_method, p_paid, v_order.id, p_customer_id, v_uid);
  END IF;

  RETURN jsonb_build_object('success', true, 'order_id', v_order.id, 'number', v_tnum);
END $function$;
CREATE OR REPLACE FUNCTION public.current_tenant_id()
 RETURNS uuid
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT tenant_id FROM public.profiles WHERE id = auth.uid()
$function$;
CREATE OR REPLACE FUNCTION public.current_tenant_timezone()
 RETURNS text
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT COALESCE(
    (SELECT t.timezone FROM public.tenants t WHERE t.id = public.current_tenant_id()),
    'Africa/Tripoli'
  );
$function$;
CREATE OR REPLACE FUNCTION public.delete_email(queue_name text, message_id bigint)
 RETURNS boolean
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pgmq'
AS $function$
BEGIN
  RETURN pgmq.delete(queue_name, message_id);
EXCEPTION WHEN undefined_table THEN
  RETURN FALSE;
END;
$function$;
CREATE OR REPLACE FUNCTION public.delete_order_with_restore_stock(p_order_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_order public.orders%ROWTYPE;
  v_it record;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_owner(v_order.tenant_id);

  -- Block deletion of courier orders that have collected money or have been settled
  IF v_order.delivery = 'courier' AND COALESCE(v_order.collected_by_courier, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_delete_courier_with_collected_money';
  END IF;
  IF COALESCE(v_order.paid, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_delete_paid_order';
  END IF;

  -- Restore stock
  FOR v_it IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
    IF v_it.product_id IS NOT NULL THEN
      UPDATE public.products SET stock = stock + v_it.qty WHERE id = v_it.product_id;
    END IF;
  END LOOP;

  DELETE FROM public.payments    WHERE order_id = p_order_id;
  DELETE FROM public.order_items WHERE order_id = p_order_id;
  DELETE FROM public.orders      WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true);
END $function$;
CREATE OR REPLACE FUNCTION public.delete_product_safe(p_product_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid;
  v_used   int;
BEGIN
  SELECT tenant_id INTO v_tenant FROM public.products WHERE id = p_product_id;
  IF v_tenant IS NULL THEN
    RAISE EXCEPTION 'product_not_found';
  END IF;

  PERFORM public._assert_owner(v_tenant);

  SELECT count(*) INTO v_used FROM public.order_items WHERE product_id = p_product_id;

  IF v_used = 0 THEN
    DELETE FROM public.products WHERE id = p_product_id;
    RETURN jsonb_build_object('deleted', true);
  ELSE
    UPDATE public.products SET is_active = false WHERE id = p_product_id;
    RETURN jsonb_build_object('archived', true, 'used_in', v_used);
  END IF;
END;
$function$;
CREATE OR REPLACE FUNCTION public.enqueue_email(queue_name text, payload jsonb)
 RETURNS bigint
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pgmq'
AS $function$
BEGIN
  RETURN pgmq.send(queue_name, payload);
EXCEPTION WHEN undefined_table THEN
  PERFORM pgmq.create(queue_name);
  RETURN pgmq.send(queue_name, payload);
END;
$function$;
CREATE OR REPLACE FUNCTION public.get_platform_admin_audit_log(p_limit integer DEFAULT 100, p_offset integer DEFAULT 0)
 RETURNS TABLE(id uuid, user_id uuid, user_email text, action text, details jsonb, created_at timestamp with time zone)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
CREATE OR REPLACE FUNCTION public.get_platform_admin_overview()
 RETURNS jsonb
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
  SELECT COALESCE(SUM(e.amount),0) INTO v_expenses_today FROM public.expenses e
    JOIN public.tenants t ON t.id = e.tenant_id
   WHERE (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date
       = (now() AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date;
  SELECT COUNT(*) INTO v_day_close_count FROM public.day_closes dc
    JOIN public.tenants t ON t.id = dc.tenant_id
   WHERE dc.closed_for = (now() AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date;
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
CREATE OR REPLACE FUNCTION public.get_platform_courier_custody_health()
 RETURNS TABLE(tenant_id uuid, tenant_name text, courier_id uuid, courier_name text, unsettled_amount numeric, orders_count integer, oldest_age_days integer, risk text)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
CREATE OR REPLACE FUNCTION public.get_platform_day_close_health(p_limit integer DEFAULT 30)
 RETURNS TABLE(id uuid, tenant_id uuid, tenant_name text, closed_for date, sales numeric, collected numeric, expenses numeric, customer_debts numeric, unsettled_custody numeric, realized_profit numeric, created_at timestamp with time zone, sales_diff numeric, collected_diff numeric, expenses_diff numeric, status text)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE v_lim int := LEAST(GREATEST(COALESCE(p_limit,30),1),200);
BEGIN
  PERFORM public._assert_platform_admin();
  PERFORM public._log_platform_admin_action('view_day_close_health', jsonb_build_object('limit', v_lim));
  RETURN QUERY
  SELECT dc.id, dc.tenant_id, t.name, dc.closed_for, dc.sales, dc.collected, dc.expenses,
         dc.customer_debts, dc.unsettled_custody, dc.realized_profit, dc.created_at,
         dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o
           WHERE o.tenant_id = dc.tenant_id
             AND (o.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p
           WHERE p.tenant_id = dc.tenant_id
             AND (p.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e
           WHERE e.tenant_id = dc.tenant_id
             AND (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0),
         CASE WHEN
           ABS(dc.sales - COALESCE((SELECT SUM(o.total) FROM public.orders o
             WHERE o.tenant_id = dc.tenant_id AND (o.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.collected - COALESCE((SELECT SUM(p.amount) FROM public.payments p
             WHERE p.tenant_id = dc.tenant_id AND (p.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
           AND ABS(dc.expenses - COALESCE((SELECT SUM(e.amount) FROM public.expenses e
             WHERE e.tenant_id = dc.tenant_id AND (e.created_at AT TIME ZONE COALESCE(t.timezone,'Africa/Tripoli'))::date = dc.closed_for),0)) < 0.01
         THEN 'Matches' ELSE 'Mismatch' END
  FROM public.day_closes dc LEFT JOIN public.tenants t ON t.id = dc.tenant_id
  ORDER BY dc.created_at DESC LIMIT v_lim;
END $function$;
CREATE OR REPLACE FUNCTION public.get_platform_financial_health()
 RETURNS TABLE(check_key text, explanation_ar text, status text, affected_count integer)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
 RETURNS jsonb
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
 RETURNS jsonb
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
CREATE OR REPLACE FUNCTION public.get_platform_tenants_health()
 RETURNS TABLE(tenant_id uuid, tenant_name text, owner_user_id uuid, created_at timestamp with time zone, products_count integer, customers_count integer, orders_count integer, total_sales numeric, total_collected numeric, open_debts numeric, unsettled_custody numeric, last_activity timestamp with time zone, health text)
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
CREATE OR REPLACE FUNCTION public.get_tenant_today_estimate()
 RETURNS jsonb
 LANGUAGE plpgsql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_tz text := public.current_tenant_timezone();
  v_today date := (now() AT TIME ZONE v_tz)::date;
  v_sales numeric(12,2);
  v_collected numeric(12,2);
  v_expenses numeric(12,2);
  v_realized_profit numeric(12,2);
BEGIN
  PERFORM public._assert_staff(v_tenant);

  SELECT COALESCE(SUM(total),0) INTO v_sales FROM public.orders
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(amount),0) INTO v_collected FROM public.payments
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(amount),0) INTO v_expenses FROM public.expenses
    WHERE tenant_id = v_tenant AND (created_at AT TIME ZONE v_tz)::date = v_today;
  SELECT COALESCE(SUM(
    CASE WHEN o.total > 0
      THEN (p.amount / o.total) *
           (SELECT COALESCE(SUM((oi.unit_price - oi.unit_cost) * oi.qty),0)
              FROM public.order_items oi WHERE oi.order_id = o.id)
      ELSE 0 END
  ), 0) INTO v_realized_profit
  FROM public.payments p JOIN public.orders o ON o.id = p.order_id
  WHERE p.tenant_id = v_tenant
    AND (p.created_at AT TIME ZONE v_tz)::date = v_today
    AND p.order_id IS NOT NULL;

  RETURN jsonb_build_object(
    'today', v_today, 'timezone', v_tz,
    'sales', v_sales, 'collected', v_collected, 'expenses', v_expenses,
    'realized_profit', v_realized_profit
  );
END $function$;
CREATE OR REPLACE FUNCTION public.has_owner_role(_uid uuid, _tid uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _uid AND tenant_id = _tid AND role = 'owner'
  )
$function$;
CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _tenant_id uuid, _role app_role)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _user_id AND tenant_id = _tenant_id AND role = _role
  )
$function$;
CREATE OR REPLACE FUNCTION public.has_staff_or_owner_role(_uid uuid, _tid uuid)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _uid AND tenant_id = _tid AND role IN ('owner','staff')
  )
$function$;
CREATE OR REPLACE FUNCTION public.is_platform_admin()
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT EXISTS (SELECT 1 FROM public.platform_admins WHERE user_id = auth.uid())
$function$;
CREATE OR REPLACE FUNCTION public.move_to_dlq(source_queue text, dlq_name text, message_id bigint, payload jsonb)
 RETURNS bigint
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pgmq'
AS $function$
DECLARE new_id BIGINT;
BEGIN
  SELECT pgmq.send(dlq_name, payload) INTO new_id;
  PERFORM pgmq.delete(source_queue, message_id);
  RETURN new_id;
EXCEPTION WHEN undefined_table THEN
  BEGIN
    PERFORM pgmq.create(dlq_name);
  EXCEPTION WHEN OTHERS THEN
    NULL;
  END;
  SELECT pgmq.send(dlq_name, payload) INTO new_id;
  BEGIN
    PERFORM pgmq.delete(source_queue, message_id);
  EXCEPTION WHEN undefined_table THEN
    NULL;
  END;
  RETURN new_id;
END;
$function$;
CREATE OR REPLACE FUNCTION public.read_email_batch(queue_name text, batch_size integer, vt integer)
 RETURNS TABLE(msg_id bigint, read_ct integer, enqueued_at timestamp with time zone, message jsonb)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pgmq'
AS $function$
BEGIN
  RETURN QUERY SELECT r.msg_id, r.read_ct, r.enqueued_at, r.message FROM pgmq.read(queue_name, vt, batch_size) r;
EXCEPTION WHEN undefined_table THEN
  PERFORM pgmq.create(queue_name);
  RETURN;
END;
$function$;
CREATE OR REPLACE FUNCTION public.return_courier_order(p_order_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_order public.orders%ROWTYPE;
  v_it record;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);
  IF v_order.delivery <> 'courier' THEN
    RAISE EXCEPTION 'not_a_courier_order';
  END IF;
  IF COALESCE(v_order.paid, 0) > 0 OR COALESCE(v_order.collected_by_courier, 0) > 0 THEN
    RAISE EXCEPTION 'cannot_return_partially_paid_order';
  END IF;

  FOR v_it IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
    IF v_it.product_id IS NOT NULL THEN
      UPDATE public.products SET stock = stock + v_it.qty WHERE id = v_it.product_id;
    END IF;
  END LOOP;

  -- M8: also clear courier assignment and mark as direct so it leaves custody lists.
  -- Keep customer link so historical record stays intact.
  UPDATE public.orders SET
    courier_state = 'returned',
    collected_by_courier = 0,
    courier_id = NULL,
    delivery = 'direct'
  WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true);
END $function$;
CREATE OR REPLACE FUNCTION public.run_security_scan(p_triggered_by text DEFAULT 'manual'::text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
$function$;
CREATE OR REPLACE FUNCTION public.settle_courier_orders(p_courier_id uuid, p_order_ids uuid[])
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_uid uuid := auth.uid();
  v_tenant uuid := public.current_tenant_id();
  v_oid uuid;
  v_order public.orders%ROWTYPE;
  v_collected numeric(12,2);
  v_new_paid numeric(12,2);
  v_status order_status;
  v_count int := 0;
  v_total_collected numeric(12,2) := 0;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF NOT EXISTS (SELECT 1 FROM public.couriers WHERE id = p_courier_id AND tenant_id = v_tenant) THEN
    RAISE EXCEPTION 'courier_not_found';
  END IF;
  IF p_order_ids IS NULL OR array_length(p_order_ids, 1) IS NULL THEN
    RAISE EXCEPTION 'invalid_orders';
  END IF;

  FOREACH v_oid IN ARRAY p_order_ids LOOP
    SELECT * INTO v_order FROM public.orders WHERE id = v_oid FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found: %', v_oid; END IF;
    IF v_order.tenant_id <> v_tenant OR v_order.courier_id <> p_courier_id THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;

    -- Source of truth: collected_by_courier set when the courier state was updated.
    -- Clamp to remaining so stale rows (where paid already covers total) don't block settlement.
    v_collected := LEAST(
      COALESCE(v_order.collected_by_courier, 0),
      GREATEST(v_order.total - v_order.paid, 0)
    );

    v_new_paid := v_order.paid + v_collected;
    v_status := CASE
      WHEN v_new_paid >= v_order.total THEN 'paid'::order_status
      WHEN v_new_paid > 0 THEN 'partial'::order_status
      ELSE 'debt'::order_status END;

    UPDATE public.orders SET
      paid = v_new_paid, status = v_status,
      delivery = 'direct', courier_id = NULL, courier_state = NULL, collected_by_courier = 0
    WHERE id = v_oid;

    IF v_collected > 0 THEN
      INSERT INTO public.payments(tenant_id, kind, method, amount, order_id, customer_id, courier_id, created_by)
        VALUES (v_tenant, 'courier_settlement', 'cash', v_collected, v_oid, v_order.customer_id, p_courier_id, v_uid);
      v_total_collected := v_total_collected + v_collected;
    END IF;
    v_count := v_count + 1;
  END LOOP;

  RETURN jsonb_build_object('success', true, 'settled_count', v_count, 'total_collected', v_total_collected);
END $function$;
CREATE OR REPLACE FUNCTION public.tenant_has_active_subscription(_tenant_id uuid, _check_env text DEFAULT 'live'::text)
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT
    EXISTS (
      SELECT 1 FROM public.subscriptions
      WHERE tenant_id = _tenant_id
        AND environment = _check_env
        AND (
          (status IN ('active', 'trialing') AND (current_period_end IS NULL OR current_period_end > now()))
          OR (status = 'canceled' AND current_period_end > now())
        )
    )
    OR EXISTS (
      SELECT 1 FROM public.tenants
      WHERE id = _tenant_id
        AND trial_ends_at IS NOT NULL
        AND trial_ends_at > now()
    );
$function$;
CREATE OR REPLACE FUNCTION public.tenant_today(_tid uuid)
 RETURNS date
 LANGUAGE sql
 STABLE SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
  SELECT (now() AT TIME ZONE COALESCE(
    (SELECT timezone FROM public.tenants WHERE id = _tid),
    'Africa/Tripoli'
  ))::date;
$function$;
CREATE OR REPLACE FUNCTION public.update_courier_order_state(p_order_id uuid, p_state text, p_collected numeric DEFAULT NULL::numeric)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_order public.orders%ROWTYPE;
  v_collected numeric(12,2) := 0;
  v_state courier_state;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.delivery <> 'courier' THEN
    RAISE EXCEPTION 'not_a_courier_order';
  END IF;

  IF p_state = 'returned' THEN
    -- Delegate to the dedicated RPC so all return rules stay in one place
    RETURN public.return_courier_order(p_order_id);
  END IF;

  IF p_state NOT IN ('pending','delivered_none','delivered_partial','delivered_full') THEN
    RAISE EXCEPTION 'invalid_state';
  END IF;
  v_state := p_state::courier_state;

  IF p_state = 'delivered_full' THEN
    v_collected := v_order.total;
  ELSIF p_state = 'delivered_partial' THEN
    v_collected := GREATEST(0, LEAST(v_order.total, COALESCE(p_collected, 0)));
  ELSE
    v_collected := 0;
  END IF;

  IF v_collected > v_order.total THEN
    RAISE EXCEPTION 'collected_exceeds_total';
  END IF;

  UPDATE public.orders
     SET courier_state = v_state,
         collected_by_courier = v_collected
   WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true, 'collected', v_collected);
END $function$;
DROP POLICY IF EXISTS monjez_live_actor ON public.couriers;
DROP POLICY IF EXISTS monjez_live_actor ON public.customers;
DROP POLICY IF EXISTS monjez_live_actor ON public.day_closes;
DROP POLICY IF EXISTS monjez_live_actor ON public.email_send_log;
DROP POLICY IF EXISTS monjez_live_actor ON public.email_send_state;
DROP POLICY IF EXISTS monjez_live_actor ON public.email_unsubscribe_tokens;
DROP POLICY IF EXISTS monjez_live_actor ON public.expenses;
DROP POLICY IF EXISTS monjez_live_actor ON public.financial_audit_log;
DROP POLICY IF EXISTS monjez_live_actor ON public.order_items;
DROP POLICY IF EXISTS monjez_live_actor ON public.orders;
DROP POLICY IF EXISTS monjez_live_actor ON public.payments;
DROP POLICY IF EXISTS monjez_live_actor ON public.platform_admin_audit_log;
DROP POLICY IF EXISTS monjez_live_actor ON public.platform_admins;
DROP POLICY IF EXISTS monjez_live_actor ON public.products;
DROP POLICY IF EXISTS monjez_live_actor ON public.profiles;
DROP POLICY IF EXISTS monjez_live_actor ON public.security_scan_findings;
DROP POLICY IF EXISTS monjez_live_actor ON public.security_scan_runs;
DROP POLICY IF EXISTS monjez_live_actor ON public.subscriptions;
DROP POLICY IF EXISTS monjez_live_actor ON public.suppressed_emails;
DROP POLICY IF EXISTS monjez_live_actor ON public.tenant_counters;
DROP POLICY IF EXISTS monjez_live_actor ON public.tenants;
DROP POLICY IF EXISTS monjez_live_actor ON public.user_roles;
DO $led$ DECLARE n int; BEGIN
  DELETE FROM supabase_migrations.schema_migrations WHERE version IN ('20261010223557','20261010225012');
  GET DIAGNOSTICS n = ROW_COUNT; IF n <> 2 THEN RAISE EXCEPTION 'LEDGER_DELETE_COUNT % <> 2', n; END IF;
END $led$;
COMMIT;
