# NAADF — New Application Architecture and Delivery Framework

Use this framework for a new product, repository, or isolated application. Stop at each approval gate. Do not compress all gates into one implementation pass.

## Gate 0 — Project Intake

Required artifacts:

- `PROJECT_BRIEF.md`
- `GOALS.md`
- `SCOPE.md`
- `OUT_OF_SCOPE.md`
- `ASSUMPTIONS.md`
- `RISKS.md`
- `SUCCESS_METRICS.md`

Required content:

- Problem and value proposition
- Target users and actors
- Core workflows
- Constraints and non-negotiable requirements
- Sensitive data and expected scale
- Known risks and measurable success criteria

Stop and obtain explicit approval before Gate 1.

## Gate 1 — Discovery and Specification

Required artifacts:

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

Review for ambiguity, contradictions, duplicate requirements, partial failure, missing authorization, and illegal state transitions. Stop and obtain approval before Gate 2.

## Gate 2 — Architecture and Data

Required artifacts:

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

Decisions that must be fixed before implementation:

- Source of truth and module ownership
- Business-logic location
- Transaction boundaries
- Authentication and authorization
- Tenant isolation
- Error model
- Idempotency and audit strategy
- Migration and compatibility strategy
- Backup, deployment, and rollback strategy

Stop and obtain approval before Gate 3.

## Gate 3 — Foundation

Create only the foundation:

- Repository structure
- Strict typing
- Linting and formatting
- Test framework
- CI
- Environment validation
- Logging and typed error handling
- Migration system
- Authentication skeleton
- Security baseline

Required state files:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.md`
- `DECISIONS.md`
- `TASKS.md`

Foundation is not accepted until install, typecheck, lint, tests, and build are executed and their actual results are recorded.

## Gate 4 — First Vertical Slice

Implement one complete production path:

`UI → validation → API → authentication → authorization → business rules → transaction → audit → response → integration test → E2E test`

The slice must not be hardcoded or mock-only.

## Gate 5 — Incremental Delivery

Each feature must define:

- Goal and context
- Business rules and constraints
- Security requirements
- Edge cases
- Acceptance criteria
- Required tests
- Out of scope
- Done-when conditions

Use one feature or one coherent change per PR. Do not combine unrelated refactoring or dependency upgrades.
