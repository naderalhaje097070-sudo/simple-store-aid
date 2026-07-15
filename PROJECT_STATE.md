# Project State

Last updated: 2026-07-15

## Current Stage

**NAADF-CMF — Change Gate 0 approved.**

Governance bootstrap is in progress on branch `governance/naadf-bootstrap`. No feature code, database migration, merge, or deployment is part of this governance change.

## Completed Work

- Existing Mongezz repository, technology stack, financial-domain rules, and Lovable synchronization constraints were inspected.
- Change Gate 0 was drafted and approved for adopting NAADF and NAADF-CMF.
- PR #17 was identified as an oversized, high-risk feature PR and is blocked from merge.
- `AGENTS.md` and `CLAUDE.md` were defined as agent entry points.

## In-Progress Work

- Add governance documents under `docs/governance/`.
- Add project context files: `PROJECT_STATE.md`, `DECISIONS.md`, and `TASKS.md`.
- Open a documentation-only pull request for governance review.

## Known Issues

1. PR #17 currently combines database, authorization, workflows, UI, and tests in one large change.
2. PR #17 Quality passed on its recorded head, but Isolated Auth UI Smoke and Ephemeral Financial Rules failed.
3. Employee-account requirements and implementation contracts have not completed NAADF-CMF Gates 1–6.
4. The hard-delete prohibition for a courier with employee-account history is not verified on the database contract.
5. README role documentation is inconsistent with the currently observed `owner` / `staff` model.
6. No production-grade employee-account feature is approved or merged.

## Decisions That Must Not Change Without an ADR

- Delivered is not settled.
- Returned orders create no customer debt and no courier custody.
- Courier-collected money remains custody until owner settlement.
- Financial writes use approved transactional server-side RPCs or equivalent server boundaries.
- Authorization and tenant isolation are enforced server-side and in the database.
- Production databases, secrets, and real customer data are unavailable to agents and automated destructive tests.
- Applied migrations are immutable; future database changes are forward-only.
- No automatic merge or deployment.
- Published Git history is not rewritten because the repository is synchronized with Lovable.

## Next Task

Complete and open `PR-GOV-001 — Engineering Governance Bootstrap` for human review. Do not merge it automatically.

After human merge approval, begin `NAADF-CMF Change Gate 1 — Baseline and Reproduction` for employee accounts.

## Verification Commands

For documentation-only governance changes:

```bash
git diff --check
git status --short
```

For application changes after the applicable gate is approved:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Database, authorization, migration, financial-regression, and E2E commands must be added by the relevant change specification and executed only against isolated non-production environments.
