# C6 3.1–3.2: transport record of the C6 package to the integration candidate (2026-11-20)

- **Branch:** `claude/c6-package-prep`, carrying the prep commits (`13e9a78`, `2b2b152`, `fa7ecc8`).
- **Base:** integration `f9807b5543e273e1b6a5370c49f7af0845010c78`, merged with a normal merge (`e516a89`). No history was rewritten.
- **Package source:** `claude/monjez-c6-upgrade-39hf77` at `deaff17da566bde7ff20d08e71bc56c396d4e170`.
- **Manifest:** `MANIFEST_deaff17.tsv` (sha256 `2786f854c196c692cc462b43de3c0170fbe70cf92ad64ea2a35f1445e2beb75f`).
- **`main`:** `1c5276fae77cb71f49d868fe71d17d84c5d3c6b3`, unchanged.
- **Not touched:** migrations, product code, workflows, existing tests, production and Lovable.

## 1. Applying the manifest decisions

| decision | rows | what was done |
|---|---|---|
| `MOVE` | 145 | **143 moved** byte for byte. 2 withheld as raw production or live output (below) |
| `MOVE-with-text-review` | 3 | semantic merge (§3) |
| `NO` | 3 | not moved: the migration is already in integration with the same blob; two files are identical to `tests/release/restore/` |
| `OUT-OF-C6` | 32 | not moved |

**Withheld from `MOVE`:** raw text and production data. The moved documents keep their summaries.

| path | reason |
|---|---|
| `docs/reviews/c6-evidence/sandbox_exec_prod_read_2026-11-18.json` | raw output of a production read: the privileges of the `sandbox_exec` role |
| `docs/reviews/c6-evidence/pwa/live_probe_2026-11-18.txt` | raw HTTP output from the live site |

- `C6_LOCK_RESTORE_PWA.md` links to the second file, so that link is broken on this branch.

**One documented exception to byte-identity:** `tests/c6-upgrade/pwa_probe.cjs`.
- **Why:** the quality workflow's `Lint changed source files` step failed on it with 7 prettier errors, all formatting.
- **What was done:** the project's prettier was applied (`1564c23`), following the repository's precedent `fbb6209`.
- **Proof:** the AST is identical, and the esbuild-minified output is byte-identical before and after (837 bytes, same directory).

| | git blob | sha256 | bytes |
|---|---|---|---|
| in the manifest | `a189a1bcae8f8909d49c7f9507e7d2dc720e97a2` | `61713f5b56039cdcd6dbd1d6180866295b8ae23c9e5e45f027a3abf3476414ce` | 1,013 |
| on this branch | `a37906ab00f541e9b767bf6811f6ae7ecc28c6bd` | `348f9e4791ae51cf6dd7feb0f23dacde3f0e263a7cac37cedfa14f1dfb2108cd` | 1,145 |

**Two transport fixes after Codex's review of `69f6795` (commit `d48a97a`).** Both files are moved files, so their blobs now differ from the manifest:

| file | manifest blob / sha256 | on this branch | why |
|---|---|---|---|
| `tests/c6-upgrade/restore/rehearse.sh` | 857d58b3 / 2dc9d59f81bf5a2c… | 40563c36 / c3e39093887cffda… (after `697df0b`) | read `prelude.sql` and `data_hash.sql` from its own directory; those rows are `NO` because the same bytes are already in `tests/release/restore/` (blobs `82a109fa`, `6117645c`). It now uses those documented helpers and refuses to run (exit 2) unless their sha256 equals the reviewed bytes |
| `tests/c6-upgrade/review_fixes.sh` | 9059923d / 789de875d17dd718… | 60f4d396 / f795fe737a0f414f… | read the pre-fix emergency revert from commit `e32f92b`, which is not in the integration history. It now uses the fixture below after checking its sha256, and compares it with `e32f92b` only when that commit is reachable |

**Added, a synthetic local-test fixture:**
- **File:** `tests/c6-upgrade/fixtures/old_emergency_revert_e32f92b.sql.fixture`.
- **Content:** the original 276 bytes of the pre-fix `EMERGENCY_unblock_legacy_frontend_revert.sql` at `e32f92b`.
- **Digests:** blob `09c3ce918063e1fcf70c08a0f2930595dca26d94`, sha256 `f357c099a3a67b0f454ebe02188eabfd62d29fe6ec1d9f10f099a61867ab0aae`.
- **Use:** `tests/c6-upgrade/fixtures/README.md` states it is local-test only. It runs only inside `BEGIN … ROLLBACK` against the gate's own replica container.
- **Unchanged:** the current emergency revert file.

**Platform COPY filter in `rehearse.sh` (commit `697df0b`, Graphify P2 on `2829ebc`):**
- **The problem:** the filter dropped only the quoted form `COPY "storage".…` / `COPY "supabase_functions".…`.
- **What the reviewed CLI emits:** 2.101.0, which release-finance pins with `setup-cli` `version: "2.101.0"`, writes only that quoted form. In the real dump, all 58 COPY headers were quoted and none unquoted.
- **Why a fix was still needed:** `rehearse.sh` takes any CLI binary and has no version pin.
- **The fix:** it now matches exactly those two schemas, quoted or unquoted. Look-alike names stay.
- **Proof:**
  - `selftest_copy_filter.py` runs the script's own filter on a synthetic dump: 11/11, while the pre-fix filter fails both unquoted forms;
  - on the real CLI 2.101.0 dump, `data_app.sql` is byte-identical before and after: 48 of 58 COPY blocks kept.
