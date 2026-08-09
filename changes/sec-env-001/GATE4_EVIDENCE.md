# SEC-ENV-001 — Gate 4 Evidence

Status: **RECONCILED / AWAITING EXACT-HEAD EXECUTION**

Accepted baseline: `main = 69d6495499e7ebb81d7b2956477e6984d5338a8d`.

Owner approved Gates 0–3 on 2026-07-28. This Gate 4 is rebuilt directly from the accepted Pilot-RC baseline; the old stacked PR #38 is superseded and must not be merged.

## Purpose

Freeze the environment-isolation gaps before changing the resolver or build configuration.

## True-green compatibility baseline

The probe first proves that explicit isolated preview values still resolve and that explicit production intent plus explicit production values remains a valid contract. SEC-ENV must not solve isolation by disabling production entirely.

## Expected-red sentinels before implementation

- `SEC_ENV_G4_E1_EXPECTED_RED` — preview with missing Supabase configuration succeeds instead of failing closed.
- `SEC_ENV_G4_E2_EXPECTED_RED` — preview can resolve the known production Supabase target.
- `SEC_ENV_G4_E3_EXPECTED_RED` — production intent can succeed without explicit Supabase configuration.

Expected-red is accepted only when the probe exits with controlled status `42` and all three exact sentinels are present. Parser, import, runtime, runner, or partial-gap failures are not accepted as Gate evidence.

## Current baseline observation

`config/supabase-build-config.ts` still contains a source-code production fallback and does not define an explicit deployment-target contract. Therefore the three pre-implementation gaps remain relevant on the accepted baseline.

## Approved target contract

Build/server-only `MONGEZZ_DEPLOY_TARGET` is one of `local|ci|preview|staging|production`.

- local/ci/preview/staging require explicit non-production URL/key/project and reject the known production target;
- production requires explicit production intent plus explicit approved production configuration;
- no source-code production fallback;
- do not infer production from `NODE_ENV`, Vite mode, branch, hostname, or undocumented platform behavior;
- browser build and SSR/build resolution obey one contract;
- no production access is required to prove this contract.

## Required Gate-4 evidence

1. SEC-ENV Gate 4 Probe confirms all three expected-red sentinels on the exact PR head;
2. Quality is GREEN;
3. Ephemeral Financial Rules / T1–T15 is GREEN;
4. Isolated Auth UI Smoke is GREEN;
5. diff remains the three Gate-4-only files;
6. `main` remains at the accepted baseline during evidence review;
7. explicit human Gate-4 approval is required before resolver/build implementation.

## Boundary

No resolver/build implementation, production access, deployment, automatic approval, or merge is authorized by this Gate-4 PR.
