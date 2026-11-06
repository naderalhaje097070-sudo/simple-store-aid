# المراجعة المستقلة لبوابة الإصدار — 2026-11-06

- **المراجِع:** وكيل مستقل للقراءة فقط، منفصل عن المنفّذ، لم يعدّل أي ملف.
- **ما راجعه:** commit `b2c9dc7` على فرع التكامل.
- **الحكم:** "Phase 1 cannot close as-is".
- **النص:** التقرير الأصلي منقول بلا تعديل في القسم الثاني. القسم الأول يذكر ما فُعل بكل بند، والـcommit
  الذي يحمله. "مُصلَح" تعني أن الكود والاختبار موجودان، ولا تعني أن CI نجح عليه. نتيجة CI تُسجَّل في
  `PROJECT_STATE.md`.

## 1. معالجة البنود

| البند | الحالة | أين |
|---|---|---|
| 1 BLOCKER: الالتفاف على الحوكمة (المساعدات المشتركة، shadowing، الإعادة التسمية، الاعتماديات) | مُصلَح: الحوكمة صارت قائمة سماح. كل ما خارج `src/` و`public/` و`supabase/migrations/` و`supabase/functions/` و`docs/` و`*.md` في الجذر يحتاج اعتمادًا. يُستخدم `--no-renames`. لكل حالة اختبار رفض | `58d84cd` `tests/release/gate.py`, `test_gate.py` |
| 1: اختبار تغطية الاستيرادات | لم يُنفَّذ كما اقتُرح. قائمة السماح تجعله غير لازم، لأن أي ملف تحت `tests/` محكوم مهما كان مساره. اختبارات `test_dependency_and_build_config_blocked` و`test_new_unknown_top_level_file_blocked` تغطي المسارات غير المعتادة | `58d84cd` |
| 2: الوسم غير مربوط بالـcommit ولا بالمالك | مُصلَح: الوسم صار `gov-ok-<SHA>`. يُقبل فقط إن كان آخر حدث له إضافة مباشرة من المالك وليست عبر تطبيق. **غير مُتحقَّق فعليًا:** وجود الحقل `performed_via_github_app` في أحداث GitHub. يفشل الفحص مغلقًا إن غاب الحقل | `58d84cd` `release-gate-trusted.yml` |
| 3: بصمات البايت في الرحلة | مُصلَح بمفتاح `MONJEZ_RELEASE_TARGET`. سلسلة الهوية القديمة في `integrated-quality` باقية عمدًا حتى يُثبت البديل، وموثّقة | `58d84cd` `tests/c5-journey/native.py` |
| 4: تغطية مفقودة | مُستعاد: c4 browser، و`selector_contract`، و`test_verdict`، وملفا `history.test.cjs`، ومقارنة كل الجداول عبر الترقية (البداية = سجل `main`، والنهاية = المرشح). مُضاف: c2 quantity. خارج الفحوص: الاستعادة (شرط Pilot) وc3 وb2–b4، وهي موثّقة كفجوات | `58d84cd`, `dd6d686`, `docs/RELEASE_COVERAGE.md` |
| 4: `profit_upgrade_exact_old_row_preserved` و`gross12_net7` | لا تعمل في الترقية الجديدة لأن مرحلة seed55 غير موجودة. بدلًا منها: `upgraded_all_base_relations_preserved` (صف `day_closes` القديم بلا تغيير) و`upgraded_saved_close_reads_margin84_net79` (القراءة عبر الـview الجديد) | `58d84cd` `tests/release/upgrade.py` |
| 5: لا controls مسماة في fresh | مُصلَح: حد أدنى مسمى لكل suite في كل mode | `58d84cd`, `dd6d686` |
| N2: مجلد مفقود، وتاريخ في المستقبل البعيد | مُصلَح. والتاريخ المستحيل مرفوض أيضًا | `58d84cd` |
| N3: احتمال فشل متقطع إن عبر البذر منتصف الليل | غير مُعالَج. خطر متبقٍ | — |
| N4: لا يُسجَّل المسار المقبول | مُصلَح: `denied_by_account_inactive` في observed | `58d84cd` |
| N5: `!paths` والـworkflows الجديدة في b7 | مُصلَح، مع اختبار أسماء فحوص فريدة | `58d84cd` |
| N7: عدد البداية 50 | مُصلَح بشكل أدق: سجل البداية يساوي سجل `main` بالضبط | `58d84cd` |
| N8: control `quarter` المتقطع | غير مُعالَج: السبب الجذري غير معروف. خطر متبقٍ | — |
| S1: `fetch` بلا اعتماد في مستودع خاص | مُصلَح: اعتماد لمرة واحدة عبر header، لا يُحفَظ | `58d84cd` |
| S2: اسم `gate` قابل للتكرار | مُصلَح: الاسم الجديد `trusted-release-gate`، و`quality` صار `integrated-quality`. b7 يفرض التفرد | `58d84cd` |
| S3: actions مثبّتة بالوسم | غير مُعالَج: خطر متبقٍ | — |
| S4: النتائج تتقادم إذا تحرك `main` | يعتمد على تفعيل "Require branches to be up to date" (إجراء المالك) | `docs/RELEASE_GATE_SETTINGS.md` |

