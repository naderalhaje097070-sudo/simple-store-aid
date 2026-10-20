# SEC-CI-001 — Rollback Impact

## Rollback scope

CI/workflow configuration only. No product code, schema, migration, or production data is changed.

## Rollback plan

If the hardened workflows prevent valid execution or break required-check integration:

1. Revert only the focused SEC-CI workflow commit(s).
2. Restore the previous workflow definitions without changing application code.
3. Re-run the same exact-head Quality, Financial Rules, and Auth UI checks.
4. Record why the hardened version failed and reopen design review before another attempt.

## Non-rollback items

- Do not reintroduce secret exposure or raw environment dumps merely to recover verbose diagnostics.
- Do not weaken T1–T15, auth smoke, or change-specific assertions.
- Do not rename checks as a workaround for branch-protection issues without human repository-setting review.

## Data recovery

None required; isolated CI fixtures are disposable.

## Administrative dependency

If the execution blocker is account budget/quota or repository Actions policy, repository rollback cannot fix it. The owner must resolve the account/repository setting, after which the unchanged exact head should be re-run.