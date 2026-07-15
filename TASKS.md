# Tasks

## Active

### GOV-001 — Engineering Governance Bootstrap

- **Framework:** NAADF-CMF
- **Gate:** Change Gate 0 approved
- **Risk:** Medium
- **Goal:** Establish NAADF, NAADF-CMF, project-state management, delivery, security, database, testing, and review policies.
- **Scope:** Documentation only.
- **Out of scope:** Feature code, database migrations, dependency changes, merge, and deploy.
- **Branch:** `governance/naadf-bootstrap`
- **Done when:** Governance files exist, internal links are coherent, the diff contains no application or database changes, and a human-review PR is open.

## Blocked

### EMP-001 — Employee Accounts, Assigned Orders, and Personal Custody

- **Framework:** NAADF-CMF
- **Current gate:** Must restart at Change Gate 1 after governance approval.
- **Risk:** High
- **Related issue:** #16
- **Existing PR:** #17
- **Blockers:**
  - PR #17 is oversized and combines multiple architectural concerns.
  - Isolated Auth UI Smoke failed on the recorded PR head.
  - Ephemeral Financial Rules failed on the recorded PR head.
  - Current and expected behavior are not fully documented.
  - Authorization matrix, database invariants, audit contract, concurrency strategy, rollback plan, and independent review are incomplete.
- **Decision:** Do not merge PR #17. Use it as implementation evidence during baseline and impact analysis.

## Planned Sequence

1. **EMP-BASE-001 — Baseline and reproduction**
   - Record current `main` behavior and verification results.
   - Reproduce PR #17 failures without changing production.
   - Add failing regression evidence where appropriate.

2. **EMP-SPEC-001 — Specification and impact analysis**
   - Actors, roles, flows, business rules, state transitions, authorization matrix, threat model, data impact, API compatibility, migration impact, rollback impact, and acceptance criteria.

3. **EMP-AUTH-001 — Employee identity and authorization foundation**
   - Focused database and authorization change only.

4. **EMP-CUSTODY-001 — Assignment, delivery state, custody, and settlement contracts**
   - Focused financial-domain change with idempotency and concurrency tests.

5. **EMP-UI-001 — Owner and employee interfaces**
   - UI only after server and database contracts are approved.

6. **EMP-E2E-001 — Authenticated E2E and pilot readiness**
   - Owner, employee A, employee B, disabled employee, mobile, desktop, rollback, and pilot checklist.

## Deferred

- Payroll.
- Attendance.
- Automatic commissions.
- GPS tracking.
- Internal chat.
- Custom per-button permission builder.
