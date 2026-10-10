# Engineering Decisions

This file records decisions that govern Mongezz until replaced by an approved ADR or later decision entry.

## DEC-001 — Delivery methodology

- Status: Accepted
- Decision: Use NAADF for new projects or independently designed subsystems and NAADF-CMF for changes to the existing Mongezz application.
- Consequence: No implementation begins before the required intake, baseline, impact, design, and safety gates are completed.

## DEC-002 — Repository documentation is the source of truth

- Status: Accepted
- Decision: `PROJECT_STATE.md`, `DECISIONS.md`, `TASKS.md`, approved specifications, migrations, tests, and source code override conversational memory.
- Consequence: Project state must be updated before ending a material work session.

## DEC-003 — Financial state ownership

- Status: Accepted
- Decision: Financial rules belong in approved domain functions and authorized server-side/database transaction boundaries, not duplicated UI calculations.
- Consequence: Debt, remaining balance, courier custody, settlement, returns, and margin calculations require central ownership and regression tests.

## DEC-004 — Delivery and settlement are distinct states

- Status: Accepted
- Decision: `Delivered` does not mean `Settled`. Money collected by a courier remains custody until an authorized settlement records it in store receipts.
- Consequence: No UI, report, RPC, or migration may collapse these states.

## DEC-005 — Returned orders

- Status: Accepted
- Decision: A returned order must not create customer debt or courier custody and must restore inventory only through the approved return transaction.
- Consequence: Return behavior requires database and financial regression tests.

## DEC-006 — Tenant and employee isolation

- Status: Accepted
- Decision: Tenant and assignment restrictions are enforced server-side and by RLS using deny-by-default and least privilege.
- Consequence: Hiding UI elements is not authorization. Negative authorization and cross-tenant tests are mandatory.

## DEC-007 — Database migration policy

- Status: Accepted
- Decision: Applied migrations are immutable. Corrections use new forward-only migrations.
- Consequence: Breaking changes require expand-and-contract, compatibility analysis, and rollback or compensating migration planning.

## DEC-008 — Production boundary

- Status: Accepted
- Decision: Automated agents and isolated tests do not access production data, production secrets, or destructive production controls.
- Consequence: Destructive actions, merge, and deployment require explicit human action.

## DEC-009 — Pull-request scope

- Status: Accepted
- Decision: One coherent feature or change per PR. Broad refactoring, global formatting, and unrelated dependency upgrades are separate work.
- Consequence: PR #17 is not a release candidate and must be baselined and decomposed before employee-account implementation proceeds.

## DEC-010 — Lovable-linked history

- Status: Accepted
- Decision: Do not force-push, rebase, amend, or otherwise rewrite published history connected to Lovable.
- Consequence: Corrections are additive commits, merge commits, or new branches and PRs.

## DEC-011 — Pilot before employee expansion

- Status: Accepted
- Decision: Validate the owner-only financial core with a controlled pilot before implementing employee accounts.
- Preconditions:
  - a synchronized and release-verified `main` baseline;
  - non-production environments cannot silently connect to production;
  - financial write operations have approved retry and idempotency protection;
  - CI reports do not expose environment credentials and use deterministic tool versions;
  - support, rollback, and reconciliation procedures are documented.
- Consequence: PR #17 is superseded and closed without merge. Employee work remains deferred until pilot evidence confirms priority and Change Gates 2–4 are approved.

## DEC-012 — Pilot blockers are release blockers

- Status: Accepted
- Decision: `FIN-COURIER-001`, `SEC-ENV-001`, `SEC-CI-001`, and `FIN-IDEM-001` must be completed and release-verified before any real-store pilot data is accepted.
- Consequence: Pilot planning may proceed, but pilot execution remains blocked. A build or smoke-test success alone does not waive these controls.

## DEC-013 — Current role model is descriptive, not final authorization design

- Status: Accepted
- Decision: The current database enum is `owner | staff`. This records existing schema reality only; it does not authorize broad employee access or define the final employee/courier role model.
- Consequence: A future restricted employee capability model requires an approved authorization matrix, RLS design, negative tests, and backward-compatibility analysis.

## DEC-014 — Courier sale, customer, custody, and primary sale flow

- Status: Accepted
- Approval record: FIN-COURIER-001 Gates 0–3 were explicitly approved by the product owner on PR #24 head `a652de164e3efeae707038f1769aee12a9e2474a` after the required Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke checks passed on that exact head. The documentation contract was merged through PR #24 as merge commit `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
- Decision:
  - customer identity is required when a transaction creates customer debt, not merely because delivery uses a courier;
  - a courier order still pending delivery may exist without a customer and remains outside financial settlement;
  - money explicitly recorded as already collected by a courier is stored as courier custody, not store cash;
  - a fully collected courier sale is represented as `delivered_full` and is immediately eligible for settlement;
  - a partially collected courier sale is represented as `delivered_partial`; the collected amount is custody and the remainder is customer debt, therefore a customer is mandatory;
  - delivery without collection that creates debt requires a customer;
  - advanced sale is the primary sale workflow on desktop, mobile, and post-sale navigation;
  - quick sale remains an explicit secondary shortcut for direct, cash, fully-paid, customer-free sales.
