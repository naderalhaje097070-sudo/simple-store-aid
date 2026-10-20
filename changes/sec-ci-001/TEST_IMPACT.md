# SEC-CI-001 — Test Impact

## Existing suites that must remain unchanged in intent

- Quality: typecheck, lint changed source, unit tests, build.
- Ephemeral Financial Rules: full isolated Supabase startup/migrations plus T1–T15.
- Isolated Auth UI Smoke: isolated authenticated build/smoke.
- Change-specific financial/UI workflows such as FIN-COURIER Gate 4 remain governed by their own contracts.

## New Gate-4 safety-net requirements for SEC-CI

Before workflow implementation, add static/policy tests that fail on:

1. `supabase/setup-cli` configured with `version: latest` in release-blocking workflows.
2. PR-comment bodies that include raw Supabase startup/test-log tails.
3. unnecessary `issues: write` / `pull-requests: write` permissions after raw PR commenting is removed.
4. missing isolated-CI sentinel before workflows perform financial/auth writes.
5. accidental use of production-looking Supabase configuration in isolated workflow definitions where statically detectable.
6. required workflow name drift without an explicit governance decision.

## Execution verification

After implementation, one exact head must prove:

- Quality reaches steps and passes.
- Financial Rules reaches steps, starts isolated Supabase, and passes T1–T15.
- Auth UI reaches steps, builds against isolated Supabase, and passes smoke.
- No PR comment/artifact exposes forbidden secret-like fields.
- Failure classification distinguishes `EXECUTION_INFRA_BLOCKED` from assertion failure.

## Negative evidence rule

A workflow run with `steps = None` or without a job log does not satisfy any test requirement and cannot be treated as expected RED.

## Production boundary

No production database or production secret is required for these tests.