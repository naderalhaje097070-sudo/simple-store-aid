-- A linked employee must not escape into a new tenant or alter access fields.
BEGIN;

INSERT INTO public.couriers(id, tenant_id, name, phone, is_active)
VALUES ('eb000003-0000-4000-8000-000000000001', :tid::uuid, 'EMPLOYEE-ESCAPE', '0933333333', true);

SELECT set_config('request.jwt.claims', json_build_object('sub', :owner, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;
SELECT public.link_courier_account(
  'eb000003-0000-4000-8000-000000000001'::uuid,
  'employee.a@mongezz.test'
);

RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :staff_a, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $employee_escape$
DECLARE
  v_tenant_blocked boolean := false;
  v_profile_blocked boolean := false;
BEGIN
  BEGIN
    INSERT INTO public.tenants(name, owner_user_id)
    VALUES ('UNAUTHORIZED EMPLOYEE TENANT', :staff_a::uuid);
  EXCEPTION WHEN OTHERS THEN
    v_tenant_blocked := true;
  END;

  BEGIN
    UPDATE public.profiles
       SET tenant_id = NULL,
           disabled_at = NULL
     WHERE id = :staff_a::uuid;
  EXCEPTION WHEN insufficient_privilege THEN
    v_profile_blocked := true;
  END;

  IF NOT v_tenant_blocked THEN
    RAISE EXCEPTION 'E5 FAIL: linked employee created a second tenant';
  END IF;
  IF NOT v_profile_blocked THEN
    RAISE EXCEPTION 'E5 FAIL: linked employee changed protected profile fields';
  END IF;

  RAISE NOTICE 'E5 OK: tenant escape and protected profile changes are blocked';
END $employee_escape$;

ROLLBACK;
