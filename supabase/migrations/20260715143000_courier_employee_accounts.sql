-- Mongezz V1 employee accounts: each staff account is linked to one courier.
-- Existing courier_id remains the single source of truth for order assignment and custody.

ALTER TABLE public.couriers
  ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL;

CREATE UNIQUE INDEX IF NOT EXISTS couriers_user_id_unique
  ON public.couriers(user_id)
  WHERE user_id IS NOT NULL;

ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS disabled_at timestamptz;

CREATE TABLE IF NOT EXISTS public.employee_settlement_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  courier_id uuid NOT NULL REFERENCES public.couriers(id) ON DELETE CASCADE,
  requested_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  amount_snapshot numeric(12,2) NOT NULL DEFAULT 0 CHECK (amount_snapshot >= 0),
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','cancelled')),
  note text,
  resolved_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz
);

CREATE UNIQUE INDEX IF NOT EXISTS employee_settlement_one_pending
  ON public.employee_settlement_requests(courier_id)
  WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS employee_settlement_tenant_created_idx
  ON public.employee_settlement_requests(tenant_id, created_at DESC);

GRANT SELECT ON public.employee_settlement_requests TO authenticated;
GRANT ALL ON public.employee_settlement_requests TO service_role;
ALTER TABLE public.employee_settlement_requests ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION public.current_courier_id()
RETURNS uuid
LANGUAGE sql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT c.id
  FROM public.couriers c
  JOIN public.profiles p ON p.id = auth.uid()
  JOIN public.user_roles ur
    ON ur.user_id = auth.uid() AND ur.tenant_id = c.tenant_id AND ur.role = 'staff'
  WHERE c.user_id = auth.uid()
    AND c.tenant_id = p.tenant_id
    AND c.is_active = true
    AND p.disabled_at IS NULL
  LIMIT 1
$$;

CREATE OR REPLACE FUNCTION public.is_active_courier_user(_uid uuid, _tid uuid)
RETURNS boolean
LANGUAGE sql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.couriers c
    JOIN public.profiles p ON p.id = _uid
    JOIN public.user_roles ur
      ON ur.user_id = _uid AND ur.tenant_id = _tid AND ur.role = 'staff'
    WHERE c.user_id = _uid
      AND c.tenant_id = _tid
      AND c.is_active = true
      AND p.tenant_id = _tid
      AND p.disabled_at IS NULL
  )
$$;

