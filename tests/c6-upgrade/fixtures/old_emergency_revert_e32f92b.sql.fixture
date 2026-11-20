begin;
revoke execute on function public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) from authenticated;
revoke execute on function public.collect_order_debt(uuid, numeric, public.payment_method) from authenticated;
commit;
