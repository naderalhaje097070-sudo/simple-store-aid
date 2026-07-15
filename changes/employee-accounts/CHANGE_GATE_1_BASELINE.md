# Change Gate 1 — Baseline and Reproduction

## Status

In review. No production implementation is authorized.

## Change

Employee Accounts, Assigned Orders, and Personal Custody.

## Sources inspected

- `main` after governance merge commit `e7088a2c58bb514aac133f303627d4b829473934`.
- Issue #16 product roadmap.
- Pull request #17 and branch `feature/employee-accounts-custody-v1`.
- PR #17 head `dd77ffcc3d5d3ba3f30d9d3485288c999264a297`.
- PR #17 changed-file list, review threads, and GitHub Actions runs.
- Current route tree, authenticated layout, settings screen, generated database types, and README.

## Verified baseline

- `main` has `owner` and `staff` in the generated `app_role` enum.
- `main` does not expose `/employee` or `/employees` routes.
- The authenticated layout verifies identity and tenant presence but does not route staff to a restricted employee portal.
- Settings displays the current role but has no employee-account management workflow.
- `orders.courier_id` already links delivery orders to `couriers`; `orders.collected_by_courier` and `orders.courier_state` already store courier custody state.
- The README role list is stale and states `owner`, `manager`, `cashier`, and `viewer`, while generated database types state `owner` and `staff`.

## PR #17 baseline

PR #17 is not merge-ready:

- 51 commits.
- 25 changed files.
- 2,892 additions and 128 deletions.
- Branch is 51 commits ahead of and 25 commits behind `main`; it has diverged from the approved baseline.
- Quality passed on the latest recorded head.
- Isolated Auth UI Smoke failed during the owner/employee authenticated smoke step.
- T1–T15 passed, but the employee-account and custody isolation suite failed.
- One active unresolved P1 review finding allows an assigned employee to rewrite a previously recorded collected amount through repeated RPC calls.
- One outdated but unresolved P1 finding identified the risk of stranding unsettled custody when unlinking disables a courier before settlement.

## Baseline conclusion

The feature need is valid, but PR #17 cannot be treated as the implementation baseline. Its branch is retained as evidence and a prototype only.

The implementation must be redesigned and delivered through smaller PRs after:

1. Impact analysis.
2. Authorization matrix.
3. State-transition and custody invariants.
4. Account disable/unlink lifecycle rules.
5. Migration, rollback, concurrency, and idempotency design.

## Gate 1 exit criteria

- Current behavior is documented.
- Expected behavior is documented without hidden design assumptions.
- PR #17 failure and review evidence is recorded.
- The scope of PR #17 is mapped and decomposition is justified.
- Unknown root causes are marked as unverified rather than guessed.
- Human approval is recorded before Change Gate 2 begins.

## Gate outcome

Pending human review. No code, migration, merge, or deployment is included in this gate.
