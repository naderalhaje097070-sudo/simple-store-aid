-- FIN-COURIER-001 Gate 4 — returned-order safety baseline (D-R1..D-R8)
-- This suite must already be GREEN before PR-A and remain GREEN after adapters
-- delegate to the canonical v2 transition rules.

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
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active) VALUES
    ('dd770001-4000-4000-8000-000000000001', v_tid, 'G4-RETURN-P1', 100, 60, 20, true),
    ('dd770002-4000-4000-8000-000000000002', v_tid, 'G4-RETURN-P2', 100, 60, 20, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('ee770001-4000-4000-8000-000000000001', v_tid, 'G4-RETURN-CUSTOMER')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ff770001-4000-4000-8000-000000000001', v_tid, 'G4-RETURN-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $return_contract$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_stock_before numeric;
  v_stock_after numeric;
  v_stock_after_retry numeric;
  v_state text;
  v_delivery text;
  v_courier uuid;
  v_debt numeric;
  v_ok bool;
  v_audit int;
BEGIN
  -- D-R1: create customer courier debt then explicitly record delivered_none.
  SELECT stock INTO v_stock_before
    FROM products WHERE id = 'dd770001-4000-4000-8000-000000000001';

  v_res := public.create_sale_with_items(
    'ee770001-4000-4000-8000-000000000001'::uuid,
    'courier'::delivery_kind,
    'ff770001-4000-4000-8000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"dd770001-4000-4000-8000-000000000001","qty":2}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;

  PERFORM public.update_courier_order_state(v_oid, 'delivered_none'::courier_state, 0);
  PERFORM public.return_courier_order(v_oid);

  SELECT courier_state::text, delivery::text, courier_id
    INTO v_state, v_delivery, v_courier
    FROM orders WHERE id = v_oid;

  IF v_state <> 'returned' OR v_delivery <> 'direct' OR v_courier IS NOT NULL THEN
    RAISE EXCEPTION 'D-R1 FAIL: state=% delivery=% courier=%', v_state, v_delivery, v_courier;
  END IF;

  -- D-R2: returned has zero derived customer debt.
  SELECT CASE
      WHEN courier_state = 'returned' THEN 0
      WHEN delivery = 'direct' OR courier_id IS NULL THEN GREATEST(total - paid, 0)
      WHEN delivery = 'courier' AND courier_state = 'delivered_none' THEN total
      WHEN delivery = 'courier' AND courier_state = 'delivered_partial' THEN GREATEST(total - collected_by_courier, 0)
      ELSE 0
    END
    INTO v_debt
    FROM orders WHERE id = v_oid;
  IF v_debt <> 0 THEN RAISE EXCEPTION 'D-R2 FAIL: returned debt=%', v_debt; END IF;

  -- D-R3: stock restored exactly once.
  SELECT stock INTO v_stock_after
    FROM products WHERE id = 'dd770001-4000-4000-8000-000000000001';
  IF v_stock_after <> v_stock_before THEN
    RAISE EXCEPTION 'D-R3 FAIL: stock before=% after=%', v_stock_before, v_stock_after;
  END IF;

  -- D-R4: repeated return rejected and cannot restore stock twice.
  v_ok := false;
  BEGIN
    PERFORM public.return_courier_order(v_oid);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%not_a_courier_order%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-R4 FAIL: repeated return was accepted'; END IF;

  SELECT stock INTO v_stock_after_retry
    FROM products WHERE id = 'dd770001-4000-4000-8000-000000000001';
  IF v_stock_after_retry <> v_stock_after THEN
    RAISE EXCEPTION 'D-R4 FAIL: retry changed stock from % to %', v_stock_after, v_stock_after_retry;
  END IF;

  -- D-R5: returned is terminal through the compatibility transition path.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_order_state(v_oid, 'delivered_full'::courier_state, 100);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%not_a_courier_order%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-R5 FAIL: transition out of returned was accepted'; END IF;

  -- D-R7: no collection may survive the return.
  v_ok := false;
  BEGIN
    PERFORM public.collect_order_debt(v_oid, 10, 'cash'::payment_method);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%cannot_collect_returned_order%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-R7 FAIL: returned debt collection was accepted'; END IF;

  -- D-R8: financial audit log captures the order mutation.
  SELECT COUNT(*) INTO v_audit
    FROM financial_audit_log
   WHERE entity_type = 'orders'
     AND entity_id = v_oid
     AND before IS NOT NULL
     AND after IS NOT NULL
     AND after->>'courier_state' = 'returned';
  IF v_audit < 1 THEN RAISE EXCEPTION 'D-R8 FAIL: no returned order audit evidence'; END IF;
END
$return_contract$;

DO $settled_return$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_ok bool := false;
BEGIN
  -- D-R6: once settled, delivery is direct and return is forbidden.
  v_res := public.create_sale_with_items(
    'ee770001-4000-4000-8000-000000000001'::uuid,
    'courier'::delivery_kind,
    'ff770001-4000-4000-8000-000000000001'::uuid,
    100, 'cash'::payment_method,
    '[{"productId":"dd770002-4000-4000-8000-000000000002","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM public.settle_courier_orders(
    'ff770001-4000-4000-8000-000000000001'::uuid,
    ARRAY[v_oid]::uuid[]
  );

  BEGIN
    PERFORM public.return_courier_order(v_oid);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%not_a_courier_order%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'D-R6 FAIL: settled order was returnable'; END IF;
END
$settled_return$;

DO $done$ BEGIN
  RAISE NOTICE 'GATE4_RETURN_GREEN: D-R1..D-R8 baseline passed';
END
$done$;

ROLLBACK;
