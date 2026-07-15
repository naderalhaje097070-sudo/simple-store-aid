# NAADF — New Application Architecture and Delivery Framework

Use this framework only for a new standalone project or a genuinely independent system. Changes to Mongezz use `NAADF-CMF.md`.

## Governing Priorities

Apply these priorities in order:

1. Correct business rules.
2. Data integrity.
3. Security and authorization.
4. Clear architecture.
5. Testability.
6. Code simplicity.
7. Performance.
8. Delivery speed.

Do not optimize for maximum code volume.

## Mandatory Intake Classification

Before implementation, record:

- Work Mode
- Project Type
- Risk Level: Low, Medium, or High
- Missing Critical Information
- Explicit Assumptions
- Proposed First Gate

Do not hide assumptions. Ask only for information that prevents a correct implementation and cannot be derived from project sources.

## Gate 0 — Project Intake

Create or propose:

- `PROJECT_BRIEF.md`
- `GOALS.md`
- `SCOPE.md`
- `OUT_OF_SCOPE.md`
- `ASSUMPTIONS.md`
- `RISKS.md`
- `SUCCESS_METRICS.md`

Define:

- Problem
- Target users
- Value proposition
- Scope
- Constraints
- Risks
- Success criteria

Stop after Gate 0 and wait for explicit approval.

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

Every requirement must define:

- Actor
- Preconditions
- Inputs
- Expected behavior
- Stored data
- Permissions
- Failure cases
- Edge cases
- Acceptance criteria
- Verification method

Review for ambiguity, contradictions, unspecified states, duplicate requirements, partial failure, missing permissions, and illegal state transitions.

Stop after Gate 1 and wait for explicit approval.

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

Fix the following before implementation:

- Source of truth for every entity
- Module ownership
- Business-logic location
- Transaction boundaries
- Authentication
- Authorization
- Tenant isolation
- Error model
- Idempotency strategy
- Audit strategy
- Migration strategy
- API compatibility
- Backup and rollback strategy

Stop after Gate 2 and wait for explicit approval.

## Gate 3 — Foundation

Create only the foundation:

- Repository structure
- Strict typing
- Linting and formatting
- Test framework
- CI
- Environment validation
- Logging
- Error handling
- Migration system
- Authentication skeleton
- Security baseline

Also create:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.md`
- `DECISIONS.md`
- `TASKS.md`

Foundation is not accepted until the actual commands are executed and reported:

- install
- typecheck
- lint
- tests
- build

## Gate 4 — First Vertical Slice

Implement one complete workflow:

UI → input validation → API → authentication → authorization → business rules → database transaction → audit → response → integration test → E2E test.

The slice must not be hardcoded or mock-only.

## Gate 5 — Incremental Delivery

Each feature becomes an independent task with:

- Goal
- Context
- Business rules
- Constraints
- Security requirements
- Edge cases
- Acceptance criteria
- Required tests
- Out of scope
- Done when

Use one feature or one coherent change per PR.

Do not mix a feature with an unrelated refactor, dependency upgrade, or broad formatting change.

## General Execution Rules

- Inspect existing project sources before proposing changes.
- Do not invent packages, APIs, functions, or framework behavior.
- Verify dependency versions and official documentation before adding dependencies.
- Do not hide errors with generic catches or silent fallbacks.
- Do not weaken tests to make code pass.
- Do not use UI as the only business-rule or authorization boundary.
- Do not allow agents to access production, secrets, or real customer data.
- Do not merge or deploy automatically.
- Destructive operations require explicit human approval.
- Report uncertainty and unverified items.

## Completion Protocol

Every completed gate or change must report:

- Summary
- Root Cause, when applicable
- Changed Files
- Contracts Changed
- Database Changes
- Commands Executed
- Tests Executed with actual results
- Acceptance Criteria: Passed, Failed, or Not Verified
- Security Review
- Remaining Risks
- Known Limitations
- Unverified Items
- Rollback Procedure
- One next recommended task
