
-- 1) Fix mutable search_path on email queue helper functions
ALTER FUNCTION public.enqueue_email(text, jsonb) SET search_path = public, pgmq;
ALTER FUNCTION public.read_email_batch(text, integer, integer) SET search_path = public, pgmq;
ALTER FUNCTION public.delete_email(text, bigint) SET search_path = public, pgmq;
ALTER FUNCTION public.move_to_dlq(text, text, bigint, jsonb) SET search_path = public, pgmq;

-- 2) Explicit deny-insert on profiles (trigger uses SECURITY DEFINER and bypasses RLS)
CREATE POLICY "Profiles are created only by signup trigger"
  ON public.profiles
  FOR INSERT
  TO authenticated, anon
  WITH CHECK (false);

-- 3) Explicit deny-all policy on tenant_counters (only next_order_number SECURITY DEFINER RPC may touch it)
CREATE POLICY "Tenant counters are internal only"
  ON public.tenant_counters
  FOR ALL
  TO authenticated, anon
  USING (false)
  WITH CHECK (false);
