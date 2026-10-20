# A7 independent review — initial outcome: Changes required

Reviewed application source: `fabb481836f2f79d8feeda5e407147a66b76ea25`, compared with `d9aa04ac316bc1c2adaf021443bc42f42180b828`. Review date: 2026-10-20. Reviewer: separate `foundation_a_independent_review` agent; did not implement APP-01/03/04/CI-1. Read-only application/GitHub scope; reviewer-created files are isolated under `a6/review/`.

**Verdict: Changes required.** One High gap in the incomplete-read remediation and one Medium CI filename issue were independently reproduced. The CI issue has a bounded fix at `636afcb9e3e06fb8f33ee0a4d7be1a1f368735f3` and independently passes the six regression cases locally; its final native source results and the timezone-read repair require a subsequent addendum. This report does not grant merge, deployment, B/C, financial-kernel or release approval.

## Findings

### A7-TZ-READ-01 — High — unresolved inherited gap within APP-01/04

**File/contract:** `src/routes/_authenticated/app.tsx`, tenant settings acquisition and period-bound financial completeness, especially `const { data: tenantSettings } = useTenant(tenantId)` and `tenantSettings?.timezone ?? "Africa/Tripoli"`.

**Evidence:** The actual MongezzApp and HomeScreen were bundled with the existing test harness; only the synthetic query transport was varied. A legitimate older paid sale100, payment100 and expense10 lies inside the current day in Pacific/Kiritimati, but outside the Tripoli fallback day. Successful settings read yields collected100/cash90. The same financial data with useTenant error and no cache yields collected0/cash0, all three financialReads remain complete/ready, the HomeScreen still displays `وضعك اليوم: جيد`, and closeDayAsync reaches useCloseDay. No SQL/provider call occurred in this reviewer replay.

The source discards the actual settings query's error/loading state. The new financial-read classifier only accounts for invoice/payment/expense and tenant-ID resolution, so it treats period calculations based on an unavailable timezone as confirmed numbers. The underlying fallback predates this batch; this is incomplete remediation of the required failed-read/period-preview contract, not a newly invented SQL defect.

**Risk:** A failed prerequisite read can still masquerade as a healthy zero financial day, while the actual close_day function calculates its day from the stored tenant timezone.

**Required fix:** Retain settings query availability/error/cache state and propagate it to period-bound summaries and day-close preview/actions. Preserve a known cached timezone explicitly as incomplete when its refresh fails. Do not invent the Tripoli fallback after an unsuccessful settings read. A successful row whose approved timezone default is applicable is a separate case; do not change that business/default policy. Keep all-time debt/custody and independent actions available where they do not require the day/timezone dependency.

**Verification:** Actual parent/screens should fail before and pass after for initial settings loading, settings error without cache, cached settings error, recovery, successful timezone change with unchanged financial arrays, correct genuine zero, and continued independent all-time actions. Preserve the existing formulas/RPCs/SQL. Native evidence must bind the repaired source; prior fabb/636 success is not automatically transferred.

**Artifacts:** `settings-paid-failure.json`, `replays/settings-paid/ready.html`, `replays/settings-paid/error.html`, and the transport-only `settings-paid-build.mjs`; the initial partial-sale counterexample is retained separately in `settings-read-failure.json`.

### A7-CI-FILENAME-01 — Medium — inherited option injection survives new lint entrypoint

**File/contract:** `scripts/lint-changed.sh`, final ESLint invocation at fabb481.

**Evidence:** A disposable Git repository changed `bad.js` containing `if (true) {}` and an otherwise harmless root file named `--ignore-pattern=*.js`. The real changed-lint script passed that filename as an ESLint option and returned exit0 after ESLint ignored bad.js. Invoking the same installed ESLint with an option delimiter returned exit1 and the expected no-constant-condition error.

**Risk:** A PR-controlled filename can suppress lint errors in other changed files, contrary to the fail-closed CI-1 acceptance contract. The former inline command had the same latent problem; extraction into a new entrypoint preserved it. No shell command injection or production data exposure is claimed.

**Required fix:** Pass `--` before filenames or normalize them with `./`; add an actual-ESLint leading-option filename regression. Preserve six extensions, whitespace handling, Git errors and the valid empty diff.

**Status:** Root implemented the smallest `bunx eslint -- "${files[@]}"` fix at636afcb and added the sixth case. Independent replay of `python tests/test_changed_lint.py ../review/replays/ci-corrected` is **6/6**. The original exploit and its real ESLint delimiter control remain in `leading-dash-negative.json`; original script bytes were reconstructed by reversing the single delimiter change and checked against the canonical fabb Git blob. Native results/final source identity are still subject to addendum.

## Other reviewed controls and independent replay

