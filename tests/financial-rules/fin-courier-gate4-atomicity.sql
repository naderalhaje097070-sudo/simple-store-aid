-- FIN-COURIER-001 Gate 4 — D-T8 forced-failure atomicity probe
-- Injects an AFTER UPDATE failure on the target order and proves the v2 RPC
-- cannot leave state/customer/custody partially persisted.

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
  ) IS NULL OR to_regprocedure(
    'public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)'
  ) IS NULL THEN
    RAISE EXCEPTION 'GATE4_ATOMICITY_EXPECTED_RED: PR-A v2 RPCs are missing';
  END IF;
END
$prereq$;

DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active)
  VALUES ('ddbb0001-8000-4000-8000-000000000001', v_tid, 'G4-ATOMICITY-P1', 100, 60, 10, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eebb0001-8000-4000-8000-000000000001', v_tid, 'G4-ATOMICITY-C1')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffbb0001-8000-4000-8000-000000000001', v_tid, 'G4-ATOMICITY-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

CREATE OR REPLACE FUNCTION pg_temp.g4_force_order_failure()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.id = current_setting('mongezz.g4_fault_oid', true)::uuid
     AND NEW.courier_state = 'delivered_partial' THEN
    RAISE EXCEPTION 'g4_forced_after_update';
  END IF;
  RETURN NEW;
END
$$;

CREATE TRIGGER gate4_force_order_failure
AFTER UPDATE ON public.orders
FOR EACH ROW EXECUTE FUNCTION pg_temp.g4_force_order_failure();

DO $atomicity$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_ok bool := false;
  v_state text;
  v_custody numeric;
  v_customer uuid;
BEGIN
  v_res := public.create_sale_with_items_v2(
    NULL,
    'courier'::delivery_kind,
    'ffbb0001-8000-4000-8000-000000000001'::uuid,
    0,
    'cash'::payment_method,
    '[{"productId":"ddbb0001-8000-4000-8000-000000000001","qty":1}]'::jsonb,
    'pending'::courier_state
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM set_config('mongezz.g4_fault_oid', v_oid::text, true);

  BEGIN
    PERFORM public.update_courier_outcome_v2(
      v_oid,
      'delivered_partial'::courier_state,
      40,
      'eebb0001-8000-4000-8000-000000000001'::uuid
    );
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%g4_forced_after_update%' THEN v_ok := true; END IF;
  END;

  IF NOT v_ok THEN
    RAISE EXCEPTION 'D-T8 FAIL: injected post-update failure did not abort RPC';
  END IF;

  SELECT courier_state::text, collected_by_courier, customer_id
    INTO v_state, v_custody, v_customer
    FROM orders WHERE id = v_oid;

  IF v_state <> 'pending' OR v_custody <> 0 OR v_customer IS NOT NULL THEN
    RAISE EXCEPTION 'D-T8 FAIL: partial write survived state=% custody=% customer=%',
      v_state, v_custody, v_customer;
  END IF;

  RAISE NOTICE 'GATE4_ATOMICITY_GREEN: D-T8 forced failure rolled back every order-field change';
END
$atomicity$;

ROLLBACK;
