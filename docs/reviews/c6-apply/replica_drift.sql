-- REPLICA ONLY: reproduce production drift on top of a local replay of main 1c5276f.
-- Source: read-only production catalog read 2026-11-18. Never run against production.
begin;
-- 1. platform_admin_audit_log as created in production by ledger entry 20260626191247
alter table public.platform_admin_audit_log drop constraint platform_admin_audit_log_user_id_fkey;
alter table public.platform_admin_audit_log alter column user_id set not null;
create policy "platform admins can read audit log" on public.platform_admin_audit_log for select to authenticated using (public.is_platform_admin());
-- 2. Lovable email tooling functions (created outside migrations); outbound URL neutralised for the replica
CREATE OR REPLACE FUNCTION public.email_queue_dispatch()
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pgmq.q_auth_emails)
     AND NOT EXISTS (SELECT 1 FROM pgmq.q_transactional_emails) THEN
    BEGIN
      -- Serialize disarm against email_queue_wake on a shared advisory lock, then
      -- re-read under it: an enqueue racing the unschedule either committed (we
      -- see its row and leave the cron) or waits and re-arms after we commit.
      PERFORM pg_catalog.pg_advisory_xact_lock(7700000000000001);
      IF EXISTS (SELECT 1 FROM pgmq.q_auth_emails)
         OR EXISTS (SELECT 1 FROM pgmq.q_transactional_emails) THEN
        RETURN;
      END IF;
      PERFORM cron.unschedule('process-email-queue');
    EXCEPTION WHEN OTHERS THEN
      RAISE WARNING 'email_queue_dispatch: cron unschedule failed: %', SQLERRM;
    END;
    RETURN;
  END IF;

  IF (SELECT retry_after_until FROM public.email_send_state WHERE id = 1) > now() THEN
    RETURN;
  END IF;

  PERFORM net.http_post(
    url := 'http://127.0.0.1:9/replica-disabled',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Lovable-Context', 'cron',
      'Authorization', 'Bearer ' || (
        SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'email_queue_service_role_key'
      )
    ),
    body := '{}'::jsonb
  );
END;
$function$;
CREATE OR REPLACE FUNCTION public.email_queue_wake()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
BEGIN
  -- Runs inside the enqueue transaction; the outer handler guarantees nothing
  -- below can roll back the customer's email. Shared advisory lock serializes
  -- arming against email_queue_dispatch's disarm.
  PERFORM pg_catalog.pg_advisory_xact_lock(7700000000000001);
  IF NOT EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'process-email-queue') THEN
    BEGIN
      PERFORM cron.schedule('process-email-queue', '5 seconds', $cron$ SELECT public.email_queue_dispatch(); $cron$);
    EXCEPTION WHEN OTHERS THEN
      RAISE WARNING 'email_queue_wake: cron schedule failed: %', SQLERRM;
    END;
  END IF;

  BEGIN
    PERFORM net.http_post(
      url := 'http://127.0.0.1:9/replica-disabled',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Lovable-Context', 'cron',
        'Authorization', 'Bearer ' || (
          SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'email_queue_service_role_key'
        )
      ),
      body := '{}'::jsonb
    );
  EXCEPTION WHEN OTHERS THEN NULL;
  END;

  RETURN NULL;
EXCEPTION WHEN OTHERS THEN
  RAISE WARNING 'email_queue_wake failed (enqueue preserved): %', SQLERRM;
  RETURN NULL;
END;
$function$;
revoke all on function public.email_queue_dispatch() from public, anon, authenticated;
grant execute on function public.email_queue_dispatch() to service_role;
revoke all on function public.email_queue_wake() from public, anon;
grant execute on function public.email_queue_wake() to authenticated, service_role;
-- 3. platform role sandbox_exec and its grants, as observed in production
do $$ begin if not exists (select 1 from pg_roles where rolname='sandbox_exec') then create role sandbox_exec login bypassrls; end if; end $$;
grant usage on schema public to sandbox_exec;
grant select, insert on all tables in schema public to sandbox_exec;
grant select, usage on all sequences in schema public to sandbox_exec;
alter default privileges for role postgres in schema public grant select, insert on tables to sandbox_exec;
alter default privileges for role postgres in schema public grant select, usage on sequences to sandbox_exec;
alter default privileges for role postgres in schema auth grant select, insert on tables to sandbox_exec;
alter default privileges for role postgres in schema auth grant select, usage on sequences to sandbox_exec;
alter default privileges for role postgres in schema extensions grant select, insert on tables to sandbox_exec;
alter default privileges for role postgres in schema extensions grant select, usage on sequences to sandbox_exec;
alter default privileges for role postgres in schema storage grant select, insert on tables to sandbox_exec;
alter default privileges for role postgres in schema storage grant select, usage on sequences to sandbox_exec;
commit;
