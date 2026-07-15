# Mongezz Project State

Last updated: 2026-07-15

## Current stage

**NAADF-CMF — Change Gate 0 approved. PR-GOV-001 is open as Draft PR #18.**

No employee-account feature code is approved for merge. No Production access, merge, or deployment is authorized.

## Completed work

- Existing repository, architecture rules, stack, Issue #16, and PR #17 were inspected.
- Change Gate 0 was drafted and explicitly approved by the product owner.
- The employee-account change was classified as High Risk because it affects authentication, authorization, RLS, tenant isolation, financial custody, settlement, and historical records.
- PR #17 was identified as an oversized implementation reference rather than an approved release candidate.
- The governance bootstrap branch was created from `main`.
- Draft PR #18 was opened for governance documentation review.

## In-progress work

- PR-GOV-001 / Draft PR #18: review NAADF, NAADF-CMF, delivery, security, database, testing, review, decision, task, and project-state documentation.

## Known issues

1. PR #17 is open and not merged.
2. PR #17 combines database, RLS, RPC, UI, routing, CI, and E2E changes in one large PR.
3. On its recorded head commit, Quality passed while Isolated Auth UI Smoke and Ephemeral Financial Rules failed.
4. Hard-delete prevention for an employee or courier with financial or authenticated history is not yet verified as a database invariant.
5. README role documentation is inconsistent with the current `owner` / `staff` model used by the employee proposal.
6. The current employee proposal has not completed baseline, impact analysis, contract review, independent security review, concurrency review, or rollback verification under NAADF-CMF.

## Decisions that must not change without an ADR

- Financial writes use approved server-side RPCs or transactions.
- `Delivered != Settled`.
- Courier-collected cash remains custody until owner settlement.
- Returned orders do not create customer debt or courier custody.
- Tenant isolation is enforced server-side and through RLS where applicable.
- Production and real customer data are unavailable to agents and automated destructive tests.
- Applied migrations are immutable and future database changes are forward-only.
- No automatic merge, deploy, force-push, or published-history rewrite.

## Next task

After human review and merge of Draft PR #18, execute **NAADF-CMF Change Gate 1 — Baseline and Reproduction** for Issue #16 and PR #17. Do not resume implementation before that gate is documented and approved.

## Verification commands

For documentation-only governance changes:

```bash
git diff --check origin/main...HEAD
```

For later application changes, the minimum baseline is:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Database, authorization, tenant-isolation, migration, financial-regression, and authenticated E2E commands must be added and recorded by the relevant change plan.
