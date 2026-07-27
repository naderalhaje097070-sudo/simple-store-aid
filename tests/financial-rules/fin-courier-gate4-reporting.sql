-- FIN-COURIER-001 Gate 4 — PR-B outcome-aware reporting safety net (G1..G8)
-- Runs after PR-A prerequisites exist. On the current pre-implementation baseline
-- it is expected RED because the approved PR-A contract is not present yet.

\set QUIET on
SET client_min_messages TO NOTICE;
BEGIN;

SELECT set_config(
  'request.jwt.claims',
  json_build_object('sub', :uid, 'role', 'authenticated')::text,
  true
);
SELECT set_config('mongezz.test_tid', :tid, true);

CREATE TEMP TABLE gate4_reporting_failures (
  test_id text PRIMARY KEY,
  detail text NOT NULL
) ON COMMIT DROP;

CREATE OR REPLACE FUNCTION pg_temp.r_fail(p_id text, p_detail text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO gate4_reporting_failures(test_id, detail)
  VALUES (p_id, p_detail)
  ON CONFLICT (test_id) DO UPDATE SET detail = EXCLUDED.detail;
END;
$$;

DO $prereq$
DECLARE
  v_ready bool;
BEGIN
  SELECT
    to_regprocedure(
      'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
    ) IS NOT NULL
    AND EXISTS (
      SELECT 1 FROM pg_constraint
       WHERE conrelid = 'public.orders'::regclass
         AND conname = 'orders_customer_required_when_debt'
    )
  INTO v_ready;

  IF NOT v_ready THEN
    PERFORM pg_temp.r_fail('G-PREQ', 'PR-A schema/RPC contract is not present');
  END IF;
END
$prereq$;

DO $reporting$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
  v_ready bool;
  v_overview jsonb;
  v_overview_debt numeric;
  v_tenant_debt numeric;
  v_bad bigint;
  v_expected numeric := 160;
  v_close jsonb;
  v_close_status text;
BEGIN
  SELECT
    to_regprocedure(
      'public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)'
    ) IS NOT NULL
    AND EXISTS (
      SELECT 1 FROM pg_constraint
       WHERE conrelid = 'public.orders'::regclass
         AND conname = 'orders_customer_required_when_debt'
    )
  INTO v_ready;
  IF NOT v_ready THEN RETURN; END IF;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eeee5555-3000-0000-0000-000000000001', v_tid, 'G4-REPORT-CUSTOMER')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffff6666-3000-0000-0000-000000000001', v_tid, 'G4-REPORT-COURIER', true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'ab000001-3000-4000-8000-000000000001', v_tid, 100, 0, 'debt', 'courier',
    'ffff6666-3000-0000-0000-000000000001', 'pending', 0, NULL
  );

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'ab000002-3000-4000-8000-000000000002', v_tid, 100, 0, 'debt', 'courier',
    'ffff6666-3000-0000-0000-000000000001', 'delivered_full', 100, NULL
  );

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'ab000003-3000-4000-8000-000000000003', v_tid, 100, 0, 'debt', 'courier',
    'ffff6666-3000-0000-0000-000000000001', 'delivered_partial', 40,
    'eeee5555-3000-0000-0000-000000000001'
  );

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'ab000004-3000-4000-8000-000000000004', v_tid, 100, 0, 'debt', 'courier',
    'ffff6666-3000-0000-0000-000000000001', 'delivered_none', 0,
    'eeee5555-3000-0000-0000-000000000001'
  );

  SELECT COALESCE(SUM(affected_count), 0)
    INTO v_bad
    FROM public.get_platform_financial_health()
   WHERE check_key IN ('courier_missing_refs', 'debt_without_customer');
  IF v_bad <> 0 THEN
    PERFORM pg_temp.r_fail('G1', format('valid mix reported affected_count=%s', v_bad));
  END IF;

  IF EXISTS (
    SELECT 1
      FROM jsonb_array_elements(
        COALESCE(public.get_platform_financial_health_rows('courier_missing_refs', 100), '[]'::jsonb)
      ) r
     WHERE r->>'id' IN (
       'ab000001-3000-4000-8000-000000000001',
       'ab000002-3000-4000-8000-000000000002'
     )
  ) THEN
    PERFORM pg_temp.r_fail('G3C', 'courier_missing_refs detail contains valid customer-less courier row');
  END IF;

  IF EXISTS (
    SELECT 1
      FROM jsonb_array_elements(
        COALESCE(public.get_platform_financial_health_rows('debt_without_customer', 100), '[]'::jsonb)
      ) r
     WHERE r->>'id' IN (
       'ab000001-3000-4000-8000-000000000001',
       'ab000002-3000-4000-8000-000000000002'
     )
  ) THEN
    PERFORM pg_temp.r_fail('G3D', 'debt_without_customer detail contains valid customer-less courier row');
  END IF;

  v_overview := public.get_platform_admin_overview();
  v_overview_debt := COALESCE((v_overview->>'open_customer_debts')::numeric, 0);
  IF v_overview_debt <> v_expected THEN
    PERFORM pg_temp.r_fail('G4/G7', format('overview debt=%s expected=%s', v_overview_debt, v_expected));
  END IF;

  SELECT open_debts
    INTO v_tenant_debt
    FROM public.get_platform_tenants_health()
   WHERE tenant_id = v_tid;
  IF COALESCE(v_tenant_debt, 0) <> v_expected THEN
    PERFORM pg_temp.r_fail('G5/G8', format('tenant debt=%s expected=%s', v_tenant_debt, v_expected));
  END IF;

  BEGIN
    v_close := public.close_day('FIN-COURIER Gate 4 reporting reconciliation');
    SELECT status
      INTO v_close_status
      FROM public.get_platform_day_close_health(100)
     WHERE tenant_id = v_tid
     ORDER BY created_at DESC
     LIMIT 1;
    IF v_close_status IS DISTINCT FROM 'Matches' THEN
      PERFORM pg_temp.r_fail('G6', format('platform day-close status=%s close=%s', v_close_status, v_close));
    END IF;
  EXCEPTION WHEN OTHERS THEN
    PERFORM pg_temp.r_fail('G6', SQLERRM);
  END;
