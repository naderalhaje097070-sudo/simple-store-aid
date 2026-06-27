# Scheduled Security Scans

Automated weekly database security audit for Mongezz.

## Schedule

- **Cadence:** every Sunday at **01:00 UTC** (03:00 Africa/Tripoli).
- **Mechanism:** `pg_cron` job `mongezz-weekly-security-scan` runs `public.run_security_scan('cron')` directly inside the database — no HTTP hop, no secrets to manage.
- **Manual trigger:** platform admins can press "تشغيل فحص الآن" in `/app/platform-admin → فحوص الأمان`.

## What it checks

| Check | Severity | Detects |
|---|---|---|
| `rls_disabled` | error | `public.*` tables without Row Level Security |
| `rls_no_policy` | warn | RLS enabled but zero policies (all access blocked) |
| `sec_definer_public_exec` | error | `SECURITY DEFINER` functions executable by `anon` or `PUBLIC` |
| `anon_select_no_policy` | warn | `GRANT SELECT … TO anon` without a matching anon policy |

Whitelist: `has_role` and `is_platform_admin` are exempt from the SECURITY DEFINER check (intentional).

## Where results live

- `public.security_scan_runs` — one row per run (started/finished, new/total counts, trigger source).
- `public.security_scan_findings` — deduplicated by `fingerprint`. A finding seen again on a later run bumps `last_seen_at`; one that disappears gets `resolved_at = now()`.
- Both tables are RLS-protected: only platform admins can read them.

## Reviewing findings

1. Open the Platform Admin panel → **فحوص الأمان** tab.
2. The KPI strip shows open errors/warnings.
3. Press **تشغيل فحص الآن** any time to re-run.
4. Findings auto-resolve once the underlying issue is fixed and the next scan no longer detects them.

## Changing the cadence

```sql
SELECT cron.unschedule('mongezz-weekly-security-scan');
SELECT cron.schedule('mongezz-weekly-security-scan', '0 1 * * *',  -- daily 03:00 Tripoli
  $cron$ SELECT public.run_security_scan('cron'); $cron$);
```

## Alerting (future work)

This release stores results only. To page the team on a new finding, wire a Resend or webhook call into a server route that polls `security_scan_runs` for `new_count > 0`, or convert `run_security_scan` into a trigger on the runs table.
