-- Mongezz V2 — Financial rules regression suite
-- Runs entirely inside a transaction and rolls back at the end, so no data persists.
-- Requires DB access as a role that can call SECURITY DEFINER RPCs and set
-- request.jwt.claims (the Supabase managed sandbox role can do this).
--
-- Usage:
--   psql -v ON_ERROR_STOP=1 -v tid="'<tenant_uuid>'" -v uid="'<owner_user_uuid>'" -f tests/financial-rules/rules.sql
-- Or use tests/financial-rules/run.sh which auto-picks the first tenant.

\set QUIET on
SET client_min_messages TO WARNING;

BEGIN;

-- ---- Auth context ----
SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role','authenticated')::text,
  true
);

-- ---- Seed isolated test fixtures (rolled back) ----
DO $seed$
DECLARE v_tid uuid := :tid;
BEGIN
  -- Three products: full stock so each test has its own
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
    jsonb_build_array(jsonb_build_object('order_id', v_oid, 'collected', 100))
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
-- All assertions passed
-- =====================================================================
DO $done$ BEGIN RAISE NOTICE '====== ALL FINANCIAL RULES TESTS PASSED ======'; END $done$;

ROLLBACK;
