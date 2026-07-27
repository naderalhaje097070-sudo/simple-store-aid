-- FIN-COURIER-001 Gate 4 — effective CHECK constraint shapes (C-CK1..C-CK8)
-- Direct table writes intentionally bypass sale RPC validation so the database
-- constraint itself is proven. Entire file runs in a transaction and rolls back.

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config('mongezz.test_tid', :tid, true);

CREATE TEMP TABLE gate4_ck_failures (
  test_id text PRIMARY KEY,
  detail text NOT NULL
) ON COMMIT DROP;

CREATE OR REPLACE FUNCTION pg_temp.ck_fail(p_id text, p_detail text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO gate4_ck_failures(test_id, detail)
  VALUES (p_id, p_detail)
  ON CONFLICT (test_id) DO UPDATE SET detail = EXCLUDED.detail;
END;
$$;

DO $fixture$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffff6666-2000-0000-0000-000000000001', v_tid, 'G4-CK-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$fixture$;

DO $checks$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
  v_has_new bool;
  v_old int;
  v_ok bool;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conrelid = 'public.orders'::regclass
       AND conname = 'orders_customer_required_when_debt'
  ) INTO v_has_new;

  SELECT COUNT(*) INTO v_old
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname IN ('orders_customer_required_when_unpaid', 'orders_courier_requires_customer_id');

  IF NOT v_has_new OR v_old <> 0 THEN
    PERFORM pg_temp.ck_fail(
      'C-CK1',
      format('replacement_present=%s legacy_constraint_count=%s', v_has_new, v_old)
    );
    RETURN;
  END IF;

  -- C-CK2: customer-less courier pending is valid.
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000001-2000-4000-8000-000000000001', v_tid, 100, 0, 'debt', 'courier',
      'ffff6666-2000-0000-0000-000000000001', 'pending', 0, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.ck_fail('C-CK2', SQLERRM);
  END;

  -- C-CK3: customer-less courier delivered_full is valid when custody=total.
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000002-2000-4000-8000-000000000002', v_tid, 100, 0, 'debt', 'courier',
      'ffff6666-2000-0000-0000-000000000001', 'delivered_full', 100, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.ck_fail('C-CK3', SQLERRM);
  END;

  -- C-CK4: returned is valid without customer even after return flips delivery=direct.
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000003-2000-4000-8000-000000000003', v_tid, 100, 0, 'debt', 'direct',
      NULL, 'returned', 0, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.ck_fail('C-CK4', SQLERRM);
  END;

  -- C-CK5: courier with NULL state and no customer must fail closed.
  v_ok := false;
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000004-2000-4000-8000-000000000004', v_tid, 100, 0, 'debt', 'courier',
      'ffff6666-2000-0000-0000-000000000001', NULL, 0, NULL
    );
  EXCEPTION WHEN check_violation THEN
    v_ok := true;
  END;
  IF NOT v_ok THEN PERFORM pg_temp.ck_fail('C-CK5', 'NULL courier_state was accepted'); END IF;

  -- C-CK6: direct debt without customer must fail.
  v_ok := false;
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000005-2000-4000-8000-000000000005', v_tid, 100, 20, 'partial', 'direct',
      NULL, NULL, 0, NULL
    );
  EXCEPTION WHEN check_violation THEN
    v_ok := true;
  END;
  IF NOT v_ok THEN PERFORM pg_temp.ck_fail('C-CK6', 'direct debt without customer was accepted'); END IF;

  -- C-CK7a: delivered_partial without customer must fail.
  v_ok := false;
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000006-2000-4000-8000-000000000006', v_tid, 100, 0, 'debt', 'courier',
      'ffff6666-2000-0000-0000-000000000001', 'delivered_partial', 40, NULL
    );
  EXCEPTION WHEN check_violation THEN
    v_ok := true;
  END;
  IF NOT v_ok THEN PERFORM pg_temp.ck_fail('C-CK7P', 'customer-less delivered_partial was accepted'); END IF;

  -- C-CK7b: delivered_none without customer must fail.
  v_ok := false;
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000007-2000-4000-8000-000000000007', v_tid, 100, 0, 'debt', 'courier',
      'ffff6666-2000-0000-0000-000000000001', 'delivered_none', 0, NULL
    );
  EXCEPTION WHEN check_violation THEN
    v_ok := true;
  END;
  IF NOT v_ok THEN PERFORM pg_temp.ck_fail('C-CK7N', 'customer-less delivered_none was accepted'); END IF;

  -- C-CK8: direct fully-paid sale without customer remains valid.
  BEGIN
    INSERT INTO orders(
      id, tenant_id, total, paid, status, delivery,
      courier_id, courier_state, collected_by_courier, customer_id
    ) VALUES (
      'aa000008-2000-4000-8000-000000000008', v_tid, 100, 100, 'paid', 'direct',
      NULL, NULL, 0, NULL
    );
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.ck_fail('C-CK8', SQLERRM);
  END;
END
$checks$;

DO $done$
DECLARE
  v_count int;
  v_detail text;
BEGIN
  SELECT COUNT(*) INTO v_count FROM gate4_ck_failures;
  IF v_count > 0 THEN
    SELECT string_agg(test_id || '=' || detail, ' | ' ORDER BY test_id)
      INTO v_detail FROM gate4_ck_failures;
    RAISE EXCEPTION 'GATE4_CK_EXPECTED_RED: % gap(s): %', v_count, v_detail;
  END IF;
  RAISE NOTICE 'GATE4_CK_GREEN: C-CK1..C-CK8 passed';
END
$done$;

ROLLBACK;
