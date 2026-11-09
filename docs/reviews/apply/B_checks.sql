-- RECOVERY-02 post-deploy functional checks (B1..B6).
-- Runs as one DO block that ALWAYS ends with RAISE, so every write inside it is rolled back.
-- The result is carried in the final error message: B_CHECKS_ROLLBACK {json}.
DO $b$
DECLARE
  v_owner uuid := 'b0b5cc7b-a577-40ea-b523-c99334b5f817';   -- owner of tenant d7b86b73 (36 orders)
  v_tenant uuid := 'd7b86b73-2f61-40ff-9fc8-dd8aa7750365';
  v_wh_owner uuid := 'ed0668dd-fc35-494d-81e3-09703e3bbd22'; -- owner of tenant b41cb398 (0 orders)
  v_wh_tenant uuid := 'b41cb398-4432-4080-8d43-3b345a27e550';
  v_ghost uuid := '00000000-0000-4000-8000-00000000b3b3';     -- not in auth.users
  v_res jsonb := '{}'::jsonb;
  v_n bigint;
  v_t text;
  v_sub jsonb;
  v_r1 jsonb; v_r2 jsonb;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'B_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  v_res := v_res || jsonb_build_object('expected_tenant_orders',
    (SELECT count(*) FROM public.orders WHERE tenant_id = v_tenant));

  -- B1/B2: active owner, impersonated via JWT claims.
  PERFORM set_config('request.jwt.claims', jsonb_build_object('sub',v_owner,'role','authenticated')::text, true);
  PERFORM set_config('request.jwt.claim.sub', v_owner::text, true);
  PERFORM set_config('role','authenticated', true);
  BEGIN
    SELECT count(*) INTO v_n FROM public.orders WHERE tenant_id = v_tenant;
    v_res := v_res || jsonb_build_object('B1_own_orders', v_n);
    SELECT count(*) INTO v_n FROM public.orders WHERE tenant_id <> v_tenant;
    v_res := v_res || jsonb_build_object('B2_other_orders', v_n);
  EXCEPTION WHEN OTHERS THEN
    v_res := v_res || jsonb_build_object('B1_B2_error', SQLSTATE||' '||SQLERRM);
  END;

  -- B6: authenticated (active owner) calls the webhook function.
  BEGIN
    PERFORM public.apply_subscription_webhook('sandbox','evt_'||repeat('b',26),'subscription.created',now(),'{}'::jsonb);
    v_res := v_res || jsonb_build_object('B6_authenticated_webhook','ALLOWED');
  EXCEPTION WHEN OTHERS THEN
    v_res := v_res || jsonb_build_object('B6_authenticated_webhook', SQLSTATE||' '||SQLERRM);
  END;
  PERFORM set_config('role','none', true);

  -- B3a: deleted/unknown account (no auth.users row) calls close_day.
  PERFORM set_config('request.jwt.claims', jsonb_build_object('sub',v_ghost,'role','authenticated')::text, true);
  PERFORM set_config('request.jwt.claim.sub', v_ghost::text, true);
  PERFORM set_config('role','authenticated', true);
  BEGIN
    PERFORM public.close_day(NULL);
    v_res := v_res || jsonb_build_object('B3a_unknown_close_day','ALLOWED');
  EXCEPTION WHEN OTHERS THEN
    v_res := v_res || jsonb_build_object('B3a_unknown_close_day', SQLSTATE||' '||SQLERRM);
  END;
  PERFORM set_config('role','none', true);

  -- B3b: the same owner, banned inside this transaction, calls close_day and reads orders.
  BEGIN
    UPDATE auth.users SET banned_until = now() + interval '1 day' WHERE id = v_owner;
    GET DIAGNOSTICS v_n = ROW_COUNT;
    v_res := v_res || jsonb_build_object('B3b_banned_rows', v_n);
    PERFORM set_config('request.jwt.claims', jsonb_build_object('sub',v_owner,'role','authenticated')::text, true);
    PERFORM set_config('request.jwt.claim.sub', v_owner::text, true);
    PERFORM set_config('role','authenticated', true);
    BEGIN
      PERFORM public.close_day(NULL);
      v_res := v_res || jsonb_build_object('B3b_banned_close_day','ALLOWED');
    EXCEPTION WHEN OTHERS THEN
      v_res := v_res || jsonb_build_object('B3b_banned_close_day', SQLSTATE||' '||SQLERRM);
    END;
    BEGIN
      SELECT count(*) INTO v_n FROM public.orders;
      v_res := v_res || jsonb_build_object('B3b_banned_orders_visible', v_n);
    EXCEPTION WHEN OTHERS THEN
      v_res := v_res || jsonb_build_object('B3b_banned_orders_visible', SQLSTATE||' '||SQLERRM);
    END;
    PERFORM set_config('role','none', true);
  EXCEPTION WHEN OTHERS THEN
    PERFORM set_config('role','none', true);
    v_res := v_res || jsonb_build_object('B3b_setup_error', SQLSTATE||' '||SQLERRM);
  END;

  -- B4: anon reads tables.
  PERFORM set_config('request.jwt.claims', '{"role":"anon"}', true);
  PERFORM set_config('request.jwt.claim.sub', '', true);
  PERFORM set_config('role','anon', true);
  FOREACH v_t IN ARRAY ARRAY['orders','tenants','profiles','products','customers','subscriptions'] LOOP
    BEGIN
      EXECUTE format('SELECT count(*) FROM public.%I', v_t) INTO v_n;
      v_res := v_res || jsonb_build_object('B4_anon_'||v_t, v_n);
    EXCEPTION WHEN OTHERS THEN
      v_res := v_res || jsonb_build_object('B4_anon_'||v_t, SQLSTATE);
    END;
  END LOOP;
  PERFORM set_config('role','none', true);

  -- B5: service_role applies a synthetic sandbox event, then the same event again.
  v_sub := jsonb_build_object('id','sub_'||repeat('b',26),'created_at','2026-11-09T12:00:00Z',
    'customer_id','ctm_'||repeat('b',26),'tenant_id',v_wh_tenant,'user_id',v_wh_owner,
    'product_id','pro_recovery02_check','price_id','pri_recovery02_check','status','active');
  PERFORM set_config('request.jwt.claims', '{"role":"service_role"}', true);
  PERFORM set_config('role','service_role', true);
  BEGIN
    v_r1 := public.apply_subscription_webhook('sandbox','evt_'||repeat('b',26),'subscription.created','2026-11-09T12:00:01Z',v_sub);
    v_r2 := public.apply_subscription_webhook('sandbox','evt_'||repeat('b',26),'subscription.created','2026-11-09T12:00:01Z',v_sub);
    v_res := v_res || jsonb_build_object('B5_first', v_r1->>'status', 'B5_repeat', v_r2->>'status');
  EXCEPTION WHEN OTHERS THEN
    v_res := v_res || jsonb_build_object('B5_error', SQLSTATE||' '||SQLERRM);
  END;
  PERFORM set_config('role','none', true);
  v_res := v_res || jsonb_build_object('B5_rows_in_txn', jsonb_build_object(
    'receipts',(SELECT count(*) FROM monjez_private.billing_webhook_receipts),
    'subscriptions',(SELECT count(*) FROM public.subscriptions)));

  RAISE EXCEPTION USING ERRCODE = 'P0001', MESSAGE = 'B_CHECKS_ROLLBACK ' || v_res::text;
END
$b$;
