-- FIN-COURIER-001 Gate 4 / PR-A safety net
-- Test-only. Runs in an isolated Supabase transaction and rolls back.
-- RED is expected on the pre-implementation Gate-4 baseline.

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

CREATE TEMP TABLE gate4_failures (
  test_id text PRIMARY KEY,
  detail text NOT NULL
) ON COMMIT DROP;

CREATE OR REPLACE FUNCTION pg_temp.g4_fail(p_id text, p_detail text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO gate4_failures(test_id, detail)
  VALUES (p_id, p_detail)
  ON CONFLICT (test_id) DO UPDATE SET detail = EXCLUDED.detail;
END;
$$;

-- Contract/catalog checks: these must be red before PR-A.
DO $catalog$
DECLARE
  v_count int;
  v_validated bool;
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  ) IS NULL THEN
    PERFORM pg_temp.g4_fail('A-RPC-1', 'create_sale_with_items_v2 is missing');
  END IF;

  IF to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  ) IS NULL THEN
    PERFORM pg_temp.g4_fail('A-RPC-2', 'update_courier_outcome_v2 is missing');
  END IF;

  SELECT COUNT(*), bool_or(convalidated)
    INTO v_count, v_validated
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname = 'orders_customer_required_when_debt';
  IF v_count <> 1 THEN
    PERFORM pg_temp.g4_fail('C-CK1', 'orders_customer_required_when_debt missing');
  ELSIF v_validated IS DISTINCT FROM false THEN
    PERFORM pg_temp.g4_fail('C-CK1V', 'replacement CHECK must initially be NOT VALID');
  END IF;

  SELECT COUNT(*) INTO v_count
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname IN (
       'orders_customer_required_when_unpaid',
       'orders_courier_requires_customer_id'
     );
  IF v_count <> 0 THEN
    PERFORM pg_temp.g4_fail('C-CK1O', 'legacy blanket customer constraints still present');
  END IF;

  SELECT COUNT(*) INTO v_count
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname IN (
       'orders_courier_requires_courier_id',
       'orders_collected_not_over_total'
     );
  IF v_count <> 2 THEN
    PERFORM pg_temp.g4_fail('C-CK1K', 'required retained courier constraints are missing');
  END IF;
END
$catalog$;

-- Isolated fixtures used automatically once _v2 exists.
DO $seed$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active) VALUES
    ('dddd4444-0000-0000-0000-000000000001', v_tid, 'G4-P1', 100, 60, 50, true),
    ('dddd4444-0000-0000-0000-000000000002', v_tid, 'G4-P2', 200, 120, 50, true),
    ('dddd4444-0000-0000-0000-000000000003', v_tid, 'G4-P3', 50, 30, 50, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eeee5555-0000-0000-0000-000000000001', v_tid, 'G4-CUSTOMER')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffff6666-0000-0000-0000-000000000001', v_tid, 'G4-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

-- Creation-time target behavior. Skipped only while _v2 does not exist.
DO $create_contract$
DECLARE
  v_has_v2 bool := to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  ) IS NOT NULL;
  v_res jsonb;
  v_oid uuid;
  v_state text;
  v_custody numeric;
  v_paid numeric;
  v_payments int;
  v_ok bool;
