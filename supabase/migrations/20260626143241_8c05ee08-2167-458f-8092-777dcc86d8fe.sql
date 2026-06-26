
-- Phase 2: products, customers, orders

-- Products
CREATE TABLE public.products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name text NOT NULL,
  sku text,
  category text,
  price numeric(12,2) NOT NULL DEFAULT 0 CHECK (price >= 0),
  cost numeric(12,2) NOT NULL DEFAULT 0 CHECK (cost >= 0),
  stock integer NOT NULL DEFAULT 0,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX products_tenant_idx ON public.products(tenant_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.products TO authenticated;
GRANT ALL ON public.products TO service_role;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read products" ON public.products FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert products" ON public.products FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update products" ON public.products FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete products" ON public.products FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE TRIGGER products_touch BEFORE UPDATE ON public.products FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

-- Customers
CREATE TABLE public.customers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  name text NOT NULL,
  phone text,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX customers_tenant_idx ON public.customers(tenant_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.customers TO authenticated;
GRANT ALL ON public.customers TO service_role;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read customers" ON public.customers FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert customers" ON public.customers FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update customers" ON public.customers FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete customers" ON public.customers FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE TRIGGER customers_touch BEFORE UPDATE ON public.customers FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

-- Orders (invoices)
CREATE TYPE public.order_status AS ENUM ('paid','partial','debt');
CREATE TABLE public.orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  customer_id uuid REFERENCES public.customers(id) ON DELETE SET NULL,
  number serial,
  total numeric(12,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
  paid numeric(12,2) NOT NULL DEFAULT 0 CHECK (paid >= 0),
  status public.order_status NOT NULL DEFAULT 'paid',
  notes text,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT paid_not_over_total CHECK (paid <= total)
);
CREATE INDEX orders_tenant_idx ON public.orders(tenant_id);
CREATE INDEX orders_customer_idx ON public.orders(customer_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.orders TO authenticated;
GRANT ALL ON public.orders TO service_role;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read orders" ON public.orders FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert orders" ON public.orders FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update orders" ON public.orders FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete orders" ON public.orders FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE TRIGGER orders_touch BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

-- Order items
CREATE TABLE public.order_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  order_id uuid NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
  product_id uuid REFERENCES public.products(id) ON DELETE SET NULL,
  name text NOT NULL,
  qty numeric(12,2) NOT NULL CHECK (qty > 0),
  unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0),
  unit_cost numeric(12,2) NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX order_items_order_idx ON public.order_items(order_id);
CREATE INDEX order_items_tenant_idx ON public.order_items(tenant_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.order_items TO authenticated;
GRANT ALL ON public.order_items TO service_role;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant members read order_items" ON public.order_items FOR SELECT TO authenticated USING (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members insert order_items" ON public.order_items FOR INSERT TO authenticated WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members update order_items" ON public.order_items FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id()) WITH CHECK (tenant_id = public.current_tenant_id());
CREATE POLICY "tenant members delete order_items" ON public.order_items FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id());
