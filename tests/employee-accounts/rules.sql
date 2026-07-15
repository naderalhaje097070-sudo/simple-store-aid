-- Mongezz employee-account regression suite.
-- All fixtures are transaction-local and rolled back.
\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config('mongezz.emp.tid', :tid, true);
SELECT set_config('mongezz.emp.owner', :owner, true);
SELECT set_config('mongezz.emp.staff_a', :staff_a, true);
SELECT set_config('mongezz.emp.staff_b', :staff_b, true);

INSERT INTO public.products(id, tenant_id, name, price, cost, stock, is_active)
VALUES ('ea000001-0000-4000-8000-000000000001', :tid::uuid, 'EMP-TEST-PRODUCT', 100, 60, 20, true);

INSERT INTO public.customers(id, tenant_id, name, phone)
VALUES ('ea000002-0000-4000-8000-000000000001', :tid::uuid, 'EMP-TEST-CUSTOMER', '0910000000');

INSERT INTO public.couriers(id, tenant_id, name, phone, is_active)
VALUES
  ('ea000003-0000-4000-8000-000000000001', :tid::uuid, 'EMPLOYEE-A', '0911111111', true),
  ('ea000003-0000-4000-8000-000000000002', :tid::uuid, 'EMPLOYEE-B', '0922222222', true);

