# Project State

Last updated: 2026-07-21

## Current stage

AUDIT-001 — Main Containment and Pilot Baseline Truth Restoration.

Employee Accounts Change Gate 1 documentation was reviewed and merged through pull request #20 as merge commit `599f84de4ef7f472da075e3ddbf1648501cbc871`. No employee feature implementation is authorized.

The project is a Functional MVP being stabilized into a reproducible and financially safe baseline before a controlled owner-only pilot. Pilot execution is blocked until the listed financial, environment, CI-reporting, and retry-safety changes are completed and release-verified.

The clean AUDIT-001 branch was created from `main` commit `906df4b89369dff17e12060de47c6d32ecca47c4`. GitHub history remains authoritative if `main` advances after this document is merged.

## Completed work

- Existing repository and technology stack inspected.
- Core financial invariants identified.
- Change Gate 0 approved by the product owner.
- NAADF, NAADF-CMF, delivery, security, database, testing, review, state, decision, and task governance merged through PR #19 as merge commit `e7088a2c58bb514aac133f303627d4b829473934`.
- Duplicate governance PR #18 closed without merge.
- Employee Accounts Change Gate 1 baseline and reproduction documentation merged through PR #20 as merge commit `599f84de4ef7f472da075e3ddbf1648501cbc871`.
- PR #20 passed Quality, Ephemeral Financial Rules T1–T15, and Isolated Auth UI Smoke before merge.
- PR #17 was reviewed as an oversized prototype, decomposed in `changes/employee-accounts/PR17_SCOPE_MAP.md`, and closed without merge as superseded by the governed delivery sequence.
- README role documentation corrected to the current database enum values: `owner` and `staff`.
- Direct Lovable changes after PR #20 were inspected through `1335d2912aa9cd1674dd082a4396c9bfb660c9c5`, including email queue, retry, generated types, dependency, and forward-only migration changes.
- Four later direct Lovable commits advanced `main` from `1335d2912aa9cd1674dd082a4396c9bfb660c9c5` to `906df4b89369dff17e12060de47c6d32ecca47c4`. Their net file scope is `.lovable/plan.md` and `src/routes/index.tsx`; they are included in the clean baseline and require the clean PR release gates.
- User-reported courier-sale defects were reproduced from effective code and recorded as Issue #22, `FIN-COURIER-001`.

## In-progress work

- Clean AUDIT-001 documentation pull request from the latest `main` baseline.
- Final Quality, full isolated migration chain / T1–T15, and Isolated Auth UI Smoke checks on the clean PR head.
- Human review and explicit merge decision after all checks pass.
- No pilot tag is created automatically. Any tag requires a separate explicit human action after the merge commit is verified.

## Known issues

### Immediate financial workflow blocker

- `FIN-COURIER-001` / Issue #22:
  - current effective database validation requires a customer for every courier order, even when no customer debt exists;
  - courier money entered during sale can remain unclear or absent from settlement until a manual delivery-state update;
  - primary desktop, mobile, and post-sale actions open quick sale instead of the advanced sale workflow;
  - the repair requires an approved state mapping, forward-only migration, server-side validation, focused UI changes, and regression tests.

### Other pilot blockers

- `SEC-ENV-001`: non-production builds must fail closed rather than silently target production Supabase through fallback configuration.
- `SEC-CI-001`: PR reports must not copy raw Supabase startup output or disposable local credentials, and material tool versions must be pinned.
- `FIN-IDEM-001`: financial write RPCs require an approved idempotency and retry-safety contract.
- Latest `main` and every release candidate must pass Quality, full migration chain, T1–T15, and Isolated Auth UI Smoke.

### Deferred until pilot evidence and approved design gates

- Existing tenant-member RLS grants are broader than a restricted employee role requires.
- Assignment source of truth, employee/courier identity, authorization matrix, historical identity, audit model, concurrency, migration, and rollback design remain unapproved.
- Billing and plan promises are not fully enforced by the application, and the authenticated route guard checks tenant presence rather than subscription validity.
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

Complete the clean AUDIT-001 pull request after final checks and human approval. Then execute `FIN-COURIER-001 — Courier Sale Workflow Correction` through approved impact, design, safety-net, implementation, and independent-review gates. Do not combine it with employee accounts, environment isolation, CI hardening, idempotency, or general refactoring.

## Verification commands

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

GitHub checks for the latest PR head are the authoritative verification source. Ephemeral Financial Rules must apply the full migration chain and pass T1–T15 on isolated Supabase. Isolated Auth UI Smoke must use an isolated account and must not access production.