## 2. التقرير الأصلي (بلا تعديل)

Phase 1 cannot close as-is. The trusted gate itself is sound, but its governance block is easy to get around, the label approval is not tied to any commit, and the journey suite still uses the old byte pins.

Branch b2c9dc7, read-only review.

**Tests run:**
- `python3 tests/release/test_gate.py`: 23/23 OK.
- `node --test tests/b7-ci-routing/contract.test.cjs`: 12/12 pass.
- Governance bypasses: I ran these in a scratch repo, using the real `gate.governance_changes`.

## Confirmed defects

**1. BLOCKER — the governance block does not stop PRs from making required checks pass trivially.** `tests/release/gate.py:42-50` and `:114-116`.

GOVERNANCE_PATTERNS only lists entry-point files. Every suite imports modules outside the list, and the governance diff hides rename sources. Each of the following passes with no label:
- **Shared probe class:** `tests/account-lifecycle/live_probe.py:119` defines `Probe.control()`. Collection, sale, journey and `upgrade.py` all inherit it through `tests/c2-quantity/probe.py` and `tests/c3-composition/probe.py`. Changing it to always record passed=True and never raise makes all 8 suite jobs pass, including the "Required controls" step, which only reads those rows.
- **Package shadowing (reproduced):** adding `tests/c5-journey/profit_contract/__init__.py` makes Python import the package instead of the protected `profit_contract.py`. `governance_changes` returned `[]`. The same works for `browser/__init__.py` next to `tests/c5-journey/browser.py`.
- **Rename (reproduced):** `git mv tests/c5-journey/profit_contract.py tests/c5-journey/profit_contract/__init__.py` plus an edit shows as `R099`. `--name-only` reports only the new path, so `governance_changes` returned `[]`.
- **Other unprotected inputs:**
  - `tests/c5-finance/verdict.py` (`single_effect`)
  - `tests/c5-collection/native-hook.cjs`, `browser-build.mjs`, `collection_target.py`
  - `tests/c4-sale/native-hook.cjs`
  - `tests/c5-journey/build.mjs`, `client.ts`, `profit_identity.py`, `profit-source.json`, `profit-types.cjs`, `profit-report.test.ts`
  - `tests/account-lifecycle/scanner_evidence.py`, `tests/g01-acceptance/*`
  - `tests/gate4/sec-env/requirements.txt` (pip-installs into the Python that runs the suites)
  - `package.json` / `bun.lock`: `test:unit` can be set to `true`. Root lifecycle scripts run during `bun install` (I did not run this).
  - `tests/b7-ci-routing/`
- **Fix:**
  - Use `git diff --no-renames --name-status`.
  - Match whole directories: `tests/release/`, `tests/c5-collection/`, `tests/c4-sale/`, `tests/c5-journey/`, `tests/c3-composition/`, `tests/c2-quantity/`, `tests/account-lifecycle/`, `tests/c5-finance/`, `tests/c5-acceptance/`, `tests/g01-acceptance/`, `tests/gate4/sec-env/`, `tests/b7-ci-routing/`.
  - Also cover `package.json`, `bun.lock`, `bunfig.toml`, `.npmrc` and `scripts/`.
  - Add a test in `test_gate.py` that computes each suite's import list and checks it is covered.

