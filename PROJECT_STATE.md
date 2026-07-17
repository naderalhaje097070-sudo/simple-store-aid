# Project State

Last updated: 2026-07-17

## Current stage

AUDIT-001 — Main Containment and Pilot Baseline Truth Restoration.

Employee Accounts Change Gate 1 documentation was reviewed and merged through pull request #20 as merge commit `599f84de4ef7f472da075e3ddbf1648501cbc871`. No employee feature implementation is authorized.

The project is a Functional MVP being stabilized into a reproducible and financially safe baseline before a controlled owner-only pilot. Pilot execution is planned but blocked until the P0 environment, CI-reporting, and financial-idempotency changes are completed and release-verified.

Current audited `main` head at the start of the final AUDIT-001 update: `1335d2912aa9cd1674dd082a4396c9bfb660c9c5` (`Fixed 429 retry & added enq_at`). GitHub history remains authoritative if `main` advances after this document is merged.

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
- Direct Lovable changes after PR #20 were inspected through `1335d2912aa9cd1674dd082a4396c9bfb660c9c5`:
  - `d4794d26d88e228776a957900b1c48dd1f86a0b9` — `@lovable.dev/vite-tanstack-config` 2.7.3 to 2.7.4.
  - `a6792b8687a891103e484c24c5c7ca47b41b5095` — regenerated Supabase types.
  - `cb0b6bd2543a826fb905e537d1afbc40506eb13f` — forward-only security migration for email helpers, `profiles`, and `tenant_counters`.
  - `bb92a4c072bd2145b550e8b4cc107d4026d9b8f5` — combined security update.
  - `cbd6d5fb33e3175723dbcf1f5483c85622dbdec2` — `@lovable.dev/vite-tanstack-config` 2.7.4 to 2.7.6.
  - `da68f17c1ea16b7102014a48c6e50b36627a795d` — rate-limit responses no longer consume the email delivery failure budget.
  - `cd709d8388739296d09a308178edb3fe9add01fd` — forward-only `read_email_batch` return-contract change adding `enqueued_at`, plus regenerated types.
  - `1335d2912aa9cd1674dd082a4396c9bfb660c9c5` — combined email retry and queue-age update.
- The email 429 behavior and `read_email_batch` / `enqueued_at` contract change were reviewed as part of AUDIT-001. No documentation-baseline blocker was identified; production reliability remains governed by the later environment, CI, and idempotency changes.
- AUDIT-001 initial local verification on `bb92a4c` recorded successful typecheck, 26 unit tests, and production build.
- GitHub checks on PR #21 are the authoritative verification source for every updated head.

## In-progress work

- Human review and explicit merge decision for AUDIT-001 pull request #21.
- Creation of an annotated pilot-baseline tag only after PR #21 is merged and the final merge commit is verified. Tag creation is a separate explicit human action, not an automatic result of this documentation PR.

## Known issues

### Pilot blockers

- `SEC-ENV-001`: `config/supabase-build-config.ts` contains a production Supabase public URL and anon-key fallback. Non-production builds must fail closed rather than silently target production.
- `SEC-CI-001`: PR reporting has historically copied local Supabase startup output and disposable local credentials into comments. Reports must contain concise evidence only, and tool versions must be pinned.
- `FIN-IDEM-001`: Financial RPCs for sale creation, debt collection, settlement, and return do not have an approved idempotency contract. A retry after a lost response can duplicate a financial operation.
- Latest `main` must pass the full release gate after any direct Lovable change: Quality, full migration chain, T1–T15, and Isolated Auth UI Smoke.

### Deferred until after pilot evidence and approved design gates

- Existing tenant-member RLS grants are broader than a restricted employee role requires.
- Assignment source of truth, employee/courier identity, authorization matrix, historical identity, audit model, concurrency, migration, and rollback design remain unapproved.
- Billing and plan promises are not fully enforced by the application, and the authenticated route guard checks tenant presence rather than subscription validity.
- Employee-account implementation remains deferred until the owner-only core is reliable and pilot evidence demonstrates priority.

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
- PR #17 is a superseded prototype and must not be merged.
- Pilot execution does not begin until the listed P0 pilot blockers are resolved and release-verified.

## Next task

Complete and merge AUDIT-001 after final checks and human approval. Then execute `SEC-ENV-001 — Environment Isolation and Fail-Closed Build Resolution` as the first implementation change. No new product feature is authorized.

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
