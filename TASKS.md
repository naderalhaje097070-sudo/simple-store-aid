# Governed Tasks

## Active

### GOV-001 — Governance bootstrap

- Gate: NAADF-CMF Change Gate 0 approved.
- Pull request: #19, open and unmerged.
- Goal: Add repository-maintained NAADF, NAADF-CMF, delivery, security, database, testing, review, state, decision, and task documentation.
- Scope: Documentation only.
- Out of scope: Feature code, migrations, database access, dependency changes, merge, and deploy.
- Current status:
  - Governance files exist on the branch.
  - Diff contains documentation only.
  - Documentation links and internal consistency were reviewed.
  - Quality passed on commit `93379d9fc7b9538c5dd0d2955a6c9e10c19fb60e`.
  - Ephemeral Financial Rules and T1–T15 passed on the same commit.
  - Isolated Auth UI Smoke passed on the same commit.
  - PR #19 remains open.
  - Automatic merge and deployment are not enabled.
- Done when:
  - Completion report is produced.
  - PR remains open for explicit human review and merge approval.

## Blocked

### EMP-000 — Employee accounts baseline and decomposition

- Blocker: GOV-001 must be reviewed and merged by explicit human decision first.
- Current artifact: PR #17, open and unmerged.
- Reason blocked:
  - PR combines database, authorization, UI, tests, and CI.
  - Latest recorded Quality passed.
  - Latest recorded Isolated Auth UI Smoke failed.
  - Latest recorded Ephemeral Financial Rules failed.
  - Hard-delete history invariant is not verified.
- Next gate: NAADF-CMF Change Gate 1 — Baseline and Reproduction.

## Planned sequence

### EMP-001 — Specification and safety baseline

- Current and expected behavior.
- Requirements, business rules, state transitions, edge cases, and acceptance criteria.
- Authorization matrix, database invariants, threat model, and test strategy.
- No production implementation.

### EMP-002 — Identity and authorization foundation

- Employee identity model.
- Owner-controlled linking and disabling.
- Tenant isolation and RLS.
- Audit requirements.
- Migration and authorization tests.

### EMP-003 — Assignment, custody, and settlement contracts

- Assignment source of truth.
- Allowed employee state transitions.
- Custody and settlement request rules.
- Idempotency, concurrency, and financial regression tests.

### EMP-004 — Owner and employee UI

- Employee management for owner.
- Assigned orders and personal custody for employee.
- RTL, desktop, and mobile behavior.
- No UI-only authorization.

### EMP-005 — E2E and pilot readiness

- Owner, employee A, employee B, and disabled employee scenarios.
- Production-like isolated environment.
- Rollback review and pilot checklist.

## Deferred

- Payroll.
- Attendance.
- Automatic commissions.
- GPS tracking.
- Internal chat.
- Custom per-button permissions.
