CREATE TABLE public.day_closes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  closed_for date NOT NULL,
  sales numeric NOT NULL DEFAULT 0,
  collected numeric NOT NULL DEFAULT 0,
  expenses numeric NOT NULL DEFAULT 0,
  realized_profit numeric NOT NULL DEFAULT 0,
  customer_debts numeric NOT NULL DEFAULT 0,
  unsettled_custody numeric NOT NULL DEFAULT 0,
  note text,
  created_by uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, closed_for)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON public.day_closes TO authenticated;
GRANT ALL ON public.day_closes TO service_role;

ALTER TABLE public.day_closes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant members read day_closes"
  ON public.day_closes FOR SELECT TO authenticated
  USING (tenant_id = public.current_tenant_id());

CREATE POLICY "tenant members insert day_closes"
  ON public.day_closes FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.current_tenant_id());

CREATE POLICY "tenant members update day_closes"
  ON public.day_closes FOR UPDATE TO authenticated
  USING (tenant_id = public.current_tenant_id())
  WITH CHECK (tenant_id = public.current_tenant_id());

CREATE POLICY "tenant members delete day_closes"
  ON public.day_closes FOR DELETE TO authenticated
  USING (tenant_id = public.current_tenant_id());

CREATE INDEX day_closes_tenant_date_idx ON public.day_closes(tenant_id, closed_for DESC);