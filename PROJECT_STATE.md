# Project State

Last updated: 2026-08-09

## Current stage

`RELEASE-BASELINE-RECON-002` — reconcile the effective `main` branch with the fixed Pilot RC1 plan before any new P0 implementation is authorized.

Current `main` observed at reconciliation start:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

The current P0 Gate-4 workstreams were created from or stacked on the older governed baseline:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

GitHub comparison shows current `main` is 11 commits ahead and changes five paths:

- `.lovable/plan.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`

The project remains a Functional MVP being stabilized into a reproducible, financially safe owner-only release candidate. No pilot or production-release authorization exists yet.

## Current release freeze

Until Pilot RC1 is explicitly approved:

- no new product features enter the release critical path;
- no employee accounts, payroll, attendance, GPS, chat, commissions, multi-branch, AI, or broad analytics;
- no direct product/dependency change to `main` outside a reviewed PR path;
- no automatic merge or deploy;
- no production data/secrets are used by isolated verification;
- any Critical/High financial-correctness or tenant-isolation defect blocks pilot;
- published Lovable-linked history is not rewritten;
- applied migrations remain immutable and corrections use forward-only migrations.

## Completed / resolved

### Governance and financial design

- Governance bootstrap merged through PR #19.
- Employee-account prototype PR #17 was superseded and closed without merge.
- AUDIT-001 baseline restoration merged through PR #23.
- FIN-COURIER-001 Gates 0–3 were owner-approved and merged through PR #24.
- SEC-CI-001, SEC-ENV-001, and FIN-IDEM-001 Gates 0–3 were owner-approved on 2026-07-28; their implementation remains gated.

### OPS-GHA-001 / Issue #36

Resolved on 2026-08-01. GitHub-hosted Actions again reaches real workflow steps and logs after the monthly Actions quota reset. Remaining failures are repository/test evidence, not runner acquisition failures.

## Current P0 workstreams

### 1. SEC-CI-001 / Issue #29

Goal: deterministic and secret-safe release CI.

Current evidence:

- Gate-4 PR #37 is Draft and unmerged.
- SEC-CI Gate-4 policy probe reached real execution and passed.
- Standard Quality reached lint/format validation and failed on formatting in `tests/gate4/sec-ci/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Required before implementation:

- reconcile the Gate-4 branch to the accepted current release baseline;
- correct test-quality failures without weakening the contract;
- prove the final stable Supabase CLI/tool pin on a real runner;
- preserve T1–T15 and Auth Smoke;
- independently review exact-head evidence;
- explicit human Gate-4 approval.

### 2. SEC-ENV-001 / Issue #30

Goal: local/CI/preview/staging must fail closed and must not silently target production Supabase.

Current evidence:

- Gate-4 PR #38 is Draft and unmerged.
- SEC-ENV Gate-4 isolation probe reached real execution and passed.
- Standard Quality reached repository validation and failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Approved target remains:

`MONGEZZ_DEPLOY_TARGET = local | ci | preview | staging | production`

Non-production requires explicit non-production configuration and rejects the production target. Production requires explicit production intent and explicit approved configuration. No source-code production fallback is accepted.

### 3. FIN-COURIER-001 / Issue #22

Priority: P0 financial workflow blocker.

Approved business contract remains unchanged:

- direct fully paid: customer optional;
- direct debt: customer required;
- courier pending: customer optional and outside settlement;
- courier fully collected: customer optional; collected money is courier custody and becomes immediately settlement-eligible;
- courier partial/none that creates customer debt: customer required;
- courier-collected money does not enter store receipts before settlement;
- Advanced Sale is primary; Quick Sale is a secondary direct/cash/fully-paid shortcut;
- Delivered is not Settled.

Current exact-head evidence on PR #27 head `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- FIN-COURIER UI contract: GREEN;
- FIN-COURIER backend contract: real execution reached the consolidated safety net and failed with exit code `3`.

This is a real Gate-4 evidence failure, not infrastructure failure. Gate 4 is **NOT APPROVED**. PR-A / PR-B / PR-C remain blocked.

