-- FIN-COURIER-001 — Gate 4 contract probes (Batch 1)
--
-- Purpose:
--   Define executable safety-net expectations before production implementation.
--   This file is intentionally separate from rules.sql / T1–T15 during review.
--   It runs inside one transaction and rolls back all fixtures and writes.
--
-- Expected pre-implementation result:
--   FAIL, with collected findings showing that the v2 contract is not present yet.
--   A failing result is evidence that the tests detect the missing target behavior;
--   it is not authorization to weaken or bypass any existing regression test.
--
-- Usage:
--   psql -v ON_ERROR_STOP=1 \
--     -v tid="'<tenant_uuid>'" \
--     -v uid="'<owner_user_uuid>'" \
--     -f tests/financial-rules/fin-courier-gate4-contract.sql

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

DO $seed$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active)
  VALUES
    ('d4a41000-0000-0000-0000-000000000001', v_tid, 'G4-P100', 100, 60, 20, true),
    ('d4a41000-0000-0000-0000-000000000002', v_tid, 'G4-P200', 200, 120, 20, true),
    ('d4a41000-0000-0000-0000-000000000003', v_tid, 'G4-P300', 300, 180, 20, true);

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('d4a42000-0000-0000-0000-000000000001', v_tid, 'G4-CUSTOMER');

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('d4a43000-0000-0000-0000-000000000001', v_tid, 'G4-COURIER', true);
END
$seed$;

-- ---------------------------------------------------------------------
-- API-1. Canonical RPCs required by the approved Gate-3 contract exist.
-- ---------------------------------------------------------------------
DO $api$
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES (
      'API-1A',
      'missing create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
    );
  END IF;

  IF to_regprocedure(
    'public.update_courier_outcome_v2(uuid,courier_state,numeric,uuid)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES (
      'API-1B',
      'missing update_courier_outcome_v2(uuid,courier_state,numeric,uuid)'
    );
  END IF;
END
$api$;

-- ---------------------------------------------------------------------
-- B1. Courier pending without customer succeeds; no debt/custody/payment.
-- ---------------------------------------------------------------------
DO $b1$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_state text;
  v_paid numeric;
  v_custody numeric;
  v_payment_count integer;
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES ('B1', 'v2 sale RPC unavailable; pending/no-customer target cannot be exercised');
    RETURN;
  END IF;

  BEGIN
    EXECUTE $sql$
      SELECT public.create_sale_with_items_v2(
        NULL,
        'courier'::delivery_kind,
        'd4a43000-0000-0000-0000-000000000001'::uuid,
        0,
        'cash'::payment_method,
        '[{"productId":"d4a41000-0000-0000-0000-000000000001","qty":1}]'::jsonb,
        'pending'::courier_state
      )
    $sql$ INTO v_res;

    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, paid, collected_by_courier
      INTO v_state, v_paid, v_custody
      FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payment_count FROM payments WHERE order_id = v_oid;

    IF v_state <> 'pending' OR v_paid <> 0 OR v_custody <> 0 OR v_payment_count <> 0 THEN
      INSERT INTO gate4_failures VALUES (
        'B1',
        format('unexpected result state=%s paid=%s custody=%s payments=%s', v_state, v_paid, v_custody, v_payment_count)
      );
    END IF;
  EXCEPTION WHEN OTHERS THEN
    INSERT INTO gate4_failures VALUES ('B1', SQLERRM);
  END;
END
$b1$;