BEGIN
  IF NOT v_has_v2 THEN RETURN; END IF;

  -- B1: pending/no-customer succeeds and creates neither custody nor payment.
  BEGIN
    v_res := public.create_sale_with_items_v2(
      NULL, 'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      0, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb,
      'pending'::courier_state
    );
    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, collected_by_courier, paid
      INTO v_state, v_custody, v_paid FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payments FROM payments WHERE order_id = v_oid;
    IF v_state <> 'pending' OR v_custody <> 0 OR v_paid <> 0 OR v_payments <> 0 THEN
      PERFORM pg_temp.g4_fail('B1', format('state=%s custody=%s paid=%s payments=%s', v_state, v_custody, v_paid, v_payments));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B1', SQLERRM);
  END;

  -- B2/B9: delivered_full/no-customer -> custody, then settlement succeeds.
  BEGIN
    v_res := public.create_sale_with_items_v2(
      NULL, 'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      200, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000002","qty":1}]'::jsonb,
      'delivered_full'::courier_state
    );
    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, collected_by_courier, paid
      INTO v_state, v_custody, v_paid FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payments FROM payments WHERE order_id = v_oid;
    IF v_state <> 'delivered_full' OR v_custody <> 200 OR v_paid <> 0 OR v_payments <> 0 THEN
      PERFORM pg_temp.g4_fail('B2', format('state=%s custody=%s paid=%s payments=%s', v_state, v_custody, v_paid, v_payments));
    ELSE
      BEGIN
        PERFORM public.settle_courier_orders(
          'ffff6666-0000-0000-0000-000000000001'::uuid,
          ARRAY[v_oid]::uuid[]
        );
      EXCEPTION WHEN OTHERS THEN
        PERFORM pg_temp.g4_fail('B9', SQLERRM);
      END;
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B2', SQLERRM);
  END;

  -- B3: partial without customer must be rejected explicitly.
  v_ok := false;
  BEGIN
    PERFORM public.create_sale_with_items_v2(
      NULL, 'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      20, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000003","qty":1}]'::jsonb,
      'delivered_partial'::courier_state
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('B3', 'partial courier debt without customer was not rejected');
  END IF;

  -- B4: delivered_none without customer must be rejected explicitly.
  v_ok := false;
  BEGIN
    PERFORM public.create_sale_with_items_v2(
      NULL, 'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      0, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000003","qty":1}]'::jsonb,
      'delivered_none'::courier_state
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('B4', 'delivered_none without customer was not rejected');
  END IF;

  -- B7: courier id is still mandatory.
  v_ok := false;
  BEGIN
    PERFORM public.create_sale_with_items_v2(
      NULL, 'courier'::delivery_kind, NULL,
      0, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb,
      'pending'::courier_state
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%courier_requires_courier%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('B7', 'courier sale without courier id was accepted');
  END IF;
END
$create_contract$;

-- Transition target. Skipped until both v2 RPCs exist.
DO $transition_contract$
DECLARE
  v_has_sale bool := to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  ) IS NOT NULL;
  v_has_transition bool := to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  ) IS NOT NULL;
  v_res jsonb;
  v_oid uuid;
  v_ok bool;
  v_state text;
  v_custody numeric;
BEGIN
  IF NOT (v_has_sale AND v_has_transition) THEN RETURN; END IF;

  v_res := public.create_sale_with_items_v2(
    NULL, 'courier'::delivery_kind,
    'ffff6666-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    'pending'::courier_state
  );
  v_oid := (v_res->>'order_id')::uuid;

  -- D-T1: pending/no-customer -> delivered_full.
  BEGIN
    PERFORM public.update_courier_outcome_v2(v_oid, 'delivered_full'::courier_state, 100, NULL);
    SELECT courier_state::text, collected_by_courier
      INTO v_state, v_custody FROM orders WHERE id = v_oid;
    IF v_state <> 'delivered_full' OR v_custody <> 100 THEN
      PERFORM pg_temp.g4_fail('D-T1', format('state=%s custody=%s', v_state, v_custody));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('D-T1', SQLERRM);
  END;

  -- D-M11: custody may not decrease / move backward.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(v_oid, 'delivered_partial'::courier_state, 50, NULL);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%custody_cannot_decrease%' OR SQLERRM LIKE '%invalid_transition%' THEN
      v_ok := true;
    END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('D-M11', 'backward/custody-reducing transition was accepted');
  END IF;
END
$transition_contract$;

-- Approved historical-data preflight query: recorded and executable before VALIDATE.
DO $preflight$
DECLARE
  v_count int;
BEGIN
  SELECT COUNT(*) INTO v_count
    FROM public.orders
   WHERE customer_id IS NULL
     AND NOT (
          (courier_state IS NOT NULL AND courier_state = 'returned')
       OR (delivery = 'direct' AND courier_state IS NULL AND paid >= total)
       OR (delivery = 'courier' AND courier_state IS NOT NULL
             AND courier_state IN ('pending','delivered_full'))
     );
  RAISE NOTICE 'C-PF1 current preflight violations=%', v_count;
END
$preflight$;

DO $done$
DECLARE
  v_count int;
  v_detail text;
BEGIN
  SELECT COUNT(*) INTO v_count FROM gate4_failures;
  IF v_count > 0 THEN
    SELECT string_agg(test_id || '=' || detail, ' | ' ORDER BY test_id)
      INTO v_detail FROM gate4_failures;
    RAISE EXCEPTION 'GATE4_EXPECTED_RED: % contract gap(s): %', v_count, v_detail;
  END IF;
  RAISE NOTICE 'GATE4_GREEN: FIN-COURIER PR-A target contract passed';
END
$done$;

ROLLBACK;
