-- stage C7
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
