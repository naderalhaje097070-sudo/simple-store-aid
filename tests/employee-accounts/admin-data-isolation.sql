-- Staff must not read owner billing, subscription, or financial audit rows.
BEGIN;

INSERT INTO public.couriers(id, tenant_id, name, phone, is_active)
VALUES ('ed000003-0000-4000-8000-000000000001', :tid::uuid, 'EMPLOYEE-ADMIN-ISOLATION', '0955555555', true);

INSERT INTO public.subscriptions(
  tenant_id,
  user_id,
  paddle_subscription_id,
  paddle_customer_id,
  product_id,
  price_id,
  status,
  environment
)
VALUES (
  :tid::uuid,
  :owner::uuid,
  'sub_employee_isolation_test',
  'ctm_employee_isolation_test',
  'pro_employee_isolation_test',
  'pri_employee_isolation_test',
  'active',
  'sandbox'
);

INSERT INTO public.financial_audit_log(
  tenant_id, user_id, action, entity_type, before, after
)
VALUES (
  :tid::uuid,
  :owner::uuid,
  'TEST',
  'employee_admin_isolation',
  '{}'::jsonb,
  '{}'::jsonb
);

SELECT set_config('request.jwt.claims', json_build_object('sub', :owner, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;
SELECT public.link_courier_account(
  'ed000003-0000-4000-8000-000000000001'::uuid,
  'employee.a@mongezz.test'
);

RESET ROLE;
SELECT set_config('request.jwt.claims', json_build_object('sub', :staff_a, 'role', 'authenticated')::text, true);
SET LOCAL ROLE authenticated;

DO $admin_isolation$
DECLARE
  v_count integer;
  v_portal jsonb;
BEGIN
  SELECT COUNT(*) INTO v_count FROM public.tenants;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E7 FAIL: employee can read tenant billing metadata'; END IF;

  SELECT COUNT(*) INTO v_count FROM public.subscriptions;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E7 FAIL: employee can read subscription data'; END IF;

  SELECT COUNT(*) INTO v_count FROM public.financial_audit_log;
  IF v_count <> 0 THEN RAISE EXCEPTION 'E7 FAIL: employee can read financial audit data'; END IF;

  v_portal := public.get_my_courier_portal();
  IF COALESCE(v_portal->>'tenant_name', '') = '' THEN
    RAISE EXCEPTION 'E7 FAIL: scoped portal lost the tenant display name';
  END IF;

  RAISE NOTICE 'E7 OK: owner billing and audit data remain private';
END $admin_isolation$;

ROLLBACK;
