-- Mongezz V2 — Financial rules regression suite
-- Runs entirely inside a transaction and rolls back at the end, so no data persists.
-- Requires DB access as a role that can call SECURITY DEFINER RPCs and set
-- request.jwt.claims (the Supabase managed sandbox role can do this).
--
-- Usage:
--   psql -v ON_ERROR_STOP=1 -v tid="'<tenant_uuid>'" -v uid="'<owner_user_uuid>'" -f tests/financial-rules/rules.sql
-- Or use tests/financial-rules/run.sh which auto-picks the first tenant.

\set QUIET on
SET client_min_messages TO NOTICE;

BEGIN;

-- ---- Auth context ----
SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role','authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

-- ---- Seed isolated test fixtures (rolled back) ----
DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active) VALUES
    ('aaaa1111-0000-0000-0000-000000000001', v_tid, 'TEST-P1', 100, 60, 50, true),
    ('aaaa1111-0000-0000-0000-000000000002', v_tid, 'TEST-P2', 200, 120, 50, true),
    ('aaaa1111-0000-0000-0000-000000000003', v_tid, 'TEST-P3',  50,  30, 50, true);

  INSERT INTO customers(id, tenant_id, name) VALUES
    ('bbbb2222-0000-0000-0000-000000000001', v_tid, 'TEST-CUST');

  INSERT INTO couriers(id, tenant_id, name, is_active) VALUES
    ('cccc3333-0000-0000-0000-000000000001', v_tid, 'TEST-COURIER', true);
END $seed$;

