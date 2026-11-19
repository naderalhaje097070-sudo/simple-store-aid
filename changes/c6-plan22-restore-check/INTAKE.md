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
