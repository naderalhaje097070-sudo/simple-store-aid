# Governed Tasks

## Active

### AUDIT-001 — Main containment and pilot baseline truth restoration

- Change type: Governance, release verification, and product readiness.
- Goal: Restore a consistent repository source of truth from the latest `main`, establish the release baseline, and define the blockers before an owner-only pilot.
- Baseline commit: `906df4b89369dff17e12060de47c6d32ecca47c4`.
- Scope:
  - `PROJECT_STATE.md`, `TASKS.md`, `DECISIONS.md`, and stale README facts.
  - Current `main` history and direct Lovable changes.
  - Final release checks on the clean PR head.
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
  - The clean branch was created directly from latest `main` without rewriting history.
  - Issue #22 records the courier-sale defects discovered during product review.
  - Final GitHub checks and human review are required before merge.
- Done when:
  - Repository state, decisions, tasks, and README are internally consistent.
  - Latest clean PR head passes Quality, full migration chain / T1–T15, and Isolated Auth UI Smoke.
  - Review findings are resolved against the actual final diff.
  - Human explicitly approves and merges the clean AUDIT-001 PR.
  - Any pilot-baseline tag is created only after the merge commit is verified.

## Immediate next change

### FIN-COURIER-001 — Courier sale workflow correction

- Issue: #22.
- Priority: P0 financial workflow blocker.
- Status: Change Intake recorded; implementation blocked until AUDIT-001 is merged and design/safety gates are approved.
- Reported defects:
  - customer is required for every courier order even when no customer debt exists;
  - courier-collected money can require an unclear manual delivery-state update before appearing in settlement;
  - primary sale actions open quick sale rather than the advanced workflow.
- Required business behavior:
  - direct fully paid sale: customer optional;
  - direct sale with debt: customer required;
  - courier pending delivery: customer optional and outside settlement;
  - courier fully collected: customer optional, money becomes custody, order appears immediately in settlement;
  - courier partially or not collected with resulting customer debt: customer required;
  - no courier-collected money enters store receipts before settlement;
  - advanced sale becomes the primary desktop, mobile, and post-sale workflow;
  - quick sale remains a secondary direct, cash, fully-paid, customer-free shortcut.
- Required gates before implementation:
  - verify latest effective RPC and CHECK-constraint definitions;
  - approve state mapping at sale creation;
  - approve backward compatibility for existing courier orders;
  - define forward-only migration and rollback/compensation plan;
  - add failing financial and UI tests before production code.
- Mandatory verification:
  - pending courier order without customer succeeds and stays outside settlement;
  - fully collected courier order without customer creates custody and appears immediately in settlement;
  - partial courier collection without customer is rejected;
  - partial courier collection with customer creates custody plus customer debt without double count;
  - no payment row is created before settlement;
  - settlement moves only stored custody into store receipts;
  - existing T1–T15 remain green;
  - mobile and desktop primary sale actions open advanced sale.

## Other pilot blockers

### SEC-ENV-001 — Environment isolation and fail-closed build resolution

- Priority: P0.
- Goal: Prevent local, CI, and preview builds from silently connecting to production Supabase.
- Required before pilot:
  - remove or tightly gate the production fallback;
  - fail closed when required variables are absent outside an explicit production deployment;
  - add environment-resolution tests;
  - prove staging and preview cannot target production accidentally.

### SEC-CI-001 — CI reporting hardening

- Priority: P0.
- Goal: Stop raw Supabase startup output and disposable local credentials from being copied to PR comments.
- Required before pilot:
  - post concise pass/fail evidence only;
  - redact environment details;
  - pin material tool versions;
  - ensure required checks run on the relevant merge path.

### FIN-IDEM-001 — Financial idempotency and retry safety

- Priority: P0.
- Goal: Prevent duplicate financial effects when a successful request is retried after a lost response.
- Required before pilot:
  - approved idempotency contract and request-hash behavior;
  - duplicate and conflicting-key behavior;
  - concurrency and retry tests;
  - forward-only migration and rollback/compensation design;
  - focused implementation after design and safety-net approval.

## Planned

### PILOT-000 — Owner-only controlled pilot

- Status: Blocked by AUDIT-001, FIN-COURIER-001, SEC-ENV-001, SEC-CI-001, FIN-IDEM-001, and final release verification.
- Target: 3–5 stores under direct supervision.
- Goal: Validate activation, daily usage, financial reconciliation, retention, and willingness to pay before employee expansion.
- No employee accounts are required for the first pilot.

### EMP-001 — Employee specification and impact analysis

- Status: Deferred until owner-only pilot evidence confirms priority and Change Gates 2–4 are approved.
- Planned output:
  - actors and role model;
  - assignment source of truth;
  - authorization matrix;
  - historical identity and hard-delete invariants;
  - custody and settlement contracts;
  - threat model, migration strategy, rollback, and test matrix.
- No production implementation.

### EMP-002 — Identity and authorization foundation

- Blocker: EMP-001 and approved Change Gates 2–4.
- Planned scope:
  - employee identity and membership model;
  - owner-controlled linking and disabling;
  - tenant and assignment isolation;
  - historical identity preservation;
  - audit and authorization tests.

### EMP-003 — Assignment, custody, and settlement contracts

- Blocker: Approved domain design and EMP-002 foundation.
- Planned scope:
  - assignment history and legal state transitions;
  - employee collection and custody rules;
  - settlement-request lifecycle;
  - idempotency, concurrency, audit, and financial regression tests.

### EMP-004 — Owner and employee UI

- Blocker: EMP-002 and EMP-003 contracts.
- Planned scope:
  - owner employee management;
  - assigned orders and personal custody for the employee;
  - typed client contracts and role routing;
  - RTL, desktop, and mobile behavior;
  - no UI-only authorization.

### EMP-005 — Employee E2E and pilot readiness

- Blocker: Completed implementation PRs and independent review.
- Planned scope:
  - Owner, Employee A, Employee B, disabled employee, and second-tenant scenarios;
  - production-like isolated environment;
  - rollback and operational checklist.

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
  - current and expected behavior;
  - reproduction evidence;
  - PR #17 scope map and decomposition;
  - recorded employee-account risks and unknowns.
- Implementation authorization: None.

### PR17-PROTOTYPE — Employee accounts prototype

- Pull request: #17.
- Result: Closed without merge as superseded.
- Reason:
  - oversized and diverged from current `main`;
  - combined database, authorization, UI, tests, and CI;
  - contained unresolved custody and lifecycle findings;
  - retained only as historical evidence.

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