-- ---------------------------------------------------------------------
-- B2. Courier delivered_full without customer succeeds; custody=total.
-- ---------------------------------------------------------------------
DO $b2$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_state text;
  v_total numeric;
  v_paid numeric;
  v_custody numeric;
  v_payment_count integer;
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES ('B2', 'v2 sale RPC unavailable; delivered_full/no-customer target cannot be exercised');
    RETURN;
  END IF;

  BEGIN
    EXECUTE $sql$
      SELECT public.create_sale_with_items_v2(
        NULL,
        'courier'::delivery_kind,
        'd4a43000-0000-0000-0000-000000000001'::uuid,
        200,
        'cash'::payment_method,
        '[{"productId":"d4a41000-0000-0000-0000-000000000002","qty":1}]'::jsonb,
        'delivered_full'::courier_state
      )
    $sql$ INTO v_res;

    v_oid := (v_res->>'order_id')::uuid;
    SELECT courier_state::text, total, paid, collected_by_courier
      INTO v_state, v_total, v_paid, v_custody
      FROM orders WHERE id = v_oid;
    SELECT COUNT(*) INTO v_payment_count FROM payments WHERE order_id = v_oid;

    IF v_state <> 'delivered_full' OR v_paid <> 0 OR v_custody <> v_total OR v_payment_count <> 0 THEN
      INSERT INTO gate4_failures VALUES (
        'B2',
        format('unexpected result state=%s total=%s paid=%s custody=%s payments=%s', v_state, v_total, v_paid, v_custody, v_payment_count)
      );
    END IF;
  EXCEPTION WHEN OTHERS THEN
    INSERT INTO gate4_failures VALUES ('B2', SQLERRM);
  END;
END
$b2$;

-- ---------------------------------------------------------------------
-- B3. Courier delivered_partial without customer is rejected for debt.
-- ---------------------------------------------------------------------
DO $b3$
DECLARE
  v_rejected boolean := false;
  v_error text;
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES ('B3', 'v2 sale RPC unavailable; rejection contract cannot be exercised');
    RETURN;
  END IF;

  BEGIN
    EXECUTE $sql$
      SELECT public.create_sale_with_items_v2(
        NULL,
        'courier'::delivery_kind,
        'd4a43000-0000-0000-0000-000000000001'::uuid,
        100,
        'cash'::payment_method,
        '[{"productId":"d4a41000-0000-0000-0000-000000000002","qty":1}]'::jsonb,
        'delivered_partial'::courier_state
      )
    $sql$;
  EXCEPTION WHEN OTHERS THEN
    v_error := SQLERRM;
    v_rejected := v_error LIKE '%customer_required_for_debt%';
  END;

  IF NOT v_rejected THEN
    INSERT INTO gate4_failures VALUES (
      'B3',
      COALESCE('expected customer_required_for_debt, received: ' || v_error, 'delivered_partial without customer was accepted')
    );
  END IF;
END
$b3$;

-- ---------------------------------------------------------------------
-- B4. Courier delivered_none without customer is rejected for debt.
-- ---------------------------------------------------------------------
DO $b4$
DECLARE
  v_rejected boolean := false;
  v_error text;
BEGIN
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)'
  ) IS NULL THEN
    INSERT INTO gate4_failures VALUES ('B4', 'v2 sale RPC unavailable; rejection contract cannot be exercised');
    RETURN;
  END IF;

  BEGIN
    EXECUTE $sql$
      SELECT public.create_sale_with_items_v2(
        NULL,
        'courier'::delivery_kind,
        'd4a43000-0000-0000-0000-000000000001'::uuid,
        0,
        'cash'::payment_method,
        '[{"productId":"d4a41000-0000-0000-0000-000000000003","qty":1}]'::jsonb,
        'delivered_none'::courier_state
      )
    $sql$;
  EXCEPTION WHEN OTHERS THEN
    v_error := SQLERRM;
    v_rejected := v_error LIKE '%customer_required_for_debt%';
  END;

  IF NOT v_rejected THEN
    INSERT INTO gate4_failures VALUES (
      'B4',
      COALESCE('expected customer_required_for_debt, received: ' || v_error, 'delivered_none without customer was accepted')
    );
  END IF;
END
$b4$;

DO $summary$
DECLARE
  v_count integer;
  v_detail text;
BEGIN
  SELECT COUNT(*) INTO v_count FROM gate4_failures;

  IF v_count > 0 THEN
    SELECT string_agg(format('%s: %s', test_id, detail), E'\n' ORDER BY test_id)
      INTO v_detail
      FROM gate4_failures;
    RAISE EXCEPTION E'FIN-COURIER Gate 4 Batch 1 FAIL (% findings):\n%', v_count, v_detail;
  END IF;

  RAISE NOTICE 'FIN-COURIER Gate 4 Batch 1 PASS: API-1 and B1-B4';
END
$summary$;

ROLLBACK;
