
-- Couriers
CREATE TABLE public.couriers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name text NOT NULL,
  phone text,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX couriers_tenant_idx ON public.couriers(tenant_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.couriers TO authenticated;
GRANT ALL ON public.couriers TO service_role;
ALTER TABLE public.couriers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read couriers" ON public.couriers FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert couriers" ON public.couriers FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update couriers" ON public.couriers FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete couriers" ON public.couriers FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE TRIGGER couriers_touch BEFORE UPDATE ON public.couriers FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

-- Orders: add delivery / courier columns
CREATE TYPE public.delivery_kind AS ENUM ('direct','courier');
CREATE TYPE public.courier_state AS ENUM ('pending','delivered_full','delivered_partial','delivered_none','returned');
ALTER TABLE public.orders
  ADD COLUMN delivery public.delivery_kind NOT NULL DEFAULT 'direct',
  ADD COLUMN courier_id uuid REFERENCES public.couriers(id) ON DELETE SET NULL,
  ADD COLUMN courier_state public.courier_state,
  ADD COLUMN collected_by_courier numeric(12,2) NOT NULL DEFAULT 0 CHECK (collected_by_courier >= 0);

-- Payments
CREATE TYPE public.payment_kind AS ENUM ('sale','debt_collection','courier_settlement');
CREATE TYPE public.payment_method AS ENUM ('cash','transfer');
CREATE TABLE public.payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  kind public.payment_kind NOT NULL,
  method public.payment_method NOT NULL,
  amount numeric(12,2) NOT NULL CHECK (amount > 0),
  order_id uuid REFERENCES public.orders(id) ON DELETE SET NULL,
  customer_id uuid REFERENCES public.customers(id) ON DELETE SET NULL,
  courier_id uuid REFERENCES public.couriers(id) ON DELETE SET NULL,
  note text,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX payments_tenant_idx ON public.payments(tenant_id);
CREATE INDEX payments_order_idx ON public.payments(order_id);
CREATE INDEX payments_courier_idx ON public.payments(courier_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.payments TO authenticated;
GRANT ALL ON public.payments TO service_role;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read payments" ON public.payments FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert payments" ON public.payments FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update payments" ON public.payments FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete payments" ON public.payments FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());

-- Expenses
CREATE TABLE public.expenses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  type text NOT NULL,
  amount numeric(12,2) NOT NULL CHECK (amount > 0),
  method public.payment_method NOT NULL DEFAULT 'cash',
  note text,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX expenses_tenant_idx ON public.expenses(tenant_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.expenses TO authenticated;
GRANT ALL ON public.expenses TO service_role;
ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read expenses" ON public.expenses FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert expenses" ON public.expenses FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update expenses" ON public.expenses FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete expenses" ON public.expenses FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
