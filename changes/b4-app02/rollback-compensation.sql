-- Owner-run forward containment; retain all data and retryable delivery failure.
BEGIN;
REVOKE EXECUTE ON FUNCTION public.apply_subscription_webhook(text,text,text,timestamptz,jsonb) FROM service_role;
COMMIT;
