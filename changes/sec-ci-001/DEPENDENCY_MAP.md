# SEC-CI-001 — Dependency Map

## Required workflows

- `.github/workflows/quality.yml`
- `.github/workflows/ephemeral-financial-rules.yml`
- `.github/workflows/isolated-auth-smoke.yml`
- FIN-COURIER Gate-4 workflow while PR #27 remains active; it is not part of `main` and must not be silently modified from this branch.

## External execution dependencies

- GitHub Actions workflow scheduler.
- Standard GitHub-hosted Ubuntu runners.
- `actions/checkout`.
- `oven-sh/setup-bun`.
- `supabase/setup-cli`.
- Docker/local Supabase images pulled by Supabase CLI.
- Ubuntu package repositories for PostgreSQL client installation.
- Python/pip/Playwright package and browser installation for UI smoke.
- GitHub artifact/log storage.

## Repository dependencies

- `bun.lock` and `package.json` for deterministic app dependencies.
- `supabase/config.toml` and migration chain for isolated database startup.
- `tests/financial-rules/run.sh` and T1–T15.
- `tests/e2e/isolated-auth-smoke.py`.

## Human/account dependencies

- Repository owner controls GitHub Actions account budget/minutes and repository Actions settings.
- A human controls branch protection/required-check configuration and merge.

## Sequencing dependencies

- SEC-CI can proceed independently of FIN-COURIER implementation.
- SEC-CI must not merge by automated action.
- FIN-COURIER Gate 4 still requires its own exact-head evidence and explicit approval.
- SEC-ENV remains a separate P0 because CI hardening does not prove application build/runtime environment resolution.