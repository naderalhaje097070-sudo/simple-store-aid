> Historical execution snapshot. For work after the 2026-10-09 source reconciliation,
> read PROJECT_STATE.md's current block and docs/PRIMARY_DELIVERY_PLAN.md.
> The checkboxes below are retained evidence, not the active queue or new approvals.

# Mongezz v1.0 Ordered Execution Plan

This file is intentionally operational. It freezes the sequence from the current governed baseline to the owner-only Pilot RC1.

## Phase 0 — Baseline reconciliation

- [x] Identify reconciliation-start `main`: `a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`.
- [x] Compare with previous Gate-4 baseline `983b746e5c6639dcdc5e6557381ad5619abaa046`.
- [x] Record start-state 11-commit / five-file drift.
- [x] Classify UI sale-save guards as client-only defense in depth, not idempotency.
- [x] Record dependency drift to `@lovable.dev/vite-tanstack-config@2.9.1`.
- [x] Diagnose Phase-0 authenticated-smoke runtime failure.
- [x] Falsify and close dependency-rollback PR #43 without merge.
- [x] Verify PR #44 exact head with Quality + T1–T15 + real Playwright Auth Smoke GREEN.
- [x] Human-merge PR #44.
- [x] Record accepted Phase-0 baseline: `main = 975a34a854c510f3da7dbe45caa9791bb0375e2d`.
- [x] Recompare accepted `main` with old Gate-4 baseline: 21 commits ahead / nine net changed paths.
- [x] Preserve concurrent rapid-click plan/results/test history from accepted `main`.
- [x] Classify rapid-click results as UI evidence only, not FIN-IDEM closure.
- [x] Classify `tests/e2e/rapid-click-sale.py` as non-production-only until fail-closed isolation is proven.
- [x] Synchronize `PROJECT_STATE.md`, `TASKS.md`, baseline reconciliation, and Human Gate.
- [x] Ensure final PR #41 diff relative to accepted `main` is documentation/governance only.
- [ ] Final PR #41 checks GREEN on one exact head.
- [ ] Explicit human merge of PR #41.
- [ ] Record resulting post-merge `main` SHA.

## Phase 1 — SEC-CI

- [ ] Reconcile Gate 4 from accepted Phase-0 baseline.
- [ ] Preserve existing policy sentinels.
- [ ] Fix probe formatting only where required by Quality.
- [ ] Validate exact stable Supabase CLI/tool pin on real runner.
- [ ] Fresh migrations + T1–T15 GREEN.
- [ ] Auth Smoke GREEN.
- [ ] Concise/redacted reporting proof.
- [ ] Least-privilege workflow permissions proof.
- [ ] Independent review.
- [ ] Explicit human Gate-4 approval.
- [ ] Focused SEC-CI implementation PR.
- [ ] Exact-head verification.
- [ ] Explicit human merge.

## Phase 2 — SEC-ENV

- [ ] Reconcile Gate 4 from accepted Phase-1 baseline.
- [ ] Fix `explicit-any`/format issues without weakening sentinels.
- [ ] Verify one build/server environment contract across client/SSR/build paths.
- [ ] Prove local/CI/preview/staging reject production target.
- [ ] Prove missing non-production configuration fails closed.
- [ ] Include financial-write test harness target isolation in the environment contract.
- [ ] Independent review.
- [ ] Explicit human Gate-4 approval.
- [ ] Focused SEC-ENV implementation PR.
- [ ] Exact-head verification.
- [ ] Explicit human merge.

## Phase 3 — FIN-COURIER

- [ ] Reconcile PR #27 assumptions to effective release baseline.
- [ ] Identify exact backend sentinel behind exit code `3`.
- [ ] Classify cause: stale baseline / probe defect / false evidence / genuine contract mismatch.
- [ ] Correct Gate-4 evidence only if needed; no financial implementation before approval.
- [ ] Quality GREEN on exact final head.
- [ ] T1–T15 GREEN.
- [ ] Auth Smoke GREEN.
- [ ] Backend Gate-4 contract reaches all true-green and expected-red outcomes.
- [ ] UI Gate-4 contract reaches all approved outcomes.
- [ ] Independent financial review.
- [ ] Explicit human FIN-COURIER Gate-4 approval.

### PR-A

- [ ] forward-only financial schema/constraint changes;
- [ ] `create_sale_with_items_v2`;
- [ ] atomic `update_courier_outcome_v2`;
- [ ] customer/debt/custody/stock correctness;
- [ ] concurrency/backward-compatibility/rollback tests;
- [ ] exact-head review and human merge.

### PR-B

- [ ] outcome-aware financial health/reporting;
- [ ] canonical debt/custody/store-cash reconciliation;
- [ ] exact-head regression proof and human merge.

### PR-C

- [ ] Advanced Sale primary on desktop/mobile/post-sale;
- [ ] Quick Sale secondary direct/cash/full-paid/customer-free only;
- [ ] courier wording/status UI;
- [ ] mobile RTL + desktop core-flow proof;
- [ ] preserve UI save guards as defense in depth;
- [ ] exact-head review and human merge.

## Phase 4 — FIN-IDEM

- [ ] Re-run Gate-4 readiness against canonical `create_sale_with_items_v2`.
- [ ] Sequential replay test.
- [ ] Same-key/different-payload conflict test.
- [ ] Concurrent duplicate test.
- [ ] Lost-response retry test.
- [ ] Failure-then-retry test.
- [ ] Tenant isolation test.
- [ ] Result fidelity test.
- [ ] Exactly-one stock/payment/debt/custody effect proof.
- [ ] Explicit human Gate-4 approval.
- [ ] Server/database idempotency implementation.
- [ ] Exact-head verification and human merge.

## Phase 5 — Pilot RC1

Create one exact release-candidate SHA and freeze it.

- [ ] frozen dependency install GREEN;
- [ ] typecheck/lint/unit/build GREEN;
- [ ] fresh isolated migration chain GREEN;
- [ ] T1–T15 GREEN;
- [ ] FIN-COURIER GREEN;
- [ ] FIN-IDEM retry/concurrency GREEN;
- [ ] tenant isolation GREEN;
- [ ] SEC-CI GREEN;
- [ ] SEC-ENV GREEN;
- [ ] mobile RTL + desktop core flows GREEN;
- [ ] backup procedure documented;
- [ ] restore procedure actually verified;
- [ ] rollback/compensation procedure reviewed;
- [ ] release notes and known limitations recorded;
- [ ] explicit human RC1 approval.

## Phase 6 — Owner-only pilot

- [ ] 3–5 owner-operated stores only.
- [ ] Fix-only release mode.
- [ ] Measure activation and time-to-first-sale.
- [ ] Measure daily usage of sales, expenses, debt, day close, and courier settlement.
- [ ] Measure reconciliation variance.
- [ ] Measure failed/duplicate writes.
- [ ] Measure D1/D7/D14/D30 retention.
- [ ] Measure willingness to pay.
- [ ] Review evidence before opening post-pilot roadmap.

## Deferred until pilot evidence

Employee accounts/RBAC/assignment, payroll, attendance, commissions, GPS, internal chat, multi-branch, broad analytics, and AI product features remain outside this release path.
