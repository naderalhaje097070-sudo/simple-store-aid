-- FIN-IDEM-001 candidate implementation for canonical sale creation.
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
