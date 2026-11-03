-- C5-COLLECTION-RETRY-01. Forward-only, owner-authorized candidate.
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