-- Existing owner financial RPCs call _assert_staff. Staff accounts introduced here
-- are delivery-only, so financial creation/collection/settlement stays owner-only.
CREATE OR REPLACE FUNCTION public._assert_staff(_tid uuid)
RETURNS void
LANGUAGE plpgsql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF _tid IS NULL OR _tid <> public.current_tenant_id() THEN
    RAISE EXCEPTION 'forbidden_tenant';
  END IF;
  IF NOT public.has_owner_role(auth.uid(), _tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
END $$;

CREATE OR REPLACE FUNCTION public.link_courier_account(
  p_courier_id uuid,
  p_email text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_user_id uuid;
  v_profile_tenant uuid;
  v_email text := lower(trim(p_email));
BEGIN
  IF NOT public.has_owner_role(auth.uid(), v_tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
  IF v_email = '' THEN RAISE EXCEPTION 'employee_email_required'; END IF;

  IF NOT EXISTS (SELECT 1 FROM public.couriers WHERE id = p_courier_id AND tenant_id = v_tid) THEN
    RAISE EXCEPTION 'courier_not_found';
  END IF;

  SELECT u.id INTO v_user_id FROM auth.users u WHERE lower(u.email) = v_email LIMIT 1;
  IF v_user_id IS NULL THEN RAISE EXCEPTION 'employee_account_not_found'; END IF;
  IF v_user_id = auth.uid() THEN RAISE EXCEPTION 'owner_cannot_be_employee'; END IF;
  IF EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = v_user_id AND role = 'owner') THEN
    RAISE EXCEPTION 'employee_is_tenant_owner';
  END IF;

  SELECT tenant_id INTO v_profile_tenant FROM public.profiles WHERE id = v_user_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'employee_profile_not_found'; END IF;
  IF v_profile_tenant IS NOT NULL AND v_profile_tenant <> v_tid THEN
    RAISE EXCEPTION 'employee_already_in_other_tenant';
  END IF;
  IF EXISTS (
    SELECT 1 FROM public.couriers
    WHERE user_id = v_user_id AND id <> p_courier_id
  ) THEN
    RAISE EXCEPTION 'employee_already_linked';
  END IF;

  UPDATE public.profiles
     SET tenant_id = v_tid, disabled_at = NULL
   WHERE id = v_user_id;

  INSERT INTO public.user_roles(user_id, tenant_id, role)
  VALUES (v_user_id, v_tid, 'staff')
  ON CONFLICT (user_id, tenant_id, role) DO NOTHING;

  UPDATE public.couriers
     SET user_id = v_user_id, is_active = true
   WHERE id = p_courier_id AND tenant_id = v_tid;

  RETURN jsonb_build_object('success', true, 'user_id', v_user_id, 'courier_id', p_courier_id);
END $$;

CREATE OR REPLACE FUNCTION public.unlink_courier_account(
  p_courier_id uuid,
  p_disable_courier boolean DEFAULT true
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_user_id uuid;
BEGIN
  IF NOT public.has_owner_role(auth.uid(), v_tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;

  SELECT user_id INTO v_user_id
    FROM public.couriers
   WHERE id = p_courier_id AND tenant_id = v_tid
   FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'courier_not_found'; END IF;

  UPDATE public.couriers
     SET user_id = NULL,
         is_active = CASE WHEN p_disable_courier THEN false ELSE is_active END
   WHERE id = p_courier_id;

  IF v_user_id IS NOT NULL THEN
    DELETE FROM public.user_roles
     WHERE user_id = v_user_id AND tenant_id = v_tid AND role = 'staff';
    UPDATE public.profiles
       SET tenant_id = NULL, disabled_at = now()
     WHERE id = v_user_id AND tenant_id = v_tid;
  END IF;

  RETURN jsonb_build_object('success', true);
END $$;

CREATE OR REPLACE FUNCTION public.list_courier_accounts()
RETURNS jsonb
LANGUAGE plpgsql
STABLE SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_result jsonb;
BEGIN
  IF NOT public.has_owner_role(auth.uid(), v_tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;

  SELECT COALESCE(jsonb_agg(jsonb_build_object(
    'courier_id', c.id,
    'name', c.name,
    'phone', c.phone,
    'is_active', c.is_active,
    'user_id', c.user_id,
    'email', u.email,
    'display_name', p.display_name,
    'custody', COALESCE((SELECT SUM(o.collected_by_courier)
      FROM public.orders o
      WHERE o.tenant_id = v_tid AND o.courier_id = c.id
        AND o.delivery = 'courier'
        AND o.courier_state IN ('delivered_full','delivered_partial')), 0),
    'pending_orders', (SELECT COUNT(*) FROM public.orders o
      WHERE o.tenant_id = v_tid AND o.courier_id = c.id
        AND o.delivery = 'courier' AND COALESCE(o.courier_state,'pending') = 'pending'),
    'pending_request', (SELECT jsonb_build_object(
        'id', r.id, 'amount', r.amount_snapshot, 'created_at', r.created_at
      ) FROM public.employee_settlement_requests r
      WHERE r.courier_id = c.id AND r.status = 'pending'
      ORDER BY r.created_at DESC LIMIT 1)
  ) ORDER BY c.created_at DESC), '[]'::jsonb)
  INTO v_result
  FROM public.couriers c
  LEFT JOIN auth.users u ON u.id = c.user_id
  LEFT JOIN public.profiles p ON p.id = c.user_id
  WHERE c.tenant_id = v_tid;

  RETURN v_result;
END $$;

CREATE OR REPLACE FUNCTION public.get_my_courier_portal()
RETURNS jsonb
LANGUAGE plpgsql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_courier_id uuid := public.current_courier_id();
  v_result jsonb;
BEGIN
  IF v_courier_id IS NULL THEN RAISE EXCEPTION 'employee_account_disabled'; END IF;

  SELECT jsonb_build_object(
    'courier', jsonb_build_object('id', c.id, 'name', c.name, 'phone', c.phone),
    'tenant_name', t.name,
    'custody', COALESCE((SELECT SUM(o.collected_by_courier)
      FROM public.orders o
      WHERE o.tenant_id = v_tid AND o.courier_id = v_courier_id
        AND o.delivery = 'courier'
        AND o.courier_state IN ('delivered_full','delivered_partial')), 0),
    'pending_orders', (SELECT COUNT(*) FROM public.orders o
      WHERE o.tenant_id = v_tid AND o.courier_id = v_courier_id
        AND o.delivery = 'courier' AND COALESCE(o.courier_state,'pending') = 'pending'),
    'orders', COALESCE((SELECT jsonb_agg(jsonb_build_object(
        'id', o.id,
        'number', COALESCE(o.tenant_number, o.number),
        'total', o.total,
        'paid', o.paid,
        'courier_state', o.courier_state,
        'collected_by_courier', o.collected_by_courier,
        'created_at', o.created_at,
        'customer', CASE WHEN cu.id IS NULL THEN NULL ELSE jsonb_build_object('name', cu.name, 'phone', cu.phone) END,
        'items', COALESCE((SELECT jsonb_agg(jsonb_build_object(
          'name', oi.name, 'qty', oi.qty, 'unit_price', oi.unit_price
        ) ORDER BY oi.created_at) FROM public.order_items oi WHERE oi.order_id = o.id), '[]'::jsonb)
      ) ORDER BY o.created_at DESC)
      FROM public.orders o
      LEFT JOIN public.customers cu ON cu.id = o.customer_id
      WHERE o.tenant_id = v_tid AND o.courier_id = v_courier_id
        AND o.delivery = 'courier' AND o.courier_state <> 'returned'), '[]'::jsonb),
    'settlement_requests', COALESCE((SELECT jsonb_agg(jsonb_build_object(
        'id', r.id, 'amount', r.amount_snapshot, 'status', r.status,
        'created_at', r.created_at, 'resolved_at', r.resolved_at
      ) ORDER BY r.created_at DESC)
      FROM public.employee_settlement_requests r
      WHERE r.tenant_id = v_tid AND r.courier_id = v_courier_id), '[]'::jsonb)
  ) INTO v_result
  FROM public.couriers c
  JOIN public.tenants t ON t.id = c.tenant_id
  WHERE c.id = v_courier_id;

  RETURN v_result;
END $$;

CREATE OR REPLACE FUNCTION public.courier_update_my_order_state(
  p_order_id uuid,
  p_state text,
  p_collected numeric DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_courier_id uuid := public.current_courier_id();
  v_order public.orders%ROWTYPE;
  v_remaining numeric(12,2);
  v_collected numeric(12,2) := COALESCE(p_collected, 0);
  v_item record;
BEGIN
  IF v_courier_id IS NULL THEN RAISE EXCEPTION 'employee_account_disabled'; END IF;

  SELECT * INTO v_order FROM public.orders
   WHERE id = p_order_id AND tenant_id = v_tid
     AND courier_id = v_courier_id AND delivery = 'courier'
   FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_assigned_to_employee'; END IF;
  IF v_order.courier_state = 'returned' THEN RAISE EXCEPTION 'order_already_returned'; END IF;

  v_remaining := GREATEST(v_order.total - v_order.paid, 0);

  IF p_state = 'delivered_full' THEN
    v_collected := v_remaining;
  ELSIF p_state = 'delivered_partial' THEN
    IF v_collected <= 0 OR v_collected >= v_remaining THEN
      RAISE EXCEPTION 'invalid_partial_collection';
    END IF;
  ELSIF p_state = 'delivered_none' THEN
    v_collected := 0;
  ELSIF p_state = 'pending' THEN
    IF COALESCE(v_order.collected_by_courier, 0) > 0 THEN
      RAISE EXCEPTION 'cannot_reset_collected_order';
    END IF;
    v_collected := 0;
  ELSIF p_state = 'returned' THEN
    IF COALESCE(v_order.paid, 0) > 0 OR COALESCE(v_order.collected_by_courier, 0) > 0 THEN
      RAISE EXCEPTION 'cannot_return_partially_paid_order';
    END IF;
    FOR v_item IN SELECT product_id, qty FROM public.order_items WHERE order_id = p_order_id LOOP
      IF v_item.product_id IS NOT NULL THEN
        UPDATE public.products SET stock = stock + v_item.qty WHERE id = v_item.product_id;
      END IF;
    END LOOP;
    UPDATE public.orders SET
      courier_state = 'returned', collected_by_courier = 0,
      delivery = 'direct', courier_id = NULL
    WHERE id = p_order_id;
    RETURN jsonb_build_object('success', true, 'state', 'returned');
  ELSE
    RAISE EXCEPTION 'invalid_courier_state';
  END IF;

  IF v_collected > v_remaining THEN RAISE EXCEPTION 'collected_exceeds_remaining'; END IF;

  UPDATE public.orders
     SET courier_state = p_state::public.courier_state,
         collected_by_courier = v_collected
   WHERE id = p_order_id;

  RETURN jsonb_build_object('success', true, 'state', p_state, 'collected', v_collected);
END $$;

CREATE OR REPLACE FUNCTION public.request_my_custody_settlement()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_courier_id uuid := public.current_courier_id();
  v_amount numeric(12,2);
  v_request_id uuid;
BEGIN
  IF v_courier_id IS NULL THEN RAISE EXCEPTION 'employee_account_disabled'; END IF;

  SELECT COALESCE(SUM(collected_by_courier),0) INTO v_amount
  FROM public.orders
  WHERE tenant_id = v_tid AND courier_id = v_courier_id
    AND delivery = 'courier'
    AND courier_state IN ('delivered_full','delivered_partial');

  IF v_amount <= 0 THEN RAISE EXCEPTION 'no_custody_to_settle'; END IF;

  INSERT INTO public.employee_settlement_requests(
    tenant_id, courier_id, requested_by, amount_snapshot, status
  ) VALUES (v_tid, v_courier_id, auth.uid(), v_amount, 'pending')
  ON CONFLICT (courier_id) WHERE status = 'pending'
  DO UPDATE SET amount_snapshot = EXCLUDED.amount_snapshot, created_at = now()
  RETURNING id INTO v_request_id;

  RETURN jsonb_build_object('success', true, 'request_id', v_request_id, 'amount', v_amount);
END $$;

CREATE OR REPLACE FUNCTION public.resolve_courier_settlement_request(
  p_request_id uuid,
  p_status text
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tid uuid := public.current_tenant_id();
  v_request public.employee_settlement_requests%ROWTYPE;
  v_current_custody numeric(12,2);
BEGIN
  IF NOT public.has_owner_role(auth.uid(), v_tid) THEN
    RAISE EXCEPTION 'forbidden_role';
  END IF;
  IF p_status NOT IN ('approved','rejected') THEN RAISE EXCEPTION 'invalid_request_status'; END IF;

  SELECT * INTO v_request FROM public.employee_settlement_requests
   WHERE id = p_request_id AND tenant_id = v_tid AND status = 'pending'
   FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'settlement_request_not_found'; END IF;

  IF p_status = 'approved' THEN
    SELECT COALESCE(SUM(collected_by_courier),0) INTO v_current_custody
    FROM public.orders
    WHERE tenant_id = v_tid AND courier_id = v_request.courier_id
      AND delivery = 'courier'
      AND courier_state IN ('delivered_full','delivered_partial');
    IF v_current_custody > 0 THEN RAISE EXCEPTION 'settle_courier_first'; END IF;
  END IF;

  UPDATE public.employee_settlement_requests
     SET status = p_status, resolved_by = auth.uid(), resolved_at = now()
   WHERE id = p_request_id;

  RETURN jsonb_build_object('success', true, 'status', p_status);
END $$;

-- Read scope: owner sees the tenant; a delivery employee sees only their own courier/orders/customers/items.
DROP POLICY IF EXISTS "tenant members read couriers" ON public.couriers;
CREATE POLICY "owner or linked courier reads couriers" ON public.couriers
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (public.has_owner_role(auth.uid(), tenant_id) OR user_id = auth.uid())
);

DROP POLICY IF EXISTS "tenant members read orders" ON public.orders;
CREATE POLICY "owner or linked courier reads orders" ON public.orders
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (public.has_owner_role(auth.uid(), tenant_id) OR courier_id = public.current_courier_id())
);

DROP POLICY IF EXISTS "tenant members read order_items" ON public.order_items;
CREATE POLICY "owner or linked courier reads order_items" ON public.order_items
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.id = order_items.order_id AND o.courier_id = public.current_courier_id()
    )
  )
);

DROP POLICY IF EXISTS "tenant members read customers" ON public.customers;
CREATE POLICY "owner or assigned courier reads customers" ON public.customers
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR EXISTS (
      SELECT 1 FROM public.orders o
      WHERE o.customer_id = customers.id AND o.courier_id = public.current_courier_id()
    )
  )
);

