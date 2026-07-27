# Project State

Last updated: 2026-07-27

## Current stage

FIN-COURIER-001 — Gate 4 Safety-Net preparation, preceded by a documentation-only pilot-baseline synchronization.

AUDIT-001 is complete. Pull request #23 was reviewed and merged into `main` as merge commit `6946cddabecb184b0edcd5ffaf9a0dcc521ae2c6`.

FIN-COURIER-001 Gates 0–3 were formally approved by the product owner on the synchronized PR #24 head `a652de164e3efeae707038f1769aee12a9e2474a` after Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke passed on that exact head. PR #24 was then merged into `main` as merge commit `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.

The latest observed `main` before this synchronization branch was cut is `e5632bff40e292583fd778f232dd0b7af5eb0e06`. Two commits after the PR #24 merge changed only `package.json` and `bun.lock` dependency resolution (`seroval` / `seroval-plugins`). Those post-merge commits are part of the current repository history but were not the PR #24 head on which the three required PR checks passed.

The project remains a Functional MVP being stabilized into a reproducible and financially safe baseline before a controlled owner-only pilot. Pilot execution is blocked until the listed financial, environment, CI-reporting, retry-safety, and final release-verification work is completed.

## Completed work

- Existing repository and technology stack inspected.
- Core financial invariants identified.
- NAADF, NAADF-CMF, delivery, security, database, testing, review, state, decision, and task governance merged through PR #19 as merge commit `e7088a2c58bb514aac133f303627d4b829473934`.
- Duplicate governance PR #18 closed without merge.
- Employee Accounts Change Gate 1 baseline and reproduction documentation merged through PR #20 as merge commit `599f84de4ef7f472da075e3ddbf1648501cbc871`.
- PR #20 passed Quality, Ephemeral Financial Rules T1–T15, and Isolated Auth UI Smoke before merge.
- PR #17 was reviewed as an oversized prototype, decomposed in `changes/employee-accounts/PR17_SCOPE_MAP.md`, and closed without merge as superseded by the governed delivery sequence.
- README role documentation corrected to the current database enum values: `owner` and `staff`.
- Direct Lovable changes after PR #20 were inspected through `1335d2912aa9cd1674dd082a4396c9bfb660c9c5`, including email queue, retry, generated types, dependency, and forward-only migration changes.
- Four later direct Lovable commits advanced `main` from `1335d2912aa9cd1674dd082a4396c9bfb660c9c5` to `906df4b89369dff17e12060de47c6d32ecca47c4`; their net file scope was `.lovable/plan.md` and `src/routes/index.tsx`.
- User-reported courier-sale defects were reproduced from effective code and recorded as Issue #22, `FIN-COURIER-001`.
- AUDIT-001 clean baseline documentation was reviewed and merged through PR #23 as merge commit `6946cddabecb184b0edcd5ffaf9a0dcc521ae2c6`.
- FIN-COURIER-001 Gate 0–3 contract documentation was synchronized to PR #23, independently reviewed, formally approved by the product owner, and merged through PR #24 as merge commit `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
- On PR #24 head `a652de164e3efeae707038f1769aee12a9e2474a`, Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke all passed before merge.

## In-progress work

- Synchronize repository source-of-truth documentation with the merged AUDIT-001 and FIN-COURIER-001 Gate 0–3 state.
- Preserve the Gate 0–3 approved contract as documentation only; no PR-A, PR-B, or PR-C implementation is authorized by this synchronization.
- After this synchronization PR is reviewed and merged by explicit human action, verify the new `main` SHA and use that exact head as the Gate 4 branch baseline.
- Gate 4 will add the mandatory FIN-COURIER safety-net tests before any corresponding production financial implementation.
- No pilot tag is created automatically. Any tag requires a separate explicit human action after a release candidate is verified.

## Known issues

### Immediate financial workflow blocker

- `FIN-COURIER-001` / Issue #22:
  - current effective database validation requires a customer for every courier order, even when no customer debt exists;
  - courier money entered during sale can remain unclear or absent from settlement until a manual delivery-state update;
  - primary desktop, mobile, and post-sale actions open quick sale instead of the advanced sale workflow;
  - the target state, migration strategy, compatibility model, rollback strategy, and state contract are approved in Gates 0–3;
  - implementation remains blocked until Gate 4 safety-net evidence is authored, reviewed, and approved.

### Other pilot blockers

- `SEC-ENV-001`: non-production builds must fail closed and must be proven unable to target production Supabase accidentally.
- `SEC-CI-001`: PR reports must not expose raw environment credentials or sensitive startup output, and material tool versions must be deterministic.
- `FIN-IDEM-001`: financial write RPCs require an approved idempotency and retry-safety contract.
- Latest `main` and every release candidate must pass the required Quality, isolated migration / financial-rule, and isolated authenticated UI verification appropriate to the change.

### Deferred until pilot evidence and approved design gates

- Existing tenant-member RLS grants are broader than a restricted employee role requires.
- Assignment source of truth, employee/courier identity, authorization matrix, historical identity, audit model, concurrency, migration, and rollback design remain unapproved for employee accounts.
- Billing and plan promises are not fully enforced by the application, and final expired-subscription behavior remains an open product/authorization decision.
- Employee-account implementation remains deferred until the owner-only core is reliable and pilot evidence demonstrates priority.

## Decisions that must not change

- Delivered is not settled.
- Returned orders create no customer debt and no courier custody.
- A customer is required only when an operation creates customer debt; courier assignment alone does not require a customer.
- Money explicitly recorded as collected by a courier is courier custody, not store cash, until settlement.
- A courier order with stored collected money must be represented by an eligible delivered state and appear in settlement without an additional manual correction step.
- Pending courier delivery remains outside financial settlement until a delivery outcome is recorded.
- Advanced sale is the primary sale workflow; quick sale is a secondary direct, cash, fully-paid shortcut.
- Financial writes use authorized server-side transactional boundaries.
- Tenant and employee isolation are enforced server-side and with RLS.
- Production data, production secrets, and destructive production controls are outside agent access.
- No automatic merge or deploy.
- Applied migrations are immutable; corrections use forward-only migrations.
- One coherent change per pull request.
- Published Lovable-linked Git history must not be rewritten.
- PR #17 is a superseded prototype and must not be merged.
- Pilot execution does not begin until all listed pilot blockers are resolved and release-verified.

## Next task

Complete this documentation-only baseline synchronization through review, required checks, and explicit human merge. Then verify the resulting `main` SHA and begin `FIN-COURIER-001` Gate 4 from that exact baseline.

Gate 4 is safety-net work only: author the required failing/new-behavior financial, constraint, state-machine, concurrency, reporting, backward-compatibility, rollback, mobile, and desktop tests while keeping existing T1–T15 green. Do not implement PR-A, PR-B, or PR-C until Gate 4 evidence is independently reviewed and explicitly approved.

Do not combine FIN-COURIER-001 with employee accounts, environment isolation, CI hardening, idempotency, performance work, billing enforcement, or general refactoring.

## Verification commands

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

GitHub checks on the final PR head are the authoritative verification source for this synchronization change. Financial-rule and authenticated UI verification must remain isolated from production.
