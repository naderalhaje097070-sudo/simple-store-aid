# NAADF-CMF — Change and Modification Framework

Use this framework for every change to Mongezz, including:

- Feature
- Business-rule change
- Bug fix
- Database change
- Refactor
- Performance improvement
- UX or UI change
- Dependency or framework upgrade
- Security or authorization change
- API or integration change

## Governing Principle

Do not begin with code. Begin by understanding the current behavior, defining the required behavior, analyzing impact, creating a safety net, and preparing rollback.

## Change Gate 0 — Change Intake

Record:

- Change goal
- Change type
- In scope
- Out of scope
- Urgency
- Risk level
- Owner
- Expected outcome
- Missing critical information
- Explicit assumptions
- Proposed first gate

No implementation begins until Gate 0 is explicitly approved.

## Change Gate 1 — Baseline and Reproduction

Before modification:

1. Inspect the repository and relevant documentation.
2. Document current behavior.
3. Document expected behavior.
4. Record reproduction steps for a defect or current-state evidence for a feature.
5. Identify environment, version, and affected data.
6. Execute existing verification commands and record actual results.
7. Add a regression test that fails before the bug fix when practical.

Do not claim to fix a bug that has not been reproduced or whose root cause is not documented. If reproduction is not possible, record the limitation and supporting evidence.

Required outputs may include:

- `CURRENT_BEHAVIOR.md`
- `EXPECTED_BEHAVIOR.md`
- `REPRODUCTION.md`
- `BASELINE_RESULTS.md`

## Change Gate 2 — Impact Analysis

Analyze effects on:

- UI
- API and RPCs
- Database
- Authentication
- Authorization
- Tenant isolation
- Business rules
- State transitions
- Financial operations
- Reports
- Background jobs
- External integrations
- Performance
- Tests
- Deployment
- Backward compatibility

Search for all callers, consumers, imports, clients, database functions, reports, tests, and jobs.

Create:

- `IMPACT_ANALYSIS.md`
- `DEPENDENCY_MAP.md`
- `DATA_IMPACT.md`
- `SECURITY_IMPACT.md`
- `API_COMPATIBILITY.md`
- `MIGRATION_IMPACT.md`
- `TEST_IMPACT.md`
- `ROLLBACK_IMPACT.md`

## Change Gate 3 — Change Design

Define:

- Root cause or capability gap
- Smallest correct change
- Files and modules affected
- Existing contracts
- Updated contracts
- Migration or backfill requirements
- Compatibility strategy
- Feature-flag strategy
- Rollout plan
- Rollback plan
- Acceptance criteria

Do not use a local patch when the root problem is in the data model, architecture boundary, state ownership, transaction design, or authorization model.

## Change Gate 4 — Safety Net

Before implementation:

1. Execute and record the existing baseline.
2. Add regression tests.
3. Add contract tests when contracts change.
4. Add authorization and tenant-isolation tests when permissions change.
5. Add concurrency and idempotency tests for sensitive operations.
6. Prepare a backup or snapshot strategy for data changes.
7. Prepare a feature flag for high-risk rollout when appropriate.
8. Define failure injection or partial-failure coverage where relevant.

The safety net must test real contracts, not only mocked happy paths.

## Change Gate 5 — Implementation

Apply the smallest correct change.

Rules:

- One focused objective per PR.
- Do not modify unrelated files without written justification.
- Do not rewrite an entire module without necessity.
- Do not edit an applied migration.
- Use a new forward-only migration.
- Update contracts and documentation with code.
- Preserve backward compatibility where required.
- Record material decisions in `DECISIONS.md` or an ADR.
- Do not introduce hardcoded production behavior, mock-only paths, silent fallbacks, or generic error suppression.
- Keep financial and authorization rules outside UI-only code.

## Change Gate 6 — Independent Review

Perform an independent, adversarial review.

Check:

- Was the root cause addressed?
- Was an existing contract broken?
- Are transaction boundaries correct?
- Is there a race condition?
- Is authorization correct?
- Is tenant isolation preserved?
- Is a business rule undocumented?
- Is the change larger than necessary?
- Is there hardcoding, a workaround, or a silent fallback?
- Do tests prove actual behavior?
- Is rollback executable?
- Are logs free of secrets and sensitive data?
- Are indexes, locks, and query costs acceptable?

Record each finding separately:

- Severity
- File or contract
- Evidence
- Risk
- Required fix
- Verification method

No high or critical finding may remain open at approval.

## Required Change Documentation

Use a change-specific directory where appropriate:

```text
changes/<change-name>/
├── CHANGE_REQUEST.md
├── CHANGE_GOAL.md
├── CHANGE_TYPE.md
├── IN_SCOPE.md
├── OUT_OF_SCOPE.md
├── ASSUMPTIONS.md
├── RISKS.md
├── SUCCESS_METRICS.md
├── CURRENT_BEHAVIOR.md
├── EXPECTED_BEHAVIOR.md
├── IMPACT_ANALYSIS.md
├── DEPENDENCY_MAP.md
├── DATA_IMPACT.md
├── SECURITY_IMPACT.md
├── API_COMPATIBILITY.md
├── MIGRATION_IMPACT.md
├── TEST_IMPACT.md
├── ROLLBACK_IMPACT.md
└── ACCEPTANCE_CRITERIA.md
```

The amount of documentation may be proportional to risk, but high-risk financial, database, authorization, or tenant-isolation changes require the full set or an explicitly justified equivalent.

## Risk Guidance

### Low

- Documentation-only changes
- Copy changes
- Isolated visual changes with no business behavior

### Medium

- Non-financial feature changes
- Refactors with stable contracts
- Operational tooling changes

### High

- Financial rules
- Authentication or authorization
- RLS or tenant isolation
- Database migrations or backfills
- Subscription and billing data
- Destructive operations
- Dependency upgrades affecting runtime or deployment
- Changes that can lose, duplicate, expose, or misstate data

## Completion Protocol

Every completed gate or modification must report:

- Summary
- Root Cause or capability gap
- Changed Files and reason
- Contracts Changed
- Database Changes
- Commands Executed
- Tests Executed and actual results
- Acceptance Criteria: Passed, Failed, or Not Verified
- Security Review
- Remaining Risks
- Known Limitations
- Unverified Items
- Rollback Procedure
- One next recommended task

Do not use “Done” as a substitute for this report.
