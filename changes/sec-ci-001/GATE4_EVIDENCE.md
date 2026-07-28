# SEC-CI-001 — Gate 4 Evidence

Status: **PREPARED / EXECUTION_INFRA_BLOCKED**

Owner decision: Gates 0–3 approved on 2026-07-28.

## Purpose

Freeze the current repository-controlled CI gaps before any workflow implementation.

## True-green baseline

- `Ephemeral Financial Rules` workflow identity remains present.
- `Isolated Auth UI Smoke` workflow identity remains present.
- The probe itself must execute on a real runner; pre-step GitHub failures are not accepted as product evidence.

## Expected-red sentinels before implementation

- `SEC_CI_G4_E1_EXPECTED_RED` — release workflow still uses `supabase/setup-cli@v1`.
- `SEC_CI_G4_E2_EXPECTED_RED` — Supabase CLI still floats on `latest`.
- `SEC_CI_G4_E3_EXPECTED_RED` — financial workflow still posts raw startup/test log tails into PR comments.
- `SEC_CI_G4_E4_EXPECTED_RED` — write permissions remain solely to support that PR reporting path.

The dedicated workflow accepts expected-red only when the probe exits with controlled status `42` and all four exact sentinels are present. Checkout/runtime/parse errors cannot masquerade as expected-red.

## Target after implementation

A later implementation PR must make the policy probe return `SEC_CI_G4_TARGET_GREEN`, then prove on the exact implementation head:

1. maintained `supabase/setup-cli@v2` action line;
2. one exact Supabase CLI version validated against this repository's migrations, T1–T15 and auth smoke;
3. no raw PR log comments;
4. least-privilege token permissions;
5. isolated target preconditions before sensitive writes;
6. standard Quality, Financial Rules and Auth Smoke actually reach steps and pass.

## Current external blocker

OPS-GHA-001 / #36 remains unresolved: current GitHub-hosted jobs are created but terminate before any step and produce no logs. Such runs are `EXECUTION_INFRA_BLOCKED`, neither PASS nor FAIL for this Gate.

## Boundary

No production/workflow hardening implementation, merge, production access or deploy is part of this Gate-4 branch.
