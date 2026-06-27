# Scheduled Security Scans

Set up a recurring job that runs the Supabase database linter + a lightweight RLS/permissions check on the Mongezz database, stores results, and notifies the team when new issues appear.

## Approach

1. **New table `security_scan_findings`** (platform-admin only)
   - `id`, `scan_run_id`, `scanner` (`supabase_linter` | `internal_rls_check`), `level` (`error`/`warn`/`info`), `name`, `title`, `detail`, `metadata jsonb`, `fingerprint` (hash of scanner+name+metadata), `first_seen_at`, `last_seen_at`, `resolved_at`.
   - RLS: only `platform_admin` role can `SELECT`; writes via service role only.
   - GRANTs per project rules.

2. **New table `security_scan_runs`**
   - `id`, `started_at`, `finished_at`, `status`, `new_count`, `total_count`, `error text`.

3. **Server route `src/routes/api/public/hooks/security-scan.ts`** (POST)
   - Verifies `apikey` header against `VITE_SUPABASE_PUBLISHABLE_KEY` (per project cron pattern).
   - Uses `supabaseAdmin` to:
     a. Run Supabase linter via `supabase--linter` equivalent: query `pg_catalog` + the documented `lint` views (`SELECT * FROM pg_catalog.pg_policies` etc.) — actually call the Supabase Management API linter endpoint when available; fall back to a curated SQL probe set (tables without RLS, public functions executable by `anon`, missing GRANTs, SECURITY DEFINER funcs callable by anon).
     b. Compute a `fingerprint` for each finding; upsert into `security_scan_findings` (new row → `first_seen_at = now()`; existing → bump `last_seen_at`; missing this run → set `resolved_at`).
     c. Insert a `security_scan_runs` row with totals.
     d. If `new_count > 0`, send an alert email via Resend (if connected) or log a `console.error` summary that surfaces in server logs.

4. **pg_cron schedule** — weekly, Sunday 03:00 Africa/Tripoli (01:00 UTC):
   ```sql
   select cron.schedule(
     'mongezz-weekly-security-scan',
     '0 1 * * 0',
     $$ select net.http_post(
       url := 'https://project--1c38f21a-8f36-4a0b-8350-ee4be6901b8d.lovable.app/api/public/hooks/security-scan',
       headers := '{"Content-Type":"application/json","apikey":"<anon>"}'::jsonb,
       body := '{}'::jsonb
     ) $$
   );
   ```

5. **Platform-admin UI section** in `src/routes/_authenticated/platform-admin.tsx`:
   - "Security Scans" card: latest run timestamp/status, count of open findings by level, table of open findings (name, level, first seen, detail), button "Run scan now" (calls the same route).

6. **Docs** — append a `docs/security-scans.md` covering schedule, how to read findings, how to mark resolved (delete row or set `resolved_at`), and how to change cadence.

## Out of scope
- No changes to financial RPCs, RLS on business tables, or PWA config.
- No third-party SAST; this is database-surface scanning only.
- Email delivery only if a Resend connection already exists; otherwise log-only alerts (you can add email later).

## Questions before I build
1. **Cadence** — weekly Sunday 03:00 store-time OK, or do you want daily?
2. **Alerts** — log-only for now, or wire it to an email/Slack channel? If email, which address?