The effective `main` now also contains client-side sale-save guards in BottomNav, Quick Sale, and PaymentSheet. These UI guards must be included in the reconciliation of FIN-COURIER UI assumptions, but they do not alter the approved financial contract.

### 4. FIN-IDEM-001 / Issue #31

Priority: P0 financial retry-safety blocker.

Current state:

- Gates 0–3: owner-approved.
- PR #39 is preparation/readiness only and remains dependency-blocked by the canonical FIN-COURIER sale v2.
- Current UI `saving`/`busy` guards do not satisfy server-side idempotency.

Required contract:

- scope key by `tenant_id + operation + idempotency_key`;
- same key + same canonical request returns original result without a second financial effect;
- same key + different request fails deterministically;
- concurrent same-key calls commit one financial effect;
- failed transaction does not poison the key;
- replay still requires normal authorization and tenant isolation.

## Baseline drift impact

Since the old Gate-4 baseline, effective `main` added:

1. client-side duplicate-click/save guards in the sale UI;
2. an update of `@lovable.dev/vite-tanstack-config` from `2.7.7` to `2.9.1` and corresponding lockfile changes;
3. planning-file updates.

Therefore no P0 Gate-4 approval may rely solely on stale exact-head evidence. Each workstream must reconcile its relevant assumptions to the accepted release baseline and run authoritative checks on its final exact head.

Client-side duplicate-click protection remains defense-in-depth only. It does not replace `FIN-IDEM-001`.

## Fixed critical path

1. Complete `RELEASE-BASELINE-RECON-002` and human-merge it.
2. Record the resulting `main` SHA.
3. SEC-CI Gate 4 reconciliation → exact-head proof → independent review → human approval.
4. SEC-CI focused implementation → exact-head verification → human merge.
5. SEC-ENV Gate 4 reconciliation → exact-head proof → independent review → human approval.
6. SEC-ENV focused implementation → exact-head verification → human merge.
7. FIN-COURIER Gate 4 backend-failure diagnosis/reconciliation → exact-head proof → independent financial review → human approval.
8. FIN-COURIER PR-A → PR-B → PR-C, each focused and release-verified.
9. FIN-IDEM Gate 4 against canonical sale v2 → human approval → focused implementation.
10. Create one exact Pilot RC1 commit and run all financial/security/reliability/UX/recovery gates together.
11. Explicit human RC1 approval.
12. Controlled owner-only pilot with 3–5 stores.

## Financial decisions that must not change

- Sale is not Cash.
- Delivered is not Settled.
- Customer debt is not Courier custody.
- Returned orders create no customer debt and no courier custody and restore stock only through the approved return transaction.
- A customer is required only when an operation creates customer debt.
- Money explicitly recorded as collected by a courier is custody, not store cash, until settlement.
- Pending courier delivery remains outside settlement until an outcome is recorded.
- Financial writes use authorized server-side/database transactional boundaries.
- Tenant isolation is enforced server-side and with RLS.
- No UI-only control is accepted as the sole protection for financial correctness or authorization.

## Pilot scope

The first pilot remains owner-only and targets 3–5 directly supervised stores. Employee accounts remain deferred until owner-only pilot evidence is reviewed.

Pilot entry is blocked by:

- FIN-COURIER-001;
- SEC-CI-001;
- SEC-ENV-001;
- FIN-IDEM-001;
- final exact-head Pilot RC1 verification;
- explicit human release approval.

## Immediate next task

Finish this documentation-only baseline reconciliation through required checks and explicit human merge. Then verify the resulting `main` SHA and begin the SEC-CI reconciliation from that exact baseline.

Do not begin SEC-CI implementation, SEC-ENV implementation, FIN-COURIER PR-A/B/C, FIN-IDEM implementation, pilot execution, or deployment before their stated gate is satisfied.

## Standard verification

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

When a change affects financial or authenticated application behavior, the appropriate isolated financial and authenticated UI suites are additionally mandatory. GitHub checks on the exact final PR head are the authoritative verification source.
