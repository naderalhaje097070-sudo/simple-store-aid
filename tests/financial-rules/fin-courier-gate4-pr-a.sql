-- FIN-COURIER-001 Gate 4 / PR-A safety net
-- Test-only. Runs in an isolated Supabase transaction and rolls back.
-- This file is expected to be RED on the pre-implementation Gate-4 baseline.
-- It becomes GREEN only when PR-A satisfies the approved contract.

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

-- ---------------------------------------------------------------------
-- A. Contract presence / schema boundary
-- ---------------------------------------------------------------------
DO $catalog$
DECLARE
  v_sale regprocedure;
  v_transition regprocedure;
  v_new_count int;
  v_new_validated bool;
  v_old_count int;
  v_keep_count int;
BEGIN
  v_sale := to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  );
  IF v_sale IS NULL THEN
    PERFORM pg_temp.g4_fail('A-RPC-1', 'create_sale_with_items_v2 exact seven-argument signature is missing');
  END IF;

  v_transition := to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  );
  IF v_transition IS NULL THEN
    PERFORM pg_temp.g4_fail('A-RPC-2', 'update_courier_outcome_v2 exact four-argument signature is missing');
  END IF;

  SELECT COUNT(*), bool_or(convalidated)
    INTO v_new_count, v_new_validated
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname = 'orders_customer_required_when_debt';

  IF v_new_count <> 1 THEN
    PERFORM pg_temp.g4_fail('C-CK1', 'orders_customer_required_when_debt must exist exactly once');
  ELSIF v_new_validated IS DISTINCT FROM false THEN
    PERFORM pg_temp.g4_fail('C-CK1V', 'orders_customer_required_when_debt must be NOT VALID immediately after PR-A');
  END IF;

  SELECT COUNT(*)
    INTO v_old_count
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname IN (
       'orders_customer_required_when_unpaid',
       'orders_courier_requires_customer_id'
     );
  IF v_old_count <> 0 THEN
    PERFORM pg_temp.g4_fail('C-CK1O', 'legacy blanket-customer constraints must be removed');
  END IF;

  SELECT COUNT(*)
    INTO v_keep_count
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname IN (
       'orders_courier_requires_courier_id',
       'orders_collected_not_over_total'
     );
  IF v_keep_count <> 2 THEN
    PERFORM pg_temp.g4_fail('C-CK1K', 'courier-id and collected<=total constraints must remain');
  END IF;
END
$catalog$;

-- ---------------------------------------------------------------------
-- Fixtures
-- ---------------------------------------------------------------------
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

