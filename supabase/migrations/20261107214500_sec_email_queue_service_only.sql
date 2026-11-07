-- SEC-EMAIL-QUEUE-01: queue RPC wrappers are SECURITY DEFINER and must be service_role only.
-- 20260715145141 revoked them FROM PUBLIC only; Supabase default privileges had already granted
-- authenticated directly, so any signed-in user could read other users' auth emails, enqueue
-- arbitrary mail and delete/move queue messages. Grants only; no row or function-body change.
BEGIN;
REVOKE EXECUTE ON FUNCTION
  public.enqueue_email(text, jsonb),
  public.read_email_batch(text, integer, integer),
  public.delete_email(text, bigint),
  public.move_to_dlq(text, text, bigint, jsonb)
FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION
  public.enqueue_email(text, jsonb),
  public.read_email_batch(text, integer, integer),
  public.delete_email(text, bigint),
  public.move_to_dlq(text, text, bigint, jsonb)
TO service_role;

-- Provider-created dispatcher (not defined in this repository): same rule where it exists.
DO $sec$
BEGIN
  IF to_regprocedure('public.email_queue_dispatch()') IS NOT NULL THEN
    REVOKE EXECUTE ON FUNCTION public.email_queue_dispatch() FROM PUBLIC, anon, authenticated;
    GRANT EXECUTE ON FUNCTION public.email_queue_dispatch() TO service_role;
  END IF;
END
$sec$;
COMMIT;
