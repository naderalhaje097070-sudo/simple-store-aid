# Delivery Protocol

## Work classification

Every request starts with:

- Work Mode
- Project Type
- Risk Level
- Missing Critical Information
- Explicit Assumptions
- Proposed First Gate

Only ask questions that block correct execution and cannot be answered from repository artifacts.

## Branch and PR discipline

- Use a dedicated branch for each coherent change.
- One feature or one coherent modification per PR.
- Separate broad refactoring, dependency upgrades, schema changes, and feature work when independently reviewable.
- Do not force-push, rebase, amend, or rewrite published history.
- Do not enable automatic merge or deployment.
- Destructive actions require explicit human approval.

## Scope control

A change task must define:

- Goal
- Context
- In scope
- Out of scope
- Business rules
- Security requirements
- Edge cases
- Acceptance criteria
- Required tests
- Done-when conditions

Do not edit unrelated files without a documented reason.

## Verification

Completion requires actual execution evidence appropriate to the change:

- Installation or dependency lock validation
- Typecheck
- Lint
- Unit tests
- Integration tests
- Build
- Database migration tests
- Contract tests
- Authorization and tenant-isolation tests
- E2E and smoke tests
- Security and independent review

A generated file, successful build, or green unit suite alone does not prove product acceptance.

## Completion report

Every completed gate or change must include:

### Summary
What changed and why.

### Root Cause
For bugs or incidents, the demonstrated underlying cause.

### Changed Files
Every changed file and its purpose.

### Contracts Changed
API, RPC, schema, state, event, or business-rule changes.

### Database Changes
Migrations, constraints, indexes, backfills, locks, and data impact.

### Commands Executed
Commands actually run, not suggested commands.

### Tests Executed
Every test and its actual result.

### Acceptance Criteria
Passed, Failed, or Not verified for each criterion.

### Security Review
Authorization, tenant isolation, data exposure, secrets, injection, IDOR, mass assignment, and audit checks.

### Remaining Risks
Known unresolved risks and ownership.

### Known Limitations
Intentional limitations of the delivered scope.

### Unverified Items
Anything not directly tested or inspected.

### Rollback Procedure
Executable rollback or compensating procedure.

### Next Recommended Task
Exactly one logical next task.
