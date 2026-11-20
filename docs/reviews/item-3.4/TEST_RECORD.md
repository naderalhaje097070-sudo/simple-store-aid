# Item 3.4 — candidate63 identity verifier: record

Branch `claude/c6-item34-candidate63-identity`, from integration `09089be291a56fd2a76ba8c0943564c30e5a4eb8` (migrations tree `08d0c94e060d3ea44b23759e41ed193adf979c0e`, 63 files). Local, synthetic data only. No production access, no merge, no publish. No migration, no frozen manifest and no `integrated_identity.py` was changed.

## Problem (measured)

`tests/b5-lifecycle/inventory.py` called the frozen B50 verifier, which requires exactly 50 migrations. Integration has 63, so every direct consumer stopped at the first step:

- B5 lifecycle (fresh and upgrade);
- B5 SSR and B5 billing;
- B50 natural expiry.

The harness also hard-coded four facts that are false on the candidate:

| Hard-coded | On the candidate |
|---|---|
| 22 public tables | 23: `financial_idempotency` is added |
| TRUNCATE denial for 44 grants | 46 |
| 50 migrations in the SSR, natural-expiry and billing probes | 63 |
| the legacy `create_sale_with_items` for every sale and denial call | not executable by `authenticated` |

On the legacy sale RPC, measured: `has_function_privilege` returns false. A banned or closed actor gets `403/42501` permission denied, not `account_inactive`, so the named-denial control would fail for the wrong reason.

Measured on the real tree: the 50 B50 migrations are **not** the first 50 entries of the 63-migration ledger. Two reviewed finance migrations sort after the original41 but before nine B50 migrations:

- `20260815170000_fin_courier_pr_a`
- `20260815171000_fin_idem_sale_create`

The verifier therefore requires B50 as an exact ordered subsequence of the ledger, and reports these two files.

## Change

1. **Candidate verifier.** `tests/g01-acceptance/candidate_identity.py` and `candidate-63-source.json` are new. The verifier accepts the tree only if every check below holds; any difference is a refusal, with no override.
   - **Protected paths:** exact path set; blob and mode match in both the index and the worktree.
   - **Ledger:** the full ordered 63-entry ledger (path, blob, mode) equals `ls-tree` of the fixed candidate base `09089be`.
   - **B50:** all 50 files, byte- and mode-identical, in their own order, equal `ls-tree` of the fixed B base `59c8a0c`.
   - **original41:** the exact ordered prefix, against the frozen A41 map.
   - **New migrations:** every non-B50 migration sorts after original41.
   - **Frozen manifests:** A41 `b79640f4…` and B50 `71895f74…` are pinned by blob, tracked as `100644` and not executable.
   - **Ancestry:** both base commits are ancestors of HEAD.
2. **Consumers.**
   - `inventory.py` uses the new verifier and returns three lists: the 63 candidate migrations, B50 and original41.
   - The B5 lifecycle step that starts the stack copies original41 for upgrade and the 63 for fresh. It runs the verifier first and checks the length: 41 or 63.
   - SSR and B50 natural expiry require the identity counts of 63, 50 and 41.
3. **Stage-exact surface.** In `tests/b5-lifecycle/candidate_surface.py`, the stage is the live ledger size: 41, 50 or 63. Any other size is refused.
   - **Public tables:** exactly the 23 named tables at 63. At 41 and 50, the historical rule is kept: 22 tables, and no `financial_idempotency`.
   - **TRUNCATE:** denied over the live set (`2 × n` grants).
   - **Sale RPC:**
     - **At 41:** the keyed sale is absent, the legacy sale is executable by `authenticated`, and the legacy path is used.
     - **At 63:** the keyed sale is executable by `authenticated` only. The legacy sale and `_v2` are not executable by any client. The keyed path is used, with a fresh key for each call.
   - **Idempotency ledger:** RLS is on, there are no policies, and anon and authenticated have no privilege of any of the 7 kinds.
   - In `owner_closure_probe.py`, the base default stays the legacy RPC. The candidate path is chosen by the adapter.
4. **Billing.** `tests/b5-lifecycle/billing_probe.py` runs the inherited `WebhookProbe` cases. Only the source and chain expectation changed: the disk files must equal the candidate ledger by blob. It supports only the fresh full chain, which is this job's whole matrix; the populated `before` phase is refused. `webhook_persistence_probe.py` is unchanged, so the dormant B4 workflow is not triggered.

## Results (commands and outputs in `unit-tests.log` and the files here)

