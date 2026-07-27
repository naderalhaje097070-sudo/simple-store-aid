-- FIN-COURIER-001 Gate 4 — backward compatibility safety net (F1/F1a/F1b/F3)
-- Safe legacy flows must delegate to the canonical v2 result; unsafe legacy
-- transitions are intentionally rejected.

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
    RAISE EXCEPTION 'GATE4_COMPAT_EXPECTED_RED: PR-A v2 RPCs are missing';
  END IF;
END
$prereq$;

DO $seed$
DECLARE v_tid uuid := current_setting('mongezz.test_tid')::uuid;
BEGIN
  INSERT INTO products(id, tenant_id, name, price, cost, stock, is_active) VALUES
    ('ddcc0001-9000-4000-8000-000000000001', v_tid, 'G4-COMPAT-P1', 100, 60, 40, true),
    ('ddcc0002-9000-4000-8000-000000000002', v_tid, 'G4-COMPAT-P2', 100, 60, 40, true),
    ('ddcc0003-9000-4000-8000-000000000003', v_tid, 'G4-COMPAT-P3', 100, 60, 40, true)
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO customers(id, tenant_id, name)
  VALUES ('eecc0001-9000-4000-8000-000000000001', v_tid, 'G4-COMPAT-C1')
  ON CONFLICT (id) DO NOTHING;

  INSERT INTO couriers(id, tenant_id, name, is_active)
  VALUES ('ffcc0001-9000-4000-8000-000000000001', v_tid, 'G4-COMPAT-COURIER', true)
  ON CONFLICT (id) DO NOTHING;
END
$seed$;

CREATE OR REPLACE FUNCTION pg_temp.assert_equivalent(p_old uuid, p_new uuid, p_case text)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  a record;
  b record;
  pa jsonb;
  pb jsonb;
BEGIN
  SELECT paid, total, delivery::text, courier_state::text, collected_by_courier,
         customer_id, courier_id, status::text
    INTO a FROM orders WHERE id=p_old;
  SELECT paid, total, delivery::text, courier_state::text, collected_by_courier,
         customer_id, courier_id, status::text
    INTO b FROM orders WHERE id=p_new;

  -- Compare the financial payment effect, not merely row counts. IDs/timestamps
  -- are intentionally excluded because equivalent calls legitimately create
  -- distinct records at different instants.
  SELECT COALESCE(
           jsonb_agg(payment_shape ORDER BY payment_shape::text),
           '[]'::jsonb
         )
    INTO pa
    FROM (
      SELECT jsonb_build_object(
        'kind', kind::text,
        'method', method::text,
        'amount', amount,
        'customer_id', customer_id,
        'courier_id', courier_id
      ) AS payment_shape
      FROM payments
      WHERE order_id=p_old
    ) q;

  SELECT COALESCE(
           jsonb_agg(payment_shape ORDER BY payment_shape::text),
           '[]'::jsonb
         )
    INTO pb
    FROM (
      SELECT jsonb_build_object(
        'kind', kind::text,
        'method', method::text,
        'amount', amount,
        'customer_id', customer_id,
        'courier_id', courier_id
      ) AS payment_shape
      FROM payments
      WHERE order_id=p_new
    ) q;

  IF a.paid IS DISTINCT FROM b.paid
     OR a.total IS DISTINCT FROM b.total
     OR a.delivery IS DISTINCT FROM b.delivery
     OR a.courier_state IS DISTINCT FROM b.courier_state
     OR a.collected_by_courier IS DISTINCT FROM b.collected_by_courier
     OR a.customer_id IS DISTINCT FROM b.customer_id
     OR a.courier_id IS DISTINCT FROM b.courier_id
     OR a.status IS DISTINCT FROM b.status
     OR pa IS DISTINCT FROM pb THEN
    RAISE EXCEPTION 'F1 FAIL %: legacy and v2 differ old=% new=% payments_old=% payments_new=%',
      p_case, row_to_json(a), row_to_json(b), pa, pb;
  END IF;
END
$$;

DO $f1$
DECLARE
  o jsonb;
  n jsonb;
