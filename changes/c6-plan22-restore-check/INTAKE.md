# C6/C7 plan item 2.2: backup/restore proof inside release-finance (NAADF-CMF intake and result)

- **Date:** 2026-11-19.
- **Owner request (Claude session):** implement plan 2.2 with synthetic data only, on a separate work branch from the integration head (`183dc50`), without weakening release-finance and without secrets or production access.
- **Branch:** `claude/c6-plan22-restore-check`.
- **Not done:** no PR, no merge, no change to `main` or integration, no Lovable or production call.

## Change
- **`release-finance.yml`:** one new step, *Logical backup and restore of the candidate database (C6/C7 plan 2.2)*.
  - It sits in the existing `suite` job, gated on `collection`, so it runs in fresh, upgrade and populated modes.
  - It is placed after the last database-using step and before *Cleanup and safe final receipts*.
  - **No existing step, check name, matrix entry, firewall rule or permission is changed.** The required check inventory in `MERGE_DELEGATION.md` is unchanged.
- **New files in `tests/release/restore/`:**
  - `fingerprint.sql`: catalog fingerprint, read-only, with ACLs normalized via `acldefault`;
  - `data_hash.sql`: per-table row count and md5, rolled back;
  - `prelude.sql`: removes the fresh stack's default grants before the schema restore;
  - `run_step_local.sh`: runs the step's own YAML text locally.
  
  The last three come from the C6 work branch (`tests/c6-upgrade/restore/`), byte-identical for `prelude.sql` and `data_hash.sql`.

## What the step proves (9 required controls, step fails otherwise)
1. The source fingerprint and data hash are non-empty, and the ledger has rows.
2. The restore with the prelude succeeds into a **fresh** stack.
3. The restored data is identical per table (`public`, `monjez_private`, `auth`, `supabase_migrations`).
4. The restored catalog is identical (normalized ACLs).
5. The catalog guard passes on the restored copy.
6. **Negative:** a restore without the prelude changes the catalog.
7. **Negative:** the guard fails on that copy (anon/authenticated grants return).
8. **Negative:** one tampered ledger row changes the data hash, on the ledger line only.

## Trust boundary
- **Unchanged.** The target stack is started on the same loopback ports after the source is stopped, so the `c5finance` firewall (54321, 54322, 4173) is unchanged.
- Repository SQL and Python (the guard) run as `c5finance`. The CLI, docker, psql and pg_dump run as the runner, like the existing stack steps.
- Dumps stay in `$RUNNER_TEMP` (`umask 077`) and are not published. The evidence holds only counts and control names.

## Governance
- `.github/workflows/` and `tests/` are acceptance-defining paths in `tests/release/gate.py`. A merge into `main` needs the owner's commit-bound approval label.
- Into integration it falls under `MERGE_DELEGATION.md` (CI maintenance that adds a control) after CI and the reviews pass.
- This branch is not proposed for merge here.

## Local verification (actual)
- **Method:** the step's `run:` text extracted from the YAML and run by `run_step_local.sh`, with the CLI pinned in CI (2.101.0) and a local `c5finance` user.
- **Source:** a fresh stack of the 61 integration migrations, `project_id` `monjez-c5sale-stack`, plus synthetic rows (owner, tenant, product with stock 7.5, order, line qty 2.5, payment, audit row). The catalog guard passes on this source.
- **Positive** (`local_positive_run.txt`): 9/9 passed, exit 0. 343 fingerprint lines, 50 data tables; without the prelude, 150 catalog lines change. Both stacks stopped afterwards.
- **Real negative** (`local_negative_run.txt`): the same step with `prelude.sql` emptied (a broken restore). It failed `restored_catalog_identical` and `restored_catalog_guard_passes`, and exited **1**. In CI that fails the step, so the `suite (collection, *)` checks, which are required, fail.
- **First local attempt** (the production-like replica as source) was not valid for control 5: the source itself fails the guard because of production drift (extra policy, `email_queue_*`). It is not counted.

## Limits
- **The firewall** and the exact runner environment were not reproduced locally. The first CI run is the real proof.
- **The behavioural suites** are not re-run on the restored copy. The proof is data equality, catalog equality and the catalog guard.
- **Platform-owned rows** in `storage` and `supabase_functions` are not restored (the postgres role cannot). Application data has none.
- **`supabase stop --no-backup`** deletes the source stack's data. That is safe only because this step is last before cleanup.
- **Timing:** adds roughly 2–4 minutes to each collection job (30-minute timeout), estimated locally and not measured in CI.

