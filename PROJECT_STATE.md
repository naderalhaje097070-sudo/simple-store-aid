# Project State

Last updated: 2026-07-17

## Current stage

AUDIT-001 — Pilot Baseline and Truth Restoration. Employee Accounts Change Gate 1
(baseline and reproduction) documentation was reviewed and **merged** into `main` as
pull request #20 (merge commit `599f84dbb...`). No employee feature implementation is
authorized. The project is a **Functional MVP** being stabilized into a trustworthy,
reproducible baseline before an owner-only pilot; no new product features are in scope.

Current `main` HEAD: `bb92a4c` (`Fixed 3 security issues`).

## Completed work

- Existing repository and technology stack inspected.
- Core financial invariants identified.
- Change Gate 0 approved by the product owner.
- NAADF, NAADF-CMF, delivery, security, database, testing, review, state, decision, and task governance merged through PR #19 (merge commit `e7088a2c58bb...`).
- Duplicate governance PR #18 closed without merge.
- Employee Accounts Change Gate 1 baseline/reproduction documentation **merged** via PR #20 (merge commit `599f84dbb...`). Quality, Ephemeral Financial Rules (T1–T15), and Isolated Auth UI Smoke passed before merge; independent documentation review found no Critical/High/Medium finding.
- Four post-#20 direct commits landed on `main` and were reviewed during AUDIT-001; all are small, non-destructive, and accepted:
  - `d4794d2` — devDependency bump `@lovable.dev/vite-tanstack-config` 2.7.3 → 2.7.4 (plus `bun.lock`).
  - `a6792b8` — regenerated `src/integrations/supabase/types.ts` (generator-owned).
  - `cb0b6bd` — forward-only migration `..._f0da86df...`: pins `search_path` on the email-queue helper functions, adds a deny-INSERT RLS policy on `profiles` (signup trigger is `SECURITY DEFINER`), and a deny-ALL RLS policy on `tenant_counters` (touched only by the `next_order_number` `SECURITY DEFINER` RPC).
  - `bb92a4c` — merge of the above (`Fixed 3 security issues`); current `main` HEAD.
- AUDIT-001 revalidated `main` locally: `bun run typecheck`, `bun run test:unit` (26 pass), and `bun run build` all pass. T1–T15 and Isolated Auth UI Smoke run in CI against the pull request (isolated Supabase; no production access).
- PR #17 closed as a superseded prototype (see "Decisions that must not change" and TASKS.md `AUDIT-001`); its Gate 1 decomposition is captured by `changes/employee-accounts/PR17_SCOPE_MAP.md`.
- README role documentation corrected to match the actual `app_role` enum (`owner`, `staff`).

## In-progress work

- AUDIT-001 documentation pull request open for human review. On merge, an annotated tag `v1.0.0-pilot-baseline` is applied to the merge commit as the pilot reference point.

## Known issues

- README previously advertised four roles (`owner` / `manager` / `cashier` / `viewer`); corrected to the true enum `owner` / `staff`. The expanded employee/courier role model remains a pending governed decision (not yet designed).
- Build-time production Supabase fallback exists in `config/supabase-build-config.ts` (project ref `dahzkekdirrngnkcxinv`, anon key). A build with no env set silently ships the production ref. This is a **known P0 for the later environment-separation phase**, not part of AUDIT-001.
- Financial RPCs (create sale, collect debt, settle, return) have no idempotency key; a retry after a lost response could duplicate a financial operation. Deferred to the later reliability phase.
- Existing tenant-member RLS grants remain broader than a future restricted-employee role will require; employee accounts must not be enabled before the authorization matrix is approved.
- Billing/plan promises are not enforced by the app, and the route guard checks tenant presence rather than subscription validity. Deferred to the later commercial-readiness phase.
- Historical CI comments once exposed disposable local development keys; affected comments were redacted, but workflow reporting still requires the separate governed change SEC-CI-001.

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

Owner-only controlled pilot preparation and execution (3–5 stores, direct supervision),
measuring real daily usage and trust in the numbers. Employee-account implementation
resumes only after the pilot demonstrates need and after Change Gates 2–4. No new
product features until the pilot baseline is proven.

## Verification commands

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

GitHub checks for the current head are the authoritative verification source. The
Ephemeral Financial Rules (T1–T15) and Isolated Auth UI Smoke workflows run in isolated
Supabase environments and must pass; they never touch production.
