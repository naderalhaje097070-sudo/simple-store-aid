-- EMERGENCY ONLY (C6): if the new frontend cannot be published after C2/C5 have committed, this
-- restores the published (legacy) frontend's sale and collection paths. It does NOT undo any
-- migration. Cost: the server no longer forces the idempotency wrapper until reverted below.
-- Revert with EMERGENCY_unblock_legacy_frontend_revert.sql as soon as the new frontend is live.
begin;
grant execute on function public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) to authenticated;
grant execute on function public.collect_order_debt(uuid, numeric, public.payment_method) to authenticated;
commit;
