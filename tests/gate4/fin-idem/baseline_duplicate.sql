-- FIN-IDEM-001 Gate 4 baseline probe.
-- Proves the current logical retry baseline is not idempotent.
-- Runs entirely inside a transaction and rolls back.

\set QUIET on
SET client_min_messages TO NOTICE;

BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active)
VALUES (
  'dddd4444-0000-0000-0000-000000000001',
  current_setting('mongezz.test_tid')::uuid,
  'FIN-IDEM-RETRY-PROBE',
  100,
  60,
  10,
  true
);

DO $probe$
DECLARE
  v_first jsonb;
  v_second jsonb;
  v_first_id uuid;
  v_second_id uuid;
  v_stock numeric;
  v_order_count integer;
  v_payment_count integer;
BEGIN
  -- Same logical request executed twice. The legacy API has no request key.
  v_first := create_sale_with_items(
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb
  );

  v_second := create_sale_with_items(
    NULL,
    'direct'::delivery_kind,
    NULL,
    100,
    'cash'::payment_method,
    '[{"productId":"dddd4444-0000-0000-0000-000000000001","qty":1}]'::jsonb
  );

  v_first_id := (v_first->>'order_id')::uuid;
  v_second_id := (v_second->>'order_id')::uuid;

  SELECT stock INTO v_stock
  FROM products
  WHERE id = 'dddd4444-0000-0000-0000-000000000001';

  SELECT COUNT(*) INTO v_order_count
  FROM orders
  WHERE id IN (v_first_id, v_second_id);

  SELECT COUNT(*) INTO v_payment_count
  FROM payments
  WHERE order_id IN (v_first_id, v_second_id);

  IF v_first_id = v_second_id THEN
    RAISE EXCEPTION 'FIN_IDEM_G4_BASELINE_FAIL: legacy retry unexpectedly returned one order';
  END IF;

  IF v_order_count <> 2 OR v_payment_count <> 2 OR v_stock <> 8 THEN
    RAISE EXCEPTION
      'FIN_IDEM_G4_BASELINE_FAIL: duplicate effects not proven orders=% payments=% stock=%',
      v_order_count, v_payment_count, v_stock;
  END IF;

  RAISE NOTICE 'FIN_IDEM_G4_E1_EXPECTED_RED: identical logical retry produced two orders, two payment effects, and two stock decrements';
END $probe$;

ROLLBACK;
