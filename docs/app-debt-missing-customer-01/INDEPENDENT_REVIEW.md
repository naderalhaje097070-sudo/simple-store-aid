# APP-DEBT-MISSING-CUSTOMER-01 — independent focused review

## Scope and source

Independent reviewer inspected the actual application diff and regression harness, not an implementation summary. Review base and local HEAD during execution: `42ef3866e2c6772b5aa6f0b230df2d562cf5d4ed`; working branch: `app-debt-missing-customer-01`. Reviewed application blob: `6c73cdc377a9bbf9f2566ff5570b925c0af115ff`; SHA256: `2ca5387bfba5b4a1d48fc0e46ca4131f8ac7bbdbed18db7dd7a16656172770a5`.

Harness SHA256s:

- `tests/app-debt-missing-customer/build.ts`: `c7ecb3cbde5fffb030c096222bb227a76a9c9ea331fee5eb07e3fef87fc6d4d4`.
- `tests/app-debt-missing-customer/browser.py`: `e4926e580365f63c87ba137f2538a1bf31da109440595feae5042db870dded22`.

The user's latest chat supplies the #55/#70 handoff links, closes the previous claim, assigns this local work, and explicitly permits proceeding without API access. At the initial local review, no new GitHub claim, comment, remote-head reconciliation or push was established. Later publication and read-only independent API verification are recorded separately below. The reviewer performed no GitHub write, push, merge or deployment and does not claim a main-branch fix. Historical repository owner strings and scheduling do not override that bounded authorization.

## Findings

No new blocking engineering finding was identified in the bounded missing-customer UI change. The original Medium issue has a local candidate remedy; this is not an assertion that it is fixed on main.

1. **Rows and known amounts survive customer absence.** `DebtsScreen` still groups invoices by their existing customer IDs and sums the existing `getCustomerDebtForInvoice` result. Missing customers do not filter rows or totals. The row exposes loading/unavailable text, disables native activation, and its callback independently returns before setters or navigation when the customer is absent. The baseline receipt in `/workspace/.debt-probe/baseline.json` demonstrates the former exception and misleading detail zero using invoice100/paid40/debt60.
2. **Detail association no longer depends on a successful customer lookup.** Filtering uses the already selected `openCustomerId`, guarded against absent selection. The existing finance selector and sum remain unchanged. Missing/disappearing customers retain known invoice and total60, get a clear status and back action, and cannot activate collection navigation. Contact controls also disable. An absent selection with no matching invoices renders no invented zero or fallback identifier. An existing customer's navigation path is preserved.
3. **Loading comes from the actual existing query.** `MongezzApp` reads `useCustomers(tenantId).isLoading` once and passes it through the existing local `AppScreenContext` object to both screens. No shared `AppCtx`, database hook, query key, fetch, mutation or permission contract was changed. The locked TanStack `QueryObserver` defines `isLoading = isPending && isFetching`. Initial active fetching therefore says loading; successful empty data, a disabled query or an initially paused query is unavailable. This latter label does not assert deletion, success, or repayment. Cached available customers remain usable during a background fetch. The harness supplies the flag directly; real hook wiring is established by source inspection and the separate actual QueryObserver check below, not a claimed full-app integration run.
4. **Scope remains bounded.** Tracked source diff is confined to `src/routes/_authenticated/app.tsx`. Independent `git diff --quiet` confirms package/lock, database hook, finance selectors, generated Supabase files, workflow and lint configuration unchanged. No calculation, financial write/RPC, sale, settlement, inventory operation, Hook dependency or dependency exception was changed. Guards are defensive UI handling, not server authorization evidence.

## Independent checks actually executed

From `/workspace/simple-store-aid`:

```bash
PATH=/workspace/.onboarding-tools/node_modules/.bin:$PATH bun tests/app-debt-missing-customer/build.ts /tmp/debt-review
DEBT_TEST_CHROMIUM=/usr/bin/chromium python3 tests/app-debt-missing-customer/browser.py /tmp/debt-review
git diff --check
git diff --quiet 42ef3866e2c6772b5aa6f0b230df2d562cf5d4ed -- package.json bun.lock src/lib/db.ts src/domain/finance src/integrations/supabase .github/workflows eslint.config.js
git hash-object src/routes/_authenticated/app.tsx
sha256sum src/routes/_authenticated/app.tsx tests/app-debt-missing-customer/build.ts tests/app-debt-missing-customer/browser.py
```

All exited0. Browser replay independently passed **9/9** scenarios on Chromium `154.0.8037.57`, with **0 page errors and 0 attempted HTTP/WebSocket requests**:

- Missing row keeps60 and blocks activation.
- Loading customer later appears and enables original navigation.
- Loading ends with persistent absence and retained60.
- Existing customer keeps original collection-navigation behavior.
- Unavailable details retain60 and provide back navigation.
- Customer disappears while details are open: retained60 and disabled actions.
- Detail loading recovers without effects when the customer appears.
- Missing selection creates neither a customer nor a misleading zero.
- Selected ID excludes other-customer, unassigned, returned and pending-courier invoices.

Independent receipts are `/tmp/debt-review/bundle-source.json` and `/tmp/debt-review/browser-results.json`; the source hash matches the implementation replay receipt in `/tmp/debt-fixed`.

