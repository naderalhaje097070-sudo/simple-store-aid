REVOKE EXECUTE ON FUNCTION public.delete_product_safe(uuid) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.delete_product_safe(uuid) TO authenticated;