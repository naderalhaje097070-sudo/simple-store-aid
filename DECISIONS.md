# Decisions

This file records accepted project decisions that affect architecture, business rules, security, data, or delivery. New material decisions require an ADR under `docs/governance/ADRS/` or a clearly linked change record.

## D-001 — Delivery Frameworks

**Status:** Accepted

- Use NAADF for new standalone projects.
- Use NAADF-CMF for every change to the existing Mongezz application.
- Implementation starts only after the applicable intake, baseline, impact, design, and safety gates are satisfied or explicitly approved.

## D-002 — Repository as Source of Truth

**Status:** Accepted

- Project files, migrations, tests, contracts, and recorded decisions override conversation memory.
- `PROJECT_STATE.md` is the current operational state.
- `DECISIONS.md` records stable decisions.
- `TASKS.md` records active and queued work.

## D-003 — Financial State Separation

**Status:** Accepted

- Customer debt, courier custody, merchant cash, and profit are separate concepts.
- Delivered does not mean settled.
- Courier collection remains custody until settlement is completed by an authorized owner-side operation.
- Returned orders do not create debt or custody.

## D-004 — Financial Mutation Boundary

**Status:** Accepted

- Financial mutations must execute through approved server-authorized, transactional RPCs or equivalent server boundaries.
- UI components do not own financial formulas or authorization decisions.
- Monetary values use PostgreSQL `numeric` or integer minor units.

## D-005 — Authorization and Tenant Isolation

**Status:** Accepted

- Deny by default.
- Enforce authorization and tenant isolation on the server and database layers.
- UI visibility is not an authorization boundary.
- IDOR and cross-tenant access require explicit negative tests.

## D-006 — Database Migration Policy

**Status:** Accepted

- Do not edit applied migrations.
- Use forward-only migrations.
- Separate large backfills from schema changes.
- High-risk changes require rollback or compensating migrations, lock analysis, and isolated migration tests.

## D-007 — Production Isolation

**Status:** Accepted

- Agents and automated destructive tests do not access production databases, production secrets, or real customer data.
- Automated database and E2E tests run in isolated non-production environments.
- Public test-cleanup RPCs are prohibited.

## D-008 — Human-Controlled Release

**Status:** Accepted

- No automatic merge or deployment.
- Destructive operations require explicit human approval.
- A green CI result is necessary but not sufficient; independent review and product acceptance remain required.

## D-009 — Lovable Git History

**Status:** Accepted

- Do not force-push, rebase, amend, or squash already-pushed repository history because the branch history synchronizes with Lovable.

## D-010 — Pull Request Scope

**Status:** Accepted

- One feature or one coherent change per PR.
- Functional PRs must not include unrelated broad refactors, global formatting, or dependency upgrades.
- Oversized PRs are treated as review inputs and must be decomposed before approval unless an explicit exception is documented.