-- ---------------------------------------------------------------------
-- B/C. Creation-time behaviour. These assertions execute only once _v2 exists.
-- ---------------------------------------------------------------------
DO $create_contract$
DECLARE
  v_has_v2 bool :=
    to_regprocedure(
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
  IF NOT v_has_v2 THEN
    RETURN;
  END IF;

  -- B1: pending courier, no customer -> succeeds; no debt/custody/payment.
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
      INTO v_state, v_custody, v_paid
      FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payments FROM payments WHERE order_id = v_oid;
    IF v_state <> 'pending' OR v_custody <> 0 OR v_paid <> 0 OR v_payments <> 0 THEN
      PERFORM pg_temp.g4_fail('B1', format('state=%s custody=%s paid=%s payments=%s', v_state, v_custody, v_paid, v_payments));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B1', SQLERRM);
  END;

  -- B2: delivered_full courier, no customer -> custody=total, no payment before settlement.
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
      INTO v_state, v_custody, v_paid
      FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payments FROM payments WHERE order_id = v_oid;
    IF v_state <> 'delivered_full' OR v_custody <> 200 OR v_paid <> 0 OR v_payments <> 0 THEN
      PERFORM pg_temp.g4_fail('B2', format('state=%s custody=%s paid=%s payments=%s', v_state, v_custody, v_paid, v_payments));
    END IF;

    -- B9: customer-less delivered_full must settle successfully.
    BEGIN
      PERFORM public.settle_courier_orders(
        'ffff6666-0000-0000-0000-000000000001'::uuid,
        ARRAY[v_oid]::uuid[]
      );
      SELECT COUNT(*) INTO v_payments
        FROM payments
       WHERE order_id = v_oid
         AND kind = 'courier_settlement';
      IF v_payments <> 1 THEN
        PERFORM pg_temp.g4_fail('B9', format('settlement payment count=%s', v_payments));
      END IF;
    EXCEPTION WHEN OTHERS THEN
      PERFORM pg_temp.g4_fail('B9', SQLERRM);
    END;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B2', SQLERRM);
  END;

  -- B3: delivered_partial without customer -> explicit customer_required_for_debt.
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
    PERFORM pg_temp.g4_fail('B3', 'delivered_partial without customer was not rejected with customer_required_for_debt');
  END IF;

  -- B4: delivered_none without customer -> explicit customer_required_for_debt.
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
    PERFORM pg_temp.g4_fail('B4', 'delivered_none without customer was not rejected with customer_required_for_debt');
  END IF;

  -- B5: delivered_none with customer -> succeeds with zero custody.
  BEGIN
    v_res := public.create_sale_with_items_v2(
      'eeee5555-0000-0000-0000-000000000001'::uuid,
      'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      0, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000003","qty":1}]'::jsonb,
      'delivered_none'::courier_state
    );
    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, collected_by_courier
      INTO v_state, v_custody
      FROM orders WHERE id = v_oid;
    IF v_state <> 'delivered_none' OR v_custody <> 0 THEN
      PERFORM pg_temp.g4_fail('B5', format('state=%s custody=%s', v_state, v_custody));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B5', SQLERRM);
  END;

  -- B6: delivered_partial with customer -> custody equals collected amount.
  BEGIN
    v_res := public.create_sale_with_items_v2(
      'eeee5555-0000-0000-0000-000000000001'::uuid,
      'courier'::delivery_kind,
      'ffff6666-0000-0000-0000-000000000001'::uuid,
      25, 'cash'::payment_method,
      '[{"productId":"dddd4444-0000-0000-0000-000000000003","qty":1}]'::jsonb,
      'delivered_partial'::courier_state
    );
    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, collected_by_courier
      INTO v_state, v_custody
      FROM orders WHERE id = v_oid;
    IF v_state <> 'delivered_partial' OR v_custody <> 25 THEN
      PERFORM pg_temp.g4_fail('B6', format('state=%s custody=%s', v_state, v_custody));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('B6', SQLERRM);
  END;

  -- B7: courier sale without courier id -> explicit courier_requires_courier.
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
    PERFORM pg_temp.g4_fail('B7', 'courier order without courier id was not rejected with courier_requires_courier');
  END IF;
END
$create_contract$;

-- ---------------------------------------------------------------------
-- D/F. Atomic transition, monotonic custody, safe legacy adapter.
-- ---------------------------------------------------------------------
DO $transition_contract$
DECLARE
  v_has_sale bool :=
    to_regprocedure(
      'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
    ) IS NOT NULL;
  v_has_transition bool :=
    to_regprocedure(
      'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
    ) IS NOT NULL;
  v_res jsonb;
  v_oid uuid;
  v_ok bool;
  v_state text;
  v_custody numeric;
  v_customer uuid;
BEGIN
  IF NOT (v_has_sale AND v_has_transition) THEN
    RETURN;
  END IF;

  -- D-T1: pending/no-customer -> delivered_full succeeds.
  v_res := public.create_sale_with_items_v2(
    NULL, 'courier'::delivery_kind,
    'ffff6666-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    'pending'::courier_state
  );
  v_oid := (v_res->>'order_id')::uuid;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_full'::courier_state, 100, NULL
    );
    SELECT courier_state::text, collected_by_courier
      INTO v_state, v_custody
      FROM orders WHERE id = v_oid;
    IF v_state <> 'delivered_full' OR v_custody <> 100 THEN
      PERFORM pg_temp.g4_fail('D-T1', format('state=%s custody=%s', v_state, v_custody));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('D-T1', SQLERRM);
  END;

  -- D-M5: delivered_full -> delivered_partial is invalid/backward.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial'::courier_state, 80, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%invalid_transition%' OR SQLERRM LIKE '%custody_cannot_decrease%' THEN
      v_ok := true;
    END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('D-M5', 'delivered_full backward transition was accepted');
  END IF;

  -- D-T2 / D-T4: pending/no-customer -> partial requires same-tenant customer atomically.
  v_res := public.create_sale_with_items_v2(
    NULL, 'courier'::delivery_kind,
    'ffff6666-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"dddd4444-0000-0000-0000-000000000002","qty":1}]'::jsonb,
    'pending'::courier_state
  );
  v_oid := (v_res->>'order_id')::uuid;

  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial'::courier_state, 80, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('D-T2', 'partial transition without customer was not rejected');
  END IF;

  SELECT courier_state::text, collected_by_courier, customer_id
    INTO v_state, v_custody, v_customer
    FROM orders WHERE id = v_oid;
  IF v_state <> 'pending' OR v_custody <> 0 OR v_customer IS NOT NULL THEN
    PERFORM pg_temp.g4_fail('D-T2A', 'failed transition was not atomic / row changed');
  END IF;

  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial'::courier_state, 80,
      'eeee5555-0000-0000-0000-000000000001'::uuid
    );
    SELECT courier_state::text, collected_by_courier, customer_id
      INTO v_state, v_custody, v_customer
      FROM orders WHERE id = v_oid;
    IF v_state <> 'delivered_partial'
       OR v_custody <> 80
       OR v_customer <> 'eeee5555-0000-0000-0000-000000000001'::uuid THEN
      PERFORM pg_temp.g4_fail('D-T4', format('state=%s custody=%s customer=%s', v_state, v_custody, v_customer));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('D-T4', SQLERRM);
  END;

  -- D-M12: same-state same-value retry is idempotent.
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial'::courier_state, 80,
      'eeee5555-0000-0000-0000-000000000001'::uuid
    );
    SELECT collected_by_courier INTO v_custody FROM orders WHERE id = v_oid;
    IF v_custody <> 80 THEN
      PERFORM pg_temp.g4_fail('D-M12', format('custody=%s after same-value retry', v_custody));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.g4_fail('D-M12', SQLERRM);
  END;

  -- D-M11: same-state lower custody is rejected.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid, 'delivered_partial'::courier_state, 50,
      'eeee5555-0000-0000-0000-000000000001'::uuid
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%custody_cannot_decrease%' OR SQLERRM LIKE '%invalid_transition%' THEN
      v_ok := true;
    END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('D-M11', 'custody reduction was accepted');
  END IF;

  -- F1b: legacy adapter must delegate to v2 safety and reject unsafe decrease.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_order_state(
      v_oid, 'delivered_partial'::courier_state, 40
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%custody_cannot_decrease%' OR SQLERRM LIKE '%invalid_transition%' THEN
      v_ok := true;
    END IF;
  END;
  IF NOT v_ok THEN
    PERFORM pg_temp.g4_fail('F1b', 'legacy transition adapter still accepts unsafe custody reduction');
  END IF;
END
$transition_contract$;

-- ---------------------------------------------------------------------
-- C-PF. Historical validation preflight.
-- ---------------------------------------------------------------------
DO $preflight$
DECLARE
  v_count int;
BEGIN
  SELECT COUNT(*)
    INTO v_count
    FROM public.orders
   WHERE customer_id IS NULL
     AND NOT (
          (courier_state IS NOT NULL AND courier_state = 'returned')
       OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
       OR (delivery = 'courier' AND courier_state IS NOT NULL
             AND courier_state IN ('pending','delivered_full'))
     );

  RAISE NOTICE 'C-PF1 preflight current violations=%', v_count;
END
$preflight$;

-- ---------------------------------------------------------------------
-- Final result
-- ---------------------------------------------------------------------
DO $done$
DECLARE
  v_count int;
  v_detail text;
BEGIN
  SELECT COUNT(*) INTO v_count FROM gate4_failures;
  IF v_count > 0 THEN
    SELECT string_agg(test_id || '=' || detail, ' | ' ORDER BY test_id)
      INTO v_detail
      FROM gate4_failures;
    RAISE EXCEPTION 'GATE4_EXPECTED_RED: % contract gap(s): %', v_count, v_detail;
  END IF;

  RAISE NOTICE 'GATE4_GREEN: FIN-COURIER PR-A contract safety net passed';
END
$done$;

ROLLBACK;
