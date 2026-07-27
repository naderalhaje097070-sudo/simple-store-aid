# Governed Tasks

## Active

### FIN-COURIER-G4 — Courier sale workflow safety net

- Parent change: `FIN-COURIER-001` / Issue #22.
- Priority: P0 financial workflow blocker.
- Gate: NAADF-CMF Change Gate 4 — Safety Net.
- Frozen baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`.
- Authoritative review PR: #27, Draft and unmerged.
- Status:
  - Gates 0–3: **APPROVED** and merged through PR #24.
  - Gate 4 assertions: **AUTHORED** across the approved TEST_PLAN.
  - Independent adversarial review: **COMPLETED WITH CORRECTIONS**; see `changes/fin-courier-001/GATE4_INDEPENDENT_REVIEW.md`.
  - Exact-head execution: **BLOCKED** because recent GitHub Actions jobs across both pre-existing and Gate-4 workflows complete before any step starts (`steps = None`).
  - Gate 4 approval: **NOT APPROVED**.
  - PR-A / PR-B / PR-C: **BLOCKED**.
- Safety-net scope authored:
  - existing T1–T15 preservation;
  - B1–B9 create/settlement contract;
  - effective CHECK matrix and historical preflight/validation;
  - atomic customer attachment and transition/state-machine matrix;
  - forced-failure atomicity;
  - returned-order baseline and audit evidence;
  - concurrency and retry baseline;
  - backward compatibility and five-state read-model snapshot;
  - outcome-aware platform reporting;
  - rollback endpoint and future corrective-rollback runner;
  - mobile RTL, desktop primary-flow, courier wording/status, and success-screen semantics.
- Independent-review corrections already applied:
  - negative CHECK cases now require the exact `orders_customer_required_when_debt` constraint rather than any `check_violation`;
  - courier UI legacy-state detection targets exact controls instead of page-wide debt/payment wording;
  - unknown browser/backend/runtime failures cannot be converted into accepted UI expected-RED evidence;
  - rollback H1 proves the original legacy CHECK semantics, not names/counts alone;
  - F1 compares normalized payment effects, not payment-row counts only;
  - B9 proves the full custody-to-receipt settlement effect.
- Current execution blocker:
  - recent exact-head Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke, Gate-4 backend, and Gate-4 UI jobs were created but reported no workflow steps;
  - no checkout, dependency install, build, migration, SQL test, or browser test ran in those attempts;
  - such runs are neither PASS nor expected RED and cannot approve the gate.
- Done when one exact final PR #27 head proves:
  - Quality GREEN;
  - Ephemeral Financial Rules / T1–T15 GREEN;
  - Isolated Auth UI Smoke GREEN;
  - Gate-4 backend true-GREEN baselines pass;
  - every pre-implementation target probe reaches its approved expected-RED sentinel rather than a harness/runtime failure;
  - final diff remains Gate-4 test/evidence/workflow/governance only;
  - a human explicitly approves Gate 4.
- Out of scope:
  - financial production implementation;
  - migration/RPC/schema/RLS implementation;
  - PR-C application UI implementation;
  - employee accounts;
  - SEC-ENV-001, SEC-CI-001, FIN-IDEM-001 implementation;
  - production access, deployment, or pilot execution.

## Immediate next change after Gate 4 approval

### FIN-COURIER-PR-A — Financial contract implementation

- Priority: P0.
- Blocker: FIN-COURIER Gate 4 exact-head evidence + explicit approval.
- Planned scope only after approval:
  - forward-only replacement constraint migration;
  - `create_sale_with_items_v2` as canonical sale RPC;
  - legacy six-parameter create adapter;
  - atomic `update_courier_outcome_v2` with row locking, transition validation, monotonic custody, and same-tenant customer attachment;
  - legacy transition adapter delegating to v2 safety;
  - typed client update;
  - all PR-A-target Gate-4 tests switch from expected RED to GREEN without weakening assertions.
- No PR-B reporting or PR-C UI work in PR-A.

### FIN-COURIER-PR-B — Outcome-aware reporting

- Priority: P0 after PR-A.
- Blocker: approved/merged PR-A and exact-head regression verification.
- Planned scope:
  - canonical SQL customer-debt source;
  - corrected `courier_missing_refs` and `debt_without_customer` health predicates;
  - corrected platform/tenant open-debt totals;
  - G1–G8 reporting tests GREEN.

### FIN-COURIER-PR-C — Advanced sale and courier UX

- Priority: P0 after PR-B.
- Blocker: approved/merged PR-B.
- Planned scope:
  - advanced sale becomes primary desktop/mobile/post-sale path;
  - quick sale remains secondary direct/cash/fully-paid shortcut;
  - courier-specific outcome controls and wording;
  - correct customer requirement UX;
  - success-screen and invoice operational-status semantics;
  - mobile/desktop Gate-4 UI probes GREEN.

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

### BASELINE-SYNC-001 — Post-approval pilot baseline synchronization

- Pull request: #26.
- Result: Reviewed and merged into `main`.
- Verified PR head: `396d683aadf94e466c230f2b63b284c944d26e4c`.
- Merge commit / Gate-4 baseline: `983b746e5c6639dcdc5e6557381ad5619abaa046`.
- Scope: repository source-of-truth synchronization after PR #23 and PR #24; documentation only.
- Verification before merge: Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke passed on the exact PR head.
- Deployment: Not performed.

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