- **Not changed:** the same quoted-only filter in the release-finance restore step (`.github`). It runs only with the pinned 2.101.0, and an unquoted platform block would make the restore fail visibly, not silently.

## 2. Verification (actual results)

| check | result |
|---|---|
| git blob, sha256 and size of the 143 moved files against the manifest, at `60009244` | **0 mismatches**; at the current head only `pwa_probe.cjs` differs, as stated in §1 |
| files added against integration | 145 = the 143 moved + the 2 files of `docs/reviews/c6-package/` (from the prep). No `NO` or `OUT-OF-C6` row present |
| modified files against integration | only `DECISIONS.md`, `PROJECT_STATE.md` and `TASKS.md`. Nothing deleted. No existing file under `tests/` or `.github/` changed |
| `docs/reviews/c6-apply/SHA256SUMS` | **20/20** |
| `supabase/migrations` tree | `ef10e8e2016240f627dcac206ae6aa7f60698c67`, **identical to integration** |
| `bash scripts/lint-changed.sh` (base = integration) | exit 0 after the formatting, exit 1 before (7 prettier errors) |
| `tests/c6-upgrade/gate_selftest.sh` (no database) | exit 0, `0 failure(s)` |
| `tests/release/test_gate.py` | exit 0, `OK` |
| scan of the moved files for keys or tokens (`eyJ…`, `sk_…`, `BEGIN`, passwords, emails) | 1 hit: the name of a vault secret inside an SQL function body (`replica_drift.sql`), with no value |

**After the transport fixes (`d48a97a`), on a clone limited to this branch** (`git clone --single-branch`; `e32f92b` is **not** reachable there):

| check | result |
|---|---|
| `rehearse.sh` helper guard | `tests/release/restore` reached, digests OK |
| `review_fixes.sh` fixture guard | fixture reached, digest OK; it is the pre-fix file (no `REVERT_REFUSED`) |
| `tests/c6-upgrade/gate_selftest.sh` | exit 0, 19 PASS, `0 failure(s)` |
| `tests/c6-upgrade/review_fixes.sh` (full gate, local replica from the `1c5276f` worktree) | exit 0, **46 PASS, `0 failure(s)`**. S4 now runs from the fixture: `old revert at C2 leaves no collection path (defect reproduced)` |
| `tests/c6-upgrade/restore/rehearse.sh` (local replica → fresh local `restoretarget`) | exit 0, `DATA identical: 50 tables` |
| negative: a synthetic change to `tests/release/restore/prelude.sql` in a copy | `REHEARSE_HELPER_MISMATCH`, exit 2, before any dump; no work directory created |
| negative: a synthetic change to the fixture in a copy | `die: old-revert fixture digest`, exit 1 |

- **Check count:** where `e32f92b` is reachable, `review_fixes.sh` adds one more check (the fixture bytes equal the commit's file). The blobs are equal (`09c3ce91`). That variant was **not run**.

**Not run:**
- the rest of the CI suites, which run on #99;
- any offensive testing, which none of this is.

## 3. State files

- **Newest resume points:** the 2026-11-20 checkpoints stay on top, so the newer resume points are not replaced.
- **Imported history:** the C6 blocks the work branch added since the merge base (17 in `PROJECT_STATE.md`, 17 in `TASKS.md`) are imported **verbatim** under a separate heading below those checkpoints, as superseded history. Their headings are demoted one level.
- **Decisions:** 4 C6-related decisions are added to `DECISIONS.md` (three on 2026-11-19 and one on 2026-11-09).
- **Not imported:** the blocks outside C6 on that branch, namely RECOVERY-02, Phase C, merges #86–#95, the GOV-AUTOMERGE proposals, JOURNEY-FLAKE-01, and the 2026-11-07 email-hotfix decision.
- **No duplication:** no block duplicates an existing one, and no line was deleted.

## 4. Sensitive content for the owner to decide

The moved reviewed documents describe the production `sandbox_exec` role's privileges (LOGIN and BYPASSRLS, plus SELECT/INSERT on public tables):
- `C6_SANDBOX_EXEC_ANALYSIS.md`;
- `C6_LOCK_RESTORE_PWA.md`;
- `C6_SIMULATION_AND_LEDGER_PLAN.md`;
- `replica_drift.sql`, which recreates the role in the replica.

The same text has been on the public work branch since 2026-11-18, and there is no secret value in it. Removing it from these documents would change reviewed files, so that is left to the owner's decision.

## 5. Item 3.4: re-measured only, the control unchanged

Measured on isolated clones with `origin/main` = `1c5276f`:

| head | `tests/b5-lifecycle/inventory.py` (direct path: `b5-lifecycle`, `b50-natural-expiry`) | `capture.py identity` → `tests/release/gate.py` |
|---|---|---|
| integration `f9807b5` | exit 1, `Protected source path set changed` (554 protected against 396 pinned: 161 extra, 3 missing) | exit 0 |
| package `1564c23` | exit 1, the same (588 protected: 195 extra, 11 of them migrations, **34 from the package**, 3 missing) | exit 0 (61 migrations, base migrations preserved) |

- **Remaining blocker:**
  - The direct path pins 50 migrations at base `59c8a0c` (`integrated_identity.py:113` and `:126`; `inventory.py:27`), and it fails on integration with or without the package.
  - Closing it means changing that control: either moving those jobs onto `gate.py`, or changing its pinned base.
  - Either one needs the owner's decision and the commit-bound `gov-ok-<sha>` label.
- **This batch:** it changes and disables nothing.
