# SEC-ENV-001 — Non-production Supabase isolation

Status: **Gates 0–3 proposed for review. No environment-resolution implementation is authorized by this documentation.**

Issue: #30

Baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

## Goal

Ensure local, CI, preview, and staging builds cannot silently target production Supabase. Missing non-production configuration must fail closed.

## Proven baseline finding

`config/supabase-build-config.ts` contains a hardcoded `PRODUCTION_SUPABASE_FALLBACK` and `resolveSupabaseBuildConfig()` returns that production URL/key/project ID when explicit variables are absent. `vite.config.ts` then injects those fallback values into `import.meta.env.VITE_SUPABASE_*` for the built application. The current unit test explicitly expects missing variables to resolve to the production fallback for Lovable preview.

The generated runtime client itself throws when Supabase URL/key are missing, but the build-time fallback normally prevents that fail-closed path by injecting production values.

## Proposed direction

Replace implicit production fallback with an explicit environment-mode contract:

- non-production → explicit non-production values required; missing/production target rejected;
- production → production target allowed only under explicit production deployment intent;
- CI isolated workflows → prove disposable local Supabase target before financial/auth writes.

## Non-goals

No CI reporting/pinning work owned by SEC-CI-001, no financial idempotency, no FIN-COURIER business logic, no production access, no automatic merge/deploy.