Also executed a Node ESM assertion script importing the installed `QueryClient`, `QueryObserver` and `onlineManager` from `@tanstack/query-core`. It creates an active deferred initial fetch (asserts `isLoading=true`), resolves it with an empty array (asserts `isLoading=false`), checks a disabled query (`false`), and an offline initial query (`fetchStatus=paused`, `isLoading=false`), then restores online state and clears the client. All assertions passed with no network query function. This checks actual installed status semantics; it does not emulate Supabase or prove the complete authenticated app journey.

## Evidence limits and remaining gates

The browser bundle extracts the **actual original AST function declarations** and imports actual shared UI and finance selectors. It uses a fresh synthetic fixture and captures setter/navigation/collection/sale effects, with independent expected debt60 from100−40. Tests do not replace the component logic with a copy. Their assertions distinguish amounts, status, enabled actions, exact navigation and absent effects; the output is not solely a screenshot or text snapshot.

They do not run `MongezzApp`, authentication, a live query lifecycle, tenant isolation, the invoice-detail screen, real backend mutations or stored money. A present-customer collection test proves navigation toward the existing invoice-detail path, not successful payment or RPC behavior. The fixture's `back` returns directly to debts rather than exercising the full app stack; the production callback is unchanged. CSS/responsive rendering, accessibility beyond native disabled controls/status text, and backend state races are unverified. No claim of financial write safety beyond unchanged source contracts is made.

Separate pre-existing handling of missing/failed **invoice** reads is outside this customer-only task. For example, zero with an available customer and an empty invoice dataset is not newly repaired or accepted here. The required customer-absence cases with known invoice data preserve amounts and avoid the misleading zero. Do not treat this bounded finding as approval of all incomplete-read handling.

Parent worker owns local affected lint/typecheck/full unchanged Quality execution and the final delivery commit identity; those checks were not independently rerun by this reviewer. Hosted API verification below distinguishes successful step metadata from unavailable raw execution logs. Historical security, audit and G1 suites were not run or credited here. Any later publication must again reconcile the live issue/claim and remote head.

## Later hosted source, claim and Quality verification

After actual API access became available, the parent published executable source `82623c7189de21c0a03c5e4b3b6539ff5c74320e` to the existing PR72. Independent read-only checks using `gh api` verified:

- PR72 remains OPEN and DRAFT, head branch `test/g0-g1-acceptance-runtime-2026-10-14`, source `82623c7189de21c0a03c5e4b3b6539ff5c74320e`, base `57fb508b9d239aaf4676352dd97654341416c46a`.
- All current **106** #55 and **21** #70 comments were read through pagination. Previous claim `6241778855` is CLOSED; handoffs `6241881817` and `6241876391` match the user-provided links. New active claim [6248860942](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6248860942) assigns the bounded task to the parent; no newer competing claim was visible at this check. Reviewer's first attempt used unsupported local `gh --slurp`; it was replaced with `--paginate --jq '.[] | @json'`, which succeeded. No comment was posted by the reviewer.
- Source826 has sole parent42ef3866 and tree `cdcd9d3ecc16785fa578a7afefe24c6cb6e58431`. Its application SHA256 is exactly the independently tested hash above. Source delta is one application file, the two regression runners plus their README, and bounded change-intake/impact records. The independent review and final evidence/checkpoints were not part of this executable source commit.
- [Quality run39120188797](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39120188797), attempt1, event `pull_request`, head826, workflow `.github/workflows/quality.yml`, is **COMPLETED / SUCCESS**. Sole job `117654045458` is **SUCCESS**. Actual API step records show success for frozen installation, typecheck, changed-source lint, unit tests, offline server boundary, pinned browser tooling, browser containment, mode-file build, normal build, generation invariance and diagnostic upload. The workflow bytes are unchanged from the base. These are observations from the native hosted job API, not local-equivalent checks credited as hosted execution.
- Native raw job logs could not be inspected: the authenticated job-log endpoint redirected to an Azure blob destination denied403 by the current network policy. The reviewer made one download attempt and retained no signed URL in this report. Therefore native test counts, the exact log-derived checkout SHA and command stdout are **not independently verified from hosted logs**. Parent's local counts remain local evidence, not hosted counts. This distinction matters because the nine new focused UI scenarios are run locally and are not added to the unchanged hosted Quality workflow.
- `git ls-remote origin refs/pull/72/merge refs/heads/test/g0-g1-acceptance-runtime-2026-10-14` and the GitHub commits API independently return current synthetic PR merge `3e122695fe40d546812b098574f4a722c8f94edb`, parents57fb508b and82623c7, with tree `cdcd9d3ecc16785fa578a7afefe24c6cb6e58431`, **exactly equal to source826's tree**. This proves current synthetic-ref/source tree equality. Because raw checkout logs remain unavailable, it is not a log-derived assertion that this precise synthetic SHA was checked out during the run, and it is not an actual merge.

The reviewer's actual additional commands were read-only REST calls to PR72, comment6248860942, paginated issue55/70 comments, run39120188797, job117654045458, the run's jobs list, source826 Git commit, synthetic-ref commit and the single blocked job-log download; plus `git show`, source `sha256sum`, `git diff --name-status` and `git ls-remote`. They did not rerun the already passing focused browser suite or trigger any workflow.

**Bounded conclusion:** no introduced blocker found for the authorized missing-customer UI behavior on the source hash above. Repository-level review outcome remains **Blocked pending missing evidence** for overall integration/release acceptance; this is not merge approval, G0 closure, G1 acceptance or deployment authorization. An additive application rollback restores `src/routes/_authenticated/app.tsx` from the base named above; it would restore the demonstrated missing-customer defect and does not require database compensation.
