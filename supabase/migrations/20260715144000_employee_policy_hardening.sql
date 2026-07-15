-- Employee-account defense in depth.
-- Remove legacy tenant-member policies so a delivery employee cannot bypass the scoped RPCs.

DO $$
DECLARE
  r record;
BEGIN
  FOR r IN
    SELECT tablename, policyname
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = ANY (ARRAY[
        'products', 'customers', 'couriers', 'orders', 'order_items',
        'payments', 'expenses', 'day_closes'
      ])
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', r.policyname, r.tablename);
  END LOOP;
END $$;

-- Owner read scope; delivery employees get only the minimum assignment-based rows.
CREATE POLICY "owners read products" ON public.products
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owner or assigned courier reads customers" ON public.customers
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR EXISTS (
      SELECT 1
      FROM public.orders o
      WHERE o.customer_id = customers.id
        AND o.tenant_id = customers.tenant_id
        AND o.courier_id = public.current_courier_id()
    )
  )
);

CREATE POLICY "owner or linked courier reads couriers" ON public.couriers
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR user_id = auth.uid()
  )
);

CREATE POLICY "owner or linked courier reads orders" ON public.orders
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR courier_id = public.current_courier_id()
  )
);

CREATE POLICY "owner or linked courier reads order_items" ON public.order_items
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND (
    public.has_owner_role(auth.uid(), tenant_id)
    OR EXISTS (
      SELECT 1
      FROM public.orders o
      WHERE o.id = order_items.order_id
        AND o.tenant_id = order_items.tenant_id
        AND o.courier_id = public.current_courier_id()
    )
  )
);

CREATE POLICY "owners read payments" ON public.payments
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owners read expenses" ON public.expenses
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owners read day_closes" ON public.day_closes
FOR SELECT TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

-- Only non-financial master data used by the owner UI keeps direct DML policies.
CREATE POLICY "owners insert products" ON public.products
FOR INSERT TO authenticated WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners update products" ON public.products
FOR UPDATE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
) WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners delete products" ON public.products
FOR DELETE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owners insert customers" ON public.customers
FOR INSERT TO authenticated WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners update customers" ON public.customers
FOR UPDATE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
) WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners delete customers" ON public.customers
FOR DELETE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owners insert couriers" ON public.couriers
FOR INSERT TO authenticated WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners update couriers" ON public.couriers
FOR UPDATE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
) WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners delete couriers" ON public.couriers
FOR DELETE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

CREATE POLICY "owners insert expenses" ON public.expenses
FOR INSERT TO authenticated WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners update expenses" ON public.expenses
FOR UPDATE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
) WITH CHECK (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);
CREATE POLICY "owners delete expenses" ON public.expenses
FOR DELETE TO authenticated USING (
  tenant_id = public.current_tenant_id()
  AND public.has_owner_role(auth.uid(), tenant_id)
);

-- Financial rows are RPC-only. SECURITY DEFINER RPCs retain access through their owner.
REVOKE INSERT, UPDATE, DELETE ON public.orders FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.order_items FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.payments FROM authenticated;
REVOKE INSERT, UPDATE, DELETE ON public.day_closes FROM authenticated;

-- Users must not be able to change tenant_id or clear disabled_at through the generic profile API.
DROP POLICY IF EXISTS "users update own profile" ON public.profiles;
REVOKE UPDATE ON public.profiles FROM authenticated;

-- A linked courier account must be explicitly unlinked before another account can replace it.
CREATE OR REPLACE FUNCTION public.prevent_courier_account_replacement()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  IF OLD.user_id IS NOT NULL
     AND NEW.user_id IS NOT NULL
     AND NEW.user_id IS DISTINCT FROM OLD.user_id THEN
    RAISE EXCEPTION 'courier_already_has_account';
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_prevent_courier_account_replacement ON public.couriers;
CREATE TRIGGER trg_prevent_courier_account_replacement
BEFORE UPDATE OF user_id ON public.couriers
FOR EACH ROW EXECUTE FUNCTION public.prevent_courier_account_replacement();

-- Delivery employees can finalize a pending order once. Corrections remain owner actions.
CREATE OR REPLACE FUNCTION public.prevent_employee_final_state_rewrite()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  IF auth.uid() IS NOT NULL
     AND public.has_role(auth.uid(), OLD.tenant_id, 'staff'::public.app_role)
     AND COALESCE(OLD.courier_state, 'pending'::public.courier_state) <> 'pending'::public.courier_state
     AND (
       NEW.courier_state IS DISTINCT FROM OLD.courier_state
       OR NEW.collected_by_courier IS DISTINCT FROM OLD.collected_by_courier
       OR NEW.delivery IS DISTINCT FROM OLD.delivery
       OR NEW.courier_id IS DISTINCT FROM OLD.courier_id
     ) THEN
    RAISE EXCEPTION 'order_state_finalized';
  END IF;
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_prevent_employee_final_state_rewrite ON public.orders;
CREATE TRIGGER trg_prevent_employee_final_state_rewrite
BEFORE UPDATE OF courier_state, collected_by_courier, delivery, courier_id ON public.orders
FOR EACH ROW EXECUTE FUNCTION public.prevent_employee_final_state_rewrite();

REVOKE ALL ON FUNCTION public.prevent_courier_account_replacement() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.prevent_employee_final_state_rewrite() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.is_active_courier_user(uuid, uuid) FROM PUBLIC, anon, authenticated;
