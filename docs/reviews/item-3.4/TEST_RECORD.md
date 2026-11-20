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
| `test_candidate_identity.py`, synthetic repositories | 28/28 OK, including 25 rejection cases (details below) and a check that the real committed manifest equals a regeneration from the tree |
| `real_negatives.sh`, 13 cases on a real-tree clone | the unchanged head is accepted (63), and all 12 mutations are refused (`real-negatives.log`) |
| `inventory.py` on the real tree | accepted: 596 protected blobs, 63 migrations, B50 and original41 preserved, 13 new, 2 sorting before the B50 max |
| B50 `test_integrated_identity.py` | OK (unchanged) |
| `test_contract.py` | 6/6, including the new stage, sale-surface, keyed-body and idempotency negatives |
| `account-lifecycle` unit suites (owner_closure, natural_expiry, mcp, tanstack_route) | OK |
| `b7-ci-routing/contract.test.cjs` | 17/17 (run with a local `js-yaml` 4) |
| `live_harness.py` on the local 63 stack | 22 real `ComposedProbe` checks passed (`live-result.json`), plus the results below |
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
- a keyed replay with the same key returns the same order, and a different body with that key gets `400 idempotency_conflict`;
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

## Heads tested

- `unit-tests.log`, `real-negatives.log` and `live-result.json`: final code head `c60da08`.
- `upgrade-result.json` and `upgrade-migration-up.log`: `60b4411`. Between that commit and `c60da08`, only `docs/` and `candidate-63-source.json` changed (`git diff --stat 60b4411 c60da08`). No harness, workflow or verifier code changed.
