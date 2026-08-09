# RELEASE-BASELINE-RECON-002 — 2026-08-09

## Purpose

Reconcile the actual `main` branch with the governed Pilot RC plan before any new P0 implementation is authorized.

This change is documentation/governance only. It does not modify production financial logic, migrations, RPCs, RLS, application behavior, workflow implementation, deployment, or production data.

## Exact baseline

Current `main` at reconciliation start:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

Previous Gate-4 baseline used by the current P0 workstreams:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

GitHub comparison shows current `main` is 11 commits ahead of that baseline and modifies exactly five paths:

- `.lovable/plan.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`

## Material drift classification

### UI sale-save guards

The effective application now contains client-side duplicate-click guards in the sale paths:

- mobile `+ Sale` navigation uses a temporary `busy`/`disabled` guard;
- Quick Sale uses local `saving` state and rejects a second local save invocation while the first is active;
- Advanced Sale `PaymentSheet` uses local `saving`, disables save while active, and prevents closing during the save.

These are UI controls only. They do **not** replace server-side financial idempotency and do not close `FIN-IDEM-001`.

Impact:

- FIN-COURIER UI Gate-4 assumptions must be rechecked against this effective UI before approval;
- FIN-IDEM must continue to prove retry/double-submit safety at the server/database transaction boundary.

### Dependency drift

`@lovable.dev/vite-tanstack-config` moved from `2.7.7` to `2.9.1` with corresponding lockfile changes.

Impact:

- release checks must run against the current dependency graph;
- SEC-CI exact-head evidence cannot be accepted solely from an older dependency baseline.

## Current P0 evidence status

### OPS-GHA-001 / #36

Resolved on 2026-08-01. GitHub-hosted Actions execution again reaches real job steps and logs. Runner/account failure is no longer the current blocker.

### SEC-CI-001 / #29

- Gates 0–3: owner-approved.
- Gate-4 PR #37: probe reached real execution and the policy probe passed.
- Standard Quality reached repository lint/format validation and failed on formatting in `tests/gate4/sec-ci/probe.ts`.
- Gate 4 remains **NOT APPROVED**.

### SEC-ENV-001 / #30

- Gates 0–3: owner-approved.
- Gate-4 PR #38: probe reached real execution and the isolation probe passed.
- Standard Quality reached repository lint/format validation and failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`.
- Gate 4 remains **NOT APPROVED**.

### FIN-COURIER-001 / #22

On PR #27 exact head `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- FIN-COURIER UI contract: GREEN and reached approved expected-red evidence;
- FIN-COURIER backend contract: executed real steps and failed with exit code `3`.

This is an application/test-evidence blocker, not runner acquisition failure. Gate 4 remains **NOT APPROVED** and PR-A/PR-B/PR-C remain blocked.

### FIN-IDEM-001 / #31

- Gates 0–3: owner-approved.
- PR #39 remains dependency-aware preparation only.
- Full target behavior must wait for the canonical `create_sale_with_items_v2` produced by FIN-COURIER PR-A.
- Current client-side save guards do not satisfy the idempotency contract.

## Release freeze effective from this reconciliation

Until Pilot RC1 is approved:

1. No new product features enter the critical path.
2. No employee-account, payroll, attendance, GPS, chat, commission, multi-branch, AI, or broad analytics work.
3. No direct product/dependency changes to `main` outside a reviewed PR path.
4. No automatic merge or deploy.
5. Any Critical/High financial-correctness or tenant-isolation defect blocks pilot.
6. Published Lovable-linked history is not rewritten.
7. Corrections use additive commits/branches/PRs and forward-only migrations.

## Fixed execution order after this baseline is accepted

1. SEC-CI-001 Gate 4 reconciliation and exact-head proof.
2. SEC-CI focused implementation and exact-head verification.
3. SEC-ENV-001 Gate 4 reconciliation and exact-head proof.
4. SEC-ENV focused implementation and exact-head verification.
5. FIN-COURIER Gate 4 backend failure diagnosis and exact-head proof.
6. Explicit human FIN-COURIER Gate-4 approval.
7. FIN-COURIER PR-A → PR-B → PR-C.
8. FIN-IDEM Gate 4 against canonical sale v2 → approval → implementation.
9. One exact Pilot RC1 commit passing all release gates together.
10. Explicit human RC1 approval.
11. Controlled owner-only pilot with 3–5 stores.

## Non-negotiable financial invariants

- Sale is not cash.
- Delivered is not settled.
- Customer debt is not courier custody.
- Returned orders create zero customer debt and zero courier custody and restore stock through the approved return transaction.
- A customer is required when an operation creates customer debt, not merely because a courier is assigned.
- Courier-collected money remains custody until authorized settlement.
- No client-only control is accepted as the sole protection against duplicate financial effects.

## Exit criteria for RELEASE-BASELINE-RECON-002

- `PROJECT_STATE.md` and `TASKS.md` reflect the exact current state;
- the current `main` SHA and five-file drift are recorded;
- stale Gate-4 evidence is explicitly classified as requiring reconciliation before approval;
- the P0 sequence is fixed;
- required checks on this documentation-only PR are reviewed;
- a human explicitly merges the PR;
- the resulting `main` SHA is recorded as the baseline for the first SEC-CI reconciliation branch.

No merge or deployment is authorized automatically by this document.
