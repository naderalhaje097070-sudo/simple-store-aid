-- FIN-COURIER-001 Gate 4 — atomic transition/state-machine safety net
-- Covers D-T2..D-T7 and D-M1..D-M13 (D-T8 fault injection is reviewed separately).

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

DO $prereq$
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  ) IS NULL OR to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  ) IS NULL THEN
    RAISE EXCEPTION 'GATE4_TRANSITION_EXPECTED_RED: PR-A v2 RPCs are missing';
  END IF;
END
$prereq$;

DO $seed$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active)
  VALUES ('ddaa0001-7000-4000-8000-000000000001', v_tid, 'G4-TRANSITION-P1', 100, 60, 80, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eeaa0001-7000-4000-8000-000000000001', v_tid, 'G4-TRANSITION-C1')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffaa0001-7000-4000-8000-000000000001', v_tid, 'G4-TRANSITION-COURIER', true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO tenants(id, name, owner_user_id)
  VALUES ('22222222-2222-4222-8222-222222222222', 'G4-OTHER-TENANT', auth.uid())
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eeaa0002-7000-4000-8000-000000000002', '22222222-2222-4222-8222-222222222222', 'G4-CROSS-TENANT-C')
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

CREATE OR REPLACE FUNCTION pg_temp.g4_new(
  p_state courier_state,
  p_collected numeric,
  p_customer uuid DEFAULT NULL
) RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  v_res jsonb;
BEGIN
  v_res := public.create_sale_with_items_v2(
    p_customer,
    'courier'::delivery_kind,
    'ffaa0001-7000-4000-8000-000000000001'::uuid,
    p_collected,
    'cash'::payment_method,
    '[{"productId":"ddaa0001-7000-4000-8000-000000000001","qty":1}]'::jsonb,
    p_state
  );
  RETURN (v_res->>'order_id')::uuid;
END
$$;

-- D-T2 / D-T3: debt transitions without customer reject and leave row unchanged.
DO $debt_without_customer$
DECLARE
  v_oid uuid;
  v_ok bool;
  v_state text;
  v_cust numeric;
  v_customer uuid;
BEGIN
  v_oid := pg_temp.g4_new('pending', 0, NULL);
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(v_oid, 'delivered_partial', 40, NULL);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-T2 FAIL: partial without customer accepted'; END IF;
  SELECT courier_state::text, collected_by_courier, customer_id INTO v_state, v_cust, v_customer FROM orders WHERE id=v_oid;
  IF v_state <> 'pending' OR v_cust <> 0 OR v_customer IS NOT NULL THEN
    RAISE EXCEPTION 'D-T2 FAIL: rejection was not atomic state=% custody=% customer=%', v_state, v_cust, v_customer;
  END IF;

  v_oid := pg_temp.g4_new('pending', 0, NULL);
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(v_oid, 'delivered_none', 0, NULL);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-T3 FAIL: delivered_none without customer accepted'; END IF;
  SELECT courier_state::text, collected_by_courier, customer_id INTO v_state, v_cust, v_customer FROM orders WHERE id=v_oid;
  IF v_state <> 'pending' OR v_cust <> 0 OR v_customer IS NOT NULL THEN
    RAISE EXCEPTION 'D-T3 FAIL: rejection was not atomic';
  END IF;
END
$debt_without_customer$;

-- D-T4/D-T5/D-T6: atomic customer attachment and tenant validation.
DO $customer_attachment$
DECLARE
  v_oid uuid;
  v_ok bool;
  v_state text;
  v_cust numeric;
  v_customer uuid;
BEGIN
  v_oid := pg_temp.g4_new('pending', 0, NULL);
  PERFORM public.update_courier_outcome_v2(
    v_oid, 'delivered_partial', 40,
    'eeaa0001-7000-4000-8000-000000000001'::uuid
  );
  SELECT courier_state::text, collected_by_courier, customer_id
    INTO v_state, v_cust, v_customer FROM orders WHERE id=v_oid;
  IF v_state <> 'delivered_partial' OR v_cust <> 40 OR v_customer <> 'eeaa0001-7000-4000-8000-000000000001'::uuid THEN
    RAISE EXCEPTION 'D-T4 FAIL: state=% custody=% customer=%', v_state, v_cust, v_customer;
  END IF;

  v_oid := pg_temp.g4_new('pending', 0, NULL);
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial', 40,
      'eeaa0002-7000-4000-8000-000000000002'::uuid
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_not_found%' OR SQLERRM LIKE '%forbidden_tenant%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-T5 FAIL: cross-tenant customer accepted'; END IF;
  SELECT courier_state::text, collected_by_courier, customer_id INTO v_state, v_cust, v_customer FROM orders WHERE id=v_oid;
  IF v_state <> 'pending' OR v_cust <> 0 OR v_customer IS NOT NULL THEN RAISE EXCEPTION 'D-T5 FAIL: cross-tenant rejection not atomic'; END IF;

  v_oid := pg_temp.g4_new('pending', 0, NULL);
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial', 40,
      'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee'::uuid
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_not_found%' OR SQLERRM LIKE '%forbidden_tenant%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-T6 FAIL: nonexistent customer accepted'; END IF;
END
$customer_attachment$;

-- D-M1: every legal transition from pending.
DO $pending_matrix$
DECLARE
  v_oid uuid;
BEGIN
  v_oid := pg_temp.g4_new('pending',0,'eeaa0001-7000-4000-8000-000000000001');
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_none',0,NULL);

  v_oid := pg_temp.g4_new('pending',0,'eeaa0001-7000-4000-8000-000000000001');
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',40,NULL);

  v_oid := pg_temp.g4_new('pending',0,NULL);
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);

  v_oid := pg_temp.g4_new('pending',0,NULL);
  PERFORM public.update_courier_outcome_v2(v_oid,'returned',0,NULL);
