-- AC-02: only the trusted backend may assign entitlement/billing metadata.
-- A table-level grant overrides column restrictions, so remove it first.
BEGIN;
REVOKE INSERT, UPDATE ON TABLE public.tenants FROM authenticated;
REVOKE INSERT (trial_ends_at, subscription_status, subscription_plan, paddle_customer_id, paddle_subscription_id),
       UPDATE (trial_ends_at, subscription_status, subscription_plan, paddle_customer_id, paddle_subscription_id) ON public.tenants FROM authenticated;
GRANT INSERT (id, name, owner_user_id, created_at, updated_at, timezone, business_type),
      UPDATE (id, name, owner_user_id, created_at, updated_at, timezone, business_type) ON public.tenants TO authenticated;
COMMIT;