END
$reporting$;

-- G2: force one genuinely corrupt debt-carrying courier row by temporarily
-- removing/re-adding the approved replacement CHECK as NOT VALID.
DO $g2_corruption$
DECLARE
  v_tid uuid := current_setting('mongezz.test_tid')::uuid;
  v_def text;
  v_health bigint;
  v_ready bool;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM pg_constraint
     WHERE conrelid = 'public.orders'::regclass
       AND conname = 'orders_customer_required_when_debt'
  ) INTO v_ready;
  IF NOT v_ready THEN RETURN; END IF;

  SELECT pg_get_constraintdef(oid)
    INTO v_def
    FROM pg_constraint
   WHERE conrelid = 'public.orders'::regclass
     AND conname = 'orders_customer_required_when_debt';

  EXECUTE 'ALTER TABLE public.orders DROP CONSTRAINT orders_customer_required_when_debt';

  INSERT INTO orders(
    id, tenant_id, total, paid, status, delivery,
    courier_id, courier_state, collected_by_courier, customer_id
  ) VALUES (
    'ab000099-3000-4000-8000-000000000099', v_tid, 100, 0, 'debt', 'courier',
    'ffff6666-3000-0000-0000-000000000001', 'delivered_partial', 40, NULL
  );

  -- pg_get_constraintdef() is not relied on to preserve validation state.
  -- Normalize and re-add explicitly NOT VALID so the deliberately corrupt
  -- historical row can remain present for the health check.
  v_def := regexp_replace(v_def, '\s+NOT VALID\s*$', '', 'i');
  EXECUTE format(
    'ALTER TABLE public.orders ADD CONSTRAINT orders_customer_required_when_debt %s NOT VALID',
    v_def
  );

  SELECT COALESCE(SUM(affected_count), 0)
    INTO v_health
    FROM public.get_platform_financial_health()
   WHERE check_key IN ('courier_missing_refs', 'debt_without_customer');

  IF v_health < 1 THEN
    PERFORM pg_temp.r_fail('G2', 'genuinely corrupt customer-less debt row was not detected');
  END IF;

  IF NOT EXISTS (
    SELECT 1
      FROM jsonb_array_elements(
        COALESCE(public.get_platform_financial_health_rows('debt_without_customer', 100), '[]'::jsonb)
      ) r
     WHERE r->>'id' = 'ab000099-3000-4000-8000-000000000099'
  ) THEN
    PERFORM pg_temp.r_fail('G2D', 'debt_without_customer detail omitted forced corrupt row');
  END IF;
END
$g2_corruption$;

DO $done$
DECLARE
  v_count int;
  v_detail text;
BEGIN
  SELECT COUNT(*) INTO v_count FROM gate4_reporting_failures;
  IF v_count > 0 THEN
    SELECT string_agg(test_id || '=' || detail, ' | ' ORDER BY test_id)
      INTO v_detail FROM gate4_reporting_failures;
    RAISE EXCEPTION 'GATE4_REPORT_EXPECTED_RED: % gap(s): %', v_count, v_detail;
  END IF;
  RAISE NOTICE 'GATE4_REPORT_GREEN: G1..G8 passed';
END
$done$;

ROLLBACK;
