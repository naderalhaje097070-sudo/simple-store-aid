# Retire automatic push runs of sec-dep-20261102.yml (2026-11-16)

**Classification:** CI/governance change (acceptance-defining), with no application, database or dependency change. It needs the owner's decision.
**Reason:** `tests/c4-sale/history.test.cjs`, a step in this workflow, pins `src/routes/_authenticated/app.tsx` to the historical C4 base blob, so it fails on every current integration head regardless of what is pushed:
- integration base `2e4c8cc`, before #93: reproduced locally, 1 pass / 1 fail;
- `fc6b39b`, after #93: push run 43887311036 failed, with `Unreviewed profit module mutation`.

`c4-sale.yml` was retired from automatic runs for the same reason on 2026-11-10.

**Correction of an earlier claim:** I previously wrote that integrated-quality covers the same tests. It does not: integrated-quality runs `c4-sale/contracts.test.cjs` and `c4-sale/test_identity.py`, but not `history.test.cjs`. Also, `set -euo pipefail` in that failed run skipped the later steps (node-server contracts, the 20261029 regressions and `git diff --exit-code`).

## Coverage map (verified)
| Check in sec-dep-20261102.yml | Where it runs after this change | Evidence |
|---|---|---|
| capture.py identity, 20261102 historical graph (16), identity (23), 20261116 graph (24), installed (6), contracts.cjs | integrated-quality SEC step, every PR | green on #93 and #92 heads |
| dependency-security.test.ts | integrated-quality unit tests, and sec-dep-20261029.yml (push) | 25/25 |
| c4-sale/contracts.test.cjs | integrated-quality and release-finance, every PR | 35/0 locally on fc6b39b |
| g0-node-server/contracts.test.cjs | **added to integrated-quality by this change**; sec-dep-20261029.yml (push) | 8/0 locally; push run 43887311036 green on fc6b39b |
| sec-dep-20261029/regressions.cjs | **added to integrated-quality by this change**; sec-dep-20261029.yml (push) | all checks passed locally; push run green on fc6b39b |
| git diff --exit-code | integrated-quality "Verify generation leaves tracked application files intact" | existing step |
| c4-sale/history.test.cjs | **historical only**: last green run 41492623491 at 552ce47 (2026-11-02), reproducible by checking out that commit | not a current-state control |

## Change
- `sec-dep-20261102.yml`: the `push` trigger is replaced by `workflow_dispatch`. Its steps are unchanged, and the coverage map is recorded in a header comment.
- `integration-verification.yml`: adds `node --test tests/g0-node-server/contracts.test.cjs` and `node tests/sec-dep-20261029/regressions.cjs` to the existing "Type erasure and actual hook callback wire replay" step.

## Verification
- The changed step was run locally on this branch: rc=0, with 4/22/35/8/11 tests passing, the regressions in "patched" mode, and all checks passing.
- b7-ci-routing: 17/17. test_gate: OK.
- Not yet verified: a manual dispatch of the retired workflow on the integration branch, after merge, which can only run once the change is on that branch. It is expected to stop at `history.test.cjs`, as documented.

## Rollback
Revert the PR. This restores the push trigger; the integrated-quality additions are independent of it.