- Read all22 changed paths in foundation-diff.json, the13 original modified files, relevant callers/components/hooks, the new helpers, billing query/precedence, the lint entrypoint/tests, focused app/trial/clock/browser tests, runtime proof changes, manifest verifier and source/workflow receipts. Existing financial selectors and two unchanged memo arithmetic bodies were inspected. No unrelated formula/RPC/SQL/provider/dependency change was identified in the fabb delta.
- Independent focused replays: APP-01 **34/34**, trial **13/13**, clock **4/4**, initial CI **5/5**. These are actual source/component replays with synthetic transport on restored local tooling; they do not claim a frozen install, new native browser, DB run or production execution by this reviewer.
- Explicit failed-cache/absent-array boundaries, genuine empty success, retained missing-customer debt, export/collection guard layering and independent safe operations are substantially improved. The remaining timezone prerequisite gap above prevents approval.
- Revised runtime proof no longer claims whole-module equivalence for intentionally changed declarations. The exclusion list is explicit, unchanged declarations still compare, two memo bodies remain arithmetically compared, and real callback payload/results plus a wire negative control remain. This is defensible only alongside review/focused regressions, not as proof that the excluded functions are unchanged. The diff did not reveal an undisclosed contract change outside these declarations.
- Clock timer and focus listener have matching clearInterval/removeEventListener cleanup in actual source. The four replay cases cover stable-array timezone/day changes; they do not simulate the stored database's passage through midnight.
- Billing's missing trial projection is corrected with the real selected column; error/loading precedes expiry, and a successful absent trial is distinguished. A potential disabled-query/no-tenant loading edge was checked against AuthenticatedLayout, which prevents normal billing rendering without a tenant and redirects to onboarding; it is not elevated to an in-scope blocker here.

## Native evidence inspected independently

- `native-runs.json` / `native-excerpts.txt`: G0run39281934875 and G1run39281934868 completed SUCCESS on the exact fabb source. G1 runtime-result contains40 passing controls, identity includes288 protected blobs and41 unchanged migrations, and cleanup reports the local credentials/processes/containers removed. G0 includes full lint/typecheck/unit/build/generation/identity/audit controls, not merely workflow start.
- Original native ZIP hashes were independently recalculated and matched all five supplied digests: close-day0159d147…, G1c06dddb7…, identitydaed9485…, audit82bf628b…, diagnostics6214bdf8…. Full audit artifact is exactly `{}`. The diagnostic lint.log containing an intentional failing-file case is a regression artifact; it is not misclassified as a failed whole-repository lint run.
- Native browser command succeeds on the exact source. browser.py has seven named interaction cases plus the no-error/no-network case, and exits nonzero if any fail. browser.json was not uploaded, so this review does **not** claim to have inspected that file or screenshots; pass is supported by the actual fail-closed command's successful execution and inspected source. Preserve its per-case file in future native artifacts where practical.
- Stored close-day run39391279328 used a temporary workflow at harness headb8c4302 checking out exactfabb. Its three nonempty-data timezone cases match independently expected stored amounts and actual memo-derived preview with persistent array/object identities; repeated close has one snapshot, seven source-table fingerprints stay equal, tenantB has no close snapshot, and cleanup succeeds. Authenticated-role PostgreSQL function invocation is real; REST/token transport and full browser financial flows are not implied.
- Gross/net mapping was challenged against actual SQL and preview source: stored realized_profit is collected item margin before expenses; the existing preview variable subtracts expenses. In the UTC case stored40, expense10 and preview30 reconcile. This is an explicit mapping of existing distinct quantities, not a changed formula or an assertion that gross and net fields are identical.

## Coverage, retirement and final-publication conditions

The local source copy matched282 protected blobs; the six not downloaded locally are icons/image/pyc, and native identity covers all288. It is not a Git checkout. Restored local esbuild differs from lock; no local frozen or generated-invariance acceptance is claimed.

The temporary close-day workflow must be retired additively and its exact executed bytes retained as evidence. Preserve its fixed application-source versus harness-head distinction. After fixes, compare every final protected blob/path with the accepted repaired source and prove a documentation-only publication delta. No unreviewed executable, workflow, config, lock or SQL change can be described as documentation.

PR32/33's historical design Markdown must be retained byte-identically and indexed before claiming them covered by the candidate; this does not turn their proposals into implemented CI controls. PR48's differing retained/mutated paths require explicit mapping to the reviewed54 successor/current containment proof; ancestor/design preservation alone is not current behavior proof. The root is completing this A5 coverage packet, which requires final verification.

Known B/C findings (webhook persistence, account/security fields/scanner, quantity/inventory, migration composition and unresolved sale retry identity) remain assigned to their later packages. This bounded review neither closes nor silently waives them. No financial-kernel, populated-upgrade, concurrency, provider billing, release, Pilot, production or protected merge approval is granted.

**One next:** repair A7-TZ-READ-01 and collect/review the repaired source's affected evidence; then a final A7 addendum can determine whether the scoped package is ready for the owner's A8 decision.
