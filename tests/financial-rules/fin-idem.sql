-- FIN-IDEM-001 — sale-create behavior tests.
-- Must run only against disposable isolated Supabase/PostgreSQL.
-- Usage mirrors rules.sql: psql -v ON_ERROR_STOP=1 -v tid="'<tenant_uuid>'" -v uid="'<owner_user_uuid>'" -f this-file

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active)
  VALUES ('fade1000-0000-0000-0000-000000000001', v_tid, 'FIN-IDEM-P1', 100, 60, 20, true);
  INSERT INTO customers(id, tenant_id, name)
  VALUES ('fade2000-0000-0000-0000-000000000001', v_tid, 'FIN-IDEM-C1');
END $seed$;

-- I1: exact replay returns the original result and applies one financial effect.
DO $i1$
DECLARE
  v_key uuid := 'fade3000-0000-0000-0000-000000000001';
  v_a jsonb;
  v_b jsonb;
  v_oid uuid;
  v_stock numeric;
  v_orders int;
  v_payments int;
  v_keys int;
BEGIN
  v_a := public.create_sale_with_items_idempotent(
    v_key,
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    NULL
  );
  v_b := public.create_sale_with_items_idempotent(
    v_key,
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    NULL
  );

  IF v_a <> v_b THEN RAISE EXCEPTION 'FIN_IDEM_I1_FAIL: replay result differs'; END IF;
  v_oid := (v_a->>'order_id')::uuid;
  SELECT stock INTO v_stock FROM products WHERE id = 'fade1000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_orders FROM orders WHERE id = v_oid;
  SELECT COUNT(*) INTO v_payments FROM payments WHERE order_id = v_oid;
  SELECT COUNT(*) INTO v_keys FROM financial_idempotency
   WHERE tenant_id = current_setting('mongezz.test_tid')::uuid
     AND operation = 'sale.create.v2'
     AND idempotency_key = v_key;

  IF v_stock <> 19 OR v_orders <> 1 OR v_payments <> 1 OR v_keys <> 1 THEN
    RAISE EXCEPTION 'FIN_IDEM_I1_FAIL: stock=% orders=% payments=% keys=%', v_stock, v_orders, v_payments, v_keys;
  END IF;
  RAISE NOTICE 'FIN_IDEM_I1_OK: exact replay has one financial effect';
END $i1$;

-- I2: same tenant+operation+key with a different canonical request conflicts.
DO $i2$
DECLARE
  v_key uuid := 'fade3000-0000-0000-0000-000000000001';
  v_ok boolean := false;
BEGIN
  BEGIN
    PERFORM public.create_sale_with_items_idempotent(
      v_key,
      NULL,
      'direct'::delivery_kind,
      NULL,
      200,
      'cash'::payment_method,
      '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":2}]'::jsonb,
      NULL
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%idempotency_conflict%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'FIN_IDEM_I2_FAIL: mismatched replay did not conflict'; END IF;
  RAISE NOTICE 'FIN_IDEM_I2_OK: mismatched replay rejected';
END $i2$;

-- I3: a different key represents a new logical request and may execute normally.
DO $i3$
DECLARE
  v_key uuid := 'fade3000-0000-0000-0000-000000000002';
  v_res jsonb;
  v_stock numeric;
BEGIN
  v_res := public.create_sale_with_items_idempotent(
    v_key,
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    NULL
  );
  IF (v_res->>'order_id') IS NULL THEN RAISE EXCEPTION 'FIN_IDEM_I3_FAIL: missing order result'; END IF;
  SELECT stock INTO v_stock FROM products WHERE id = 'fade1000-0000-0000-0000-000000000001';
  IF v_stock <> 18 THEN RAISE EXCEPTION 'FIN_IDEM_I3_FAIL: new key did not execute exactly once, stock=%', v_stock; END IF;
  RAISE NOTICE 'FIN_IDEM_I3_OK: different key is a new logical request';
END $i3$;

-- I4: a failed canonical financial write must roll the reservation back.
-- Reusing that key for a corrected retry must not be poisoned by the failed request.
DO $i4$
DECLARE
  v_key uuid := 'fade3000-0000-0000-0000-000000000003';
  v_failed boolean := false;
  v_res jsonb;
  v_rows int;
BEGIN
  BEGIN
    PERFORM public.create_sale_with_items_idempotent(
      v_key,
      NULL,
      'direct'::delivery_kind,
      NULL,
      99900,
      'cash'::payment_method,
      '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":999}]'::jsonb,
      NULL
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%insufficient_stock%' THEN v_failed := true; END IF;
  END;
  IF NOT v_failed THEN RAISE EXCEPTION 'FIN_IDEM_I4_FAIL: forced owner failure did not occur'; END IF;

  SELECT COUNT(*) INTO v_rows FROM financial_idempotency
   WHERE tenant_id = current_setting('mongezz.test_tid')::uuid
     AND operation = 'sale.create.v2'
     AND idempotency_key = v_key;
  IF v_rows <> 0 THEN RAISE EXCEPTION 'FIN_IDEM_I4_FAIL: failed transaction poisoned key'; END IF;

  v_res := public.create_sale_with_items_idempotent(
    v_key,
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"fade1000-0000-0000-0000-000000000001","qty":1}]'::jsonb,
    NULL
  );
  IF (v_res->>'order_id') IS NULL THEN RAISE EXCEPTION 'FIN_IDEM_I4_FAIL: corrected retry did not execute'; END IF;
  RAISE NOTICE 'FIN_IDEM_I4_OK: failed owner transaction does not poison retry';
END $i4$;

-- I5: application roles cannot write/read reservation storage directly.
DO $i5$
BEGIN
  IF has_table_privilege('authenticated', 'public.financial_idempotency', 'SELECT')
     OR has_table_privilege('authenticated', 'public.financial_idempotency', 'INSERT')
     OR has_table_privilege('authenticated', 'public.financial_idempotency', 'UPDATE')
     OR has_table_privilege('authenticated', 'public.financial_idempotency', 'DELETE') THEN
    RAISE EXCEPTION 'FIN_IDEM_I5_FAIL: authenticated has direct reservation-table privileges';
  END IF;
  RAISE NOTICE 'FIN_IDEM_I5_OK: reservation storage is RPC-only';
END $i5$;

ROLLBACK;
\echo 'FIN_IDEM_BEHAVIOR_GREEN'
