-- FIN-COURIER-001 Gate 4 — rollback endpoint contract (H1/H2/H3)
-- The current pre-change baseline already represents the required database end
-- state after a future forward-only corrective rollback. This test fingerprints
-- that endpoint now and must be rerun after the future corrective migration.

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

DO $h1_catalog$
DECLARE
  v_count int;
  v_validated int;
BEGIN
  -- Replacement constraint is absent at the rollback endpoint.
  SELECT COUNT(*) INTO v_count
    FROM pg_constraint
   WHERE conrelid='public.orders'::regclass
     AND conname='orders_customer_required_when_debt';
  IF v_count <> 0 THEN
    RAISE EXCEPTION 'H1 FAIL: replacement debt constraint still exists';
  END IF;

  -- Original constraints are restored, both NOT VALID.
  SELECT COUNT(*), COUNT(*) FILTER (WHERE NOT convalidated)
    INTO v_count, v_validated
    FROM pg_constraint
   WHERE conrelid='public.orders'::regclass
     AND conname IN (
       'orders_customer_required_when_unpaid',
       'orders_courier_requires_customer_id'
     );
  IF v_count <> 2 OR v_validated <> 2 THEN
    RAISE EXCEPTION 'H1 FAIL: legacy constraints count=% not_valid_count=%', v_count, v_validated;
  END IF;

  -- v2 surfaces are removed at the rollback endpoint; legacy signatures remain.
  IF to_regprocedure(
    'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
  ) IS NOT NULL THEN
    RAISE EXCEPTION 'H1 FAIL: create_sale_with_items_v2 still exists';
  END IF;
  IF to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  ) IS NOT NULL THEN
    RAISE EXCEPTION 'H1 FAIL: update_courier_outcome_v2 still exists';
  END IF;
  IF to_regprocedure(
    'public.create_sale_with_items(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb)'
  ) IS NULL THEN
    RAISE EXCEPTION 'H1 FAIL: legacy create_sale_with_items is missing';
  END IF;
  IF to_regprocedure(
    'public.update_courier_order_state(uuid,public.courier_state,numeric)'
  ) IS NULL THEN
    RAISE EXCEPTION 'H1 FAIL: legacy update_courier_order_state is missing';
  END IF;
END
$h1_catalog$;

DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id,tenant_id,name,price,cost,stock,is_active)
  VALUES ('ddee0001-b000-4000-8000-000000000001',v_tid,'G4-ROLLBACK-P1',100,60,10,true)
  ON CONFLICT (id) DO NOTHING;
  INSERT INTO customers(id,tenant_id,name)
  VALUES ('eeee0001-b000-4000-8000-000000000001',v_tid,'G4-ROLLBACK-C1')
  ON CONFLICT (id) DO NOTHING;
  INSERT INTO couriers(id,tenant_id,name,is_active)
  VALUES ('ffee0001-b000-4000-8000-000000000001',v_tid,'G4-ROLLBACK-COURIER',true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $h3_legacy$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_state text;
BEGIN
  -- H3: legacy create path works at the rollback endpoint.
  v_res := public.create_sale_with_items(
    'eeee0001-b000-4000-8000-000000000001'::uuid,
    'courier'::delivery_kind,
    'ffee0001-b000-4000-8000-000000000001'::uuid,
    0,
    'cash'::payment_method,
    '[{"productId":"ddee0001-b000-4000-8000-000000000001","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  SELECT courier_state::text INTO v_state FROM orders WHERE id=v_oid;
  IF v_state <> 'pending' THEN
    RAISE EXCEPTION 'H3 FAIL: legacy courier create state=%', v_state;
  END IF;
END
$h3_legacy$;

DO $h2_data$
DECLARE v_bad int;
BEGIN
  SELECT COUNT(*) INTO v_bad
    FROM orders
   WHERE delivery='courier'
     AND customer_id IS NULL
     AND courier_state IN ('delivered_partial','delivered_none');
  IF v_bad <> 0 THEN
    RAISE EXCEPTION 'H2 FAIL: customer-less debt-creating courier rows=%', v_bad;
  END IF;
END
$h2_data$;

DO $done$ BEGIN
  RAISE NOTICE 'GATE4_ROLLBACK_GREEN: H1/H2/H3 rollback endpoint fingerprint passed';
END
$done$;

ROLLBACK;
