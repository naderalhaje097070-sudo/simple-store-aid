
-- =========================================================
-- Fix: tenant_id_selfupdate
-- =========================================================
DROP POLICY IF EXISTS "users update own profile" ON public.profiles;

CREATE POLICY "users update own profile" ON public.profiles
  FOR UPDATE TO authenticated
  USING (id = auth.uid())
  WITH CHECK (
    id = auth.uid()
    AND (
      tenant_id IS NOT DISTINCT FROM (
        SELECT p.tenant_id FROM public.profiles p WHERE p.id = auth.uid()
      )
      OR EXISTS (
        SELECT 1 FROM public.tenants t
        WHERE t.id = profiles.tenant_id AND t.owner_user_id = auth.uid()
      )
    )
  );

-- =========================================================
-- Fix: role_clientside_only
-- Roles available in this project: 'owner', 'staff'.
-- =========================================================

CREATE OR REPLACE FUNCTION public.has_owner_role(_uid uuid, _tid uuid)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _uid AND tenant_id = _tid AND role = 'owner'
  )
$$;

CREATE OR REPLACE FUNCTION public.has_staff_or_owner_role(_uid uuid, _tid uuid)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _uid AND tenant_id = _tid AND role IN ('owner','staff')
  )
$$;

REVOKE EXECUTE ON FUNCTION public.has_owner_role(uuid, uuid) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION public.has_staff_or_owner_role(uuid, uuid) FROM PUBLIC, anon, authenticated;

-- ---------- Staff-writable tables (owner or staff for INSERT/UPDATE; owner-only DELETE) ----------

-- orders
DROP POLICY IF EXISTS "tenant members insert orders" ON public.orders;
DROP POLICY IF EXISTS "tenant members update orders" ON public.orders;
DROP POLICY IF EXISTS "tenant members delete orders" ON public.orders;
CREATE POLICY "staff insert orders" ON public.orders FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "staff update orders" ON public.orders FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete orders" ON public.orders FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- order_items
DROP POLICY IF EXISTS "tenant members insert order_items" ON public.order_items;
DROP POLICY IF EXISTS "tenant members update order_items" ON public.order_items;
DROP POLICY IF EXISTS "tenant members delete order_items" ON public.order_items;
CREATE POLICY "staff insert order_items" ON public.order_items FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "staff update order_items" ON public.order_items FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete order_items" ON public.order_items FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- customers
DROP POLICY IF EXISTS "tenant members insert customers" ON public.customers;
DROP POLICY IF EXISTS "tenant members update customers" ON public.customers;
DROP POLICY IF EXISTS "tenant members delete customers" ON public.customers;
CREATE POLICY "staff insert customers" ON public.customers FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "staff update customers" ON public.customers FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete customers" ON public.customers FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- payments
DROP POLICY IF EXISTS "tenant members insert payments" ON public.payments;
DROP POLICY IF EXISTS "tenant members update payments" ON public.payments;
DROP POLICY IF EXISTS "tenant members delete payments" ON public.payments;
CREATE POLICY "staff insert payments" ON public.payments FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "staff update payments" ON public.payments FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_staff_or_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete payments" ON public.payments FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- ---------- Owner-only writable tables ----------

-- products
DROP POLICY IF EXISTS "tenant members insert products" ON public.products;
DROP POLICY IF EXISTS "tenant members update products" ON public.products;
DROP POLICY IF EXISTS "tenant members delete products" ON public.products;
CREATE POLICY "owners insert products" ON public.products FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update products" ON public.products FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete products" ON public.products FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- couriers
DROP POLICY IF EXISTS "tenant members insert couriers" ON public.couriers;
DROP POLICY IF EXISTS "tenant members update couriers" ON public.couriers;
DROP POLICY IF EXISTS "tenant members delete couriers" ON public.couriers;
CREATE POLICY "owners insert couriers" ON public.couriers FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update couriers" ON public.couriers FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete couriers" ON public.couriers FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- expenses
DROP POLICY IF EXISTS "tenant members insert expenses" ON public.expenses;
DROP POLICY IF EXISTS "tenant members update expenses" ON public.expenses;
DROP POLICY IF EXISTS "tenant members delete expenses" ON public.expenses;
CREATE POLICY "owners insert expenses" ON public.expenses FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update expenses" ON public.expenses FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete expenses" ON public.expenses FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));

-- day_closes
DROP POLICY IF EXISTS "tenant members insert day_closes" ON public.day_closes;
DROP POLICY IF EXISTS "tenant members update day_closes" ON public.day_closes;
DROP POLICY IF EXISTS "tenant members delete day_closes" ON public.day_closes;
CREATE POLICY "owners insert day_closes" ON public.day_closes FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners update day_closes" ON public.day_closes FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id))
  WITH CHECK (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
CREATE POLICY "owners delete day_closes" ON public.day_closes FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id() AND public.has_owner_role(auth.uid(), tenant_id));
