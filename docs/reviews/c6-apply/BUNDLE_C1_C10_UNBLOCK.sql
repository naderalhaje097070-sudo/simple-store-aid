-- C6 bundle C1..C10 (unblock). ONE transaction: any failure leaves the database exactly at C0.
-- Each block checks the exact ledger versions and content. Run as postgres, after the runbook identity checks.
BEGIN;
-- stage B.1
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '9235c3834be88ce50dba444bb15b5262' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20260815170000: expected exactly 52 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> 'a3de2f506b1da505ae41c9fd553c87d7' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20260815170000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src4581e59e$-- FIN-COURIER-001 / PR-A candidate implementation.
-- Forward-only schema/RPC change. Repository-only candidate: do not deploy before Gate-4 evidence and human approval.

ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_debt;
ALTER TABLE public.orders
  ADD CONSTRAINT orders_customer_required_when_debt
  CHECK (
    customer_id IS NOT NULL
    OR (courier_state IS NOT NULL AND courier_state = 'returned')
    OR (delivery = 'direct' AND courier_state IS NULL AND paid >= total)
    OR (
      delivery = 'courier'
      AND courier_state IS NOT NULL
      AND courier_state IN ('pending', 'delivered_full')
    )
  ) NOT VALID;

CREATE OR REPLACE FUNCTION public._create_sale_with_items_core(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state,
  p_infer_courier_state boolean
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_total numeric(12,2) := 0;
  v_status public.order_status;
  v_order public.orders%ROWTYPE;
  v_tnum int;
  v_item jsonb;
  v_pid uuid;
  v_qty numeric(12,2);
  v_prod public.products%ROWTYPE;
  v_order_paid numeric(12,2);
  v_order_collected numeric(12,2);
  v_state public.courier_state := p_courier_state;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN RAISE EXCEPTION 'invalid_paid'; END IF;

  IF p_customer_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_tenant
  ) THEN
    RAISE EXCEPTION 'customer_not_found';
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_courier_id IS NOT NULL THEN RAISE EXCEPTION 'courier_id_must_be_null_for_direct'; END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NOT NULL THEN
      RAISE EXCEPTION 'courier_state_must_be_null_for_direct';
    END IF;
    v_state := NULL;
  ELSE
    IF p_courier_id IS NULL THEN RAISE EXCEPTION 'courier_requires_courier'; END IF;
    IF NOT EXISTS (
      SELECT 1 FROM public.couriers
       WHERE id = p_courier_id AND tenant_id = v_tenant AND is_active = true
    ) THEN
      RAISE EXCEPTION 'courier_not_found';
    END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NULL THEN RAISE EXCEPTION 'courier_state_required'; END IF;
    IF p_courier_state = 'returned' THEN RAISE EXCEPTION 'returned_not_allowed_at_creation'; END IF;
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    BEGIN
      v_pid := (v_item->>'productId')::uuid;
      v_qty := (v_item->>'qty')::numeric;
    EXCEPTION WHEN OTHERS THEN
      RAISE EXCEPTION 'invalid_item';
    END;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0 THEN RAISE EXCEPTION 'invalid_item'; END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_found'; END IF;
    IF NOT v_prod.is_active THEN RAISE EXCEPTION 'product_inactive: %', v_prod.name; END IF;
    IF v_prod.stock < v_qty THEN RAISE EXCEPTION 'insufficient_stock: %', v_prod.name; END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN RAISE EXCEPTION 'paid_exceeds_total'; END IF;

  IF p_delivery = 'courier' AND p_infer_courier_state THEN
    v_state := CASE
      WHEN p_paid = 0 THEN 'pending'::public.courier_state
      WHEN p_paid = v_total THEN 'delivered_full'::public.courier_state
      ELSE 'delivered_partial'::public.courier_state
    END;
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_paid < v_total AND p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
    v_order_paid := p_paid;
    v_order_collected := 0;
    v_status := CASE
      WHEN p_paid >= v_total THEN 'paid'::public.order_status
      WHEN p_paid > 0 THEN 'partial'::public.order_status
      ELSE 'debt'::public.order_status
    END;
  ELSE
    IF v_state IS NULL OR v_state = 'returned' THEN RAISE EXCEPTION 'invalid_state'; END IF;
    CASE v_state
      WHEN 'pending' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_none' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_partial' THEN
        IF p_paid <= 0 OR p_paid >= v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := p_paid;
      WHEN 'delivered_full' THEN
        IF p_paid <> v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := v_total;
      ELSE
        RAISE EXCEPTION 'invalid_state';
    END CASE;
    v_order_paid := 0;
    v_status := 'debt'::public.order_status;
  END IF;

  v_tnum := public.next_order_number(v_tenant);
  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by, tenant_number
  ) VALUES (
    v_tenant, p_customer_id, v_total, v_order_paid, v_status, p_delivery,
    p_courier_id, v_state, v_order_collected, v_uid, v_tnum
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
END;
$$;

REVOKE ALL ON FUNCTION public._create_sale_with_items_core(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state, boolean
) FROM PUBLIC, anon, authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items_v2(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    p_courier_state, false
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) TO authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    NULL, true
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_outcome_v2(
  p_order_id uuid,
  p_state public.courier_state,
  p_collected numeric,
  p_customer_id uuid
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_target_collected numeric(12,2);
  v_customer_id uuid;
BEGIN
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.delivery <> 'courier' OR v_order.courier_state IS NULL THEN RAISE EXCEPTION 'not_a_courier_order'; END IF;
  IF p_state IS NULL THEN RAISE EXCEPTION 'invalid_state'; END IF;

  IF p_state = 'returned' THEN
    IF v_order.courier_state NOT IN ('pending', 'delivered_none') THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN public.return_courier_order(p_order_id);
  END IF;

  IF p_state IN ('pending', 'delivered_none') THEN
    v_target_collected := 0;
  ELSIF p_state = 'delivered_partial' THEN
    IF p_collected IS NULL OR p_collected <= 0 OR p_collected >= v_order.total THEN RAISE EXCEPTION 'invalid_collected'; END IF;
    v_target_collected := p_collected;
  ELSIF p_state = 'delivered_full' THEN
    v_target_collected := v_order.total;
  ELSE
    RAISE EXCEPTION 'invalid_state';
  END IF;

  IF p_state = v_order.courier_state THEN
    IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;
    IF v_target_collected <> COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN jsonb_build_object(
      'success', true, 'order_id', v_order.id, 'state', v_order.courier_state,
      'collected', COALESCE(v_order.collected_by_courier, 0), 'idempotent', true
    );
  END IF;

  IF NOT (
    (v_order.courier_state = 'pending' AND p_state IN ('delivered_none','delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_none' AND p_state IN ('delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_partial' AND p_state = 'delivered_full')
  ) THEN
    RAISE EXCEPTION 'invalid_transition';
  END IF;

  IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;

  v_customer_id := v_order.customer_id;
  IF p_state IN ('delivered_none', 'delivered_partial') THEN
    IF v_customer_id IS NULL THEN
      IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
      IF NOT EXISTS (
        SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_order.tenant_id
      ) THEN
        RAISE EXCEPTION 'customer_not_found';
      END IF;
      v_customer_id := p_customer_id;
    ELSIF p_customer_id IS NOT NULL AND p_customer_id <> v_customer_id THEN
      RAISE EXCEPTION 'customer_mismatch';
    END IF;
  END IF;

  UPDATE public.orders
     SET courier_state = p_state,
         collected_by_courier = v_target_collected,
         customer_id = v_customer_id
   WHERE id = p_order_id;

  RETURN jsonb_build_object(
    'success', true, 'order_id', p_order_id, 'state', p_state,
    'collected', v_target_collected, 'customer_id', v_customer_id
  );
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_order_state(
  p_order_id uuid,
  p_state text,
  p_collected numeric DEFAULT NULL
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_state public.courier_state;
BEGIN
  IF p_state IS NULL OR p_state NOT IN ('pending','delivered_none','delivered_partial','delivered_full','returned') THEN
    RAISE EXCEPTION 'invalid_state';
  END IF;
  v_state := p_state::public.courier_state;
  RETURN public.update_courier_outcome_v2(p_order_id, v_state, p_collected, NULL);
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_order_state(uuid, text, numeric) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_order_state(uuid, text, numeric) TO authenticated;
$src4581e59e$;
  IF md5(src) <> 'aaad5a46c941dc296810f522f6237a48' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20260815170000_fin_courier_pr_a'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20260815170000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20260815170000'; END IF;
  body := src;
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20260815170000', 'fin_courier_pr_a', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.2
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '095f17473e27d695e797382431ede0ab' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20260815171000: expected exactly 53 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '19fd5f17ea8c3cc4ea10e77a404a6bdd' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20260815171000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src8096ca4e$-- FIN-IDEM-001 candidate implementation for canonical sale creation.
-- Repository-only candidate. Do not deploy before FIN-COURIER PR-A, Gate-4 evidence,
-- exact-head financial verification, independent review, and human approval.

CREATE TABLE IF NOT EXISTS public.financial_idempotency (
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  operation text NOT NULL,
  idempotency_key uuid NOT NULL,
  request_hash text NOT NULL,
  request_payload jsonb NOT NULL,
  result jsonb,
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  PRIMARY KEY (tenant_id, operation, idempotency_key),
  CONSTRAINT financial_idempotency_operation_nonempty CHECK (btrim(operation) <> ''),
  CONSTRAINT financial_idempotency_hash_shape CHECK (char_length(request_hash) = 32),
  CONSTRAINT financial_idempotency_completion_consistent CHECK (
    (result IS NULL AND completed_at IS NULL)
    OR (result IS NOT NULL AND completed_at IS NOT NULL)
  )
);

ALTER TABLE public.financial_idempotency ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE public.financial_idempotency FROM PUBLIC, anon, authenticated;
GRANT ALL ON TABLE public.financial_idempotency TO service_role;

CREATE INDEX IF NOT EXISTS financial_idempotency_created_idx
  ON public.financial_idempotency (tenant_id, created_at DESC);

CREATE OR REPLACE FUNCTION public.create_sale_with_items_idempotent(
  p_idempotency_key uuid,
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_operation constant text := 'sale.create.v2';
  v_request jsonb;
  v_request_hash text;
  v_inserted integer := 0;
  v_existing_hash text;
  v_existing_request jsonb;
  v_result jsonb;
BEGIN
  PERFORM public._assert_staff(v_tenant);

  IF p_idempotency_key IS NULL THEN
    RAISE EXCEPTION 'idempotency_key_required';
  END IF;

  -- jsonb gives deterministic object-key serialization. Array order remains part
  -- of the request identity deliberately: item order is part of the submitted
  -- canonical sale request until the canonical sale RPC defines otherwise.
  v_request := jsonb_build_object(
    'customer_id', p_customer_id,
    'delivery', p_delivery,
    'courier_id', p_courier_id,
    'paid', p_paid,
    'method', p_method,
    'items', p_items,
    'courier_state', p_courier_state
  );

  -- MD5 is only a compact diagnostic fingerprint. Replay authorization also
  -- requires exact jsonb request equality, so a hash collision cannot authorize
  -- a mismatched financial request.
  v_request_hash := md5(v_request::text);

  INSERT INTO public.financial_idempotency(
    tenant_id,
    operation,
    idempotency_key,
    request_hash,
    request_payload,
    created_by
  ) VALUES (
    v_tenant,
    v_operation,
    p_idempotency_key,
    v_request_hash,
    v_request,
    v_uid
  )
  ON CONFLICT (tenant_id, operation, idempotency_key) DO NOTHING;

  GET DIAGNOSTICS v_inserted = ROW_COUNT;

  IF v_inserted = 1 THEN
    -- Reservation and financial write share one PostgreSQL transaction. Any
    -- uncaught canonical-write failure rolls the reservation back too.
    v_result := public.create_sale_with_items_v2(
      p_customer_id,
      p_delivery,
      p_courier_id,
      p_paid,
      p_method,
      p_items,
      p_courier_state
    );

    UPDATE public.financial_idempotency
       SET result = v_result,
           completed_at = now()
     WHERE tenant_id = v_tenant
       AND operation = v_operation
       AND idempotency_key = p_idempotency_key;

    RETURN v_result;
  END IF;

  -- A same-key concurrent INSERT waits on the unique key. Once the owner
  -- transaction commits this row carries the original result; if it rolls back,
  -- the waiting INSERT can become the owner instead.
  SELECT request_hash, request_payload, result
    INTO v_existing_hash, v_existing_request, v_result
    FROM public.financial_idempotency
   WHERE tenant_id = v_tenant
     AND operation = v_operation
     AND idempotency_key = p_idempotency_key
   FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'idempotency_state_missing';
  END IF;

  IF v_existing_hash <> v_request_hash OR v_existing_request <> v_request THEN
    RAISE EXCEPTION 'idempotency_conflict';
  END IF;

  IF v_result IS NULL THEN
    RAISE EXCEPTION 'idempotency_incomplete';
  END IF;

  RETURN v_result;
END;
$$;

REVOKE ALL ON FUNCTION public.create_sale_with_items_idempotent(
  uuid, uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items_idempotent(
  uuid, uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) TO authenticated;

-- FIN-IDEM must be server-enforced, not merely a client convention. Once this
-- migration lands, application roles cannot bypass the idempotency wrapper by
-- calling either the canonical v2 write or the legacy six-argument adapter.
REVOKE EXECUTE ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) FROM authenticated;
REVOKE EXECUTE ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) FROM authenticated;
$src8096ca4e$;
  IF md5(src) <> '273ca4dc85ea00486cfea04955e64745' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20260815171000_fin_idem_sale_create'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20260815171000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20260815171000'; END IF;
  body := src;
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20260815171000', 'fin_idem_sale_create', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.3
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> 'f05259714b39f3a6eda55fdbf6c5ee77' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261028213608: expected exactly 54 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '46495017f081401715147fe2ef32ce89' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261028213608: ledger statements differ from the recorded production ledger'; END IF;
  src := $srcc3d6c60b$-- C2 owner-approved fractional quantities; original two-decimal item precision.
BEGIN;
SET LOCAL lock_timeout = '5s';
LOCK TABLE public.products, public.order_items IN ACCESS EXCLUSIVE MODE;
DO $preflight$
BEGIN
  IF EXISTS (SELECT 1 FROM public.products WHERE NOT (stock >= 0 AND stock <= 9999999999.99 AND stock = trunc(stock::numeric, 2)))
     OR EXISTS (SELECT 1 FROM public.order_items WHERE NOT (qty > 0 AND qty <= 9999999999.99 AND qty = trunc(qty, 2))) THEN
    RAISE EXCEPTION 'fractional_quantity_historical_data_requires_review';
  END IF;
END $preflight$;
-- No typemod: constraints reject excess precision rather than rounding before CHECK.
ALTER TABLE public.products ALTER COLUMN stock TYPE numeric USING stock::numeric;
ALTER TABLE public.order_items ALTER COLUMN qty TYPE numeric USING qty::numeric;
ALTER TABLE public.products ADD CONSTRAINT products_stock_quantity_precision
  CHECK (stock >= 0 AND stock <= 9999999999.99 AND stock = trunc(stock, 2));
ALTER TABLE public.order_items ADD CONSTRAINT order_items_quantity_precision
  CHECK (qty > 0 AND qty <= 9999999999.99 AND qty = trunc(qty, 2));

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
  v_qty    numeric;
  v_prod   public.products%ROWTYPE;
  v_order_paid          numeric(12,2);
  v_order_collected     numeric(12,2);
  v_order_courier_state courier_state;
BEGIN
  PERFORM monjez_private.assert_active_actor();
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
    IF v_pid IS NULL OR v_qty IS NULL OR NOT (v_qty > 0 AND v_qty <= 9999999999.99 AND v_qty = trunc(v_qty, 2)) THEN
      RAISE EXCEPTION 'invalid_item';
    END IF;
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

NOTIFY pgrst, 'reload schema';
COMMIT;
$srcc3d6c60b$;
  IF md5(src) <> 'cea0b58f0279a46fda7f44411d17cc76' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261028213608_fractional_quantity_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261028213608') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261028213608'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261028213608', 'fractional_quantity_01', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.4
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '593523ff3c517255c2415399c0bcf524' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261029044024: expected exactly 55 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '2771e74c4161f1b68d61a50451880879' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261029044024: ledger statements differ from the recorded production ledger'; END IF;
  src := $src5360da50$-- C3 FIN-02: final, order-independent financial adapters above A+B+C2.
-- Original August migrations and all51 accepted SQL files remain byte-immutable.
-- No row backfill or new money/state policy. Existing idempotency ACL stays closed.
BEGIN;
SET LOCAL lock_timeout = '5s';

CREATE OR REPLACE FUNCTION public._create_sale_with_items_core(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state,
  p_infer_courier_state boolean
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_total numeric(12,2) := 0;
  v_status public.order_status;
  v_order public.orders%ROWTYPE;
  v_tnum int;
  v_item jsonb;
  v_pid uuid;
  v_qty numeric;
  v_prod public.products%ROWTYPE;
  v_order_paid numeric(12,2);
  v_order_collected numeric(12,2);
  v_state public.courier_state := p_courier_state;
BEGIN
  PERFORM monjez_private.assert_active_actor();
  PERFORM public._assert_staff(v_tenant);

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'empty_items';
  END IF;
  IF p_paid IS NULL OR p_paid < 0 THEN RAISE EXCEPTION 'invalid_paid'; END IF;

  IF p_customer_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_tenant
  ) THEN
    RAISE EXCEPTION 'customer_not_found';
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_courier_id IS NOT NULL THEN RAISE EXCEPTION 'courier_id_must_be_null_for_direct'; END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NOT NULL THEN
      RAISE EXCEPTION 'courier_state_must_be_null_for_direct';
    END IF;
    v_state := NULL;
  ELSE
    IF p_courier_id IS NULL THEN RAISE EXCEPTION 'courier_requires_courier'; END IF;
    IF NOT EXISTS (
      SELECT 1 FROM public.couriers
       WHERE id = p_courier_id AND tenant_id = v_tenant AND is_active = true
    ) THEN
      RAISE EXCEPTION 'courier_not_found';
    END IF;
    IF NOT p_infer_courier_state AND p_courier_state IS NULL THEN RAISE EXCEPTION 'courier_state_required'; END IF;
    IF p_courier_state = 'returned' THEN RAISE EXCEPTION 'returned_not_allowed_at_creation'; END IF;
  END IF;

  FOR v_item IN SELECT * FROM jsonb_array_elements(p_items) LOOP
    BEGIN
      v_pid := (v_item->>'productId')::uuid;
      v_qty := (v_item->>'qty')::numeric;
    EXCEPTION WHEN OTHERS THEN
      RAISE EXCEPTION 'invalid_item';
    END;
    IF v_pid IS NULL OR v_qty IS NULL OR v_qty <= 0
       OR v_qty > 9999999999.99 OR v_qty <> trunc(v_qty, 2) THEN
      RAISE EXCEPTION 'invalid_item';
    END IF;
    SELECT * INTO v_prod FROM public.products WHERE id = v_pid FOR UPDATE;
    IF NOT FOUND OR v_prod.tenant_id <> v_tenant THEN RAISE EXCEPTION 'product_not_found'; END IF;
    IF NOT v_prod.is_active THEN RAISE EXCEPTION 'product_inactive: %', v_prod.name; END IF;
    IF v_prod.stock < v_qty THEN RAISE EXCEPTION 'insufficient_stock: %', v_prod.name; END IF;
    v_total := v_total + (v_prod.price * v_qty);
  END LOOP;

  IF p_paid > v_total THEN RAISE EXCEPTION 'paid_exceeds_total'; END IF;

  IF p_delivery = 'courier' AND p_infer_courier_state THEN
    v_state := CASE
      WHEN p_paid = 0 THEN 'pending'::public.courier_state
      WHEN p_paid = v_total THEN 'delivered_full'::public.courier_state
      ELSE 'delivered_partial'::public.courier_state
    END;
  END IF;

  IF p_delivery = 'direct' THEN
    IF p_paid < v_total AND p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
    v_order_paid := p_paid;
    v_order_collected := 0;
    v_status := CASE
      WHEN p_paid >= v_total THEN 'paid'::public.order_status
      WHEN p_paid > 0 THEN 'partial'::public.order_status
      ELSE 'debt'::public.order_status
    END;
  ELSE
    IF v_state IS NULL OR v_state = 'returned' THEN RAISE EXCEPTION 'invalid_state'; END IF;
    CASE v_state
      WHEN 'pending' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_none' THEN
        IF p_paid <> 0 THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := 0;
      WHEN 'delivered_partial' THEN
        IF p_paid <= 0 OR p_paid >= v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
        v_order_collected := p_paid;
      WHEN 'delivered_full' THEN
        IF p_paid <> v_total THEN RAISE EXCEPTION 'invalid_paid_for_courier_state'; END IF;
        v_order_collected := v_total;
      ELSE
        RAISE EXCEPTION 'invalid_state';
    END CASE;
    v_order_paid := 0;
    v_status := 'debt'::public.order_status;
  END IF;

  v_tnum := public.next_order_number(v_tenant);
  INSERT INTO public.orders(
    tenant_id, customer_id, total, paid, status, delivery, courier_id,
    courier_state, collected_by_courier, created_by, tenant_number
  ) VALUES (
    v_tenant, p_customer_id, v_total, v_order_paid, v_status, p_delivery,
    p_courier_id, v_state, v_order_collected, v_uid, v_tnum
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
END;
$$;

REVOKE ALL ON FUNCTION public._create_sale_with_items_core(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state, boolean
) FROM PUBLIC, anon, authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items_v2(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  PERFORM monjez_private.assert_active_actor();
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    p_courier_state, false
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb, public.courier_state
) TO authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items(
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  PERFORM monjez_private.assert_active_actor();
  RETURN public._create_sale_with_items_core(
    p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items,
    NULL, true
  );
END;
$$;
REVOKE ALL ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_outcome_v2(
  p_order_id uuid,
  p_state public.courier_state,
  p_collected numeric,
  p_customer_id uuid
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_order public.orders%ROWTYPE;
  v_target_collected numeric(12,2);
  v_customer_id uuid;
BEGIN
  PERFORM monjez_private.assert_active_actor();
  SELECT * INTO v_order FROM public.orders WHERE id = p_order_id FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_order.tenant_id);

  IF v_order.delivery <> 'courier' OR v_order.courier_state IS NULL THEN RAISE EXCEPTION 'not_a_courier_order'; END IF;
  IF p_state IS NULL THEN RAISE EXCEPTION 'invalid_state'; END IF;

  IF p_state = 'returned' THEN
    IF v_order.courier_state NOT IN ('pending', 'delivered_none') THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN public.return_courier_order(p_order_id);
  END IF;

  IF p_state IN ('pending', 'delivered_none') THEN
    v_target_collected := 0;
  ELSIF p_state = 'delivered_partial' THEN
    IF p_collected IS NULL OR p_collected <= 0 OR p_collected >= v_order.total THEN RAISE EXCEPTION 'invalid_collected'; END IF;
    v_target_collected := p_collected;
  ELSIF p_state = 'delivered_full' THEN
    v_target_collected := v_order.total;
  ELSE
    RAISE EXCEPTION 'invalid_state';
  END IF;

  IF p_state = v_order.courier_state THEN
    IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;
    IF v_target_collected <> COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'invalid_transition'; END IF;
    RETURN jsonb_build_object(
      'success', true, 'order_id', v_order.id, 'state', v_order.courier_state,
      'collected', COALESCE(v_order.collected_by_courier, 0), 'idempotent', true
    );
  END IF;

  IF NOT (
    (v_order.courier_state = 'pending' AND p_state IN ('delivered_none','delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_none' AND p_state IN ('delivered_partial','delivered_full'))
    OR (v_order.courier_state = 'delivered_partial' AND p_state = 'delivered_full')
  ) THEN
    RAISE EXCEPTION 'invalid_transition';
  END IF;

  IF v_target_collected < COALESCE(v_order.collected_by_courier, 0) THEN RAISE EXCEPTION 'custody_cannot_decrease'; END IF;

  v_customer_id := v_order.customer_id;
  IF p_state IN ('delivered_none', 'delivered_partial') THEN
    IF v_customer_id IS NULL THEN
      IF p_customer_id IS NULL THEN RAISE EXCEPTION 'customer_required_for_debt'; END IF;
      IF NOT EXISTS (
        SELECT 1 FROM public.customers WHERE id = p_customer_id AND tenant_id = v_order.tenant_id
      ) THEN
        RAISE EXCEPTION 'customer_not_found';
      END IF;
      v_customer_id := p_customer_id;
    ELSIF p_customer_id IS NOT NULL AND p_customer_id <> v_customer_id THEN
      RAISE EXCEPTION 'customer_mismatch';
    END IF;
  END IF;

  UPDATE public.orders
     SET courier_state = p_state,
         collected_by_courier = v_target_collected,
         customer_id = v_customer_id
   WHERE id = p_order_id;

  RETURN jsonb_build_object(
    'success', true, 'order_id', p_order_id, 'state', p_state,
    'collected', v_target_collected, 'customer_id', v_customer_id
  );
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_outcome_v2(uuid, public.courier_state, numeric, uuid)
  TO authenticated;

CREATE OR REPLACE FUNCTION public.update_courier_order_state(
  p_order_id uuid,
  p_state text,
  p_collected numeric DEFAULT NULL
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE
  v_state public.courier_state;
BEGIN
  PERFORM monjez_private.assert_active_actor();
  IF p_state IS NULL OR p_state NOT IN ('pending','delivered_none','delivered_partial','delivered_full','returned') THEN
    RAISE EXCEPTION 'invalid_state';
  END IF;
  v_state := p_state::public.courier_state;
  RETURN public.update_courier_outcome_v2(p_order_id, v_state, p_collected, NULL);
END;
$$;
REVOKE ALL ON FUNCTION public.update_courier_order_state(uuid, text, numeric) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.update_courier_order_state(uuid, text, numeric) TO authenticated;

CREATE OR REPLACE FUNCTION public.create_sale_with_items_idempotent(
  p_idempotency_key uuid,
  p_customer_id uuid,
  p_delivery public.delivery_kind,
  p_courier_id uuid,
  p_paid numeric,
  p_method public.payment_method,
  p_items jsonb,
  p_courier_state public.courier_state
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_tenant uuid := public.current_tenant_id();
  v_uid uuid := auth.uid();
  v_operation constant text := 'sale.create.v2';
  v_request jsonb;
  v_request_hash text;
  v_inserted integer := 0;
  v_existing_hash text;
  v_existing_request jsonb;
  v_result jsonb;
BEGIN
  PERFORM monjez_private.assert_active_actor();
  PERFORM public._assert_staff(v_tenant);

  IF p_idempotency_key IS NULL THEN
    RAISE EXCEPTION 'idempotency_key_required';
  END IF;

  -- jsonb gives deterministic object-key serialization. Array order remains part
  -- of the request identity deliberately: item order is part of the submitted
  -- canonical sale request until the canonical sale RPC defines otherwise.
  v_request := jsonb_build_object(
    'customer_id', p_customer_id,
    'delivery', p_delivery,
    'courier_id', p_courier_id,
    'paid', p_paid,
    'method', p_method,
    'items', p_items,
    'courier_state', p_courier_state
  );

  -- MD5 is only a compact diagnostic fingerprint. Replay authorization also
  -- requires exact jsonb request equality, so a hash collision cannot authorize
  -- a mismatched financial request.
  v_request_hash := md5(v_request::text);

  INSERT INTO public.financial_idempotency(
    tenant_id,
    operation,
    idempotency_key,
    request_hash,
    request_payload,
    created_by
  ) VALUES (
    v_tenant,
    v_operation,
    p_idempotency_key,
    v_request_hash,
    v_request,
    v_uid
  )
  ON CONFLICT (tenant_id, operation, idempotency_key) DO NOTHING;

  GET DIAGNOSTICS v_inserted = ROW_COUNT;

  IF v_inserted = 1 THEN
    -- Reservation and financial write share one PostgreSQL transaction. Any
    -- uncaught canonical-write failure rolls the reservation back too.
    v_result := public.create_sale_with_items_v2(
      p_customer_id,
      p_delivery,
      p_courier_id,
      p_paid,
      p_method,
      p_items,
      p_courier_state
    );

    UPDATE public.financial_idempotency
       SET result = v_result,
           completed_at = now()
     WHERE tenant_id = v_tenant
       AND operation = v_operation
       AND idempotency_key = p_idempotency_key;

    RETURN v_result;
  END IF;

  -- A same-key concurrent INSERT waits on the unique key. Once the owner
  -- transaction commits this row carries the original result; if it rolls back,
  -- the waiting INSERT can become the owner instead.
  SELECT request_hash, request_payload, result
    INTO v_existing_hash, v_existing_request, v_result
    FROM public.financial_idempotency
   WHERE tenant_id = v_tenant
     AND operation = v_operation
     AND idempotency_key = p_idempotency_key
   FOR UPDATE;

  IF NOT FOUND THEN
    RAISE EXCEPTION 'idempotency_state_missing';
  END IF;

  IF v_existing_hash <> v_request_hash OR v_existing_request <> v_request THEN
    RAISE EXCEPTION 'idempotency_conflict';
  END IF;

  IF v_result IS NULL THEN
    RAISE EXCEPTION 'idempotency_incomplete';
  END IF;

  RETURN v_result;
END;
$$;

REVOKE ALL ON FUNCTION public.create_sale_with_items_idempotent(
  uuid, uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.create_sale_with_items_idempotent(
  uuid, uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) TO authenticated;

-- FIN-IDEM must be server-enforced, not merely a client convention. Once this
-- migration lands, application roles cannot bypass the idempotency wrapper by
-- calling either the canonical v2 write or the legacy six-argument adapter.
REVOKE EXECUTE ON FUNCTION public.create_sale_with_items_v2(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb,
  public.courier_state
) FROM authenticated;
REVOKE EXECUTE ON FUNCTION public.create_sale_with_items(
  uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb
) FROM authenticated;

NOTIFY pgrst, 'reload schema';
COMMIT;
$src5360da50$;
  IF md5(src) <> 'a6ecc666fa0381aa9f87d0efdae9f48b' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261029044024_c3_reconcile_financial_adapters'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261029044024') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261029044024'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261029044024', 'c3_reconcile_financial_adapters', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.5
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> 'd92c3f6bcde14e89e86709cdb704fd19' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261103060658: expected exactly 56 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '4a164bf476878af908a2cbfbc6b9f180' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261103060658: ledger statements differ from the recorded production ledger'; END IF;
  src := $srce18e719a$-- C5-COLLECTION-RETRY-01. Forward-only, owner-authorized candidate.
-- No financial formula, table data, rounding or existing function body changes.
BEGIN;
CREATE FUNCTION public.collect_order_debt_idempotent(
  p_idempotency_key uuid, p_order_id uuid, p_amount numeric,
  p_method public.payment_method
)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = ''
AS $collection$
DECLARE
  v_actor uuid := auth.uid();
  v_tenant uuid;
  v_operation constant text := 'order.debt.collect.v1';
  v_request jsonb;
  v_inserted integer;
  v_existing public.financial_idempotency%ROWTYPE;
  v_result jsonb;
BEGIN
  PERFORM monjez_private.assert_active_actor();
  IF v_actor IS NULL THEN RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'unauthenticated'; END IF;
  SELECT tenant_id INTO v_tenant FROM public.orders WHERE id = p_order_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'order_not_found'; END IF;
  PERFORM public._assert_staff(v_tenant);
  IF p_idempotency_key IS NULL THEN RAISE EXCEPTION 'idempotency_key_required'; END IF;
  v_request := jsonb_build_object('order_id',p_order_id,'amount',p_amount,'method',p_method);
  INSERT INTO public.financial_idempotency(tenant_id,operation,idempotency_key,request_hash,request_payload,created_by)
    VALUES (v_tenant,v_operation,p_idempotency_key,md5(v_request::text),v_request,v_actor)
    ON CONFLICT (tenant_id,operation,idempotency_key) DO NOTHING;
  GET DIAGNOSTICS v_inserted = ROW_COUNT;
  IF v_inserted = 1 THEN
    -- The existing canonical row lock and accounting remain authoritative.
    -- Any failure rolls back this reservation and all financial effects.
    v_result := public.collect_order_debt(p_order_id,p_amount,p_method);
    UPDATE public.financial_idempotency SET result = v_result, completed_at = now()
      WHERE tenant_id = v_tenant AND operation = v_operation AND idempotency_key = p_idempotency_key;
    RETURN v_result;
  END IF;
  -- Unique-key conflict waits for the owner transaction. Check live authority
  -- again after that wait before exposing any original result.
  PERFORM public._assert_staff(v_tenant);
  SELECT * INTO v_existing FROM public.financial_idempotency
    WHERE tenant_id = v_tenant AND operation = v_operation AND idempotency_key = p_idempotency_key
    FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'idempotency_state_missing'; END IF;
  IF v_existing.created_by IS DISTINCT FROM v_actor
     OR v_existing.request_payload IS DISTINCT FROM v_request
     OR v_existing.request_hash IS DISTINCT FROM md5(v_request::text) THEN
    RAISE EXCEPTION 'idempotency_conflict';
  END IF;
  IF v_existing.result IS NULL THEN RAISE EXCEPTION 'idempotency_incomplete'; END IF;
  RETURN v_existing.result;
END;
$collection$;
REVOKE ALL ON FUNCTION public.collect_order_debt_idempotent(uuid,uuid,numeric,public.payment_method) FROM PUBLIC,anon;
GRANT EXECUTE ON FUNCTION public.collect_order_debt_idempotent(uuid,uuid,numeric,public.payment_method) TO authenticated;
REVOKE EXECUTE ON FUNCTION public.collect_order_debt(uuid,numeric,public.payment_method) FROM PUBLIC,anon,authenticated;
COMMIT;
$srce18e719a$;
  IF md5(src) <> 'c9aa3c9d59fc7973741a61bcb4888caa' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261103060658_c5_keyed_debt_collection'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261103060658') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261103060658'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261103060658', 'c5_keyed_debt_collection', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.6
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '51cfbefdfef5431f6b838a3f41014ef3' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261106145346: expected exactly 57 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '6919a6c20e109b900a8534c3343f269a' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261106145346: ledger statements differ from the recorded production ledger'; END IF;
  src := $src5636a42b$-- C5-PROFIT-BASIS-01: additive reporting only; legacy snapshots stay unchanged.
BEGIN;
SET LOCAL lock_timeout = '5s';

CREATE VIEW public.day_close_profit_report
WITH (security_invoker = true)
AS
SELECT
  dc.id, dc.tenant_id, dc.closed_for,
  dc.sales, dc.collected, dc.expenses,
  dc.realized_profit,
  dc.realized_profit AS realized_margin_before_expenses,
  dc.realized_profit - dc.expenses AS realized_net_profit,
  dc.customer_debts, dc.unsettled_custody,
  dc.note, dc.created_at
FROM public.day_closes AS dc;

-- Simple views can be updatable. Expose only SELECT, using the caller's RLS.
REVOKE ALL ON TABLE public.day_close_profit_report FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.day_close_profit_report TO authenticated;

COMMENT ON VIEW public.day_close_profit_report IS
  'Recorded collection-based closing margin and net after recorded expenses; legacy values and history unchanged.';
COMMENT ON COLUMN public.day_close_profit_report.realized_profit IS
  'Legacy before-expense payment-weighted margin; retained for compatibility.';
COMMENT ON COLUMN public.day_close_profit_report.realized_net_profit IS
  'Saved before-expense margin minus saved expenses once; not a reconstruction or audit of historical inputs.';

COMMIT;
$src5636a42b$;
  IF md5(src) <> '1d313800b3bbaa1b1ef0c7b3e9517269' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261106145346_c5_day_close_profit_report'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261106145346') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261106145346'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261106145346', 'c5_day_close_profit_report', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.7
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '8b5d67ee766f61b071d71e3e2dc11f47' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110090000: expected exactly 58 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> 'd390be75dc0ea79bfaa86dbd633f82db' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261110090000: ledger statements differ from the recorded production ledger'; END IF;
  src := $srca5c95672$-- C-COURIER-SETTLE-01: settlement accepts only orders currently in this courier's custody.
-- Forward-only replacement of settle_courier_orders; only the custody check changes.
-- No data is modified. Grants are preserved by CREATE OR REPLACE.
BEGIN;
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
  PERFORM monjez_private.assert_active_actor();
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
    -- NULL-safe: return_courier_order and a prior settlement both clear courier_id.
    -- With "<>", a NULL courier_id made the check NULL (not true), so a returned
    -- order passed and settlement erased its returned mark (it became debt again).
    IF v_order.tenant_id IS DISTINCT FROM v_tenant
       OR v_order.courier_state IS NOT DISTINCT FROM 'returned'::courier_state THEN
      RAISE EXCEPTION 'order_not_in_courier_custody';
    END IF;
    -- Accepted retry contract: a repeated settlement of an order already settled
    -- (custody cleared, not returned) succeeds with no second cash and no change.
    IF v_order.courier_id IS NULL AND v_order.courier_state IS NULL
       AND v_order.delivery = 'direct'::delivery_kind
       AND COALESCE(v_order.collected_by_courier, 0) = 0 THEN
      CONTINUE;
    END IF;
    IF v_order.courier_id IS DISTINCT FROM p_courier_id
       OR v_order.delivery IS DISTINCT FROM 'courier'::delivery_kind THEN
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
COMMIT;
$srca5c95672$;
  IF md5(src) <> '70cd7a3a78fba2e41c07d841aa6588fd' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110090000_courier_settle_custody_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110090000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110090000'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110090000', 'courier_settle_custody_01', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.8
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> 'a2290bc69f202f533f608e9da705620e' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110130000: expected exactly 59 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> 'fe486e75744ff85b9cd172dcc09dbb15' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261110130000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src8c783649$-- C-PADDLE-01: the webhook locks the tenant row FOR NO KEY UPDATE instead of FOR UPDATE.
-- Body is 20261021140746_webhook_errors_01 with only the tenant lock changed.
BEGIN;
CREATE OR REPLACE FUNCTION public.apply_subscription_webhook(
  p_environment text, p_event_id text, p_event_type text,
  p_occurred_at timestamptz, p_subscription jsonb
) RETURNS jsonb
LANGUAGE plpgsql SECURITY INVOKER
SET search_path = pg_catalog, pg_temp
SET lock_timeout = '2s'
SET timezone = 'UTC'
AS $function$
DECLARE
  v_subscription_id text := p_subscription->>'id';
  v_request jsonb;
  v_receipt monjez_private.billing_webhook_receipts%ROWTYPE;
  v_previous monjez_private.billing_webhook_receipts%ROWTYPE;
  v_history monjez_private.billing_webhook_receipts%ROWTYPE;
  v_binding monjez_private.billing_tenant_bindings%ROWTYPE;
  v_old public.subscriptions%ROWTYPE;
  v_tenant public.tenants%ROWTYPE;
  v_tenant_id uuid;
  v_user_id uuid;
  v_floor timestamptz;
  v_state jsonb;
  v_old_state jsonb;
  v_created_at timestamptz;
  v_known_created_at timestamptz;
  v_binding_floor timestamptz;
  v_project boolean := false;
  v_outcome text := 'applied';
  v_rows integer;
BEGIN
  IF current_user <> 'service_role' OR current_setting('role',true) IS DISTINCT FROM 'service_role' THEN
    RAISE EXCEPTION USING ERRCODE='42501', MESSAGE='billing_service_required';
  END IF;
  IF p_environment IS NULL OR p_environment NOT IN ('sandbox','live')
    OR p_event_id IS NULL OR p_event_id !~ '^evt_[a-z0-9]{26}$'
    OR p_event_type IS NULL OR p_event_type NOT IN ('subscription.created','subscription.updated','subscription.canceled')
    OR p_occurred_at IS NULL OR NOT isfinite(p_occurred_at)
    OR jsonb_typeof(p_subscription) IS DISTINCT FROM 'object'
    OR octet_length(p_subscription::text)>8192
    OR v_subscription_id IS NULL OR v_subscription_id !~ '^sub_[a-z0-9]{26}$'
    OR p_subscription->>'status' IS NULL OR p_subscription->>'status' NOT IN ('active','trialing','past_due','paused','canceled')
    OR (p_event_type='subscription.canceled' AND p_subscription->>'status'<>'canceled')
    OR p_subscription->>'customer_id' IS NULL OR p_subscription->>'customer_id' !~ '^ctm_[a-z0-9]{26}$'
  THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_event_invalid';
  END IF;
  IF EXISTS (SELECT 1 FROM jsonb_object_keys(p_subscription) k
    WHERE k NOT IN ('id','created_at','customer_id','tenant_id','user_id','product_id','price_id','status','period_start','period_end','cancel_at_period_end'))
    OR p_subscription->>'created_at' IS NULL
    OR p_subscription->>'created_at' !~ '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$' THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_event_shape_invalid';
  END IF;
  v_created_at := (p_subscription->>'created_at')::timestamptz;
  IF NOT isfinite(v_created_at) OR v_created_at>p_occurred_at THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_creation_time_invalid';
  END IF;
  v_request := jsonb_build_object('type',p_event_type,'occurred_epoch',extract(epoch FROM p_occurred_at),'subscription',p_subscription);
  -- Global provider-ID serialization also protects the existing global unique key across environments.
  PERFORM pg_advisory_xact_lock(hashtextextended('monjez:billing:subscription:'||v_subscription_id,0));
  PERFORM pg_advisory_xact_lock(hashtextextended('monjez:billing:event:'||p_environment||':'||p_event_id,0));
  SELECT * INTO v_receipt FROM monjez_private.billing_webhook_receipts
    WHERE environment=p_environment AND event_id=p_event_id;
  IF FOUND THEN
    IF v_receipt.request IS DISTINCT FROM v_request THEN
      RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_event_id_conflict';
    END IF;
    RETURN jsonb_build_object('status','duplicate');
  END IF;
  SELECT * INTO v_old FROM public.subscriptions WHERE paddle_subscription_id=v_subscription_id FOR UPDATE;
  IF v_old.id IS NULL AND p_event_type<>'subscription.created' THEN
    RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_creation_snapshot_required';
  END IF;
  SELECT * INTO v_history FROM monjez_private.billing_webhook_receipts
    WHERE environment IN ('sandbox','live') AND paddle_subscription_id=v_subscription_id LIMIT 1;
  IF FOUND AND (v_history.environment IS DISTINCT FROM p_environment OR v_old.id IS NULL) THEN
    RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_historical_identity_requires_reconciliation';
  END IF;
  IF v_old.id IS NOT NULL AND v_old.environment IS DISTINCT FROM p_environment THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_environment_conflict';
  END IF;
  IF v_old.id IS NOT NULL AND v_old.paddle_customer_id IS DISTINCT FROM p_subscription->>'customer_id' THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_customer_conflict';
  END IF;
  SELECT subscription_created_at INTO v_known_created_at FROM monjez_private.billing_webhook_receipts
    WHERE environment=p_environment AND paddle_subscription_id=v_subscription_id LIMIT 1;
  IF FOUND AND v_known_created_at IS DISTINCT FROM v_created_at THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_creation_time_conflict';
  END IF;
  v_tenant_id := coalesce((p_subscription->>'tenant_id')::uuid,v_old.tenant_id);
  v_user_id := coalesce((p_subscription->>'user_id')::uuid,v_old.user_id);
  IF v_tenant_id IS NULL OR v_user_id IS NULL OR
    (v_old.id IS NOT NULL AND (v_old.tenant_id IS DISTINCT FROM v_tenant_id OR v_old.user_id IS DISTINCT FROM v_user_id)) THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_mapping_invalid';
  END IF;
  -- FOR NO KEY UPDATE: still excludes every other writer of this tenant row, but no longer
  -- waits on the FK KEY SHARE locks held by concurrent sales/collections of the same tenant.
  -- The UPDATE below changes only non-key columns, so it needs no stronger lock.
  SELECT * INTO v_tenant FROM public.tenants WHERE id=v_tenant_id FOR NO KEY UPDATE;
  IF NOT FOUND OR v_tenant.owner_user_id IS DISTINCT FROM v_user_id THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_owner_invalid';
  END IF;
  IF v_old.id IS NULL AND EXISTS (SELECT 1 FROM public.subscriptions
    WHERE tenant_id=v_tenant_id AND environment=p_environment AND created_at=v_created_at
      AND paddle_subscription_id<>v_subscription_id) THEN
    RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_creation_order_ambiguous';
  END IF;
  -- Both environments use the existing public created_at ordering in billing.
  -- A legacy arrival timestamp cannot silently outrank a new provider creation.
  IF p_event_type='subscription.created' AND EXISTS (SELECT 1 FROM public.subscriptions s
    WHERE s.tenant_id=v_tenant_id AND s.environment=p_environment AND s.paddle_subscription_id<>v_subscription_id
      AND s.created_at>=coalesce(v_old.created_at,v_created_at)
      AND NOT EXISTS (SELECT 1 FROM monjez_private.billing_webhook_receipts r
        WHERE r.environment=p_environment AND r.paddle_subscription_id=s.paddle_subscription_id
          AND r.subscription_created_at=s.created_at)) THEN
    RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_legacy_display_order_unknown';
  END IF;
  -- Preserve the prior handler's existing plan/customer and canceled-period semantics.
  v_state := jsonb_build_object(
    'tenant_id',v_tenant_id,'user_id',v_user_id,'id',v_subscription_id,
    'customer_id',CASE WHEN v_old.id IS NOT NULL AND p_event_type<>'subscription.created' THEN v_old.paddle_customer_id ELSE p_subscription->>'customer_id' END,
    'product_id',CASE WHEN v_old.id IS NOT NULL AND p_event_type<>'subscription.created' THEN v_old.product_id ELSE p_subscription->>'product_id' END,
    'price_id',CASE WHEN v_old.id IS NOT NULL AND p_event_type<>'subscription.created' THEN v_old.price_id ELSE p_subscription->>'price_id' END,
    'status',p_subscription->>'status',
    'period_start',CASE WHEN v_old.id IS NOT NULL AND p_event_type='subscription.canceled' THEN v_old.current_period_start
      ELSE coalesce((p_subscription->>'period_start')::timestamptz,v_old.current_period_start) END,
    'period_end',CASE WHEN v_old.id IS NOT NULL AND p_event_type='subscription.canceled' THEN v_old.current_period_end
      ELSE coalesce((p_subscription->>'period_end')::timestamptz,v_old.current_period_end) END,
    'cancel_at_period_end',CASE WHEN p_event_type='subscription.created' OR (v_old.id IS NOT NULL AND p_event_type<>'subscription.updated') THEN coalesce(v_old.cancel_at_period_end,false)
      ELSE coalesce((p_subscription->>'cancel_at_period_end')::boolean,false) END);
  IF coalesce(length(v_state->>'product_id'),0) NOT BETWEEN 1 AND 256
    OR coalesce(length(v_state->>'price_id'),0) NOT BETWEEN 1 AND 256 THEN
    RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_product_mapping_missing';
  END IF;
  SELECT * INTO v_previous FROM monjez_private.billing_webhook_receipts
    WHERE environment=p_environment AND paddle_subscription_id=v_subscription_id AND outcome<>'stale'
    ORDER BY occurred_at DESC,event_id DESC LIMIT 1;
  SELECT max(legacy_floor) INTO v_floor FROM monjez_private.billing_webhook_receipts
    WHERE environment=p_environment AND paddle_subscription_id=v_subscription_id;
  IF v_previous.event_id IS NULL AND v_old.id IS NOT NULL THEN
    v_floor := v_old.updated_at;
  END IF;
  v_old_state := jsonb_build_object(
    'tenant_id',v_old.tenant_id,'user_id',v_old.user_id,'id',v_old.paddle_subscription_id,
    'customer_id',v_old.paddle_customer_id,'product_id',v_old.product_id,'price_id',v_old.price_id,'status',v_old.status,
    'period_start',v_old.current_period_start,'period_end',v_old.current_period_end,'cancel_at_period_end',coalesce(v_old.cancel_at_period_end,false));
  IF v_previous.event_id IS NOT NULL AND p_occurred_at<v_previous.occurred_at THEN
    v_outcome := 'stale';
  ELSIF v_previous.event_id IS NOT NULL AND p_occurred_at=v_previous.occurred_at THEN
    IF v_state IS DISTINCT FROM v_previous.resolved_state THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_event_order_ambiguous';
    END IF;
    v_outcome := 'unchanged';
  ELSIF v_floor IS NOT NULL AND p_occurred_at<=v_floor
    AND (v_previous.event_id IS NULL OR v_previous.occurred_at<v_floor) THEN
    IF v_state IS DISTINCT FROM v_old_state THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_legacy_order_unknown';
    END IF;
    v_outcome := 'legacy_repaired';
  END IF;
  -- Only a created event may replace a known non-null binding. Other streams remain durable/non-current.
  IF p_environment='live' THEN
    SELECT * INTO v_binding FROM monjez_private.billing_tenant_bindings WHERE tenant_id=v_tenant_id FOR UPDATE;
    IF v_binding.tenant_id IS NOT NULL AND v_tenant.paddle_subscription_id IS DISTINCT FROM v_binding.paddle_subscription_id THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_binding_cache_conflict';
    END IF;
    IF v_binding.tenant_id IS NULL AND v_tenant.paddle_subscription_id IS NOT NULL THEN
      IF v_tenant.paddle_subscription_id=v_subscription_id THEN
        v_binding.subscription_created_at:=v_created_at;
      ELSE
        SELECT created_at INTO v_binding_floor FROM public.subscriptions
          WHERE paddle_subscription_id=v_tenant.paddle_subscription_id AND environment='live'
            AND tenant_id=v_tenant_id AND user_id=v_user_id;
        v_binding.legacy_floor:=coalesce(v_binding_floor,v_tenant.updated_at);
      END IF;
      v_binding.tenant_id:=v_tenant_id;
      v_binding.paddle_subscription_id:=v_tenant.paddle_subscription_id;
    END IF;
    IF v_binding.tenant_id IS NULL THEN
      v_binding.tenant_id:=v_tenant_id;
      v_binding.paddle_subscription_id:=v_subscription_id;
      v_binding.subscription_created_at:=v_created_at;
      v_project:=true;
    ELSIF v_binding.paddle_subscription_id=v_subscription_id THEN
      IF v_binding.subscription_created_at IS NOT NULL AND v_binding.subscription_created_at<>v_created_at THEN
        RAISE EXCEPTION USING ERRCODE='22023', MESSAGE='billing_binding_creation_conflict';
      END IF;
      v_binding.subscription_created_at:=v_created_at;
      v_binding.legacy_floor:=NULL;
      v_project:=true;
    ELSIF p_event_type='subscription.created' THEN
      IF v_binding.subscription_created_at IS NULL THEN
        IF v_created_at<=v_binding.legacy_floor THEN
          RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_legacy_binding_order_unknown';
        END IF;
        v_project:=true;
      ELSIF v_created_at=v_binding.subscription_created_at THEN
        RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_binding_order_ambiguous';
      ELSE
        v_project:=v_created_at>v_binding.subscription_created_at;
      END IF;
      IF v_project THEN
        v_binding.paddle_subscription_id:=v_subscription_id;
        v_binding.subscription_created_at:=v_created_at;
        v_binding.legacy_floor:=NULL;
      END IF;
    END IF;
    -- Existing billing reads order public created_at. Legacy arrival clocks must never
    -- silently make a newly projected binding disagree with that existing consumer.
    IF v_project AND EXISTS (SELECT 1 FROM public.subscriptions
      WHERE tenant_id=v_tenant_id AND environment='live' AND paddle_subscription_id<>v_subscription_id
        AND created_at>=coalesce(v_old.created_at,v_created_at)) THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_legacy_display_order_unknown';
    END IF;
    INSERT INTO monjez_private.billing_tenant_bindings AS b(tenant_id,paddle_subscription_id,subscription_created_at,legacy_floor)
      VALUES(v_tenant_id,v_binding.paddle_subscription_id,v_binding.subscription_created_at,v_binding.legacy_floor)
      ON CONFLICT(tenant_id) DO UPDATE SET paddle_subscription_id=excluded.paddle_subscription_id,
        subscription_created_at=excluded.subscription_created_at,legacy_floor=excluded.legacy_floor;
    GET DIAGNOSTICS v_rows=ROW_COUNT;
    IF v_rows<>1 THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_required_binding_missing';
    END IF;
  END IF;
  IF v_outcome='applied' THEN
    IF v_old.id IS NULL THEN
      INSERT INTO public.subscriptions(tenant_id,user_id,paddle_subscription_id,paddle_customer_id,product_id,price_id,
        status,current_period_start,current_period_end,cancel_at_period_end,environment,created_at)
      VALUES(v_tenant_id,v_user_id,v_subscription_id,v_state->>'customer_id',v_state->>'product_id',v_state->>'price_id',
        v_state->>'status',(v_state->>'period_start')::timestamptz,(v_state->>'period_end')::timestamptz,
        (v_state->>'cancel_at_period_end')::boolean,p_environment,v_created_at);
    ELSE
      UPDATE public.subscriptions SET paddle_customer_id=v_state->>'customer_id',product_id=v_state->>'product_id',
        price_id=v_state->>'price_id',status=v_state->>'status',current_period_start=(v_state->>'period_start')::timestamptz,
        current_period_end=(v_state->>'period_end')::timestamptz,cancel_at_period_end=(v_state->>'cancel_at_period_end')::boolean,
        updated_at=now()
      WHERE id=v_old.id AND tenant_id=v_tenant_id AND user_id=v_user_id AND environment=p_environment;
    END IF;
    GET DIAGNOSTICS v_rows=ROW_COUNT;
    IF v_rows<>1 THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_required_row_missing';
    END IF;
  END IF;
  IF v_project THEN
    -- A late created notification may repair binding, but must project the newest stored stream state.
    IF v_outcome='stale' THEN
      v_state:=v_old_state;
    END IF;
    IF (v_tenant.subscription_status,v_tenant.subscription_plan,v_tenant.paddle_customer_id,v_tenant.paddle_subscription_id)
      IS DISTINCT FROM (v_state->>'status',v_state->>'product_id',v_state->>'customer_id',v_subscription_id) THEN
    UPDATE public.tenants SET subscription_status=v_state->>'status',subscription_plan=v_state->>'product_id',
      paddle_customer_id=v_state->>'customer_id',paddle_subscription_id=v_subscription_id
      WHERE id=v_tenant_id AND owner_user_id=v_user_id;
    GET DIAGNOSTICS v_rows=ROW_COUNT;
    IF v_rows<>1 THEN
      RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_required_tenant_missing';
    END IF;
    END IF;
  ELSIF p_environment='live' AND v_outcome='applied' THEN
    v_outcome:='non_current';
  END IF;
  INSERT INTO monjez_private.billing_webhook_receipts(environment,event_id,event_type,occurred_at,
    paddle_subscription_id,subscription_created_at,tenant_id,request,resolved_state,outcome,tenant_projected,legacy_floor)
  VALUES(p_environment,p_event_id,p_event_type,p_occurred_at,v_subscription_id,v_created_at,v_tenant_id,v_request,v_state,v_outcome,v_project,v_floor);
  GET DIAGNOSTICS v_rows=ROW_COUNT;
  IF v_rows<>1 THEN
    RAISE EXCEPTION USING ERRCODE='P0001', MESSAGE='billing_receipt_missing';
  END IF;
  RETURN jsonb_build_object('status',v_outcome);
END;
$function$;
REVOKE ALL ON FUNCTION public.apply_subscription_webhook(text,text,text,timestamptz,jsonb) FROM PUBLIC, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.apply_subscription_webhook(text,text,text,timestamptz,jsonb) TO service_role;
COMMIT;
$src8c783649$;
  IF md5(src) <> '9bbee16dc92735a1480c27547b92e583' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110130000_paddle_webhook_no_key_update_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110130000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110130000'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110130000', 'paddle_webhook_no_key_update_01', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.9
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> 'f0ce5eb1d369d3dca6cb930a74e19f19' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110140000: expected exactly 60 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> 'b80939110cdcd881eb07c46b5d1c22d7' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261110140000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src137a8ad6$-- C-TENANT-01: a signed-in client may write only the tenant columns the app writes.
-- App writes: INSERT(name, owner_user_id) at onboarding; UPDATE(name | business_type | timezone).
-- Before: authenticated held INSERT and UPDATE on (id, name, owner_user_id, created_at,
-- updated_at, timezone, business_type) from 20261021080927_tenant_entitlement_01.
-- After:  INSERT(name, owner_user_id, timezone, business_type); UPDATE(name, timezone, business_type).
-- id, created_at and updated_at keep their defaults and the touch trigger; ownership is
-- set only at insert (RLS CHECK owner_user_id = auth.uid()). service_role is unchanged.
BEGIN;
REVOKE INSERT (id, created_at, updated_at) ON public.tenants FROM authenticated;
REVOKE UPDATE (id, owner_user_id, created_at, updated_at) ON public.tenants FROM authenticated;
COMMIT;
$src137a8ad6$;
  IF md5(src) <> 'ccfed6b0972c49823b4924c602cc615d' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110140000_tenants_narrow_client_grants_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110140000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110140000'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110140000', 'tenants_narrow_client_grants_01', ARRAY[src], 'claude-c6');
END
$stage$;
-- stage B.10
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '1b94210e7c6bf663cba496d2421612ad' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261110150000: expected exactly 61 known versions'; END IF;
  IF (SELECT md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\n')), '-'), ',' ORDER BY version)) FROM supabase_migrations.schema_migrations) <> '3bc3238516417d971fc5127f2bcfa513' THEN RAISE EXCEPTION 'LEDGER_CONTENT_MISMATCH before 20261110150000: ledger statements differ from the recorded production ledger'; END IF;
  src := $src1b9ab46e$-- C-DEFPRIV-01: functions that postgres creates from now on are not executable by PUBLIC
-- (and therefore not by anon) unless a migration grants it explicitly.
-- Before: no global default ACL for postgres, so acldefault('f') = {=X/postgres,...}:
-- every new function, in any schema, was callable by anon until its migration
-- remembered REVOKE ... FROM PUBLIC.
-- Unchanged: existing functions keep their ACLs; the per-schema default for postgres in
-- public still grants EXECUTE on new public functions to authenticated and service_role.
-- Consequence: a new function outside public (e.g. a monjez_private helper used by an RLS
-- policy) needs an explicit GRANT EXECUTE to the roles that call it.
-- Not attempted: supabase_admin's defaults (postgres is not a member of supabase_admin).
-- Rollback: ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT EXECUTE ON FUNCTIONS TO PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
$src1b9ab46e$;
  IF md5(src) <> '731a07309336c928bc77c32cb4e3ca6b' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261110150000_defpriv_function_execute_01'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261110150000') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261110150000'; END IF;
  body := src;
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261110150000', 'defpriv_function_execute_01', ARRAY[src], 'claude-c6');
END
$stage$;
-- legacy-frontend unblock, inside the same transaction (no gap). Revert only after the new frontend is live.
grant execute on function public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) to authenticated;
grant execute on function public.collect_order_debt(uuid, numeric, public.payment_method) to authenticated;
COMMIT;
