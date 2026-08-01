-- FIN-COURIER-001 Gate 4 — F2 pre/post migration financial read-model snapshot
-- This is GREEN on the approved baseline and must remain GREEN unchanged after PR-A.

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
  INSERT INTO customers(id,tenant_id,name)
  VALUES ('eeff0001-c000-4000-8000-000000000001',v_tid,'G4-F2-CUSTOMER')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id,tenant_id,name,is_active)
  VALUES ('ffff0001-c000-4000-8000-000000000001',v_tid,'G4-F2-COURIER',true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO orders(
    id,tenant_id,total,paid,status,delivery,courier_id,courier_state,
    collected_by_courier,customer_id,created_at
  ) VALUES
    ('ac000001-c000-4000-8000-000000000001',v_tid,100,0,'debt','courier','ffff0001-c000-4000-8000-000000000001','pending',0,'eeff0001-c000-4000-8000-000000000001',now()),
    ('ac000002-c000-4000-8000-000000000002',v_tid,100,0,'debt','courier','ffff0001-c000-4000-8000-000000000001','delivered_full',100,'eeff0001-c000-4000-8000-000000000001',now()),
    ('ac000003-c000-4000-8000-000000000003',v_tid,100,0,'debt','courier','ffff0001-c000-4000-8000-000000000001','delivered_partial',40,'eeff0001-c000-4000-8000-000000000001',now()),
    ('ac000004-c000-4000-8000-000000000004',v_tid,100,0,'debt','courier','ffff0001-c000-4000-8000-000000000001','delivered_none',0,'eeff0001-c000-4000-8000-000000000001',now()),
    ('ac000005-c000-4000-8000-000000000005',v_tid,100,0,'debt','direct',NULL,'returned',0,'eeff0001-c000-4000-8000-000000000001',now())
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $snapshot$
DECLARE
  v_debt numeric;
  v_custody numeric;
  v_close_debt numeric;
  v_close_custody numeric;
  v_close jsonb;
BEGIN
  SELECT
    SUM(CASE
      WHEN courier_state='returned' THEN 0
      WHEN delivery='direct' OR courier_id IS NULL THEN GREATEST(total-paid,0)
      WHEN delivery='courier' AND courier_state='delivered_none' THEN total
      WHEN delivery='courier' AND courier_state='delivered_partial' THEN GREATEST(total-collected_by_courier,0)
      ELSE 0
    END),
    SUM(CASE
      WHEN delivery='courier' AND courier_state IN ('delivered_partial','delivered_full')
      THEN collected_by_courier ELSE 0 END)
  INTO v_debt, v_custody
  FROM orders
  WHERE id IN (
    'ac000001-c000-4000-8000-000000000001',
    'ac000002-c000-4000-8000-000000000002',
    'ac000003-c000-4000-8000-000000000003',
    'ac000004-c000-4000-8000-000000000004',
    'ac000005-c000-4000-8000-000000000005'
  );

  IF v_debt <> 160 OR v_custody <> 140 THEN
    RAISE EXCEPTION 'F2 FAIL canonical snapshot debt=% custody=% expected=160/140', v_debt, v_custody;
  END IF;

  v_close := public.close_day('FIN-COURIER Gate 4 F2 snapshot');
  SELECT customer_debts, unsettled_custody
    INTO v_close_debt, v_close_custody
    FROM day_closes
   WHERE tenant_id = current_setting('mongezz.test_tid')::uuid
   ORDER BY created_at DESC
   LIMIT 1;

  IF v_close_debt <> 160 OR v_close_custody <> 140 THEN
    RAISE EXCEPTION 'F2 FAIL close_day snapshot debt=% custody=% expected=160/140 close=%',
      v_close_debt, v_close_custody, v_close;
  END IF;

  RAISE NOTICE 'GATE4_F2_GREEN: five-state read-model snapshot debt=160 custody=140';
END
$snapshot$;

ROLLBACK;