| Check | Result |
|---|---|
| `test_candidate_identity.py`, synthetic repositories | 33/33 OK: 30 rejection cases, including 5 commit-binding cases (see the Codex review section), and a check that the real committed manifest equals a regeneration from the tree |
| `real_negatives.sh`, 13 cases on a real-tree clone | the unchanged head is accepted (63), and all 12 mutations are refused (`real-negatives.log`) |
| `inventory.py` on the real tree | accepted: 596 protected blobs, 63 migrations, B50 and original41 preserved, 13 new, 2 sorting before the B50 max |
| B50 `test_integrated_identity.py` | OK (unchanged) |
| `test_contract.py` | 6/6, including the new stage, sale-surface, keyed-body and idempotency negatives |
| `account-lifecycle` unit suites (owner_closure, natural_expiry, mcp, tanstack_route) | OK |
| `b7-ci-routing/contract.test.cjs` | 17/17 (run with a local `js-yaml` 4) |
| `live_harness.py` on the local 63 stack, after the target guard | 25 real `ComposedProbe` checks passed (`live-result.json`), including 3 row-level replay checks, plus the results below |
| `upgrade_check.py` on the local original41 stack, then a real `supabase migration up --local` | exit 0 (`upgrade-migration-up.log`), with all 41 checks and the 8 keyed-fixture checks passed (`upgrade-result.json`; full list below) |

The 25 synthetic rejection cases cover:

- an old file corrupted, a whitespace-only change, or deleted;
- the same count with a replaced, renamed or non-SQL file;
- a ledger blob forged or reordered;
- a new file sorting inside original41;
- an extra path or migration;
- a mode change in the worktree, the index or a commit;
- a frozen manifest edited, or the candidate manifest uncommitted;
- a wrong base, or a base that is not an ancestor;
- a protected source change.

Wherever the tamper can be committed, it is also tried committed with a regenerated manifest.

The 12 real-tree mutations are:

- a B50 or A41 file corrupted (worktree, or committed with the manifest regenerated);
- a B50 file deleted;
- a B50 file swapped for a new one at the same count;
- an extra path or migration;
- a mode change;
- the frozen B50 manifest edited;
- the verifier source edited without review.

`live_harness.py` on the local 63 stack also showed:

- the legacy call is refused with `403/42501`, so `explicit_inactive` is false;
- the keyed sale's replay safety, asserted on the stored rows, not only on the response:
  - the first call writes exactly 1 order, 1 item and 1 payment, moves stock by −2 (the quantity sold), and adds exactly one completed `financial_idempotency` row, whose key is the request key and whose stored result equals the response;
  - the exact replay returns the same result and changes no order, item, payment, stock or ledger row;
  - a different body with the same key gets `400 idempotency_conflict` and changes nothing;
- a banned actor gets an explicit `account_inactive` from `current_tenant_id`, `get_tenant_today_estimate` and the keyed sale, and the state is unchanged;
- the B50 snapshot has 23 tables;
- the billing source check passes.

`upgrade_check.py` covered:

- the legacy seed on original41;
- the 22 original tables and auth identities preserved;
- the exact 63 chain;
- the sale surface at 63;
- the new private tables and `financial_idempotency` empty;
- `client_truncate_denied_all23`;
- the idempotency lock;
- the keyed fixture for a fresh owner;
- a banned owner's named denials, with the state unchanged.

## Limits (not verified here)

- No CI run yet. B5 lifecycle and natural expiry do not run on PRs into integration; they run on the integration push after merge (B5 paths) and on PRs into main.
- The local checks bypass the probe constructor, which needs the CI containment preflight: dedicated UID, firewall and redirect guard. They do not run the built app, OAuth/PKCE, Nitro MCP, the price route, the SSR browser runtime, natural token expiry, closure through the app, or the billing webhook cases. Those run only in CI.
- The local stacks run Supabase CLI 2.101.0 with the default local keys. The CI images may differ in patch level.
- The 41-stage sale-surface rule was confirmed only on this local original41 stack.
- The billing populated `before` phase (47→50) is not in the job matrix and is refused by the adapter, so it is not covered.
- Production: nothing was read or written. Whether production can apply the two August-dated migrations after later versions is a production ledger question, not answered here.

## Rollback

Revert this PR's commits. `integrated_identity.py`, the A41 and B50 manifests, all migrations and the B50 tests are unchanged, so reverting restores the previous state exactly.

## Codex review of `773805ab` — fixes

**1. Commit binding (verifier).** At `773805ab`, the verifier compared the manifest with the index and the worktree, and the manifest file with `HEAD`. It did not check that `HEAD`'s tree carries the same protected files. It now also requires that `ls-tree -r --full-tree HEAD`, restricted to protected paths, equals the reviewed snapshot exactly: path set, blob and mode. A non-blob entry is refused. The three manifests must also be identical in `HEAD` and the index.

Five new synthetic cases cover a commit that differs while the index and worktree still agree with the committed manifest:
- `HEAD` blob differs, with the index and worktree matching the manifest;
- `HEAD` lacks a file that the index, worktree and manifest all hold;
- `HEAD` holds a file absent from the index, worktree and manifest;
- `HEAD` mode differs;
- the manifest in the index differs from the one in `HEAD`.

The first four fail closed with `Protected HEAD tree differs from reviewed snapshot`. The fifth fails with the existing uncommitted-manifest check.

The past checks are unchanged:
- `integrated_identity.py` and its tests;
- the A41/B50 manifests;
- the release gate (`capture.py identity` / `tests/release/gate.py`).

