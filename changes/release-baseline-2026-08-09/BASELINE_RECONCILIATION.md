# RELEASE-BASELINE-RECON-002 — 2026-08-09

## Purpose

Reconcile the actual `main` branch with the governed Pilot RC plan before any new P0 implementation is authorized.

This change is documentation/governance only. It does not modify production financial logic, migrations, RPCs, RLS, application behavior, deployment, or production data.

## Exact baselines

Reconciliation start `main`:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

Previous Gate-4 baseline used by the current P0 workstreams:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

Accepted current Phase-0 baseline after explicit human merge of PR #44:

`975a34a854c510f3da7dbe45caa9791bb0375e2d`

At reconciliation start, `main` was 11 commits ahead of the old Gate-4 baseline and changed five paths. Additional repository history landed before the #44 merge. Comparing the accepted current Phase-0 baseline directly with the old Gate-4 baseline now shows **21 commits ahead** and net changes across **nine paths**:

- `.github/workflows/isolated-auth-smoke.yml`
- `.lovable/plan.md` removed/moved
- `.lovable/plan/اختبار-الضغط-المتكرر-على-زر-بيع-وحفظ-الفاتورة-mobile-390px-2026-08-09.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`
- `docs/rapid-click-sale-results.md`
- `tests/e2e/rapid-click-sale.py`

The Phase-0 reconciliation PR must preserve all of this accepted `main` history rather than silently reverting concurrent changes.

## Material drift classification

### UI sale-save guards

The effective application contains client-side duplicate-click guards in the sale paths:

- mobile `+ Sale` navigation uses a temporary `busy`/`disabled` guard;
- Quick Sale uses local `saving` state and rejects a second local save invocation while the first is active;
- Advanced Sale `PaymentSheet` uses local `saving`, disables save while active, and prevents closing during the save.

These are UI controls only. They do **not** replace server-side financial idempotency and do not close `FIN-IDEM-001`.

### Dependency drift

`@lovable.dev/vite-tanstack-config` moved from `2.7.7` to `2.9.1` with corresponding lockfile changes.

Impact:

- release checks must run against the current dependency graph;
- SEC-CI exact-head evidence cannot be accepted solely from an older dependency baseline.

### Rapid-click QA artifacts

The accepted `main` now contains:

- a dated Lovable plan for mobile rapid-click sale verification;
- `docs/rapid-click-sale-results.md` reporting 6/6 UI duplicate-click scenarios passed;
- `tests/e2e/rapid-click-sale.py`.

The result document explicitly states the historical run used an injected real owner session in a local dev-server context and left paid test orders that could not be deleted under financial policy. The script reads Supabase configuration from `.env`, uses the injected user session, writes a test product/orders, and later attempts cleanup through normal production RPCs.

Classification:

- this is **not** server-side idempotency evidence;
- it is **not** approved for production execution;
- it is not currently an approved release workflow;
- future execution must be isolated to a disposable/non-production tenant and fail closed before any write if the target is production or ambiguous;
- the historical files are preserved as accepted repository history, not rewritten during Phase 0.

### Phase-0 authenticated-smoke containment

The first synchronized Phase-0 run reached successful isolated Supabase start, QA seed, and production application build, but failed before Playwright because generated Worker config required compatibility date `2026-08-09` while the local workerd binary supported through `2026-08-08`.

PR #43 tested a dependency rollback and reproduced the failure, so it was closed without merge.

PR #44 changed only the isolated local emulator command to pass `--compatibility-date 2026-08-08`.

On PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- Cloudflare emulator: GREEN;
- Playwright installation and read-only authenticated smoke: GREEN.

PR #44 was explicitly human-approved and merged as `975a34a854c510f3da7dbe45caa9791bb0375e2d`. No deployment or production access occurred in that merge operation.

## Current P0 evidence status

### OPS-GHA-001 / #36

Resolved on 2026-08-01. GitHub-hosted Actions execution reaches real job steps and logs.

### BASELINE-RUNTIME-001 / #42

Resolved by PR #44. Rejected rollback candidate PR #43 is closed without merge.

### SEC-CI-001 / #29

- Gates 0–3: owner-approved.
- Gate-4 PR #37: policy probe reached real execution and passed.
- Standard Quality previously failed on formatting in `tests/gate4/sec-ci/probe.ts`.
- Gate 4 remains **NOT APPROVED**.

### SEC-ENV-001 / #30

- Gates 0–3: owner-approved.
- Gate-4 PR #38: isolation probe reached real execution and passed.
- Standard Quality previously failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`.
- The rapid-click script's target ambiguity reinforces the fail-closed environment requirement.
- Gate 4 remains **NOT APPROVED**.

### FIN-COURIER-001 / #22

On PR #27 exact head `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- FIN-COURIER UI contract: GREEN;
- FIN-COURIER backend contract: executed real steps and failed with exit code `3`.

This is an application/test-evidence blocker, not runner acquisition failure. Gate 4 remains **NOT APPROVED** and PR-A/PR-B/PR-C remain blocked.

### FIN-IDEM-001 / #31

- Gates 0–3: owner-approved.
- PR #39 remains dependency-aware preparation only.
- Full target behavior must wait for canonical `create_sale_with_items_v2` from FIN-COURIER PR-A.
- UI save guards and the rapid-click 6/6 result do not satisfy the idempotency contract.

## Release freeze effective from this reconciliation

Until Pilot RC1 is approved:

1. No new product features enter the critical path.
2. No employee-account, payroll, attendance, GPS, chat, commission, multi-branch, AI, or broad analytics work.
3. No direct product/dependency change to `main` outside a reviewed PR path.
4. No automatic merge or deploy.
5. Any Critical/High financial-correctness or tenant-isolation defect blocks pilot.
6. Published Lovable-linked history is not rewritten.
7. Corrections use additive commits/branches/PRs and forward-only migrations.
8. Test harnesses capable of financial writes must not run against production or an ambiguous target.

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

- `PROJECT_STATE.md` and `TASKS.md` reflect the accepted current repository state;
- reconciliation start SHA is recorded;
- accepted Phase-0 baseline `975a34a854c510f3da7dbe45caa9791bb0375e2d` is recorded;
- direct comparison with old Gate-4 baseline records 21 commits / nine net changed paths;
- concurrent rapid-click test/planning history is preserved and its production-execution risk is classified;
- stale Gate-4 evidence is explicitly classified as requiring reconciliation before approval;
- the P0 sequence is fixed;
- final PR #41 diff relative to accepted `main` is documentation/governance only;
- required checks on the exact final PR head are reviewed;
- a human explicitly merges PR #41;
- the resulting post-merge `main` SHA is recorded as the baseline for SEC-CI reconciliation.

No automatic merge or deployment is authorized by this document.
