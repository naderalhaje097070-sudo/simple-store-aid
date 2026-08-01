-- FIN-COURIER-001 Gate 4 — retry / idempotency baseline (E3, E4)
-- E3 deliberately documents the known non-idempotent sale-create baseline.
-- True request-key idempotency remains FIN-IDEM-001 and is out of scope here.

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
  ) IS NULL THEN
    RAISE EXCEPTION 'GATE4_RETRY_EXPECTED_RED: create_sale_with_items_v2 is missing';
  END IF;
END
$prereq$;

DO $seed$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active) VALUES
    ('dd880001-5000-4000-8000-000000000001', v_tid, 'G4-RETRY-P1', 100, 60, 10, true),
    ('dd880002-5000-4000-8000-000000000002', v_tid, 'G4-RETRY-P2', 100, 60, 10, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ff880001-5000-4000-8000-000000000001', v_tid, 'G4-RETRY-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $e3$
DECLARE
  v_r1 jsonb;
  v_r2 jsonb;
  v_o1 uuid;
  v_o2 uuid;
  v_n1 bigint;
  v_n2 bigint;
  v_stock numeric;
  v_count int;
BEGIN
  -- Same logical request is intentionally executed twice. Without FIN-IDEM-001,
  -- both calls create independent sales. Gate 4 freezes that baseline explicitly.
  v_r1 := public.create_sale_with_items_v2(
    NULL, 'direct'::delivery_kind, NULL,
    100, 'cash'::payment_method,
    '[{"productId":"dd880001-5000-4000-8000-000000000001","qty":1}]'::jsonb,
    NULL::courier_state
  );
  v_r2 := public.create_sale_with_items_v2(
    NULL, 'direct'::delivery_kind, NULL,
    100, 'cash'::payment_method,
    '[{"productId":"dd880001-5000-4000-8000-000000000001","qty":1}]'::jsonb,
    NULL::courier_state
  );

  v_o1 := (v_r1->>'order_id')::uuid;
  v_o2 := (v_r2->>'order_id')::uuid;
  IF v_o1 = v_o2 THEN RAISE EXCEPTION 'E3 FAIL: duplicate calls returned one order'; END IF;

  SELECT tenant_number INTO v_n1 FROM orders WHERE id = v_o1;
  SELECT tenant_number INTO v_n2 FROM orders WHERE id = v_o2;
  SELECT stock INTO v_stock FROM products WHERE id = 'dd880001-5000-4000-8000-000000000001';
  SELECT COUNT(*) INTO v_count FROM orders WHERE id IN (v_o1, v_o2);

  IF v_count <> 2 OR v_stock <> 8 THEN
    RAISE EXCEPTION 'E3 FAIL: count=% stock=%', v_count, v_stock;
  END IF;
  IF v_n1 IS NULL OR v_n2 IS NULL OR v_n1 = v_n2 THEN
    RAISE EXCEPTION 'E3 FAIL: tenant numbers did not advance independently (% / %)', v_n1, v_n2;
  END IF;
END
$e3$;

DO $e4$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_ok bool := false;
  v_payments int;
  v_amount numeric;
BEGIN
  v_res := public.create_sale_with_items_v2(
    NULL, 'courier'::delivery_kind,
    'ff880001-5000-4000-8000-000000000001'::uuid,
    100, 'cash'::payment_method,
    '[{"productId":"dd880002-5000-4000-8000-000000000002","qty":1}]'::jsonb,
    'delivered_full'::courier_state
  );
  v_oid := (v_res->>'order_id')::uuid;

  PERFORM public.settle_courier_orders(
    'ff880001-5000-4000-8000-000000000001'::uuid,
    ARRAY[v_oid]::uuid[]
  );

  BEGIN
    PERFORM public.settle_courier_orders(
      'ff880001-5000-4000-8000-000000000001'::uuid,
      ARRAY[v_oid]::uuid[]
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%order_not_in_courier_custody%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'E4 FAIL: second settlement was not rejected'; END IF;

  SELECT COUNT(*), COALESCE(SUM(amount), 0)
    INTO v_payments, v_amount
    FROM payments
   WHERE order_id = v_oid
     AND kind = 'courier_settlement';
  IF v_payments <> 1 OR v_amount <> 100 THEN
    RAISE EXCEPTION 'E4 FAIL: settlement rows=% amount=%', v_payments, v_amount;
  END IF;
END
$e4$;

DO $done$ BEGIN
  RAISE NOTICE 'GATE4_RETRY_GREEN: E3 non-idempotent baseline and E4 settlement retry passed';
END
$done$;

ROLLBACK;
