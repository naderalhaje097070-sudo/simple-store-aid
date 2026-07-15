<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

# Mongezz Agent Operating Rules

This repository uses two mandatory delivery frameworks:

- **NAADF** for new projects or genuinely new standalone systems.
- **NAADF-CMF** for every change to this existing application, including features, bug fixes, refactors, database changes, security changes, dependency upgrades, performance work, and UX changes.

The detailed process is defined in:

- `docs/governance/NAADF.md`
- `docs/governance/NAADF-CMF.md`
- `docs/governance/DELIVERY_PROTOCOL.md`
- `docs/governance/SECURITY_BASELINE.md`
- `docs/governance/DATABASE_CHANGE_POLICY.md`
- `docs/governance/TESTING_POLICY.md`
- `docs/governance/REVIEW_PROTOCOL.md`

## Mandatory Start Protocol

Before changing files, classify the work and record:

1. Work mode: New Project or Existing Project Change.
2. Change type: Feature, Bug Fix, Refactor, Database Change, Security Change, Dependency Upgrade, or another explicit type.
3. Risk level: Low, Medium, or High.
4. Missing critical information.
5. Explicit assumptions.
6. The first required gate.

Do not start implementation before the applicable intake gate is approved.

## Non-negotiable Delivery Rules

1. Inspect the repository and current contracts before proposing changes.
2. Treat repository files as the source of truth, not conversation memory.
3. Update `PROJECT_STATE.md`, `DECISIONS.md`, and `TASKS.md` as the project state changes.
4. One feature or one coherent change per pull request.
5. Do not combine a feature with a broad refactor, global formatting, or unrelated dependency upgrade.
6. Do not claim completion without executing and reporting the relevant verification commands.
7. Do not weaken, delete, or bypass a test merely to make a change pass.
8. Do not introduce hardcoded production behavior, mock-only production paths, silent fallbacks, or generic error suppression.
9. Do not invent packages, APIs, database functions, or framework behavior.
10. Do not merge or deploy automatically. Merge and deployment require explicit human action.
11. Do not perform destructive operations without explicit human approval.
12. Agents must not access production databases, production secrets, or real customer data.
13. Do not force-push, rebase, amend, or squash already-pushed history because the repository is synchronized with Lovable.
14. Keep rollback and backward compatibility explicit for high-risk changes.
15. Record unverified items instead of guessing.

## Mongezz Financial and Domain Invariants

1. Financial writes must go through approved, server-authorized RPCs or equivalent transactional server boundaries.
2. Do not duplicate debt, custody, remaining, or margin formulas in UI screens.
3. Reuse centralized finance-domain functions.
4. Returned orders must never appear as customer debt or courier custody.
5. **Delivered is not settled.** Courier-collected money remains custody until owner settlement is completed.
6. Tenant isolation and authorization must be enforced by the database or server, not only by hidden UI elements.
7. Monetary values must use PostgreSQL `numeric` or integer minor units, never floating-point storage.
8. Financial mutations must be transactional, authorized, auditable, retry-safe where applicable, and protected against duplicate execution.
9. No public test-cleanup RPCs or destructive E2E paths may exist in production.
10. Production must never be used for destructive or fixture-creating automated tests.

## Database Rules

1. Never edit a migration that may already have been applied.
2. Create forward-only migrations for schema or policy changes.
3. Use constraints, foreign keys, checks, indexes, transactions, row locking, idempotency, and RLS when the invariant belongs in the database.
4. Separate large backfills from schema changes.
5. Assess lock time, index cost, compatibility, rollback, backup, and restore impact.
6. High-risk data changes require a tested rollback or compensating migration plan.

## Required Completion Report

Every completed gate or change must report:

- Summary
- Root Cause, when applicable
- Changed Files
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

## Current Project State

Read `PROJECT_STATE.md` before starting work. If it is stale, updating it is part of the current task before implementation proceeds.