## Rollback
Revert the commit: the step and the four files. No data or migration is involved.

---

# Review round 1 (Codex, #97 comment 7017598664, on 8962b2b): changes required, fixed

| finding | verification | fix (commit) |
|---|---|---|
| 1. `prelude.sql` (PR-controlled SQL) ran under the runner's psql, contrary to the intake text | **correct**: the positive restore passed `$GITHUB_WORKSPACE/.../prelude.sql` to a runner-owned `psql` | `ae28a99`: the whole restore (roles, prelude, schema, data, ledger) runs as `c5finance`. The dumps are copied into `/tmp/monjez-c5sale/restore-private` (owner `c5finance`, mode 0700), outside the published evidence, and deleted by the step's `trap`. No runner-side `psql` remains. The firewall, ports and permissions are unchanged. `02638df` records `id -un` of that wrapper and requires `c5finance` (control `repository_sql_runs_as_c5finance`) |
| 2. Plan 2.2 requires the behavioural suites on the restored database | **correct**: 8962b2b ran only the equivalence checks and the guard | `ae28a99`: the candidate's own `tests/c5-collection/native.py` runs on the restored copy as `c5finance` (same ports, `CONTRACT_MODE=fresh`, its own actors, separate evidence `evidence/restore-suite` and private state). Its exit and `financial_acceptance` are required, and so is the **same 8-control core set** the job's "Required controls" step demands for collection (checked identical by script) |

**New finding, from running the suite on the restored copy:**
- **What failed:** on the restored copy a new sign-up got no profile (`C3_owner_A_profile_seeded` failed).
- **Cause, proven:** the CLI schema dump contains `public.handle_new_user()` but **not** the trigger `on_auth_user_created` on `auth.users`, which was created by migration `20260626142422` and lives in the `auth` schema. **The same gap applies to a production backup taken this way.**
- **Fix, `0694981`:**
  - `app_triggers_outside.sql` generates, from the source, every non-internal trigger on a table outside `public`/`monjez_private` whose function is in those schemas (schema-qualified);
  - the restore applies them after the schema, in the same transaction;
  - `fingerprint.sql` now covers such triggers.
- **Consequence for the first delivery:** `restored_catalog_identical` at 8962b2b was a pass with a blind spot on this point.

## Controls now (12, all required)
1. `repository_sql_runs_as_c5finance`
2. `source_fingerprint_nonempty`
3. `source_data_hash_nonempty`
4. `restore_with_prelude_succeeded`
5. `restored_data_identical_per_table`
6. `restored_catalog_identical`
7. `restored_catalog_guard_passes`
8. `restored_collection_suite_financial_acceptance`
9. `restored_collection_suite_core_controls`
10. `negative_without_prelude_catalog_differs`
11. `negative_without_prelude_guard_fails`
12. `negative_tampered_ledger_row_detected`

## Local reruns on 02638df (`local_runs_02638df.txt`)
- **Setup:**
  - `run_step_local.sh` runs the step text from the **committed** YAML of the tested commit, in a `c5finance`-owned clone, as CI lays it out.
  - Before each run, the source (fresh stack, 61 integration migrations) was filled by running the collection suite on it, as the job does: exit 0, 108 controls; 119 public rows, 107 auth rows, ledger 61.
- **Results:**

| run | commit | result |
|---|---|---|
| positive | `02638df` | 12/12, exit 0; restored-copy suite 108 controls, exit 0 |
| negative A: `prelude.sql` emptied (local-only commit, not pushed) | `e4681b8` | failed: catalog identical, guard, suite acceptance, suite core; **exit 1** |
| negative B: restore without the application triggers (local-only commit, not pushed) | `c589319` | failed: catalog identical, suite acceptance, suite core; **exit 1** |

## CI status
- **None.** GitHub Actions lists **0 runs** for this branch: its workflows trigger on PRs and on pushes to the integration branch, and no PR was opened (as instructed).
- **The step has never run under the real firewall and runner image.**
- **2.2 is NOT complete** until CI passes on the reviewed head.

## Limits (updated)
- **Locally:** Python Playwright 1.62 was given the locally installed headless shell (build 1243) under the name it expects (1234), through a scratch directory. CI installs its own browser.
- **Other suites:** only the collection behavioural suite runs on the restored copy. The sale, journey and quantity suites do not; they would need the same pattern in their jobs, or a decision that collection is sufficient.
- **Platform rows:** `storage`/`supabase_functions` rows are not restored; application data has none.
- **Timing:** the suite on the restored copy adds several minutes per collection job (30-minute timeout). This is not measured in CI.