**What a regenerated manifest can and cannot admit:** `--print-manifest` rebuilds the snapshot from the committed tree.
- **Non-migration files:** a regenerated manifest admits any change to them. Such a change is accepted only through review of the commit that carries it.
- **Migrations:** a regenerated manifest cannot admit them. The full ordered ledger must equal the fixed reviewed `CANDIDATE_BASE_SHA` (`09089be`), and the B50 subsequence must equal the fixed B base (`59c8a0c`). Moving to a new ledger requires a reviewed change of `CANDIDATE_BASE_SHA` in `candidate_identity.py`.

The same text is in the verifier's docstring.

**2. Lab helpers: target guard before any write.** `lab/lab_guard.py` runs before the first request or SQL statement that can write, in both `live_harness.py` and `upgrade_check.py`. It applies the same target rules as `live_probe.Probe.__init__`:
- `require_write_harness()`: explicit opt-in, no proxy routing, loopback PG on 54322, target local/ci;
- `CI_ISOLATED_SUPABASE=1`;
- the status `API_URL` equals `config.supabase_url`, which equals `http://127.0.0.1:54321`;
- both disposable keys are present.

It adds one check of its own: every existing `auth.users` identity on the target must be synthetic (`example.test`, `example.invalid` or `mongezz.test`).

Negatives (`guard-negatives.log`): 8 refused and 2 accepted.
- **Refused:** wrong API port, remote API URL, missing key, no isolation marker, config URL mismatch, proxy routing, and a non-synthetic identity present on the target.
- **Accepted:** the valid local target, before the non-synthetic identity was inserted and after it was removed.

**3. Replay evidence:** the row-level assertions listed above replace the earlier response-only claim.

## Heads tested

- `unit-tests.log`, `real-negatives.log` and `live-result.json`: final code head `c60da08`.
- `upgrade-result.json` and `upgrade-migration-up.log`: `60b4411`. Between that commit and `c60da08`, only `docs/` and `candidate-63-source.json` changed (`git diff --stat 60b4411 c60da08`). No harness, workflow or verifier code changed.

## What was tested, and what still needs CI on the acceptance path

The code I changed, and the place each part is verified:

| Part | Verified here (local, synthetic) | CI on PR into integration (#103) | Still needs CI on the acceptance path |
|---|---|---|---|
| Candidate verifier and manifest | 28 synthetic tests, 12 real-tree rejections, accepted on the real tree | Yes: the new step in `integration-verification.yml` (`integrated-quality`) runs `inventory.py`, `test_candidate_identity.py` and `test_contract.py` | — |
| B50/A41 frozen identity | `test_integrated_identity` unchanged and passing | Yes (existing step) | — |
| Stage rules: tables, TRUNCATE, sale RPC, idempotency lock | unit tests; live on a 63 stack; live 41→63 upgrade | unit tests only | Live B5 lifecycle `fresh` and `upgrade` |
| Composed flow: app, OAuth/PKCE, Nitro MCP, price route, ban, closure through the app | not run (needs the containment preflight) | No (B5 lifecycle does not trigger on PRs into integration) | B5 lifecycle `fresh` + `upgrade` |
| SSR browser/runtime | count check only, via inventory | No | B5 `ssr` job |
| Billing webhook cases | the source/ledger check only | No | B5 `billing` job |
| Natural token expiry | snapshot override only (23 tables) | No | `B50 Real Token Expiry` |

**When the CI-only rows run:** B5 lifecycle runs on a push to integration that touches `tests/b5-lifecycle/**`, its workflow file or the candidate files. `B50 Real Token Expiry` runs on a push to integration that touches its paths, which now include the candidate files. Both also run on PRs into main. So the merge of #103 into integration is the first run of these four jobs. Until those runs are green on the merge commit, the B5/B50 rows are **not accepted**. No PR into main was opened, and no check was relaxed or skipped.

## Opinion on the rest of 3.4 and the Pilot (Claude, not a decision)

Recommended order, from what blocks the most:

1. **Merge #103 into integration, then read the four post-merge runs on the merge SHA.** This is the only route to the CI rows above without a PR into main. If a run fails, fix it on a new branch; never fix it by relaxing a control.
2. **Read the production migration ledger, read-only, under the scope the owner approves (count, ordered versions).** This is now a release blocker: two August-dated migrations sort before nine October B50 migrations. If production has already applied the October ones without the August ones, an ordinary `migration up` will refuse or skip them. Nothing about apply method, backup or date should be decided before this is known. The query can be added to the existing `C7_PROD_READ_SCOPE.sql` approval, so the owner approves one read, not two.
3. **Production backup and isolated restore.** Then the C6/C7 apply under the owner's approval, then the main PR with the full acceptance suite (which also re-runs B5/B50 on the main PR).
4. **Owner-only Pilot**, after all of the above.

**Alternative I consider better than re-pinning by hand at every step:** make the candidate manifest the only thing that changes per candidate. Generate it in review; the verifier pins the base commit and the frozen B50/A41, and refuses anything else. That is what #103 does. The verifier then needs no code change for the next candidate; only the reviewed base SHA and counts move. A single "latest" verifier that reads the counts from the tree would be simpler, but weaker, because nothing would pin the ledger to a reviewed commit. I do not recommend it.
