-- Courier account links are access-control data, not ordinary courier master data.
-- Owners may edit the visible courier fields directly, but user_id changes must
-- go through link_courier_account / unlink_courier_account (SECURITY DEFINER).

REVOKE INSERT, UPDATE ON public.couriers FROM authenticated;
GRANT INSERT (tenant_id, name, phone, is_active) ON public.couriers TO authenticated;
GRANT UPDATE (name, phone, is_active) ON public.couriers TO authenticated;

CREATE OR REPLACE FUNCTION public.prevent_linked_courier_delete()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  IF OLD.user_id IS NOT NULL THEN
    RAISE EXCEPTION 'unlink_employee_before_delete' USING ERRCODE = '42501';
  END IF;
  RETURN OLD;
END $$;

DROP TRIGGER IF EXISTS trg_prevent_linked_courier_delete ON public.couriers;
CREATE TRIGGER trg_prevent_linked_courier_delete
BEFORE DELETE ON public.couriers
FOR EACH ROW EXECUTE FUNCTION public.prevent_linked_courier_delete();

REVOKE ALL ON FUNCTION public.prevent_linked_courier_delete() FROM PUBLIC, anon, authenticated;