-- =====================================================================
-- T1. Direct sale, fully paid → status=paid, payment row, stock decrement
-- =====================================================================
DO $t1$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_paid numeric; v_status text; v_stock numeric; v_pay_count int;
BEGIN
  v_res := create_sale_with_items(
    NULL, 'direct'::delivery_kind, NULL, 100, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000001","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  SELECT paid, status::text INTO v_paid, v_status FROM orders WHERE id = v_oid;
  SELECT stock INTO v_stock FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_pay_count FROM payments WHERE order_id = v_oid;
  IF v_paid <> 100 OR v_status <> 'paid' THEN RAISE EXCEPTION 'T1 FAIL: paid=% status=%', v_paid, v_status; END IF;
  IF v_stock <> 49 THEN RAISE EXCEPTION 'T1 FAIL: stock not decremented (=%)', v_stock; END IF;
  IF v_pay_count <> 1 THEN RAISE EXCEPTION 'T1 FAIL: payment row missing (count=%)', v_pay_count; END IF;
  RAISE NOTICE 'T1 OK: direct full paid';
END $t1$;

-- =====================================================================
-- T2. Direct partial w/ customer → status=partial, debt = total - paid
-- =====================================================================
DO $t2$
DECLARE v_res jsonb; v_oid uuid; v_paid numeric; v_status text;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid, 'direct'::delivery_kind, NULL, 60, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000002","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  SELECT paid, status::text INTO v_paid, v_status FROM orders WHERE id = v_oid;
  IF v_paid <> 60 OR v_status <> 'partial' THEN RAISE EXCEPTION 'T2 FAIL: paid=% status=%', v_paid, v_status; END IF;
  RAISE NOTICE 'T2 OK: direct partial';
END $t2$;

-- =====================================================================
-- T3. Direct debt without customer must fail
-- =====================================================================
DO $t3$
DECLARE v_ok bool := false;
BEGIN
  BEGIN
    PERFORM create_sale_with_items(
      NULL, 'direct'::delivery_kind, NULL, 0, 'cash'::payment_method,
      '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":1}]'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%customer_required_for_debt%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T3 FAIL: debt without customer was allowed'; END IF;
  RAISE NOTICE 'T3 OK: blocks debt without customer';
END $t3$;

-- =====================================================================
-- T4. paid > total must fail
-- =====================================================================
DO $t4$
DECLARE v_ok bool := false;
BEGIN
  BEGIN
    PERFORM create_sale_with_items(
      NULL, 'direct'::delivery_kind, NULL, 9999, 'cash'::payment_method,
      '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":1}]'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%paid_exceeds_total%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T4 FAIL: overpay was allowed'; END IF;
  RAISE NOTICE 'T4 OK: blocks overpay';
END $t4$;

-- =====================================================================
-- T5. Courier delivered_none (paid=0): orders.paid=0, custody=0, NO payment row
-- =====================================================================
DO $t5$
DECLARE v_res jsonb; v_oid uuid; v_paid numeric; v_cust numeric; v_state text; v_pay_count int;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000001","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  SELECT paid, collected_by_courier, courier_state::text INTO v_paid, v_cust, v_state
    FROM orders WHERE id = v_oid;
  SELECT COUNT(*) INTO v_pay_count FROM payments WHERE order_id = v_oid;
  IF v_paid <> 0 OR v_cust <> 0 OR v_state <> 'pending' THEN
    RAISE EXCEPTION 'T5 FAIL: paid=% cust=% state=%', v_paid, v_cust, v_state;
  END IF;
  IF v_pay_count <> 0 THEN
    RAISE EXCEPTION 'T5 FAIL: courier pending should not create payment (count=%)', v_pay_count;
  END IF;
  RAISE NOTICE 'T5 OK: courier pending = custody only';
END $t5$;

-- =====================================================================
-- T6. Courier with money at creation → custody (not cash). orders.paid=0.
-- =====================================================================
DO $t6$
DECLARE v_res jsonb; v_oid uuid; v_paid numeric; v_cust numeric; v_state text; v_pay_count int;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    80, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000002","qty":1}]'::jsonb -- price 200
  );
  v_oid := (v_res->>'order_id')::uuid;
  SELECT paid, collected_by_courier, courier_state::text INTO v_paid, v_cust, v_state
    FROM orders WHERE id = v_oid;
  SELECT COUNT(*) INTO v_pay_count FROM payments WHERE order_id = v_oid;
  IF v_paid <> 0 OR v_cust <> 80 OR v_state <> 'delivered_partial' THEN
    RAISE EXCEPTION 'T6 FAIL: paid=% cust=% state=%', v_paid, v_cust, v_state;
  END IF;
  IF v_pay_count <> 0 THEN
    RAISE EXCEPTION 'T6 FAIL: courier custody should NOT create payment row yet (count=%)', v_pay_count;
  END IF;
  RAISE NOTICE 'T6 OK: courier money stays in custody until settlement';
END $t6$;

-- =====================================================================
-- T7. collect_order_debt while courier holds custody must fail (settle_courier_first)
-- =====================================================================
DO $t7$
DECLARE v_res jsonb; v_oid uuid; v_ok bool := false;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    30, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  BEGIN
    PERFORM collect_order_debt(v_oid, 10, 'cash'::payment_method);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%settle_courier_first%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T7 FAIL: debt collection allowed while courier holds custody'; END IF;
  RAISE NOTICE 'T7 OK: collect blocked while courier holds order';
END $t7$;

-- =====================================================================
-- T8. settle_courier_orders → cash enters box, custody clears, courier_id=NULL
-- =====================================================================
DO $t8$
DECLARE
  v_res jsonb; v_oid uuid;
  v_paid numeric; v_cust numeric; v_courier uuid; v_delivery text;
  v_settle_pay_count int; v_settle_amount numeric;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    100, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000002","qty":1}]'::jsonb -- total 200
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM settle_courier_orders(
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    ARRAY[v_oid]::uuid[]
  );

  SELECT paid, collected_by_courier, courier_id, delivery::text
    INTO v_paid, v_cust, v_courier, v_delivery
    FROM orders WHERE id = v_oid;
  SELECT COUNT(*), COALESCE(SUM(amount),0) INTO v_settle_pay_count, v_settle_amount
    FROM payments WHERE order_id = v_oid AND kind = 'courier_settlement';
  IF v_paid <> 100 OR v_cust <> 0 OR v_courier IS NOT NULL OR v_delivery <> 'direct' THEN
    RAISE EXCEPTION 'T8 FAIL: paid=% cust=% courier=% delivery=%', v_paid, v_cust, v_courier, v_delivery;
  END IF;
  IF v_settle_pay_count <> 1 OR v_settle_amount <> 100 THEN
    RAISE EXCEPTION 'T8 FAIL: settlement payment wrong (count=% amount=%)', v_settle_pay_count, v_settle_amount;
  END IF;
  RAISE NOTICE 'T8 OK: settlement moves custody → cash';
END $t8$;

-- =====================================================================
-- T9. return_courier_order before any collection → stock restored, off custody
-- =====================================================================
DO $t9$
DECLARE
  v_res jsonb; v_oid uuid; v_stock_before numeric; v_stock_after numeric;
  v_state text; v_courier uuid; v_delivery text;
BEGIN
  SELECT stock INTO v_stock_before FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000003';
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":2}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM return_courier_order(v_oid);
  SELECT stock INTO v_stock_after FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000003';
  SELECT courier_state::text, courier_id, delivery::text INTO v_state, v_courier, v_delivery
    FROM orders WHERE id = v_oid;
  IF v_stock_after <> v_stock_before THEN
    RAISE EXCEPTION 'T9 FAIL: stock not restored (before=% after=%)', v_stock_before, v_stock_after;
  END IF;
  IF v_state <> 'returned' OR v_courier IS NOT NULL OR v_delivery <> 'direct' THEN
    RAISE EXCEPTION 'T9 FAIL: state=% courier=% delivery=%', v_state, v_courier, v_delivery;
  END IF;
  RAISE NOTICE 'T9 OK: return restores stock and clears custody';
END $t9$;

-- =====================================================================
-- T10. return_courier_order after partial collection must fail
-- =====================================================================
DO $t10$
DECLARE v_res jsonb; v_oid uuid; v_ok bool := false;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    20, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  BEGIN
    PERFORM return_courier_order(v_oid);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%cannot_return_partially_paid_order%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T10 FAIL: return after collection was allowed'; END IF;
  RAISE NOTICE 'T10 OK: return blocked after collection';
END $t10$;

-- =====================================================================
-- T11. delete_order_with_restore_stock on unpaid direct order → stock restored
-- =====================================================================
DO $t11$
DECLARE v_res jsonb; v_oid uuid; v_before numeric; v_after numeric; v_exists int;
BEGIN
  SELECT stock INTO v_before FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000001';
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'direct'::delivery_kind, NULL, 0, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000001","qty":3}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM delete_order_with_restore_stock(v_oid);
  SELECT stock INTO v_after FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_exists FROM orders WHERE id = v_oid;
  IF v_after <> v_before THEN RAISE EXCEPTION 'T11 FAIL: stock not restored (b=% a=%)', v_before, v_after; END IF;
  IF v_exists <> 0 THEN RAISE EXCEPTION 'T11 FAIL: order still exists'; END IF;
  RAISE NOTICE 'T11 OK: delete restores stock';
END $t11$;

-- =====================================================================
-- T12. delete on paid order must fail
-- =====================================================================
DO $t12$
DECLARE v_res jsonb; v_oid uuid; v_ok bool := false;
BEGIN
  v_res := create_sale_with_items(
    NULL, 'direct'::delivery_kind, NULL, 100, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000001","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  BEGIN
    PERFORM delete_order_with_restore_stock(v_oid);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%cannot_delete_paid_order%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T12 FAIL: deleting paid order was allowed'; END IF;
  RAISE NOTICE 'T12 OK: cannot delete paid order';
END $t12$;

-- =====================================================================
-- T13. Insufficient stock must fail and not create an order
-- =====================================================================
DO $t13$
DECLARE v_ok bool := false;
BEGIN
  BEGIN
    PERFORM create_sale_with_items(
      NULL, 'direct'::delivery_kind, NULL, 0, 'cash'::payment_method,
      '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":99999}]'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%insufficient_stock%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'T13 FAIL: oversell was allowed'; END IF;
  RAISE NOTICE 'T13 OK: blocks oversell';
END $t13$;

-- =====================================================================
-- T14. settle_courier_orders uses orders.collected_by_courier as source of truth
--      (no caller-supplied amount in new signature)
-- =====================================================================
DO $t14$
DECLARE
  v_res jsonb; v_oid uuid;
  v_paid numeric; v_settle_amount numeric;
BEGIN
  -- Create courier order, total = 200, courier already collected 150 at door
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    150, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000002","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  -- Settle: must use stored collected (150), not anything else
  PERFORM settle_courier_orders(
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    ARRAY[v_oid]::uuid[]
  );
  SELECT paid INTO v_paid FROM orders WHERE id = v_oid;
  SELECT COALESCE(SUM(amount),0) INTO v_settle_amount
    FROM payments WHERE order_id = v_oid AND kind = 'courier_settlement';
  IF v_paid <> 150 OR v_settle_amount <> 150 THEN
    RAISE EXCEPTION 'T14 FAIL: stored custody not used (paid=% settled=%)', v_paid, v_settle_amount;
  END IF;
  RAISE NOTICE 'T14 OK: settlement uses stored collected_by_courier';
END $t14$;

-- =====================================================================
-- T15. A returned courier order is NOT customer debt and cannot be collected
--      (P0-1 regression: return restores stock but leaves status='debt')
-- =====================================================================
DO $t15$
DECLARE
  v_res jsonb; v_oid uuid;
  v_stock_before numeric; v_stock_after numeric;
  v_order_debt numeric; v_custody numeric;
  v_collect_blocked bool := false;
BEGIN
  SELECT stock INTO v_stock_before FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000001';
  -- Courier order, full debt (paid=0), with customer + courier
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000001","qty":2}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;

  PERFORM return_courier_order(v_oid);

  -- 1) Stock restored
  SELECT stock INTO v_stock_after FROM products WHERE id = 'aaaa1111-0000-0000-0000-000000000001';
  IF v_stock_after <> v_stock_before THEN
    RAISE EXCEPTION 'T15 FAIL: stock not restored (before=% after=%)', v_stock_before, v_stock_after;
  END IF;

  -- 2) close_day's customer_debts formula must yield 0 for this order
  SELECT CASE
      WHEN courier_state = 'returned' THEN 0
      WHEN delivery = 'direct' OR courier_id IS NULL THEN GREATEST(total - paid, 0)
      WHEN delivery = 'courier' AND courier_state = 'delivered_none' THEN total
      WHEN delivery = 'courier' AND courier_state = 'delivered_partial' THEN GREATEST(total - collected_by_courier, 0)
      ELSE 0
    END
    INTO v_order_debt
    FROM orders WHERE id = v_oid;
  IF v_order_debt <> 0 THEN
    RAISE EXCEPTION 'T15 FAIL: returned order counted as customer debt (=%)', v_order_debt;
  END IF;

  -- 3) Courier custody must be 0
  SELECT COALESCE(collected_by_courier, 0) INTO v_custody FROM orders WHERE id = v_oid;
  IF v_custody <> 0 THEN
    RAISE EXCEPTION 'T15 FAIL: returned order still in custody (=%)', v_custody;
  END IF;

  -- 4) collect_order_debt must reject a returned order
  BEGIN
    PERFORM collect_order_debt(v_oid, 10, 'cash'::payment_method);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%cannot_collect_returned_order%' THEN v_collect_blocked := true; END IF;
  END;
  IF NOT v_collect_blocked THEN
    RAISE EXCEPTION 'T15 FAIL: collection on returned order was allowed';
  END IF;

  RAISE NOTICE 'T15 OK: returned order is not customer debt and cannot be collected';
