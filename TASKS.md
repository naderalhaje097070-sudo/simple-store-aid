# Governed Tasks

## Active

### AUDIT-001 — Main containment and pilot baseline truth restoration

- Change type: Governance, release verification, and product readiness.
- Pull request: #21, open and unmerged.
- Goal: Restore a consistent repository source of truth, review direct changes that entered `main`, establish the latest release baseline, and define the blockers before an owner-only pilot.
- Scope:
  - `PROJECT_STATE.md`, `TASKS.md`, `DECISIONS.md`, and stale README facts.
  - Current `main` history and direct Lovable changes.
  - Final release checks on the latest synchronized PR head.
  - Explicit pilot blockers and sequencing.
- Out of scope:
  - Feature code.
  - New migrations, RLS, RPC, or schema changes.
  - Dependency or workflow changes.
  - Production access.
  - Merge, deploy, or tag creation without explicit human action.
- Current status:
  - PR #20 is merged.
  - PR #17 is closed without merge as a superseded prototype.
  - PR #21 was synchronized with current `main` without rewriting published history.
  - Final GitHub checks and human review are required before merge.
- Done when:
  - Repository state, decisions, tasks, and README are internally consistent.
  - Latest PR head passes Quality, full migration chain / T1–T15, and Isolated Auth UI Smoke.
  - Review threads are resolved based on actual changes.
  - Human explicitly approves and merges PR #21.
  - The pilot-baseline tag is created only after the merge commit is verified.

## Pilot blockers

### SEC-ENV-001 — Environment isolation and fail-closed build resolution

- Priority: P0.
- Goal: Prevent local, CI, and preview builds from silently connecting to production Supabase.
- Required before pilot:
  - Remove or tightly gate the production fallback.
  - Fail closed when required variables are absent outside an explicit production deployment.
  - Add environment-resolution tests.
  - Prove staging and preview cannot target production accidentally.

### SEC-CI-001 — CI reporting hardening

- Priority: P0.
- Goal: Stop raw Supabase startup output and local disposable credentials from being copied to PR comments.
- Required before pilot:
  - Post concise pass/fail evidence only.
  - Redact environment details.
  - Pin Supabase CLI and other material tool versions.
  - Ensure required checks run on the relevant merge path.

### FIN-IDEM-001 — Financial idempotency and retry safety

- Priority: P0.
- Goal: Prevent duplicate financial effects when a successful request is retried after a lost response.
- Required before pilot:
  - Approved idempotency contract and request-hash behavior.
  - Duplicate and conflicting-key behavior.
  - Concurrency and retry tests.
  - Forward-only migration and rollback/compensation design.
  - Implementation in focused PRs after design and safety-net approval.

## Planned

### PILOT-000 — Owner-only controlled pilot

- Status: Blocked by AUDIT-001, SEC-ENV-001, SEC-CI-001, FIN-IDEM-001, and final release verification.
- Target: 3–5 stores under direct supervision.
- Goal: Validate activation, daily usage, financial reconciliation, retention, and willingness to pay before employee expansion.
- No employee accounts are required for the first pilot.

### EMP-001 — Employee specification and impact analysis

- Status: Deferred until owner-only pilot evidence confirms priority and Change Gates 2–4 are approved.
- Planned output:
  - Actors and role model.
  - Assignment source of truth.
  - Authorization matrix.
  - Historical identity and hard-delete invariants.
  - Custody and settlement contracts.
  - Threat model, migration strategy, rollback, and test matrix.
- No production implementation.

### EMP-002 — Identity and authorization foundation

- Blocker: EMP-001 and approved Change Gates 2–4.
- Planned scope:
  - Employee identity and membership model.
  - Owner-controlled linking and disabling.
  - Tenant and assignment isolation.
  - Historical identity preservation.
  - Audit and authorization tests.

### EMP-003 — Assignment, custody, and settlement contracts

- Blocker: Approved domain design and EMP-002 foundation.
- Planned scope:
  - Assignment history and legal state transitions.
  - Employee collection and custody rules.
  - Settlement-request lifecycle.
  - Idempotency, concurrency, audit, and financial regression tests.

### EMP-004 — Owner and employee UI

- Blocker: EMP-002 and EMP-003 contracts.
- Planned scope:
  - Owner employee management.
  - Assigned orders and personal custody for the employee.
  - Typed client contracts and role routing.
  - RTL, desktop, and mobile behavior.
  - No UI-only authorization.

### EMP-005 — Employee E2E and pilot readiness

- Blocker: Completed implementation PRs and independent review.
- Planned scope:
  - Owner, Employee A, Employee B, disabled employee, and second-tenant scenarios.
  - Production-like isolated environment.
  - Rollback and operational checklist.

## Completed

### GOV-001 — Governance bootstrap

- Pull request: #19.
- Result: Reviewed and merged into `main`.
- Merge commit: `e7088a2c58bb514aac133f303627d4b829473934`.
- Verification: Quality, Ephemeral Financial Rules T1–T15, and Isolated Auth UI Smoke passed before merge.
- Deployment: Not performed.

### EMP-000 — Employee accounts baseline and decomposition

- Gate: NAADF-CMF Change Gate 1 — Baseline and Reproduction.
- Product source: Issue #16.
- Pull request: #20.
- Result: Reviewed and merged into `main`.
- Merge commit: `599f84de4ef7f472da075e3ddbf1648501cbc871`.
- Deliverables:
  - Current and expected behavior.
  - Reproduction evidence.
  - PR #17 scope map and decomposition.
  - Recorded employee-account risks and unknowns.
- Implementation authorization: None.

### PR17-PROTOTYPE — Employee accounts prototype

- Pull request: #17.
- Result: Closed without merge as superseded.
- Reason:
  - Oversized and diverged from current `main`.
  - Combined database, authorization, UI, tests, and CI.
  - Contained unresolved custody and lifecycle findings.
  - Retained only as historical evidence; approved work must follow the governed sequence.

## Deferred product scope

- Payroll.
- Attendance.
- Automatic commissions.
- GPS tracking.
- Internal chat.
- Custom per-button permissions.
- Multi-branch expansion.
- Additional MCP tools.
- AI features inside the product.