---

# Review round 2 (Codex, #97 comment 7018331280, on a56248f): one isolation fix, done

- **Finding (verified):** `data_hash.sql` begins with a comment line, so `head -n 1` put the tamper `UPDATE` **before** its `begin;`. psql ran it in autocommit, so the tampered ledger row **persisted** while the restored behavioural suite ran.
- **Fix (`bbe1c49`):**
  1. The `UPDATE` is inserted directly after the first `begin;` line. The awk insertion fails the step (exit 3) if no such line exists. Tamper and hash now share one transaction, which the file rolls back.
  2. Right after the probe, `data_hash.sql` runs again, and its output must equal the restored hashes (`cmp`). Otherwise the step stops with `RELEASE_RESTORE_TAMPER_NOT_ROLLED_BACK` **before** the suite.
  3. The new required control `tamper_rolled_back_before_suite` requires the post-probe hashes to equal both the restored and the source hashes. There are now 13 controls.
- **Focused local runs (`local_runs_bbe1c49.txt`):** the source was filled by the collection suite before each run.

| run | commit | result |
|---|---|---|
| positive | `bbe1c49` | 13/13, exit 0; the restored-copy suite passed 108 controls |
| focused negative C: tamper before `BEGIN`, the reviewed defect (local-only commit, not pushed) | `760b4c2` | `RELEASE_RESTORE_TAMPER_NOT_ROLLED_BACK`, exit 1; **the suite did not start** (no suite log or evidence) |

- **Not re-run:** negatives A and B, because the diff does not touch the prelude or trigger paths. Their results at `02638df` are kept in `local_runs_02638df.txt`.
- **CI:** still not run (no PR opened). Plan 2.2 is not complete until CI passes on the reviewed head.

---

# Review round 3 (Graphify review 5981314899 on dafb73a, both P2, confirmed by Codex): two fixes, done (`8f3b224`)

- **Finding 1 (reproduced):** the `rel` line of `fingerprint.sql` left out the defining query of a view or materialized view. A restored view with a changed query but the same columns compared equal.
  - **Step-level reproduction (local-only negative D-prefix):** the restored `public.day_close_profit_report` was replaced by `select * from (<its own definition>) s where false`, keeping the same columns and options. With the dafb73a fingerprint, **all 13 controls passed, including the 108-control restored suite**.
- **Fix 1:** for `relkind` `v`/`m`, the `rel` line now includes `pg_get_viewdef`. The new self-test `selftest_view_fingerprint.sh` runs on a throwaway database and checks 4 cases, all passing; on the dafb73a file, 2 of the 4 fail.
- **Finding 2 (reproduced):** `run_step_local.sh` ended with `echo "STEP_EXIT=$?"`, so the helper exited 0 even when the step failed. It also ran without `set -e`, so a failed setup (bad commit, missing restore step, failed fetch) still reached or skipped the step and returned 0.
- **Fix 2:**
  - `set -euo pipefail` for the setup;
  - the commit is verified first;
  - step extraction must find exactly one non-empty restore step;
  - the step runs with its status captured, which is printed as `STEP_EXIT=` and returned as the helper's exit status.
- **Self-test for fix 2:** the new `selftest_run_step_local.sh` checks 5 cases on stub repositories, all passing; on the dafb73a helper, 4 of the 5 fail.
- **Restore runs through the fixed helper (`local_runs_8f3b224.txt`):**

| run | commit | result | helper exit |
|---|---|---|---|
| positive | `8f3b224` | 13/13, restored suite 108 controls | 0 |
| negative D: restored view query changed, same columns (local-only) | `646c059` | failed: `restored_catalog_identical` only | 1 |
| negative D-prefix: D with the dafb73a fingerprint (local-only) | `70050a0` | failed: none (the finding) | 0 |
| negative C: tamper before `BEGIN` (local-only) | `d00ddb4` | `RELEASE_RESTORE_TAMPER_NOT_ROLLED_BACK`, the suite did not start | 1 |

- **Not re-run on `8f3b224`:** negatives A (empty prelude) and B (no app triggers). The added view text cannot make two differing fingerprint lines equal, but this was not proven by a run.
- **Other limits:**
  - the fingerprint still does not cover view `reloptions` such as `security_invoker`, or a trigger's enable state (Strix hardening note);
  - nothing in this round changes the workflow YAML, migrations, product code, `main`, production or publishing;
  - the local-only negative commits exist only as local branches and are not pushed.
- **CI:** the new head needs CI and review, which Codex runs. Plan 2.2 is not complete until that passes.
