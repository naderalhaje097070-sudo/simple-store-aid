# SEC-ENV-001 — Gate 4 Evidence

Status: **PREPARED / EXECUTION_INFRA_BLOCKED**

Owner decision: Gates 0–3 approved on 2026-07-28.

## Purpose

Freeze the environment-isolation gaps before changing the resolver or build configuration.

## True-green baseline

Explicit isolated values must continue to resolve correctly. The Gate-4 probe verifies a local URL/project before evaluating target gaps.

## Expected-red sentinels before implementation

- `SEC_ENV_G4_E1_EXPECTED_RED` — preview with missing Supabase config succeeds instead of failing closed.
- `SEC_ENV_G4_E2_EXPECTED_RED` — preview can resolve the known production project.
- `SEC_ENV_G4_E3_EXPECTED_RED` — production intent can succeed without explicit Supabase configuration.

The wrapper accepts expected-red only when the probe exits with controlled status `42` and all exact sentinels are present. Runtime/import/harness failures cannot substitute for target evidence.

## Approved target contract

Build/server-only `MONGEZZ_DEPLOY_TARGET` is one of `local|ci|preview|staging|production`.

- local/ci/preview/staging require explicit non-production URL/key/project and reject the known production target;
- production requires explicit target plus explicit approved production configuration;
- no source-code production fallback;
- do not infer production from NODE_ENV, Vite mode, branch, hostname or undocumented platform behavior;
- browser build and SSR/build resolution obey one contract.

## Target evidence after implementation

The probe must return `SEC_ENV_G4_TARGET_GREEN`, then unit/build/auth isolation tests on the exact implementation head must prove the same contract without production access.

## Current external blocker

OPS-GHA-001 / #36 remains unresolved. A job created without steps/logs is `EXECUTION_INFRA_BLOCKED`, not Gate-4 PASS/FAIL evidence.

## Boundary

No resolver/build implementation, production access, merge or deployment is included here.
