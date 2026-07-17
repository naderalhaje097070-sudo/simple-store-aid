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
  - A synchronized and release-verified `main` baseline.
  - Non-production environments cannot silently connect to production.
  - Financial write operations have approved retry and idempotency protection.
  - CI reports do not expose environment credentials and use deterministic tool versions.
  - Support, rollback, and reconciliation procedures are documented.
- Consequence: PR #17 is superseded and closed without merge. Employee work remains deferred until pilot evidence confirms priority and Change Gates 2–4 are approved.

## DEC-012 — Pilot blockers are release blockers

- Status: Accepted
- Decision: `SEC-ENV-001`, `SEC-CI-001`, and `FIN-IDEM-001` must be completed and release-verified before any real-store pilot data is accepted.
- Consequence: Pilot planning may proceed, but pilot execution remains blocked. A build or smoke-test success alone does not waive these controls.

## DEC-013 — Current role model is descriptive, not final authorization design

- Status: Accepted
- Decision: The current database enum is `owner | staff`. This records existing schema reality only; it does not authorize broad employee access or define the final employee/courier role model.
- Consequence: A future restricted employee capability model requires an approved authorization matrix, RLS design, negative tests, and backward-compatibility analysis.

## Pending decisions

- Employee assignment source of truth: existing `orders.courier_id` versus a dedicated assignment model.
- Employee historical identity and hard-delete invariant after unlinking.
- Final restricted employee/courier capability model beyond the existing `owner | staff` enum.
- Audit event model for employee order-state and custody changes.
- Final billing enforcement and expired-subscription behavior.
