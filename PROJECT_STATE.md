# Project State

Last updated: 2026-08-09

## Current stage

`RELEASE-BASELINE-RECON-002` — reconcile the effective `main` branch with the fixed Pilot RC1 plan before any new P0 implementation is authorized.

Reconciliation start `main`:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

Accepted current Phase-0 baseline after human merge of PR #44:

`975a34a854c510f3da7dbe45caa9791bb0375e2d`

The current P0 Gate-4 workstreams were created from or stacked on the older governed baseline:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

At reconciliation start, `main` was 11 commits ahead of that older baseline and changed five paths. Before PR #44 was merged, additional direct repository history landed. The accepted current `main` is now 21 commits ahead of the older Gate-4 baseline with net changes across nine paths:

- `.github/workflows/isolated-auth-smoke.yml`
- `.lovable/plan.md` removed/moved into a dated plan file
- `.lovable/plan/اختبار-الضغط-المتكرر-على-زر-بيع-وحفظ-الفاتورة-mobile-390px-2026-08-09.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`
- `docs/rapid-click-sale-results.md`
- `tests/e2e/rapid-click-sale.py`

The application source drift still consists of the client-side sale-save guards already classified as defense in depth. The later rapid-click files are test/planning/evidence artifacts; they do not provide server-side idempotency and are not authorized for production execution.

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

### BASELINE-RUNTIME-001 / Issue #42

Resolved by explicit human merge of PR #44 as `975a34a854c510f3da7dbe45caa9791bb0375e2d`.

Evidence sequence:

- Phase-0 PR #41 originally reached a successful isolated Supabase start, QA seed, and production build, then failed before Playwright because the generated Worker compatibility date was `2026-08-09` while the local workerd binary supported through `2026-08-08`.
- PR #43 tested a dependency rollback hypothesis and reproduced the same failure, so it was closed without merge.
- PR #44 changed one local Auth Smoke command only, passing `--compatibility-date 2026-08-08` to `wrangler dev`.
- On PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937`, Quality, Ephemeral Financial Rules / T1–T15, and Isolated Auth UI Smoke all passed; Playwright executed successfully.
- No application logic, financial logic, dependency rollback, production access, or deployment was performed.

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

The newly landed `tests/e2e/rapid-click-sale.py` reinforces this requirement: its historical evidence says it used an injected owner session and could leave undeletable paid test orders. The script is not wired into an approved release gate and must not be run against production; future execution must use an isolated tenant and fail-closed environment proof.

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

The effective `main` contains client-side sale-save guards in BottomNav, Quick Sale, and PaymentSheet. The rapid-click QA artifact reports 6/6 human-style duplicate-click scenarios passed on one injected session, but this remains UI evidence only and does not alter the approved financial or idempotency contract.

### 4. FIN-IDEM-001 / Issue #31

Priority: P0 financial retry-safety blocker.

Current state:

- Gates 0–3: owner-approved.
- PR #39 is preparation/readiness only and remains dependency-blocked by the canonical FIN-COURIER sale v2.
- Current UI `saving`/`busy` guards and rapid-click results do not satisfy server-side idempotency.

Required contract:

- scope key by `tenant_id + operation + idempotency_key`;
- same key + same canonical request returns original result without a second financial effect;
- same key + different request fails deterministically;
- concurrent same-key calls commit one financial effect;
- failed transaction does not poison the key;
- replay still requires normal authorization and tenant isolation.

## Baseline drift impact

Compared with old Gate-4 baseline `983b746e5c6639dcdc5e6557381ad5619abaa046`, accepted current `main` `975a34a854c510f3da7dbe45caa9791bb0375e2d` is 21 commits ahead with nine changed paths. Material categories are:

1. client-side duplicate-click/save guards in the sale UI;
2. `@lovable.dev/vite-tanstack-config` `2.7.7` → `2.9.1` and lockfile changes;
3. planning-history relocation/update;
4. rapid-click sale QA script/results artifacts;
5. isolated Auth Smoke local-emulator compatibility-date containment merged through PR #44.

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

Complete exact-head checks on Phase-0 PR #41 after synchronizing its tree to accepted `main = 975a34a854c510f3da7dbe45caa9791bb0375e2d`, preserving all concurrent repository history. Then require an explicit human merge. After that merge, record the resulting `main` SHA and begin SEC-CI reconciliation from that exact baseline.

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
