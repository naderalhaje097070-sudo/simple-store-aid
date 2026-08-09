# SEC-CI-001 — Gate 4 Evidence

Status: **RECONCILED / AWAITING EXACT-HEAD EXECUTION**

Owner decision: Gates 0–3 approved on 2026-07-28.

Accepted Phase-0 baseline:

`main = f4efaa2abdf7ab691f3f784aa1b662c50a5c0f2f`

## Purpose

Freeze the current repository-controlled CI gaps on the accepted release baseline before any workflow-hardening implementation.

## True-green baseline

- `Ephemeral Financial Rules` workflow identity remains present.
- `Isolated Auth UI Smoke` workflow identity remains present.
- GitHub-hosted Actions execution is restored; OPS-GHA-001 / #36 is resolved.
- The probe must execute on a real runner; runtime/parse/setup failure is not accepted as Gate evidence.
- Phase-0 Auth Smoke runtime containment from PR #44 is part of the accepted baseline and must remain intact.

## Expected-red sentinels before implementation

- `SEC_CI_G4_E1_EXPECTED_RED` — release workflows still use `supabase/setup-cli@v1`.
- `SEC_CI_G4_E2_EXPECTED_RED` — Supabase CLI still floats on `latest` rather than one exact semver pin.
- `SEC_CI_G4_E3_EXPECTED_RED` — financial workflow still posts raw startup/test log tails into PR comments.
- `SEC_CI_G4_E4_EXPECTED_RED` — financial workflow still grants issue/PR write permissions to support that reporting path.

The dedicated workflow accepts expected-red only when the probe exits with controlled status `42` and all four exact sentinels are present. Any partial gap set or harness/runtime failure is a Gate failure.

## Reconciliation findings on accepted baseline

Direct inspection of `main` at `f4efaa2abdf7ab691f3f784aa1b662c50a5c0f2f` confirms all four gaps remain present:

1. `.github/workflows/ephemeral-financial-rules.yml` uses `supabase/setup-cli@v1` with `version: latest`.
2. `.github/workflows/isolated-auth-smoke.yml` uses `supabase/setup-cli@v1` with `version: latest`.
3. `Ephemeral Financial Rules` builds a PR comment containing tails from `/tmp/supabase-start.log` and `/tmp/financial-rules.log`.
4. `Ephemeral Financial Rules` grants `issues: write` and `pull-requests: write`.

No production workflow has been modified by this Gate-4 reconciliation.

## Target after implementation

A later, separately approved implementation PR must make the policy probe return `SEC_CI_G4_TARGET_GREEN`, then prove on one exact implementation head:

1. maintained `supabase/setup-cli@v2` action line in release-blocking Supabase workflows;
2. one exact Supabase CLI semver validated against this repository's fresh migrations, T1–T15 and authenticated UI smoke;
3. no raw infrastructure/test-log PR comments;
4. least-privilege workflow token permissions;
5. explicit isolated-CI preconditions before sensitive test writes;
6. Quality, Ephemeral Financial Rules and Isolated Auth UI Smoke reach real steps and pass;
7. infrastructure/acquisition failure remains distinguishable from assertion failure.

The design-time candidate `2.101.0` is not promoted merely by documentation. It must be validated on a real runner before implementation approval.

## Boundary

This Gate-4 reconciliation adds only the policy probe, its dedicated workflow, and this evidence record. It does not harden production workflows, access production, change financial logic, modify migrations/RPC/RLS, deploy, or authorize automatic merge.