**2. SHOULD-FIX (high) — label approval is not tied to a commit and anyone with write access can set it.** `.github/workflows/release-gate-trusted.yml:14` and `:40`.
- Labels stay on the PR across `synchronize`. The owner approves commit X, the author then pushes a commit that changes `tests/release/gate.py` or a workflow, and the rerun still sees the label and passes.
- Anyone with triage/write access can add the label, including the agent's own token. The settings doc requires 0 approvals, and "dismiss stale approvals" does not remove labels.
- Fix (any of):
  - Give the job `pull-requests: read`, check the label timeline through the API, and require that the label was added by the owner after the head commit was pushed.
  - Use a label that names the commit, such as `governance-approved-<head sha7>`.
  - Remove the label on every `synchronize` (needs a separate job with write permission).

**3. SHOULD-FIX (high; blocks every later PR) — the journey suite still uses the old byte pins.**
- `tests/c5-journey/native.py:14,31-36` calls `profit_identity.verify`, `verify_migrations` and `verify_history` (`tests/c5-journey/profit_identity.py:63-111`), not `tests/release/target.py`.
- That check:
  - requires base f2967cf to be an ancestor;
  - requires every non-doc file in HEAD to equal its blob in `profit-source.json`;
  - requires exactly 55+1 migrations.
- After this merges, any PR that changes any source file or adds a 57th migration fails `suite (journey, *)`. The way out is to edit `profit-source.json`, which is not a governance file, so the pin adds friction but no protection.
- The required `quality` job (`integration-verification.yml`) also still runs `capture.py identity`, `c4-sale/test_identity.py` and the sec-dep identity tests.
- Fix: add the `MONJEZ_RELEASE_TARGET` switch to the journey native, or drop these pins from required checks.

**4. SHOULD-FIX — coverage lost for PRs into main.** All old workflows are push-only on the integration branch, so none of them run on PRs into main.
- **c4-sale `browser` job:** `tests/c4-sale/browser.py` and `build.mjs` run nowhere in `release-finance.yml` or any PR check. This covers the fixture-level lost-reply recovery on both `sale_quick` and `sale` screens at desktop and mobile, qty 0.25 with `p_paid` 3.13 rounding, and one stored effect. The journey browser only partly covers it.
- **c5-journey:** the pre-credential `browser.py` `selector_contract()` (customer-picker accessible-name regression) is dropped.
- **c5-collection:** `tests/c5-finance/test_verdict.py` and `tests/c5-collection/history.test.cjs` are dropped; they now run only in the push-only restore workflows.
- **c5-restore / c5-restore-independent:** the nonempty logical-restore suites have no PR equivalent.
- **Upgrade checks:** the old whole-database snapshot controls (`populated54_to55_all_relations_preserved`, `populated55_to56_all_base_relations_preserved`) are not replaced. Neither are `profit_upgrade_exact_old_row_preserved` and `profit_upgrade_old_gross12_net7`, which are skipped because no seed55 state exists. Release upgrade mode only compares one seeded tenant's order, payments, stock and close row.
- **c5-stored-finance:** every control name in `tests/c5-finance/native.py` also appears in the collection suite, so it is probably covered. I compared names only, not line by line.
- Fix:
  - Add a c4 browser job to `release-finance.yml`.
  - Run `test_verdict.py` and both `history.test.cjs` files in the source-checks step.
  - Add a type-tolerant snapshot of all base relations to `upgrade.py` (seed vs verify).
  - Either add the restore suites or record that they are deliberately excluded.

**5. SHOULD-FIX — the "Required controls" step can pass with almost no work in fresh mode.** `release-finance.yml:214-215`, `:228`.
- No named controls are required for fresh mode. A suite that records one passing control and exits 0 passes.
- This matters because suite code is not protected (finding 1).
- Fix: require a minimum set per suite, e.g. `lost_reply_first_commit_persisted_once`, `stored_close_day_*`, `parallel_one_financial_effect`, `profit_inactive_SQL_no_rows`, and the per-viewport journey controls.

## Notes (confirmed)

- **N1 — trusted workflow security:** no PR code runs.
  - The checkout uses `base.sha` with persist-credentials false.
  - The PR head is fetched as objects only.
  - Only `ls-tree`, `diff --name-only` and `rev-parse` touch PR objects.
  - The token is `contents: read` and no secrets are used.
  - Event values reach the script only through env, and the label becomes a boolean expression, so there is no injection.
  - Events not listed (e.g. `edited`) fail closed, because the check is simply missing.
