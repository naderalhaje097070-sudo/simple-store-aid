# Mongezz Tasks

## GOV-001 — Engineering governance bootstrap

**Status:** In progress  
**Current gate:** NAADF-CMF Change Gate 0 approved

Goal: add the repository governance, project-state, decision, security, database, testing, and review documentation.

Acceptance criteria:

- Required files exist and cross-reference correctly.
- Lovable history constraints and Mongezz financial invariants are preserved.
- The change contains documentation only.
- The documentation diff is reviewed and validated.
- Final integration remains a human decision.

## EMP-000 — Existing employee accounts proposal

**Status:** Blocked pending governed review

Known blockers:

- The existing proposal combines multiple architectural concerns.
- Recorded Auth UI and financial or employee regression workflows are failing.
- Baseline, impact, contract, rollback, and independent review artifacts are incomplete.

## EMP-001 — Baseline and reproduction

**Status:** Pending  
**Gate:** NAADF-CMF Change Gate 1

Document current and expected behavior, run the `main` baseline, reproduce failures, identify affected environments and data, and establish regression evidence.

## EMP-002 — Impact analysis

**Status:** Pending  
**Gate:** NAADF-CMF Change Gate 2

Analyze UI, RPCs, database, authentication, authorization, RLS, tenant isolation, financial rules, state transitions, reports, deployment, compatibility, migrations, tests, and rollback.

## EMP-003 — Change design

**Status:** Pending  
**Gate:** NAADF-CMF Change Gate 3

Define the smallest correct architecture, contracts, source of truth, transaction boundaries, idempotency, audit behavior, rollout, rollback, and acceptance criteria.

## EMP-004 — Safety net

**Status:** Pending  
**Gate:** NAADF-CMF Change Gate 4

Establish regression, database-contract, authorization, tenant-isolation, migration, concurrency, idempotency, financial-regression, and authenticated E2E coverage.

## EMP-005 — Incremental implementation

**Status:** Pending  
**Gate:** NAADF-CMF Change Gate 5

Deliver identity and RBAC, assignment and custody, and UI and E2E as focused reviewable changes.