END $t15$;

-- =====================================================================
-- T16. A returned courier order cannot be settled
--      (return clears courier_id; a NULL-unsafe custody check let settlement
--       erase the returned mark and turn the order back into customer debt)
-- =====================================================================
DO $t16$
DECLARE
  v_res jsonb; v_oid uuid;
  v_blocked bool := false; v_err text;
  v_state text; v_status text; v_paid numeric; v_settle_count int; v_order_debt numeric;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    0, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000003","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM return_courier_order(v_oid);

  BEGIN
    PERFORM settle_courier_orders(
      'cccc3333-0000-0000-0000-000000000001'::uuid,
      ARRAY[v_oid]::uuid[]
    );
  EXCEPTION WHEN OTHERS THEN
    v_err := SQLERRM;
    IF v_err LIKE '%order_not_in_courier_custody%' THEN v_blocked := true; END IF;
  END;
  IF NOT v_blocked THEN
    RAISE EXCEPTION 'T16 FAIL: settlement of a returned order was allowed (error=%)', v_err;
  END IF;

  SELECT courier_state::text, status::text, paid INTO v_state, v_status, v_paid FROM orders WHERE id = v_oid;
  SELECT COUNT(*) INTO v_settle_count FROM payments WHERE order_id = v_oid AND kind = 'courier_settlement';
  SELECT CASE
      WHEN courier_state = 'returned' THEN 0
      WHEN delivery = 'direct' OR courier_id IS NULL THEN GREATEST(total - paid, 0)
      ELSE 0
    END INTO v_order_debt FROM orders WHERE id = v_oid;
  IF v_state IS DISTINCT FROM 'returned' OR v_paid <> 0 OR v_settle_count <> 0 OR v_order_debt <> 0 THEN
    RAISE EXCEPTION 'T16 FAIL: returned order changed (state=% status=% paid=% settlements=% debt=%)',
      v_state, v_status, v_paid, v_settle_count, v_order_debt;
  END IF;
  RAISE NOTICE 'T16 OK: returned order cannot be settled and stays returned';