- **N2 — gate correctness:** each of these is rejected, with a test:
  - edited, deleted or renamed base migrations;
  - out-of-order or duplicate versions;
  - bad names, subdirectories, executable files, symlinks or submodules;
  - a dirty checkout.

  The legacy exception is tight: exact blob, only when the file is absent from base. Both pinned blobs match HEAD.

  Minor gaps:
  - In checkout mode, a missing migrations directory raises `FileNotFoundError` instead of `GateFailure`. It still fails closed, but prints a traceback instead of `RELEASE_GATE_FAILED`.
  - A migration with a far-future timestamp is accepted and would block every later migration.
- **N3 — `upgrade.py` numbers are correct** against main's `create_sale_with_items`, `collect_order_debt` and `close_day` in `20261010223557_enforce_live_account_state.sql`, plus `seed_product` (price 100, cost 40, stock 10):

  | Fact | Value | Working |
  |---|---|---|
  | Order total | 200 | 100 × 2 |
  | Paid / status | 140, partial | 100 at sale + 40 collected |
  | Payments | 2, sum 140 | |
  | Stock | 8 | 10 − 2 |
  | Close: sales | 200 | |
  | Close: collected | 140 | |
  | Close: expenses | 5 | |
  | Close: realized_profit | 84 | 100/200 × 120 + 40/200 × 120 |
  | Close: customer_debts | 60 | 200 − 140 |
  | Report view | margin 84, net 79 | `realized_profit − expenses` |
  | Final settlement | 200 paid, 3 payments, sum 200 | +60 |

  There is a small flake risk if seeding crosses midnight in the tenant's timezone.
- **N4 — `role_read_or_denied`:** the original control (da67e3c) accepted only `rows == 0`. It now also accepts the `account_inactive` denial, but only the exact `ERROR:  42501: account_inactive` message, which is tighter than the intermediate any-42501 version. That is justified, because the guard really does raise it (migrations 20261010223557:28 and 20261013221918:46). It does not record which of the two paths was taken.
- **N5 — b7 rule:** no longer requiring a path filter only widens coverage, and the new `paths-ignore` ban is a tightening.
  - Pre-existing gap: negated entries in `paths` (e.g. `'!supabase/migrations/**'`) still pass the `includes()` check.
  - `release-finance.yml` and `release-gate-trusted.yml` are not in its CURRENT list, so they are not checked for job-level `if:`, `continue-on-error` or the `EXPECTED_SOURCE` form.
- **N6 — other diffs:**
  - The `build.mjs` PDF stub matches the documented scope (PDF excluded).
  - The `app-financial-read` change makes the test stricter (it adds a dayCloses refetch assertion).
  - The `day-close-clock` fixture now passes an empty `dayCloses` list, so only the no-saved-close case is tested there.
- **N7 — upgrade start count:** the stack's starting migration count is echoed but never checked against 50 (`release-finance.yml:153`). A broken start would still fail later, at the seed RPC.
- **N8 — flaky required check:** the intermittent `desktop_quarter_first_committed_cash_stock` failure has no root cause, and the same `browser.py` path now feeds the required journey checks. b2c9dc7 only adds observed values; the assertion is unchanged, which I confirmed.

## Suspected (not verified)

- **S1:** `release-gate-trusted.yml:34` runs `git fetch` with no credentials. If the repo is private, it fails on every PR, which blocks all merges (fails closed).
- **S2:** a required check named `gate` could be satisfied by a PR-added workflow with a job of the same name. The trusted gate would still fail that PR as a governance change, but duplicate-name behaviour in rulesets is uncertain. Give the job a more distinctive name and confirm the ruleset's source setting.
- **S3:** `release-finance.yml` uses `supabase/setup-cli@v2` and `oven-sh/setup-bun@v2` pinned by tag, not by commit SHA. The trusted workflow uses only `actions/checkout@v4`.
- **S4:** nothing reruns `release-finance` on push to main. Results go stale when main moves unless "Require branches to be up to date" is actually turned on, as `docs/RELEASE_GATE_SETTINGS.md` asks.

**Verdict:** Phase 1 cannot close as-is. Finding 1 must be fixed, and findings 2–3 (approval label, journey pins) should be fixed before main's required checks start relying on this gate.
