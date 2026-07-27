# Project State

Last updated: 2026-07-27

## Current stage

FIN-COURIER-001 — **Change Gate 4 Safety Net: authored and independently reviewed; exact-head execution blocked by GitHub Actions jobs failing before their first workflow step. Gate 4 is NOT approved.**

The frozen Gate-4 implementation baseline is:

`main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

This is the merge commit of baseline-synchronization PR #26. PR #27 is the authoritative Draft Gate-4 review PR. PR #28 is closed as a duplicate Batch-1 subset.

No FIN-COURIER production implementation is authorized. PR-A, PR-B, and PR-C remain blocked until Gate 4 receives exact-head executable evidence, independent review remains satisfied, and the product owner explicitly approves the gate.

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
- FIN-COURIER-001 Gates 0–3 were independently reviewed, formally approved by the product owner, and merged through PR #24 as merge commit `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
- On PR #24 head `a652de164e3efeae707038f1769aee12a9e2474a`, Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke all passed before merge.
- Post-approval repository truth was synchronized through PR #26. Its exact head `396d683aadf94e466c230f2b63b284c944d26e4c` passed Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke before PR #26 merged as `983b746e5c6639dcdc5e6557381ad5619abaa046`.
- Gate 4 safety-net coverage has been authored across financial creation, constraints, historical preflight, transition atomicity, state machine, returns, concurrency, retry baseline, backward compatibility, five-state read model, reporting, rollback, mobile RTL, desktop, and success-screen semantics.
- Gate 4 received an adversarial independent review recorded in `changes/fin-courier-001/GATE4_INDEPENDENT_REVIEW.md`.
- Material test-quality findings were corrected, including exact CHECK attribution, UI false-positive scope, UI runtime-failure masking, rollback semantic fingerprinting, payment-effect compatibility, and complete B9 settlement-effect assertions.

## In-progress work

- PR #27 remains **DRAFT and unmerged** as the authoritative FIN-COURIER Gate-4 evidence PR.
- A previously verified checkpoint reached execution and proved T1–T15 GREEN plus initial expected-RED FIN-COURIER backend/UI gaps.
- Later exact-head GitHub Actions attempts across Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke, and both Gate-4 jobs have been created but completed with `steps = None`; no checkout, build, migration, SQL assertion, browser assertion, or test step ran.
- Those pre-step failures are classified as workflow-execution / runner-acquisition blockers and are explicitly rejected as Gate-4 PASS/FAIL evidence.
- One fresh exact PR head must execute all required workflows after the independent-review corrections. No test is weakened to accommodate infrastructure failures.

## Known issues

### Immediate financial workflow blocker

- `FIN-COURIER-001` / Issue #22:
  - current effective database validation requires a customer for every courier order, even when no customer debt exists;
  - courier money entered during sale can remain unclear or absent from settlement until a manual delivery-state update;
  - primary desktop, mobile, and post-sale actions open quick sale instead of the advanced sale workflow;
  - the target state, migration strategy, compatibility model, rollback strategy, and state contract are approved in Gates 0–3;
  - Gate-4 safety-net assertions are authored and independently reviewed;
  - implementation remains blocked until exact-head Gate-4 execution evidence is obtained and Gate 4 is explicitly approved.

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

Resolve the Gate-4 execution blocker without modifying production code or weakening the tests. On one exact final PR #27 head, require:

1. Quality GREEN.
2. Ephemeral Financial Rules / T1–T15 GREEN.
3. Isolated Auth UI Smoke GREEN.
4. FIN-COURIER Gate 4 Probe to reach every true-GREEN baseline and each approved expected-RED sentinel; runner/seed/build/browser/runtime failures do not count.
5. Final diff review confirming Gate-4 scope only.
6. Explicit human Gate-4 approval.

Only after those conditions are satisfied may PR-A begin. PR-A → PR-B → PR-C remains the approved implementation order.

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

GitHub checks on the exact final PR head are the authoritative execution evidence. Financial-rule and authenticated UI verification must remain isolated from production.
