# NAADF — New Application Architecture and Delivery Framework

Use this framework for a new project or an independently designed subsystem. Each stop gate requires explicit approval before the next stage begins.

## Operating priorities

1. Business-rule correctness.
2. Data integrity.
3. Security and authorization.
4. Architectural clarity.
5. Testability.
6. Code simplicity.
7. Performance.
8. Delivery speed.

Do not maximize code volume. Do not start implementation before the required gates are complete.

## Initial classification

Record:

- Work Mode.
- Project Type.
- Risk Level: Low / Medium / High.
- Missing Critical Information.
- Explicit Assumptions.
- Proposed First Gate.

Classify the work as one or more of: New Project, Existing Project Change, Bug Fix, Feature, Refactor, Database Change, Security Change, Dependency Upgrade.

## Gate 0 — Project Intake

Create or approve:

- `PROJECT_BRIEF.md`
- `GOALS.md`
- `SCOPE.md`
- `OUT_OF_SCOPE.md`
- `ASSUMPTIONS.md`
- `RISKS.md`
- `SUCCESS_METRICS.md`

Define the problem, users, value, scope, constraints, risks, sensitive data, expected scale, non-negotiable requirements, and measurable success criteria.

**Stop after Gate 0 and wait for approval.**

## Gate 1 — Discovery and Specification

Create:

- `PRD.md`
- `ACTORS_AND_ROLES.md`
- `USER_FLOWS.md`
- `BUSINESS_RULES.md`
- `STATE_TRANSITIONS.md`
- `EDGE_CASES.md`
- `ACCEPTANCE_CRITERIA.md`
- `NON_FUNCTIONAL_REQUIREMENTS.md`

Each requirement must define:

- Actor.
- Preconditions.
- Inputs.
- Expected behavior.
- Stored data.
- Permissions.
- Failure cases.
- Edge cases.
- Acceptance criteria.
- Verification method.

Review for ambiguity, contradictions, duplicate requirements, partial failure, missing permissions, and illegal state transitions.

**Stop after Gate 1 and wait for approval.**

## Gate 2 — Architecture and Data

Create:

- `ARCHITECTURE.md`
- `SYSTEM_CONTEXT.md`
- `MODULE_BOUNDARIES.md`
- `DATABASE_ERD.md`
- `TABLE_DICTIONARY.md`
- `DATABASE_INVARIANTS.md`
- `API_CONTRACTS/`
- `AUTHORIZATION_MATRIX.md`
- `THREAT_MODEL.md`
- `TEST_STRATEGY.md`
- `DEPLOYMENT_ARCHITECTURE.md`
- `ADRS/`

Fix before implementation:

- Source of truth for each entity.
- Module ownership.
- Business-logic location.
- Transaction boundaries.
- Authentication and authorization.
- Tenant isolation.
- Error model.
- Idempotency strategy.
- Audit strategy.
- Migration strategy.
- API compatibility.
- Backup and rollback strategy.

**Stop after Gate 2 and wait for approval.**

## Gate 3 — Foundation

Create only the foundation:

- Repository structure.
- Strict typing.
- Linting and formatting.
- Test framework.
- CI.
- Environment validation.
- Logging and typed error handling.
- Migration system.
- Authentication skeleton.
- Security baseline.

Also create:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.md`
- `DECISIONS.md`
- `TASKS.md`

Foundation succeeds only after actual install, typecheck, lint, tests, and build results are recorded.

## Gate 4 — First Vertical Slice

Implement one complete workflow:

UI → input validation → API → authentication → authorization → business rules → database transaction → audit → response → integration test → E2E test.

The slice must use real contracts and persistence. It must not be hardcoded or mock-only.

## Gate 5 — Incremental Delivery

Each feature task must contain:

- Goal.
- Context.
- Business rules.
- Constraints.
- Security requirements.
- Edge cases.
- Acceptance criteria.
- Required tests.
- Out of scope.
- Done when.

Use one coherent feature or change per PR. Keep refactors and dependency upgrades separate unless strictly required.

## Completion protocol

Every stage report must include:

- Summary.
- Root Cause for defects.
- Changed Files.
- Contracts Changed.
- Database Changes.
- Commands Executed.
- Tests Executed and actual results.
- Acceptance Criteria: Passed / Failed / Not verified.
- Security Review.
- Remaining Risks.
- Known Limitations.
- Unverified Items.
- Rollback Procedure.
- One next recommended task.
