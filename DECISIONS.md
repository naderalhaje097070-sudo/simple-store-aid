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
- Consequence: Corrections are additive commits or new branches/PRs.

## Pending decisions

- Employee assignment source of truth: existing `orders.courier_id` versus a dedicated assignment model.
- Employee historical identity and hard-delete invariant after unlinking.
- Final role model and compatibility with README role documentation.
- Audit event model for employee order-state and custody changes.
