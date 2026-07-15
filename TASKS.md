# Governed Tasks

## Active

### EMP-000 — Employee accounts baseline and decomposition

- Gate: NAADF-CMF Change Gate 1 — Baseline and Reproduction.
- Product source: Issue #16.
- Pull request: #20, open as a draft and unmerged.
- Reference implementation: PR #17, open and unmerged.
- Goal: Establish the approved current behavior, expected behavior, reproducible failure evidence, and decomposition boundary before impact analysis or implementation.
- Scope:
  - Current `main` behavior.
  - Expected product behavior.
  - PR #17 scope and branch state.
  - Latest recorded CI results.
  - Open review findings.
  - Reproduction procedures.
- Out of scope:
  - Feature code.
  - Migrations, RLS, RPCs, and schema changes.
  - Dependency or workflow changes.
  - Production access.
  - Merge or deploy.
- Current findings:
  - PR #17 is 51 commits ahead and 25 commits behind `main`.
  - PR #17 Quality passed.
  - PR #17 Isolated Auth UI Smoke failed during the authenticated owner/employee smoke.
  - PR #17 T1–T15 passed, but the employee-account and custody isolation suite failed.
  - Active unresolved P1: repeated employee delivery RPC calls may rewrite collected custody.
  - Outdated unresolved P1: disabling/unlinking may strand unsettled custody.
  - Exact failing SQL and Playwright assertions remain unverified and must be reproduced without guessing.
- Current status:
  - Gate 1 documents created.
  - PR #20 contains documentation only.
  - CI and independent review are pending on the latest head.
- Done when:
  - Gate 1 documents are internally consistent.
  - Documentation-only PR checks pass.
  - Human explicitly approves Gate 1.
- Next gate: Change Gate 2 — Impact Analysis.

## Completed

### GOV-001 — Governance bootstrap

- Gate: NAADF-CMF Change Gate 0.
- Pull request: #19.
- Result: Reviewed and merged into `main`.
- Merge commit: `e7088a2c58bb514aac133f303627d4b829473934`.
- Scope: Documentation only.
- Verification: Quality, Ephemeral Financial Rules / T1–T15, and Isolated Auth UI Smoke passed before merge.
- Deployment: Not performed.

## Blocked

### EMP-001 — Specification and safety baseline

- Blocker: EMP-000 Gate 1 must be reviewed and approved.
- Planned output:
  - Actors and roles.
  - Requirements and acceptance criteria.
  - Business rules and state transitions.
  - Edge cases and failure cases.
  - Authorization matrix.
  - Database invariants.
  - Threat model and test strategy.
- No production implementation.

### EMP-002 — Identity and authorization foundation

- Blocker: EMP-001 specification and Change Gates 2–4.
- Planned scope:
  - Employee identity model.
  - Owner-controlled linking and disabling.
  - Tenant isolation and RLS.
  - Historical identity preservation.
  - Audit requirements.
  - Migration and authorization tests.

### EMP-003 — Assignment, custody, and settlement contracts

- Blocker: Approved assignment source of truth and domain design.
- Planned scope:
  - Legal assignment and state transitions.
  - Collection and custody rules.
  - Settlement-request lifecycle.
  - Idempotency, concurrency, audit, and financial regression tests.

### EMP-004 — Owner and employee UI

- Blocker: EMP-002 and EMP-003 contracts.
- Planned scope:
  - Employee management for owner.
  - Assigned orders and personal custody for employee.
  - Typed client contracts and role routing.
  - RTL, desktop, and mobile behavior.
  - No UI-only authorization.

### EMP-005 — E2E and pilot readiness

- Blocker: Completed implementation PRs and independent review.
- Planned scope:
  - Owner, Employee A, Employee B, disabled employee, and second-tenant scenarios.
  - Production-like isolated environment.
  - Rollback review and pilot checklist.

## Planned governance follow-up

### SEC-CI-001 — Redact local Supabase keys from PR reports

- Change type: Security and CI reporting change.
- Reason: Historical workflow comments copied disposable local Supabase keys into PR discussions.
- Requirement: Report concise pass/fail evidence without printing startup credentials or tokens.
- Must use a separate NAADF-CMF change; not part of Employee Accounts Gate 1.

## Deferred product scope

- Payroll.
- Attendance.
- Automatic commissions.
- GPS tracking.
- Internal chat.
- Custom per-button permissions.
