# Governed Tasks

## Active

### BASELINE-SYNC-001 — Post-approval pilot baseline synchronization

- Change type: Governance and source-of-truth synchronization.
- Priority: P0 sequencing prerequisite.
- Goal: Synchronize repository state after AUDIT-001 / PR #23 and FIN-COURIER-001 Gate 0–3 / PR #24 were merged, and establish the exact sequencing boundary before Gate 4.
- Starting `main` observed when this branch was cut: `e5632bff40e292583fd778f232dd0b7af5eb0e06`.
- Scope:
  - `PROJECT_STATE.md`, `TASKS.md`, `DECISIONS.md`, and `changes/fin-courier-001/README.md`.
  - Record PR #23 and PR #24 as merged.
  - Record FIN-COURIER-001 Gates 0–3 as formally approved by the product owner.
  - Record that two dependency-resolution commits followed the PR #24 merge on `main`.
  - Establish that Gate 4 must branch from the verified `main` head after this synchronization is merged, not from a stale pre-merge SHA.
- Out of scope:
  - Gate 4 test implementation.
  - Financial production code.
  - New migrations, RPCs, schema, RLS, UI, dependency, or workflow changes.
  - PR-A, PR-B, PR-C.
  - Production access, deployment, or pilot execution.
- Done when:
  - Repository state, tasks, decisions, and the FIN-COURIER index are internally consistent.
  - The final diff is documentation only.
  - Required GitHub checks on the final PR head are reviewed.
  - A human explicitly merges the synchronization PR.
  - The resulting `main` SHA is verified before Gate 4 begins.

## Immediate next change

### FIN-COURIER-001 — Courier sale workflow correction

- Issue: #22.
- Priority: P0 financial workflow blocker.
- Status:
  - Gates 0–3: **APPROVED** by the product owner and merged through PR #24.
  - PR #24 approved head: `a652de164e3efeae707038f1769aee12a9e2474a`.
  - PR #24 merge commit: `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
  - Gate 4: **NEXT — not yet approved or implemented**.
  - PR-A / PR-B / PR-C: **BLOCKED until Gate 4 approval**.
- Reported defects:
  - customer is required for every courier order even when no customer debt exists;
  - courier-collected money can require an unclear manual delivery-state update before appearing in settlement;
  - primary sale actions open quick sale rather than the advanced workflow.
- Approved business behavior:
  - direct fully paid sale: customer optional;
  - direct sale with debt: customer required;
  - courier pending delivery: customer optional and outside settlement;
  - courier fully collected: customer optional, money becomes custody, order appears immediately in settlement;
  - courier partially or not collected with resulting customer debt: customer required;
  - no courier-collected money enters store receipts before settlement;
  - advanced sale becomes the primary desktop, mobile, and post-sale workflow;
  - quick sale remains a secondary direct, cash, fully-paid, customer-free shortcut.
- Gate 4 scope before implementation:
  - preserve existing T1–T15 regression behavior;
  - add failing/new-behavior financial tests for customer-less debt-free courier states and debt-creating states;
  - add effective CHECK-constraint tests and historical-data preflight tests;
  - add atomic state-transition and monotonic-custody tests;
  - add concurrency and retry-baseline tests;
  - add backward-compatibility and rollback tests;
  - add outcome-aware platform reporting tests;
  - add mobile RTL and desktop primary-flow tests.
- Mandatory verification target:
  - pending courier order without customer succeeds and stays outside settlement;
  - fully collected courier order without customer creates custody and appears immediately in settlement;
  - partial courier collection without customer is rejected;
  - partial courier collection with customer creates custody plus customer debt without double count;
  - no payment row is created before settlement;
  - settlement moves only stored custody into store receipts;
  - existing T1–T15 remain green;
  - mobile and desktop primary sale actions open advanced sale.
- Implementation sequence after Gate 4 approval:
  - **PR-A** — financial schema constraints + `create_sale_with_items_v2` + atomic `update_courier_outcome_v2` + SQL safety tests.
  - **PR-B** — outcome-aware platform health/reporting + regression tests.
  - **PR-C** — advanced-sale default + courier UI + wording + success/status display.

## Other pilot blockers

### SEC-ENV-001 — Environment isolation and fail-closed build resolution

- Priority: P0.
- Goal: Prevent local, CI, and preview builds from silently connecting to production Supabase.
- Required before pilot:
  - fail closed when required variables are absent outside an explicit production deployment;
  - add environment-resolution tests;
  - prove staging and preview cannot target production accidentally;
  - independently review all relevant client/SSR/build resolution paths before closing the blocker.

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

- Status: Blocked by FIN-COURIER-001, SEC-ENV-001, SEC-CI-001, FIN-IDEM-001, and final release verification.
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

### AUDIT-001 — Main containment and pilot baseline truth restoration

- Pull request: #23.
- Result: Reviewed and merged into `main`.
- Merge commit: `6946cddabecb184b0edcd5ffaf9a0dcc521ae2c6`.
- Scope: repository source-of-truth restoration and pilot blocker sequencing; documentation only.
- Verification before merge: Quality, full isolated migration chain / Financial Rules T1–T15, and Isolated Auth UI Smoke passed on the synchronized PR head.
- Deployment: Not performed.

### FIN-COURIER-G0-G3 — Courier sale contract design

- Pull request: #24.
- Result: Gates 0–3 formally approved by the product owner and documentation merged into `main`.
- Approved PR head: `a652de164e3efeae707038f1769aee12a9e2474a`.
- Merge commit: `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
- Deliverables:
  - intake and evidenced current/expected behavior;
  - dependency/data/security/API/migration/test/rollback impact analysis;
  - courier state machine and customer requirement contract;
  - backward-compatibility and rollback design;
  - mandatory Gate 4 test plan;
  - PR-A / PR-B / PR-C decomposition.
- Verification before merge: Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke passed on the exact approved PR head.
- Implementation authorization: None; Gate 4 is next.

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