END
$pending_matrix$;

-- D-M2: delivered_none -> partial/full/returned are legal.
DO $none_matrix$
DECLARE v_oid uuid;
BEGIN
  v_oid := pg_temp.g4_new('delivered_none',0,'eeaa0001-7000-4000-8000-000000000001');
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',40,NULL);

  v_oid := pg_temp.g4_new('delivered_none',0,'eeaa0001-7000-4000-8000-000000000001');
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);

  v_oid := pg_temp.g4_new('delivered_none',0,'eeaa0001-7000-4000-8000-000000000001');
  PERFORM public.update_courier_outcome_v2(v_oid,'returned',0,NULL);
END
$none_matrix$;

-- D-M3 + D-M12 + D-M13 + D-M11 on partial state.
DO $partial_matrix$
DECLARE
  v_oid uuid;
  v_ok bool;
  v_cust numeric;
BEGIN
  v_oid := pg_temp.g4_new('delivered_partial',40,'eeaa0001-7000-4000-8000-000000000001');

  -- D-M12 same state/same value is idempotent.
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',40,NULL);
  SELECT collected_by_courier INTO v_cust FROM orders WHERE id=v_oid;
  IF v_cust <> 40 THEN RAISE EXCEPTION 'D-M12 FAIL: custody=%', v_cust; END IF;

  -- D-M13 higher same-state custody accepted.
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',60,NULL);
  SELECT collected_by_courier INTO v_cust FROM orders WHERE id=v_oid;
  IF v_cust <> 60 THEN RAISE EXCEPTION 'D-M13 FAIL: higher custody not stored'; END IF;

  -- D-M11 lower custody rejected.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',50,NULL);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%custody_cannot_decrease%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M11 FAIL: lower custody accepted'; END IF;

  -- D-M3 partial -> full legal.
  PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);
END
$partial_matrix$;

-- D-M4..D-M10: forbidden backward/terminal transitions.
DO $invalid_matrix$
DECLARE
  v_oid uuid;
  v_ok bool;
BEGIN
  -- D-M4 any -> pending.
  v_oid := pg_temp.g4_new('delivered_none',0,'eeaa0001-7000-4000-8000-000000000001');
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'pending',0,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M4 FAIL: backward to pending accepted'; END IF;

  -- D-M5 full -> partial and none forbidden.
  v_oid := pg_temp.g4_new('delivered_full',100,NULL);
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_partial',80,'eeaa0001-7000-4000-8000-000000000001');
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%invalid_transition%' OR SQLERRM LIKE '%custody_cannot_decrease%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M5 FAIL: full->partial accepted'; END IF;
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_none',0,'eeaa0001-7000-4000-8000-000000000001');
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%invalid_transition%' OR SQLERRM LIKE '%custody_cannot_decrease%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M5 FAIL: full->none accepted'; END IF;

  -- D-M6 partial -> none forbidden.
  v_oid := pg_temp.g4_new('delivered_partial',40,'eeaa0001-7000-4000-8000-000000000001');
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_none',0,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%invalid_transition%' OR SQLERRM LIKE '%custody_cannot_decrease%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M6 FAIL: partial->none accepted'; END IF;

  -- D-M7 partial -> returned forbidden while custody > 0.
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'returned',0,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%cannot_return_partially_paid_order%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M7 FAIL: partial->returned accepted'; END IF;

  -- D-M8 returned is terminal.
  v_oid := pg_temp.g4_new('pending',0,NULL);
  PERFORM public.update_courier_outcome_v2(v_oid,'returned',0,NULL);
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%not_a_courier_order%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M8 FAIL: returned transition accepted'; END IF;

  -- D-M9 settled order has no courier transition surface.
  v_oid := pg_temp.g4_new('delivered_full',100,NULL);
  PERFORM public.settle_courier_orders('ffaa0001-7000-4000-8000-000000000001',ARRAY[v_oid]);
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%not_a_courier_order%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M9 FAIL: settled order accepted outcome transition'; END IF;

  -- D-M10 delivered_full is settlement-only, even same-state outcome retry.
  v_oid := pg_temp.g4_new('delivered_full',100,NULL);
  v_ok := false;
  BEGIN PERFORM public.update_courier_outcome_v2(v_oid,'delivered_full',100,NULL);
  EXCEPTION WHEN OTHERS THEN IF SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF; END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-M10 FAIL: delivered_full outcome retry accepted'; END IF;
END
$invalid_matrix$;

-- D-T7: returned path delegates to the approved return transaction and restores stock.
DO $returned_delegate$
DECLARE
  v_oid uuid;
  v_before numeric;
  v_after numeric;
  v_state text;
BEGIN
  SELECT stock INTO v_before FROM products WHERE id='ddaa0001-7000-4000-8000-000000000001';
  v_oid := pg_temp.g4_new('pending',0,NULL);
  PERFORM public.update_courier_outcome_v2(v_oid,'returned',0,NULL);
  SELECT stock INTO v_after FROM products WHERE id='ddaa0001-7000-4000-8000-000000000001';
  SELECT courier_state::text INTO v_state FROM orders WHERE id=v_oid;
  IF v_state <> 'returned' OR v_after <> v_before THEN
    RAISE EXCEPTION 'D-T7 FAIL: state=% stock_before=% stock_after=%', v_state, v_before, v_after;
  END IF;
END
$returned_delegate$;

DO $done$ BEGIN
  RAISE NOTICE 'GATE4_TRANSITION_GREEN: D-T2..D-T7 and D-M1..D-M13 passed';
END
$done$;

ROLLBACK;
