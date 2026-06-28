CREATE OR REPLACE FUNCTION public.delete_product_safe(p_product_id uuid)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_tenant uuid;
  v_used   int;
BEGIN
  SELECT tenant_id INTO v_tenant FROM public.products WHERE id = p_product_id;
  IF v_tenant IS NULL THEN
    RAISE EXCEPTION 'product_not_found';
  END IF;

  PERFORM public._assert_owner(v_tenant);

  SELECT count(*) INTO v_used FROM public.order_items WHERE product_id = p_product_id;

  IF v_used = 0 THEN
    DELETE FROM public.products WHERE id = p_product_id;
    RETURN jsonb_build_object('deleted', true);
  ELSE
    UPDATE public.products SET is_active = false WHERE id = p_product_id;
    RETURN jsonb_build_object('archived', true, 'used_in', v_used);
  END IF;
END;
$function$;