# Project State

Last updated: 2026-07-15

## Current stage

NAADF-CMF — Employee Accounts Change Gate 1: Baseline and Reproduction. Governance PR #19 was reviewed and merged into `main` as merge commit `e7088a2c58bb514aac133f303627d4b829473934`. Gate 1 documentation is open as pull request #20 and ready for human review. Independent review found no documentation-level blocker. Explicit human Gate 1 approval is still required; no employee feature implementation is authorized.

## Completed work

- Existing repository and technology stack inspected.
- Core financial invariants identified.
- Change Gate 0 approved by the product owner.
- NAADF, NAADF-CMF, delivery, security, database, testing, review, state, decision, and task governance merged through PR #19.
- Duplicate governance PR #18 closed without merge.
- PR #17 confirmed open, unmerged, and diverged from current `main`.
- Issue #16, current `main`, PR #17 scope, review threads, and latest recorded workflows inspected.
- Current behavior, expected behavior, reproduction evidence, and PR #17 scope decomposition documented for Change Gate 1.
- PR #20 opened from `docs/employee-accounts-gate-1-baseline` with documentation-only scope and marked ready for human review.
- Quality passed during PR verification: dependency install, typecheck, changed-source lint, unit tests, and production build.
- Ephemeral Financial Rules passed during PR verification: isolated Supabase, full migration chain, and T1–T15.
- Isolated Auth UI Smoke passed during PR verification: isolated account, production build, Cloudflare emulator, Playwright smoke, evidence upload, and teardown.
- Independent documentation review found no Critical, High, or Medium finding in PR #20.

## In-progress work

- GitHub checks on the current PR #20 head; GitHub checks are the authoritative verification source whenever the head changes.
- Human review and explicit approval or correction request for Change Gate 1.

## Known issues

- PR #17 is open, unmerged, 51 commits ahead and 25 commits behind `main`, and combines database, authorization, UI, tests, and CI changes.
- PR #17 latest recorded Quality workflow passed.
- PR #17 latest recorded Isolated Auth UI Smoke failed in the owner/employee authenticated-smoke step.
- PR #17 T1–T15 passed, but the employee-account and custody isolation suite failed.
- An active unresolved P1 finding indicates that repeated employee RPC calls may rewrite previously recorded courier custody.
- An outdated but unresolved P1 finding identified a risk of stranding unsettled custody when unlinking disables a courier.
- Employee hard-delete protection after unlinking is not verified.
- README role documentation is inconsistent with the generated `owner` / `staff` enum.
- Assignment source of truth, employee/courier identity semantics, authorization matrix, audit model, concurrency, idempotency, migration, and rollback design are not approved.
- Historical CI comments exposed disposable local development keys; affected comments were redacted, but workflow reporting still requires a separate governed change.

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
- PR #17 is evidence and a prototype, not an approved release candidate.

## Next task

Human review and explicit approval of PR #20 and Employee Accounts Change Gate 1. After approval, begin Change Gate 2 — Impact Analysis without writing feature code.

## Verification commands

For the Gate 1 documentation PR:

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Existing isolated financial and authenticated UI workflows must also pass on the documentation-only branch.

When employee implementation resumes, database, migration, authorization, tenant-isolation, cross-employee, financial regression, concurrency, idempotency, integration, E2E, security, and smoke tests are mandatory according to the affected contracts.