BEGIN
  -- Direct fully paid, customer optional.
  o := public.create_sale_with_items(
    NULL,'direct'::delivery_kind,NULL,100,'cash'::payment_method,
    '[{"productId":"ddcc0001-9000-4000-8000-000000000001","qty":1}]'::jsonb
  );
  n := public.create_sale_with_items_v2(
    NULL,'direct'::delivery_kind,NULL,100,'cash'::payment_method,
    '[{"productId":"ddcc0001-9000-4000-8000-000000000001","qty":1}]'::jsonb,
    NULL::courier_state
  );
  PERFORM pg_temp.assert_equivalent((o->>'order_id')::uuid,(n->>'order_id')::uuid,'direct_full');

  -- Legacy courier paid=0 maps to pending.
  o := public.create_sale_with_items(
    'eecc0001-9000-4000-8000-000000000001','courier'::delivery_kind,
    'ffcc0001-9000-4000-8000-000000000001',0,'cash'::payment_method,
    '[{"productId":"ddcc0002-9000-4000-8000-000000000002","qty":1}]'::jsonb
  );
  n := public.create_sale_with_items_v2(
    'eecc0001-9000-4000-8000-000000000001','courier'::delivery_kind,
    'ffcc0001-9000-4000-8000-000000000001',0,'cash'::payment_method,
    '[{"productId":"ddcc0002-9000-4000-8000-000000000002","qty":1}]'::jsonb,
    'pending'::courier_state
  );
  PERFORM pg_temp.assert_equivalent((o->>'order_id')::uuid,(n->>'order_id')::uuid,'courier_pending');

  -- Legacy partial collection maps to delivered_partial.
  o := public.create_sale_with_items(
    'eecc0001-9000-4000-8000-000000000001','courier'::delivery_kind,
    'ffcc0001-9000-4000-8000-000000000001',40,'cash'::payment_method,
    '[{"productId":"ddcc0003-9000-4000-8000-000000000003","qty":1}]'::jsonb
  );
  n := public.create_sale_with_items_v2(
    'eecc0001-9000-4000-8000-000000000001','courier'::delivery_kind,
    'ffcc0001-9000-4000-8000-000000000001',40,'cash'::payment_method,
    '[{"productId":"ddcc0003-9000-4000-8000-000000000003","qty":1}]'::jsonb,
    'delivered_partial'::courier_state
  );
  PERFORM pg_temp.assert_equivalent((o->>'order_id')::uuid,(n->>'order_id')::uuid,'courier_partial');
END
$f1$;

DO $f1a_f1b$
DECLARE
  v_res jsonb;
  v_oid uuid;
  v_ok bool;
  v_state text;
  v_cust numeric;
BEGIN
  -- F1a: safe legacy transition delegates and succeeds.
  v_res := public.create_sale_with_items(
    'eecc0001-9000-4000-8000-000000000001','courier'::delivery_kind,
    'ffcc0001-9000-4000-8000-000000000001',0,'cash'::payment_method,
    '[{"productId":"ddcc0002-9000-4000-8000-000000000002","qty":1}]'::jsonb
  );
  v_oid := (v_res->>'order_id')::uuid;
  PERFORM public.update_courier_order_state(v_oid,'delivered_full'::courier_state,100);
  SELECT courier_state::text,collected_by_courier INTO v_state,v_cust FROM orders WHERE id=v_oid;
  IF v_state <> 'delivered_full' OR v_cust <> 100 THEN
    RAISE EXCEPTION 'F1a FAIL: state=% custody=%', v_state, v_cust;
  END IF;

  -- F1b: unsafe custody-reducing/backward legacy call must be rejected by v2 safety.
  v_ok := false;
  BEGIN
    PERFORM public.update_courier_order_state(v_oid,'delivered_none'::courier_state,0);
  EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%custody_cannot_decrease%' OR SQLERRM LIKE '%invalid_transition%' THEN v_ok := true; END IF;
  END;
  IF NOT v_ok THEN RAISE EXCEPTION 'F1b FAIL: unsafe legacy backward transition accepted'; END IF;
END
$f1a_f1b$;

DO $f3$
DECLARE v_bad int;
BEGIN
  SELECT COUNT(*) INTO v_bad
    FROM orders
   WHERE customer_id IS NULL
     AND delivery='courier'
     AND courier_state IN ('delivered_partial','delivered_none');
  IF v_bad <> 0 THEN
    RAISE EXCEPTION 'F3 FAIL: rollback-preflight-invalid customer-less debt rows=%', v_bad;
  END IF;
END
$f3$;

DO $done$ BEGIN
  RAISE NOTICE 'GATE4_COMPAT_GREEN: F1/F1a/F1b/F3 passed';
END
$done$;

ROLLBACK;
