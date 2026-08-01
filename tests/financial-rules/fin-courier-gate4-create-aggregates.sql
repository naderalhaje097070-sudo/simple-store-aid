-- FIN-COURIER-001 Gate 4 — B5/B6/B8 creation + aggregate safety net

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
    RAISE EXCEPTION 'GATE4_CREATE_AGG_EXPECTED_RED: create_sale_with_items_v2 is missing';
  END IF;
END
$prereq$;

DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id,tenant_id,name,price,cost,stock,is_active) VALUES
    ('dd120001-d000-4000-8000-000000000001',v_tid,'G4-B8-PENDING',100,60,10,true),
    ('dd120002-d000-4000-8000-000000000002',v_tid,'G4-B8-FULL',100,60,10,true),
    ('dd120003-d000-4000-8000-000000000003',v_tid,'G4-B8-NONE',100,60,10,true),
    ('dd120004-d000-4000-8000-000000000004',v_tid,'G4-B8-PARTIAL',100,60,10,true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id,tenant_id,name)
  VALUES ('ee120001-d000-4000-8000-000000000001',v_tid,'G4-B8-CUSTOMER')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id,tenant_id,name,is_active)
  VALUES ('ff120001-d000-4000-8000-000000000001',v_tid,'G4-B8-COURIER',true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $create_and_aggregate$
DECLARE
  r_pending jsonb;
  r_full jsonb;
  r_none jsonb;
  r_partial jsonb;
  o_none uuid;
  o_partial uuid;
  v_state text;
  v_custody numeric;
  v_payments int;
  v_close jsonb;
  v_debt numeric;
  v_unsettled numeric;
BEGIN
  r_pending := public.create_sale_with_items_v2(
    NULL,'courier'::delivery_kind,'ff120001-d000-4000-8000-000000000001',
    0,'cash'::payment_method,
    '[{"productId":"dd120001-d000-4000-8000-000000000001","qty":1}]'::jsonb,
    'pending'::courier_state
  );

  r_full := public.create_sale_with_items_v2(
    NULL,'courier'::delivery_kind,'ff120001-d000-4000-8000-000000000001',
    100,'cash'::payment_method,
    '[{"productId":"dd120002-d000-4000-8000-000000000002","qty":1}]'::jsonb,
    'delivered_full'::courier_state
  );

  -- B5: create-time delivered_none with customer.
  r_none := public.create_sale_with_items_v2(
    'ee120001-d000-4000-8000-000000000001','courier'::delivery_kind,
    'ff120001-d000-4000-8000-000000000001',0,'cash'::payment_method,
    '[{"productId":"dd120003-d000-4000-8000-000000000003","qty":1}]'::jsonb,
    'delivered_none'::courier_state
  );
  o_none := (r_none->>'order_id')::uuid;
  SELECT courier_state::text,collected_by_courier INTO v_state,v_custody FROM orders WHERE id=o_none;
  IF v_state <> 'delivered_none' OR v_custody <> 0 THEN
    RAISE EXCEPTION 'B5 FAIL: state=% custody=%', v_state, v_custody;
  END IF;

  -- B6: create-time delivered_partial with customer.
  r_partial := public.create_sale_with_items_v2(
    'ee120001-d000-4000-8000-000000000001','courier'::delivery_kind,
    'ff120001-d000-4000-8000-000000000001',40,'cash'::payment_method,
    '[{"productId":"dd120004-d000-4000-8000-000000000004","qty":1}]'::jsonb,
    'delivered_partial'::courier_state
  );
  o_partial := (r_partial->>'order_id')::uuid;
  SELECT courier_state::text,collected_by_courier INTO v_state,v_custody FROM orders WHERE id=o_partial;
  IF v_state <> 'delivered_partial' OR v_custody <> 40 THEN
    RAISE EXCEPTION 'B6 FAIL: state=% custody=%', v_state, v_custody;
  END IF;

  -- No courier create path may emit a store payment before settlement.
  SELECT COUNT(*) INTO v_payments
    FROM payments
   WHERE order_id IN (
     (r_pending->>'order_id')::uuid,
     (r_full->>'order_id')::uuid,
     o_none,
     o_partial
   );
  IF v_payments <> 0 THEN
    RAISE EXCEPTION 'B5/B6 FAIL: courier creation emitted % payment row(s)', v_payments;
  END IF;

  -- B8: pending 0/0, full debt0/custody100, none debt100/custody0,
  -- partial debt60/custody40 => debt160 / unsettled custody140.
  v_close := public.close_day('FIN-COURIER Gate 4 B8');
  SELECT customer_debts, unsettled_custody
    INTO v_debt, v_unsettled
    FROM day_closes
   WHERE tenant_id = current_setting('mongezz.test_tid')::uuid
   ORDER BY created_at DESC
   LIMIT 1;

  IF v_debt <> 160 OR v_unsettled <> 140 THEN
    RAISE EXCEPTION 'B8 FAIL: debt=% custody=% expected=160/140 close=%', v_debt, v_unsettled, v_close;
  END IF;

  RAISE NOTICE 'GATE4_CREATE_AGG_GREEN: B5/B6/B8 passed debt=160 custody=140';
END
$create_and_aggregate$;

ROLLBACK;
