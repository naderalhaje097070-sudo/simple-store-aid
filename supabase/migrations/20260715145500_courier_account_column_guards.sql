-- Courier account links are access-control data, not ordinary courier master data.
-- Authenticated table writes may edit normal courier fields, but user_id changes
-- must run inside the SECURITY DEFINER account-link RPCs.

CREATE OR REPLACE FUNCTION public.require_courier_account_rpc()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  -- SECURITY DEFINER RPC statements run with the function-owner current_user.
  -- Direct PostgREST writes run as authenticated and are rejected here.
  IF current_user = 'authenticated' THEN
    IF TG_OP = 'INSERT' AND NEW.user_id IS NOT NULL THEN
      RAISE EXCEPTION 'courier_account_rpc_required' USING ERRCODE = '42501';
    END IF;

    IF TG_OP = 'UPDATE' AND NEW.user_id IS DISTINCT FROM OLD.user_id THEN
      RAISE EXCEPTION 'courier_account_rpc_required' USING ERRCODE = '42501';
    END IF;
  END IF;

  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_require_courier_account_rpc ON public.couriers;
CREATE TRIGGER trg_require_courier_account_rpc
BEFORE INSERT OR UPDATE ON public.couriers
FOR EACH ROW EXECUTE FUNCTION public.require_courier_account_rpc();

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

REVOKE ALL ON FUNCTION public.require_courier_account_rpc() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.prevent_linked_courier_delete() FROM PUBLIC, anon, authenticated;
