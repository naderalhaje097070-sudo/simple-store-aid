# SEC-CI-001 — Current Behavior

Baseline: `983b746e5c6639dcdc5e6557381ad5619abaa046`

## Quality

File: `.github/workflows/quality.yml`

- Runs on pull requests and pushes to `main`.
- Uses `ubuntu-latest`.
- Pins Bun to `1.2.14`.
- Uses frozen dependency installation.
- Runs typecheck, changed-file lint, unit tests, and build.
- Uploads limited lint diagnostics as an artifact.
- Does not post raw CI logs into PR comments.

## Ephemeral Financial Rules

File: `.github/workflows/ephemeral-financial-rules.yml`

- Runs on pull requests to `main`.
- Uses isolated local Supabase and T1–T15.
- Uses `supabase/setup-cli@v1` with `version: latest`.
- Captures the local Supabase environment into `/tmp/supabase.env`.
- Seeds a disposable owner/tenant and runs financial regression SQL against local Postgres.
- Posts a PR comment containing tails of raw Supabase startup and financial-rule logs.
- Grants the workflow token issue/PR write permissions to post that comment.

## Isolated Auth UI Smoke

File: `.github/workflows/isolated-auth-smoke.yml`

- Runs on pull requests to `main`.
- Pins Bun to `1.2.14`.
- Uses `supabase/setup-cli@v1` with `version: latest`.
- Starts local Supabase and exports local URL/key/DB values to the job environment.
- Creates a disposable QA account using run-specific credentials.
- Builds the production app against the isolated Supabase instance and executes a Playwright smoke test.
- Uploads app/test/build artifacts.

## Current Gate-4 execution incident

On FIN-COURIER PR #27, multiple exact heads created jobs for Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke, and FIN-COURIER Gate 4. The jobs then completed as failures before any workflow step started:

- `steps = None`;
- no checkout step;
- no test/build/migration/browser assertion;
- no downloadable job-log blob.

These runs are not accepted as product or test failures.

## Current proven risks

1. Material Supabase CLI behavior is non-deterministic across runs because `latest` is resolved at execution time.
2. Financial workflow PR comments can unnecessarily expose raw infrastructure/test output.
3. CI evidence currently lacks a formal classification boundary between runner/account execution failure and test assertion failure.
4. The account/repository cause of the current pre-step failures is not visible through the connected API surface.