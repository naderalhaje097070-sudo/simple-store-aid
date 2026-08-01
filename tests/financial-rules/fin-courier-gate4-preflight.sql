-- FIN-COURIER-001 Gate 4 — historical-data preflight / deferred VALIDATE (C-PF1/C-PF2)
-- Requires PR-A replacement CHECK to exist as NOT VALID.

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config('mongezz.test_tid', :tid, true);

DO $prereq$
DECLARE
  v_validated bool;
BEGIN
  SELECT convalidated
    INTO v_validated
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname = 'orders_customer_required_when_debt';

  IF NOT FOUND THEN
    RAISE EXCEPTION 'GATE4_PREFLIGHT_EXPECTED_RED: replacement CHECK is missing';
  END IF;
  IF v_validated THEN
    RAISE EXCEPTION 'C-PF2 FAIL: PR-A constraint is already validated; validation must be deferred';
  END IF;
END
$prereq$;

DO $seed$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffdd0001-a000-4000-8000-000000000001', v_tid, 'G4-PREFLIGHT-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

DO $preflight$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
  v_def text;
  v_count int;
  v_ok bool := false;
BEGIN
  SELECT pg_get_constraintdef(oid)
    INTO v_def
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname = 'orders_customer_required_when_debt';

  -- Seed one representative legacy violation. New writes cannot normally create
  -- this shape, so the rollback-only test temporarily removes/re-adds the same
  -- approved CHECK as NOT VALID.
  EXECUTE 'ALTER TABLE public.orders DROP CONSTRAINT orders_customer_required_when_debt';

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'aadd0001-a000-4000-8000-000000000001', v_tid, 100, 0, 'debt', 'courier',
    'ffdd0001-a000-4000-8000-000000000001', 'delivered_partial', 40, NULL
  );

  v_def := regexp_replace(v_def, '\s+NOT VALID\s*$', '', 'i');
  EXECUTE format(
    'ALTER TABLE public.orders ADD CONSTRAINT orders_customer_required_when_debt %s NOT VALID',
    v_def
  );

  -- C-PF1: approved preflight must find the deliberately violating row.
  SELECT COUNT(*) INTO v_count
  FROM public.orders
  WHERE customer_id IS NULL
    AND NOT (
         (courier_state IS NOT NULL AND courier_state = 'returned')
      OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
      OR (delivery = 'courier' AND courier_state IS NOT NULL
            AND courier_state IN ('pending','delivered_full'))
    );
  IF v_count <> 1 THEN
    RAISE EXCEPTION 'C-PF1 FAIL: preflight expected one seeded violation, got %', v_count;
  END IF;

  -- C-PF2: blind validation while a violation exists must fail.
  BEGIN
    ALTER TABLE public.orders VALIDATE CONSTRAINT orders_customer_required_when_debt;
  EXCEPTION WHEN check_violation THEN
    v_ok := true;
  END;
  IF NOT v_ok THEN
    RAISE EXCEPTION 'C-PF2 FAIL: VALIDATE succeeded while violating historical row existed';
  END IF;

  DELETE FROM orders WHERE id = 'aadd0001-a000-4000-8000-000000000001';

  -- Preflight must now be zero, then controlled validation may succeed.
  SELECT COUNT(*) INTO v_count
  FROM public.orders
  WHERE customer_id IS NULL
    AND NOT (
         (courier_state IS NOT NULL AND courier_state = 'returned')
      OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
      OR (delivery = 'courier' AND courier_state IS NOT NULL
            AND courier_state IN ('pending','delivered_full'))
    );
  IF v_count <> 0 THEN
    RAISE EXCEPTION 'C-PF2 FAIL: preflight still has % violation(s) after cleanup', v_count;
  END IF;

  ALTER TABLE public.orders VALIDATE CONSTRAINT orders_customer_required_when_debt;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conrelid = 'public.orders'::regclass
       AND conname = 'orders_customer_required_when_debt'
       AND convalidated
  ) THEN
    RAISE EXCEPTION 'C-PF2 FAIL: controlled validation did not set convalidated=true';
  END IF;

  RAISE NOTICE 'GATE4_PREFLIGHT_GREEN: C-PF1/C-PF2 detection and deferred validation passed';
END
$preflight$;

ROLLBACK;
