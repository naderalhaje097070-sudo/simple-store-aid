# Project State

Last updated: 2026-07-15

## Current stage

NAADF-CMF — Change Gate 0 approved. PR-GOV-001 is open as pull request #19 and is awaiting CI completion and human review.

## Completed work

- Existing repository and technology stack inspected.
- Core financial invariants identified.
- Employee Accounts, Assigned Orders, and Personal Custody change intake drafted.
- Pull request #17 identified as oversized and blocked from merge.
- Change Gate 0 approved by the product owner.
- Governance branch created from `main` without rewriting Lovable-linked history.
- NAADF, NAADF-CMF, delivery, security, database, testing, and review policies added.
- Project state, decision, and governed task records added.
- PR-GOV-001 opened as pull request #19 without automatic merge or deploy.

## In-progress work

- Review the documentation-only diff for internal consistency.
- Wait for the applicable GitHub Actions workflows on pull request #19.
- Leave pull request #19 open for human review; do not merge automatically.

## Known issues

- PR #17 is open, unmerged, and combines database, authorization, UI, tests, and CI changes.
- PR #17 latest recorded Quality workflow passed, while Isolated Auth UI Smoke and Ephemeral Financial Rules failed.
- Employee hard-delete protection after unlinking is not verified.
- README role documentation is inconsistent with the current `owner` / `staff` model.
- The full employee feature baseline, impact analysis, authorization matrix, and rollback analysis are not yet approved.

## Decisions that must not change

- Delivered is not settled.
- Returned orders create no customer debt and no courier custody.
- Financial writes use authorized server-side transactional boundaries.
- Tenant and employee isolation are enforced server-side and with RLS.
- Production data, production secrets, and destructive production controls are outside agent access.
- No automatic merge or deploy.
- Applied migrations are immutable; corrections use forward-only migrations.
- One coherent change per pull request.
- Published Lovable-linked Git history must not be rewritten.

## Next task

Complete the independent documentation review and CI verification for pull request #19, then leave it open for explicit human merge approval.

## Verification commands

For documentation-only governance changes:

```bash
git diff --check
```

When implementation resumes, use the commands applicable to the change:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Database, migration, authorization, financial regression, integration, E2E, and smoke tests are mandatory when their contracts are affected.
