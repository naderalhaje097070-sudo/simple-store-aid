# Delivery Protocol

## Change preparation

Every task must state:

- Work mode and change type.
- Goal and expected outcome.
- In scope and out of scope.
- Risk classification.
- Explicit assumptions.
- Business rules and constraints.
- Security requirements.
- Acceptance criteria.
- Required tests.
- Rollback or compensation plan.

Only ask for information that blocks correct execution. Inspect the repository and documentation before asking questions that can be answered from them.

## Pull-request discipline

- One coherent feature or change per PR.
- Keep feature work separate from broad refactoring, formatting, dependency upgrades, and unrelated cleanup.
- Use small, reviewable commits without rewriting published Lovable-linked history.
- Do not modify generated files manually when a generator owns them.
- Do not modify applied migrations.
- Do not include production credentials, customer data, or secrets.
- Do not enable automatic merge or deploy.

## Implementation discipline

- Implement the smallest correct change.
- Preserve clear boundaries between UI, application/domain logic, and infrastructure/database logic.
- Use strong typing and precise names.
- Avoid dead code, premature abstractions, god modules, silent fallbacks, and generic error swallowing.
- Comments should explain non-obvious reasons or constraints, not restate visible code.
- Update contracts, decisions, project state, and tasks with the implementation.

## Verification

Record the actual commands and actual results. Use the checks required by the affected contracts, including as applicable:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Add migration, database contract, authorization, tenant-isolation, concurrency, idempotency, integration, E2E, security, performance, and smoke tests where relevant.

Test happy paths and negative paths:

- Invalid input.
- Unauthenticated access.
- Forbidden access.
- Cross-tenant or cross-employee access.
- Missing data.
- Duplicate and retry behavior.
- Concurrent requests.
- Partial failure.
- Boundary values.
- Illegal state transitions.

## Completion report

Every completed stage or proposed merge must report:

### Summary
What was implemented or reviewed?

### Root Cause
For a defect, what caused it and what evidence supports that conclusion?

### Changed Files
List every changed file and why it changed.

### Contracts Changed
List API, RPC, schema, state, authorization, or business-rule changes.

### Database Changes
List migrations, constraints, indexes, backfills, lock impact, and compensation strategy.

### Commands Executed
List commands actually run. Do not list commands that were only recommended.

### Tests Executed
List each test and its actual result.

### Acceptance Criteria
Mark each criterion Passed, Failed, or Not verified.

### Security Review
State what authorization, tenant isolation, input validation, secret handling, and abuse cases were reviewed.

### Remaining Risks
List unresolved risks and their severity.

### Known Limitations
State intentional limitations.

### Unverified Items
State everything that has not been proven.

### Rollback Procedure
Provide the actual rollback or compensation steps.

### Next Recommended Task
Provide one logical next task only.

Do not use “Done” as a substitute for this report. A branch or successful build is not a release; merge and deployment require human action.
