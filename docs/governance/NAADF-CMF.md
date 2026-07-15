# NAADF-CMF — Change and Modification Framework

Use this framework for every change to an existing application, including features, bug fixes, business-rule changes, database changes, refactoring, performance work, UI changes, dependency upgrades, security changes, and integration changes.

## Change Gate 0 — Change Intake

Record:

- Change goal
- Change type
- In scope and out of scope
- Urgency
- Risk level
- Owner
- Expected outcome
- Explicit assumptions and missing blocking information

No implementation begins before this gate is approved.

## Change Gate 1 — Baseline and Reproduction

Before changing behavior:

- Inspect the repository and relevant documentation.
- Record current behavior and expected behavior.
- Record reproduction steps, environment, version, and affected data.
- Run existing tests and save actual baseline results.
- Add a failing regression test for a proven bug when practical.

Do not claim a root cause that has not been demonstrated or documented.

## Change Gate 2 — Impact Analysis

Analyze impact on:

- UI
- API and RPC contracts
- Database and migrations
- Authentication and authorization
- Tenant isolation and RLS
- Business rules and state transitions
- Financial operations and reports
- Background jobs and integrations
- Performance
- Tests and deployment
- Backward compatibility and rollback

Required artifacts:

- `IMPACT_ANALYSIS.md`
- `DEPENDENCY_MAP.md`
- `DATA_IMPACT.md`
- `SECURITY_IMPACT.md`
- `API_COMPATIBILITY.md`
- `MIGRATION_IMPACT.md`
- `TEST_IMPACT.md`
- `ROLLBACK_IMPACT.md`

Search all callers, consumers, imports, clients, database functions, tests, reports, and jobs.

## Change Gate 3 — Change Design

Define:

- Root cause or change rationale
- Smallest correct change
- Affected files and modules
- Current and updated contracts
- Migration or backfill requirements
- Compatibility and feature-flag strategy
- Rollout and rollback plan
- Acceptance criteria

Do not apply a local patch when the defect belongs to the data model, architecture boundary, state ownership, transaction design, or authorization model.

## Change Gate 4 — Safety Net

Before implementation:

- Run and record the current test baseline.
- Add regression tests.
- Add contract tests for contract changes.
- Add authorization and tenant-isolation tests for permission changes.
- Add concurrency and idempotency tests for sensitive operations.
- Prepare backup or snapshot procedures for data changes.
- Prepare a feature flag for high-risk changes when appropriate.

A safety net must test real behavior, not only mocks or UI visibility.

## Change Gate 5 — Implementation

Apply the smallest correct change.

Rules:

- One coherent goal per PR.
- Do not edit unrelated files without documented cause.
- Do not rewrite a module without demonstrated need.
- Do not edit an applied migration.
- Use a new forward-only migration.
- Update contracts and documentation with the code.
- Preserve backward compatibility where required.
- Record durable decisions in `DECISIONS.md`.

## Change Gate 6 — Independent Review

Perform an independent, adversarial review:

- Was the root cause or requirement actually addressed?
- Did an existing contract break?
- Are transaction boundaries correct?
- Is there a race condition or duplicate-processing risk?
- Is authorization server-side and deny-by-default?
- Is tenant isolation preserved?
- Are business rules documented and centralized?
- Is the change larger than necessary?
- Is there hardcoding, silent fallback, or workaround behavior?
- Do tests prove real behavior?
- Is rollback executable?

Record every finding with severity, file, evidence, risk, required fix, and verification method. Do not close the change until critical and high findings are resolved or explicitly accepted by a human owner.
