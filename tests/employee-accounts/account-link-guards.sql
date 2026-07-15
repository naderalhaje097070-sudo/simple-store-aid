-- Courier user_id must never be changed through direct table writes.
BEGIN;

SELECT set_config('mongezz.guard.tid', :tid, true);
SELECT set_config('mongezz.guard.owner', :owner, true);
SELECT set_config('mongezz.guard.staff_a', :staff_a, true);

INSERT INTO public.couriers(id, tenant_id, name, phone, is_active)
VALUES ('ec000003-0000-4000-8000-000000000001', :tid::uuid, 'EMPLOYEE-GUARD', '0944444444', true);

SELECT set_config('request.jwt.claims', json_build_object('sub', :owner, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $guards$
DECLARE
  v_blocked boolean;
  v_rows integer;
BEGIN
  v_blocked := false;
  BEGIN
    UPDATE public.couriers
       SET user_id = current_setting('mongezz.guard.staff_a')::uuid
     WHERE id = 'ec000003-0000-4000-8000-000000000001'::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_blocked := SQLERRM LIKE '%courier_account_rpc_required%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E6 FAIL: direct courier account link was allowed'; END IF;

  PERFORM public.link_courier_account(
    'ec000003-0000-4000-8000-000000000001'::uuid,
    'employee.a@mongezz.test'
  );

  v_blocked := false;
  BEGIN
    UPDATE public.couriers
       SET user_id = NULL
     WHERE id = 'ec000003-0000-4000-8000-000000000001'::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_blocked := SQLERRM LIKE '%courier_account_rpc_required%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E6 FAIL: direct courier account unlink was allowed'; END IF;

  v_blocked := false;
  BEGIN
    DELETE FROM public.couriers
     WHERE id = 'ec000003-0000-4000-8000-000000000001'::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_blocked := SQLERRM LIKE '%unlink_employee_before_delete%';
  END;
  IF NOT v_blocked THEN RAISE EXCEPTION 'E6 FAIL: linked courier was deleted'; END IF;

  PERFORM public.unlink_courier_account(
    'ec000003-0000-4000-8000-000000000001'::uuid,
    false
  );

  DELETE FROM public.couriers
   WHERE id = 'ec000003-0000-4000-8000-000000000001'::uuid;
  GET DIAGNOSTICS v_rows = ROW_COUNT;
  IF v_rows <> 1 THEN RAISE EXCEPTION 'E6 FAIL: unlinked courier could not be deleted'; END IF;

  RAISE NOTICE 'E6 OK: courier account links require link/unlink RPCs';
END $guards$;

ROLLBACK;
