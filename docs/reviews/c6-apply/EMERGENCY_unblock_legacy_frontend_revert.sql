-- Revert of the legacy-frontend unblock (review fix 2026-11-19: stage-aware).
-- Refuses unless ALL ten C6 versions are in the ledger, so the new idempotent sale (C2) and collection (C5)
-- paths exist before the legacy ones are withdrawn. The database cannot see the frontend: run this only after
-- the live site serves the new frontend and the shops have reloaded (runbook step).
DO $revert$
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN
      ('20260815170000','20260815171000','20261028213608','20261029044024','20261103060658',
       '20261106145346','20261110090000','20261110130000','20261110140000','20261110150000')) <> 10 THEN
    RAISE EXCEPTION 'REVERT_REFUSED: C6 is not fully applied; withdrawing the legacy paths now would stop sales or collection';
  END IF;
  REVOKE EXECUTE ON FUNCTION public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) FROM authenticated;
  REVOKE EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, public.payment_method) FROM authenticated;
END
$revert$;
