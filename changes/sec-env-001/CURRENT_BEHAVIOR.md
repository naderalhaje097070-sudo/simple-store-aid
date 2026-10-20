# SEC-ENV-001 — Current Behavior

Baseline: `983b746e5c6639dcdc5e6557381ad5619abaa046`

## Build-time resolver

File: `config/supabase-build-config.ts`

- Accepts `VITE_SUPABASE_*` and `SUPABASE_*` aliases.
- Prefers non-empty explicit variables.
- If values are absent, returns hardcoded production Supabase URL, publishable key, and project ID from `PRODUCTION_SUPABASE_FALLBACK`.

## Vite injection

File: `vite.config.ts`

- Calls `resolveSupabaseBuildConfig(process.env)` at build time.
- Injects resolved URL/key/project ID into `import.meta.env.VITE_SUPABASE_*`.
- Comments state the production fallback exists because Lovable Preview may omit connected database variables.

## Runtime client

File: `src/integrations/supabase/client.ts`

- Reads `import.meta.env.VITE_SUPABASE_URL` / publishable key first, then SSR `process.env` aliases.
- Throws when URL/key are missing.
- Because Vite injects production fallback values when build variables are absent, this runtime fail-closed path is bypassed for those builds.

## Existing unit tests

File: `tests/unit/supabase-build-config.test.ts`

- Proves explicit VITE values override fallback.
- Proves server aliases work.
- Explicitly asserts that missing environment values return `PRODUCTION_SUPABASE_FALLBACK` for Lovable preview.
- Proves blank values do not override usable aliases.

## Risk statement

A build with absent explicit Supabase variables can be successfully produced with production Supabase configuration even when the build is a preview, CI, local, or staging context. Current logic does not require proof that production targeting is intentional.