DROP POLICY IF EXISTS "tenant members read products" ON public.products;
CREATE POLICY "owners read products" ON public.products
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id)
);

DROP POLICY IF EXISTS "tenant members read payments" ON public.payments;
CREATE POLICY "owners read payments" ON public.payments
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id)
);

DROP POLICY IF EXISTS "tenant members read expenses" ON public.expenses;
CREATE POLICY "owners read expenses" ON public.expenses
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id)
);

DROP POLICY IF EXISTS "tenant members read day_closes" ON public.day_closes;
CREATE POLICY "owners read day_closes" ON public.day_closes
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id)
);

DROP POLICY IF EXISTS "members read roles in own tenant" ON public.user_roles;
CREATE POLICY "owners read tenant roles or users read own role" ON public.user_roles
FOR SELECT TO authenticated USING (
  user_id = auth.uid()
  OR (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
);

CREATE POLICY "owners read settlement requests" ON public.employee_settlement_requests
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "couriers read own settlement requests" ON public.employee_settlement_requests
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id() AND courier_id = public.current_courier_id()
);

-- Direct writes previously allowed to staff are now owner-only. Employee delivery updates use the scoped RPC above.
DROP POLICY IF EXISTS "staff insert orders" ON public.orders;
DROP POLICY IF EXISTS "staff update orders" ON public.orders;
CREATE POLICY "owners insert orders" ON public.orders FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update orders" ON public.orders FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

