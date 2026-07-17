-- Add enqueued_at to read_email_batch so the queue processor's TTL fallback
-- can expire stale emails even if the enqueuing caller forgot to stamp queued_at.
-- Must DROP first because return-type signature is changing.
DROP FUNCTION IF EXISTS public.read_email_batch(text, integer, integer);

CREATE OR REPLACE FUNCTION public.read_email_batch(queue_name text, batch_size integer, vt integer)
 RETURNS TABLE(msg_id bigint, read_ct integer, enqueued_at timestamptz, message jsonb)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'pgmq'
AS $function$
BEGIN
  RETURN QUERY SELECT r.msg_id, r.read_ct, r.enqueued_at, r.message FROM pgmq.read(queue_name, vt, batch_size) r;
EXCEPTION WHEN undefined_table THEN
  PERFORM pgmq.create(queue_name);
  RETURN;
END;
$function$;

REVOKE EXECUTE ON FUNCTION public.read_email_batch(text, integer, integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.read_email_batch(text, integer, integer) TO service_role;