-- Owner links two accounts and creates one assigned order for each employee.
SELECT set_config('request.jwt.claims', json_build_object('sub', :owner, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $owner_seed$
DECLARE
  v_order_a uuid;
  v_order_b uuid;
BEGIN
  PERFORM public.link_courier_account(
    'ea000003-0000-4000-8000-000000000001'::uuid,
    'employee.a@mongezz.test'
  );
  PERFORM public.link_courier_account(
    'ea000003-0000-4000-8000-000000000002'::uuid,
    'employee.b@mongezz.test'
  );

  v_order_a := (public.create_sale_with_items(
    'ea000002-0000-4000-8000-000000000001'::uuid,
    'courier'::public.delivery_kind,
    'ea000003-0000-4000-8000-000000000001'::uuid,
    0,
    'cash'::public.payment_method,
    '[{"productId":"ea000001-0000-4000-8000-000000000001","qty":1}]'::jsonb
  )->>'order_id')::uuid;

  v_order_b := (public.create_sale_with_items(
    'ea000002-0000-4000-8000-000000000001'::uuid,
    'courier'::public.delivery_kind,
    'ea000003-0000-4000-8000-000000000002'::uuid,
    0,
    'cash'::public.payment_method,
    '[{"productId":"ea000001-0000-4000-8000-000000000001","qty":1}]'::jsonb
  )->>'order_id')::uuid;

  PERFORM set_config('mongezz.emp.order_a', v_order_a::text, true);
  PERFORM set_config('mongezz.emp.order_b', v_order_b::text, true);
END $owner_seed$;

-- Employee A sees only A data and cannot bypass scoped RPCs or owner policies.
RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :staff_a, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $employee_a$
DECLARE
  v_count integer;
  v_rows integer;
  v_portal jsonb;
  v_blocked boolean;
BEGIN
  IF public.current_courier_id() <> 'ea000003-0000-4000-8000-000000000001'::uuid THEN
    RAISE EXCEPTION 'E1 FAIL: employee A courier mapping is wrong';
  END IF;

  SELECT COUNT(*) INTO v_count FROM public.orders;
  IF v_count <> 1 THEN RAISE EXCEPTION 'E1 FAIL: employee A sees % orders', v_count; END IF;
  SELECT COUNT(*) INTO v_count FROM public.order_items;
  IF v_count <> 1 THEN RAISE EXCEPTION 'E1 FAIL: employee A sees % order items', v_count; END IF;
  SELECT COUNT(*) INTO v_count FROM public.customers;
  IF v_count <> 1 THEN RAISE EXCEPTION 'E1 FAIL: employee A sees % customers', v_count; END IF;
  SELECT COUNT(*) INTO v_count FROM public.couriers;
  IF v_count <> 1 THEN RAISE EXCEPTION 'E1 FAIL: employee A sees % couriers', v_count; END IF;

  SELECT COUNT(*) INTO v_count FROM public.products;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E1 FAIL: employee can read products'; END IF;
  SELECT COUNT(*) INTO v_count FROM public.payments;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E1 FAIL: employee can read payments'; END IF;
  SELECT COUNT(*) INTO v_count FROM public.expenses;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E1 FAIL: employee can read expenses'; END IF;
  SELECT COUNT(*) INTO v_count FROM public.day_closes;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E1 FAIL: employee can read day closes'; END IF;

  v_portal := public.get_my_courier_portal();
  IF jsonb_array_length(v_portal->'orders') <> 1
     OR (v_portal->'orders'->0->>'id')::uuid <> current_setting('mongezz.emp.order_a')::uuid THEN
    RAISE EXCEPTION 'E1 FAIL: employee portal exposed the wrong order set';
  END IF;

  v_blocked := false;
  BEGIN
    PERFORM public.create_sale_with_items(
      NULL,
      'direct'::public.delivery_kind,
      NULL,
      100,
      'cash'::public.payment_method,
      '[{"productId":"ea000001-0000-4000-8000-000000000001","qty":1}]'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN
    v_blocked := SQLERRM LIKE '%forbidden_role%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee used owner sale RPC'; END IF;

  v_blocked := false;
  BEGIN
    UPDATE public.orders
       SET notes = 'UNAUTHORIZED'
     WHERE id = current_setting('mongezz.emp.order_a')::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee directly updated an order'; END IF;

  v_blocked := false;
  BEGIN
    INSERT INTO public.products(tenant_id, name, price, cost, stock)
    VALUES (current_setting('mongezz.emp.tid')::uuid, 'UNAUTHORIZED', 1, 1, 1);
  EXCEPTION WHEN OTHERS THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee directly inserted a product'; END IF;

  v_blocked := false;
  BEGIN
    INSERT INTO public.payments(tenant_id, kind, method, amount)
    VALUES (current_setting('mongezz.emp.tid')::uuid, 'sale', 'cash', 1);
  EXCEPTION WHEN OTHERS THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee directly inserted a payment'; END IF;

  -- An UPDATE rejected by RLS may affect zero rows without raising. Verify the row effect.
  UPDATE public.couriers
     SET name = 'UNAUTHORIZED'
   WHERE id = 'ea000003-0000-4000-8000-000000000001'::uuid;
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows <> 0 THEN RAISE EXCEPTION 'E1 FAIL: employee directly updated courier master data'; END IF;

  v_blocked := false;
  BEGIN
    UPDATE public.profiles
       SET tenant_id = NULL,
           disabled_at = NULL
     WHERE id = current_setting('mongezz.emp.staff_a')::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_blocked := true;
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee changed protected profile fields'; END IF;

  v_blocked := false;
  BEGIN
    PERFORM public.courier_update_my_order_state(
      current_setting('mongezz.emp.order_b')::uuid,
      'delivered_full',
      NULL
    );
  EXCEPTION WHEN OTHERS THEN
    v_blocked := SQLERRM LIKE '%order_not_assigned_to_employee%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee A updated employee B order'; END IF;

  PERFORM public.courier_update_my_order_state(
    current_setting('mongezz.emp.order_a')::uuid,
    'delivered_partial',
    40
  );

  v_blocked := false;
  BEGIN
    PERFORM public.courier_update_my_order_state(
      current_setting('mongezz.emp.order_a')::uuid,
      'delivered_none',
      NULL
    );
  EXCEPTION WHEN OTHERS THEN
    v_blocked := SQLERRM LIKE '%order_state_finalized%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E1 FAIL: employee rewrote a finalized delivery state'; END IF;

  v_portal := public.get_my_courier_portal();
  IF (v_portal->>'custody')::numeric <> 40 THEN
    RAISE EXCEPTION 'E1 FAIL: employee A custody is %', v_portal->>'custody';
  END IF;

  PERFORM public.request_my_custody_settlement();
  PERFORM public.request_my_custody_settlement();
  SELECT COUNT(*) INTO v_count
    FROM public.employee_settlement_requests
   WHERE status = 'pending';
  IF v_count <> 1 THEN RAISE EXCEPTION 'E1 FAIL: duplicate pending settlement requests = %', v_count; END IF;

  RAISE NOTICE 'E1 OK: employee A is isolated and cannot bypass owner controls';
END $employee_a$;

-- Employee B cannot see A order or A custody.
RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :staff_b, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $employee_b$
DECLARE
  v_count integer;
  v_portal jsonb;
BEGIN
  SELECT COUNT(*) INTO v_count FROM public.orders;
  IF v_count <> 1 THEN RAISE EXCEPTION 'E2 FAIL: employee B sees % orders', v_count; END IF;

  v_portal := public.get_my_courier_portal();
  IF (v_portal->>'custody')::numeric <> 0 THEN
    RAISE EXCEPTION 'E2 FAIL: employee B sees A custody';
  END IF;
  IF (v_portal->'orders'->0->>'id')::uuid <> current_setting('mongezz.emp.order_b')::uuid THEN
    RAISE EXCEPTION 'E2 FAIL: employee B portal returned another employee order';
  END IF;

  RAISE NOTICE 'E2 OK: employee B cannot see employee A data';
END $employee_b$;

-- Owner must use explicit unlink/relink and settle custody before approving the request.
RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :owner, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $owner_review$
DECLARE
  v_accounts jsonb;
  v_request_id uuid;
  v_blocked boolean;
  v_paid numeric;
  v_collected numeric;
  v_delivery text;
  v_courier uuid;
  v_payment_count integer;
  v_payment_amount numeric;
BEGIN
  v_accounts := public.list_courier_accounts();
  IF jsonb_array_length(v_accounts) <> 2 THEN
    RAISE EXCEPTION 'E3 FAIL: owner account list count is %', jsonb_array_length(v_accounts);
  END IF;

  v_blocked := false;
  BEGIN
    UPDATE public.couriers
       SET user_id = current_setting('mongezz.emp.staff_b')::uuid
     WHERE id = 'ea000003-0000-4000-8000-000000000001'::uuid;
  EXCEPTION WHEN OTHERS THEN
    v_blocked := SQLERRM LIKE '%courier_already_has_account%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E3 FAIL: linked account was silently replaced'; END IF;

  SELECT id INTO v_request_id
    FROM public.employee_settlement_requests
   WHERE courier_id = 'ea000003-0000-4000-8000-000000000001'::uuid
     AND status = 'pending';

  v_blocked := false;
  BEGIN
    PERFORM public.resolve_courier_settlement_request(v_request_id, 'approved');
  EXCEPTION WHEN OTHERS THEN
    v_blocked := SQLERRM LIKE '%settle_courier_first%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E3 FAIL: request approved while custody existed'; END IF;

  PERFORM public.settle_courier_orders(
    'ea000003-0000-4000-8000-000000000001'::uuid,
    ARRAY[current_setting('mongezz.emp.order_a')::uuid]
  );
  PERFORM public.resolve_courier_settlement_request(v_request_id, 'approved');

  SELECT paid, collected_by_courier, delivery::text, courier_id
    INTO v_paid, v_collected, v_delivery, v_courier
    FROM public.orders
   WHERE id = current_setting('mongezz.emp.order_a')::uuid;

  SELECT COUNT(*), COALESCE(SUM(amount), 0)
    INTO v_payment_count, v_payment_amount
    FROM public.payments
   WHERE order_id = current_setting('mongezz.emp.order_a')::uuid
     AND kind = 'courier_settlement';

  IF v_paid <> 40 OR v_collected <> 0 OR v_delivery <> 'direct' OR v_courier IS NOT NULL THEN
    RAISE EXCEPTION 'E3 FAIL: invalid post-settlement state';
  END IF;
  IF v_payment_count <> 1 OR v_payment_amount <> 40 THEN
    RAISE EXCEPTION 'E3 FAIL: settlement payment count=% amount=%', v_payment_count, v_payment_amount;
  END IF;

  PERFORM public.unlink_courier_account(
    'ea000003-0000-4000-8000-000000000001'::uuid,
    true
  );

  RAISE NOTICE 'E3 OK: owner settlement records cash exactly once';
END $owner_review$;

-- Disabled employee loses identity, portal, and mutation access.
RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :staff_a, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $disabled_employee$
DECLARE
  v_portal_blocked boolean := false;
  v_mutation_blocked boolean := false;
BEGIN
  IF public.current_courier_id() IS NOT NULL THEN
    RAISE EXCEPTION 'E4 FAIL: disabled employee still has courier identity';
  END IF;

  BEGIN
    PERFORM public.get_my_courier_portal();
  EXCEPTION WHEN OTHERS THEN
    v_portal_blocked := SQLERRM LIKE '%employee_account_disabled%';
  END;

  BEGIN
    PERFORM public.courier_update_my_order_state(
      current_setting('mongezz.emp.order_b')::uuid,
      'delivered_none',
      NULL
    );
  EXCEPTION WHEN OTHERS THEN
    v_mutation_blocked := SQLERRM LIKE '%employee_account_disabled%';
  END;

  IF NOT v_portal_blocked OR NOT v_mutation_blocked THEN
    RAISE EXCEPTION 'E4 FAIL: disabled employee retained portal or mutation access';
  END IF;

  RAISE NOTICE 'E4 OK: disabled employee access is blocked';
END $disabled_employee$;

RESET ROLE;
DO $done$ BEGIN RAISE NOTICE '====== ALL EMPLOYEE ACCOUNT RULES PASSED ======'; END $done$;
ROLLBACK;