DROP POLICY IF EXISTS "staff insert order_items" ON public.order_items;
DROP POLICY IF EXISTS "staff update order_items" ON public.order_items;
CREATE POLICY "owners insert order_items" ON public.order_items FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update order_items" ON public.order_items FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

DROP POLICY IF EXISTS "staff insert customers" ON public.customers;
DROP POLICY IF EXISTS "staff update customers" ON public.customers;
CREATE POLICY "owners insert customers" ON public.customers FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update customers" ON public.customers FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

DROP POLICY IF EXISTS "staff insert payments" ON public.payments;
DROP POLICY IF EXISTS "staff update payments" ON public.payments;
CREATE POLICY "owners insert payments" ON public.payments FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update payments" ON public.payments FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

REVOKE ALL ON FUNCTION public.current_courier_id() FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.is_active_courier_user(uuid, uuid) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.link_courier_account(uuid, text) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.unlink_courier_account(uuid, boolean) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.list_courier_accounts() FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.get_my_courier_portal() FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.courier_update_my_order_state(uuid, text, numeric) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.request_my_custody_settlement() FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.resolve_courier_settlement_request(uuid, text) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public._assert_staff(uuid) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.current_courier_id() TO authenticated;
GRANT EXECUTE ON FUNCTION public.is_active_courier_user(uuid, uuid) TO authenticated;
GRANT EXECUTE ON FUNCTION public.link_courier_account(uuid, text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.unlink_courier_account(uuid, boolean) TO authenticated;
GRANT EXECUTE ON FUNCTION public.list_courier_accounts() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_my_courier_portal() TO authenticated;
GRANT EXECUTE ON FUNCTION public.courier_update_my_order_state(uuid, text, numeric) TO authenticated;
GRANT EXECUTE ON FUNCTION public.request_my_custody_settlement() TO authenticated;
GRANT EXECUTE ON FUNCTION public.resolve_courier_settlement_request(uuid, text) TO authenticated;