END $t16$;

-- =====================================================================
-- T17. An already settled courier order cannot be settled again
-- =====================================================================
DO $t17$
DECLARE
  v_res jsonb; v_oid uuid;
  v_blocked bool := false; v_err text;
  v_settle_count int; v_settle_amount numeric; v_paid numeric;
BEGIN
  v_res := create_sale_with_items(
    'bbbb2222-0000-0000-0000-000000000001'::uuid,
    'courier'::delivery_kind,
    'cccc3333-0000-0000-0000-000000000001'::uuid,
    50, 'cash'::payment_method,
    '[{"productId":"aaaa1111-0000-0000-0000-000000000002","qty":1}]'::jsonb -- total 200
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM settle_courier_orders('cccc3333-0000-0000-0000-000000000001'::uuid, ARRAY[v_oid]::uuid[]);

  BEGIN
    PERFORM settle_courier_orders('cccc3333-0000-0000-0000-000000000001'::uuid, ARRAY[v_oid]::uuid[]);
  EXCEPTION WHEN OTHERS THEN
    v_err := SQLERRM;
    IF v_err LIKE '%order_not_in_courier_custody%' THEN v_blocked := true; END IF;
  END;
  IF NOT v_blocked THEN
    RAISE EXCEPTION 'T17 FAIL: second settlement was allowed (error=%)', v_err;
  END IF;

  SELECT paid INTO v_paid FROM orders WHERE id = v_oid;
  SELECT COUNT(*), COALESCE(SUM(amount),0) INTO v_settle_count, v_settle_amount
    FROM payments WHERE order_id = v_oid AND kind = 'courier_settlement';
  IF v_paid <> 50 OR v_settle_count <> 1 OR v_settle_amount <> 50 THEN
    RAISE EXCEPTION 'T17 FAIL: paid=% settlements=% amount=%', v_paid, v_settle_count, v_settle_amount;
  END IF;
  RAISE NOTICE 'T17 OK: settled order cannot be settled twice';
END $t17$;

-- =====================================================================
-- All assertions passed
-- =====================================================================
DO $done$ BEGIN RAISE NOTICE '====== ALL FINANCIAL RULES TESTS PASSED ======'; END $done$;

ROLLBACK;