- Consequence:
  - effective database constraints and RPC validation must be corrected through a forward-only migration;
  - the UI must use courier-specific states rather than ambiguous direct-payment labels;
  - existing T1–T15 plus new financial, state-transition, mobile, and desktop tests are mandatory;
  - `Delivered` remains distinct from `Settled`;
  - Gate 4 safety-net work is the only next FIN-COURIER stage authorized for preparation; PR-A, PR-B, and PR-C remain blocked until Gate 4 evidence is independently reviewed and explicitly approved;
  - after the baseline-synchronization PR is merged, the Gate 4 branch must be cut from the verified resulting `main` head rather than from a stale earlier SHA.

## Pending decisions

- Employee assignment source of truth: existing `orders.courier_id` versus a dedicated assignment model.
- Employee historical identity and hard-delete invariant after unlinking.
- Final restricted employee/courier capability model beyond the existing `owner | staff` enum.
- Audit event model for employee order-state and custody changes.
- Final billing enforcement and expired-subscription behavior.
- Final backward-compatibility treatment for existing courier orders that are `pending` but contain inconsistent legacy financial fields.


## DEC-015 — Original-project source and pinned execution plan

- Status: Owner-directed planning/governance; documentation candidate on a review branch.
- Owner instruction on 2026-10-09: consolidate instructions from both repositories,
  define the final-product plan, then pin starting steps so work can begin.
- Source: `naderalhaje0970-droid/simple-store-aid`; verified main `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
- Current plan: `docs/PRIMARY_DELIVERY_PLAN.md`; one current state/task queue.
- `mongezz` and PR137 retain historical evidence only; transfer candidates require
  source comparison and new verification. Plan1.2 identifiers are mapping history.
- Scheduling adjustment: prepare PRIMARY-SEC-001 dependency-security work before
  environment acceptance and financial write verification; reconcile SEC-CI and
  existing PR48/49/50 rather than repeat them from stale August instructions.
- This record does not approve an unreviewed financial policy, waive NAADF-CMF,
  close a release gate, merge, deploy, or authorize production access.

## DEC-016 — Framework transport and serializer candidate pins (2026-10-09)

Within the owner's authorized security batch, use the official minimum patched react-start1.168.60 graph with matching react-router1.170.41/router-plugin1.168.42. Preserve Lovable2.9.1. Pin Seroval1.6.7 in its direct declaration, overrides and resolutions because the old lock is affected and the new framework requires ^1.6.7. Retain seroval-plugins policy and all unrelated root declarations.

Use provider ErrorComponentProps in the two error boundaries; retain behavior and accept error:unknown without casts. Generated route/lock files come from their generators. Lock resolution uses Bun1.3.14 with the existing24-hour release-age policy; the current CI Bun1.2.14 was tested for frozen-install compatibility but its supply-chain enforcement gap is not claimed fixed.

Candidate status only: native29 tests/typecheck/build pass; existing lint, broader audit, hosted CI and review block global acceptance. PRIMARY-SEC-002 is prioritized by newly proven audit evidence before PRIMARY-ENV-001. No financial rule, schema, release approval, merge or deployment decision is changed. See changes/primary-sec-001/VERIFICATION.md.

## DEC-017 — Critical/High dependency advisory floors (2026-10-10)

- Status: Candidate decision in the owner's authorized security batch; not merged or released.
- Decision: preserve explicit patched floors for current Critical/High audit groups: `@modelcontextprotocol/sdk` 1.31.0, `proxy-addr` 2.0.8, `shell-quote` 1.11.0, `brace-expansion` 1.1.21 / 2.1.7 / 5.0.12 by major line, `browserslist` 4.29.3, `fast-uri` 3.1.8, `ip-address` 10.7.3, `js-yaml` 4.3.2, `nanoid` 3.3.19, `postcss` 8.5.29, and `source-map-js` 1.2.2.
- Rationale: `bun audit` on the prior candidate still reported 2 Critical and 33 High package/advisory records. After these floors, current audit has 0 Critical and 0 High records.
- Tooling note: Bun 1.3.14 did not apply nested overrides for the three `brace-expansion` major lines, so the lockfile carries the compatible major-specific entries and the unit guard enforces them. Frozen install was verified with Bun 1.3.14 and Bun 1.2.14.
- Consequence: future dependency refreshes must keep the dependency-security guard green and must not silently reintroduce the vulnerable floors. Remaining Moderate/Low audit records, hosted CI, independent review, runtime auth/MCP, financial gates, merge, and deployment remain outside this decision.

## DEC-018 - Generator-owned PRIMARY-SEC-002 lock remediation (2026-10-10)

- Status: Candidate implementation under the owner's authorized review-remediation request; final review/hosted CI remain open.
- Supersedes the manual-lock procedure described in DEC-017, preserving its patched security floors.
- Use verified Bun 1.4.0 transitive update support on the original PR52 lock and the final manifest/config. Do not hand-edit generated lock entries. See `changes/primary-sec-002/LOCK_REGENERATION.md` for source blobs, commands and graph impact.
- Pin `@lovable.dev/mcp-js` to the already-tested/resolved 0.20.1 to avoid an accidental downgrade during regeneration. Remove unsupported brace-expansion resolution paths; preserve the major-aware dependency guard and frozen installations.
- Keep the existing 24-hour resolution-age configuration and exclusions unchanged. The regenerated lock remains version 1 and installs with Bun 1.2.14 and 1.3.14; no CI toolchain or application runtime upgrade is made here.
- Put the synthetic MCP adapter compatibility tests in `tests/unit` so existing Quality includes them. These tests do not approve application JWT, tenant isolation or financial behavior.
- Hosted execution is blocked by the observed GitHub account payment/spending annotation. No billing change, spending increase, merge or deployment is authorized by this engineering decision.
