# SEC-ENV-001 — Dependency Map

## Primary files

- `config/supabase-build-config.ts` — build-time resolution and current production fallback.
- `vite.config.ts` — injects resolved Supabase values into `import.meta.env`.
- `src/integrations/supabase/client.ts` — client/SSR consumption and runtime missing-value guard.
- `tests/unit/supabase-build-config.test.ts` — current resolver contract tests.

## CI consumers

- `.github/workflows/isolated-auth-smoke.yml` exports local Supabase values before building the app.
- `.github/workflows/ephemeral-financial-rules.yml` starts isolated Supabase for database tests.
- FIN-COURIER Gate-4 UI workflow follows the same local-build pattern on PR #27.

## Deployment consumers

- Lovable production deployment.
- Lovable Preview.
- Any future staging/preview deployment supplying VITE/SUPABASE aliases.

## Contract dependencies

- `@lovable.dev/vite-tanstack-config` VITE env injection/build behavior.
- Supabase project URL/publishable key/project-ID consistency.

## Sequencing

- Verify an explicit production-deployment signal before implementation.
- Gate-4 tests must be authored before resolver change.
- SEC-CI remains separate: tool pinning/log redaction is not part of this change.
- No production access is required.