# NAADF-CMF — Change and Modification Framework

Use this framework for every change to the existing Mongezz application, including features, bug fixes, business-rule changes, database changes, refactors, performance work, UI changes, dependency upgrades, security changes, and integration changes.

## Governing principle

Do not start with code. First analyze impact, establish the current behavior, define the expected behavior, create a safety net and rollback plan, then implement the smallest correct change.

## Change Gate 0 — Change Intake

Record:

- Change goal.
- Change type.
- In scope.
- Out of scope.
- Urgency.
- Risk level.
- Owner.
- Expected outcome.
- Missing blocking information.
- Explicit assumptions.

**Stop and obtain approval before implementation.**

## Change Gate 1 — Baseline and Reproduction

Before changing code:

- Inspect the repository and existing documentation.
- Document current behavior.
- Document expected behavior.
- Record reproduction steps for defects.
- Identify environment, version, and affected data.
- Run the existing verification suite and record the baseline.
- Add a failing regression test before a bug fix when feasible.

Do not fix an unproven defect without documenting the evidence and suspected root cause.

## Change Gate 2 — Impact Analysis

Analyze impact on:

- UI.
- API and RPC contracts.
- Database schema and data.
- Authentication and authorization.
- Tenant isolation.
- Business rules and state transitions.
- Financial operations and reports.
- Background jobs.
- External integrations.
- Performance.
- Tests and CI.
- Deployment and rollback.
- Backward compatibility.

Search for all callers, consumers, imports, clients, database functions, tests, reports, and jobs.

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

- Root cause.
- Smallest correct change.
- Files and modules affected.
- Existing and updated contracts.
- Migration or backfill requirements.
- Compatibility strategy.
- Feature-flag strategy where risk requires it.
- Rollout plan.
- Rollback or compensation plan.
- Acceptance criteria.

Do not use a local patch when the root cause is in the data model, architecture boundary, state ownership, transaction design, or authorization model.

## Change Gate 4 — Safety Net

Before implementation:

- Run and record the current test baseline.
- Add regression tests.
- Add contract tests when contracts change.
- Add authorization and tenant-isolation tests when permissions change.
- Add concurrency and idempotency tests for sensitive operations.
- Prepare a backup or snapshot plan for data changes.
- Prepare a feature flag for high-risk rollout when applicable.

Never weaken an existing test solely to make a change pass.

## Change Gate 5 — Implementation

Apply the smallest correct change.

Rules:

- One coherent goal per PR.
- No unrelated file changes without justification.
- No broad rewrite without demonstrated necessity.
- Never edit an applied migration.
- Use a new forward-only migration.
- Update contracts and documentation with the code.
- Preserve backward compatibility where required.
- Record new architectural or business decisions in `DECISIONS.md` or an ADR.
- Do not add dependencies without a documented need and official-version verification.

## Change Gate 6 — Independent Review

Perform an adversarial review independent from implementation. Check:

- Was the root cause addressed?
- Was an existing contract broken?
- Are transaction boundaries correct?
- Are race conditions, retries, and duplicate requests safe?
- Is authorization correct and deny-by-default?
- Is tenant isolation preserved?
- Is any business rule undocumented?
- Is the change larger than required?
- Is there hardcoding, mock production behavior, or a workaround?
- Do tests prove real behavior and negative cases?
- Is rollback executable?

Record each finding with:

- Severity.
- File or contract.
- Evidence.
- Risk.
- Required fix.
- Verification method.

## Merge and deployment boundary

- Passing tests do not authorize merge or deployment.
- Automated agents do not merge or deploy.
- A human reviews the final evidence and performs the release action.
- Destructive operations require explicit human approval.
- Production data and secrets remain outside automated work.

## Completion report

Use the completion protocol in `DELIVERY_PROTOCOL.md` and explicitly identify all unverified items.
