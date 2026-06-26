
REVOKE EXECUTE ON FUNCTION public.create_sale_with_items(uuid, delivery_kind, uuid, numeric, payment_method, jsonb) FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, payment_method) FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION public.settle_courier_orders(uuid, jsonb) FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION public.return_courier_order(uuid) FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION public.close_day(text) FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION public._assert_staff(uuid) FROM PUBLIC, anon, authenticated;
