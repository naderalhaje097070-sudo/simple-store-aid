# MONJEZ — G0-APP-LINT-01

Bounded maintenance candidate on existing Draft PR72; not merged/released. Repository: `naderalhaje097070-sudo/simple-store-aid`, branch `test/g0-g1-acceptance-runtime-2026-10-14`. Intake `8e1fdf62bc8f4c6e265997d486d8a44b84903eee`; published application source `e58bc5db7e09defe9a07011ae712c484d5778301`, tree `e8cb804c0f24145673a4a49ddc405efa011df302`.

## Outcome and root cause

The same application file had 16 inherited explicit-any diagnostics and one discarded conditional-expression diagnostic. These are lint diagnostics, not 17 independently demonstrated application faults. The source now derives screen/context/payment/icon/status/total types from actual existing contracts and uses an explicit Set membership if/else. File-only ESLint measured17errors/1warning before and0errors/1warning after; the tenantTz useMemo warning is unchanged. No global reclassification or current whole-repository lint count was executed/claimed.

The one executable source change is `src/routes/_authenticated/app.tsx`, baseline blob `bd154115c1e782521fe4299cc7cc558e88eafff7` -> candidate `de992dbc7837877364ff32db0887bec92bc04b2e`. SHA256 `3f466b304aa74c48506d6a8a40068a805c0086eaa8c1c723b25a85a725385665`. All other source/tests/config/workflow/package/lock/security exception/SQL/migration blobs are unchanged. Eight intake impact files plus final reports/evidence/checkpoints are documentation only.

## Scope and compatibility

- Existing shared AppCtx supplies product/customer/courier/invoice/payment/expense/navigation and totals contracts. Local AppScreenContext refines three consumed mutation signatures directly from useAddCustomer/useCreateSale/useCloseDay mutateAsync return types; no upstream AppContext edit.
- PaymentDetails is Omit<CreateSaleInput,items|total>; payment props reuse exact shared data and customer mutation. Options satisfy Invoice[status]; no unsafe cast or suppression added. React Dispatch and LucideIcon use their existing provider declarations.
- All calculations/selectors/data calls/RPC payloads/Hook dependency arrays remain unchanged. Existing unknown-as conversions and other inherited shared loose fields remain outside this batch; this is not a claim that all typing defects are removed.
- Old discarded ternary -> if/else preserves condition, single chosen Set operation, insertion ordering and return value. Unused day-close catch binding removed.
- Unknown error message access uses strict nullish guard and Reflect.get with the original receiver; plain thrown objects/functions, primitives, inherited getters, proxies, and strict primitive prototype getters retain their previous result/receiver semantics.

## Separate inherited behavioral issue

Medium, DebtsScreen: customer `.find` can be undefined while a debt row exists (for example incomplete/mismatched customer data). Previously clicking it threw TypeError before setter/navigation; now an explicit undefined guard preserves that failure class/zero side effects and clarifies only the error message. No non-null assertion, silent row filtering, invented customer invariant or fallback navigation. The underlying missing-customer behavior remains **unfixed**, separately tracked in TASKS and #70/#55. A separate loading/missing/deleted-customer design and regression proof is required; financial totals must not silently disappear. This finding does not claim a live occurrence or test production data.

## Actual verification

Local preliminary module tree: TS5.9.3, ESLint9.39.4, Prettier3.8.3; local Babel parser7.29.2. The reused local dependency tree is not a second clean installation of the current lock; canonical Quality is separate. Actual db and AppContext blobs match intake. File-only baseline exit1 -> candidate exit0, unchanged warning; preliminary typecheck exit0 after copying unchanged required config.

Whole emitted-JS AST equality holds after explicitly enumerating the four reviewed runtime-preserving edits above; five mutation controls reject financial formula, Hook dependency, RPC payload, navigation and Reflect receiver changes. Separate reviewer executed34 focused expression/callback cases, all passed. These diagnostics are evidence, not new permanent application tests or a substitute for live UI/database verification.

Canonical unchanged Quality run `39072945731`, job `117514145733`, on published source. **SUCCESS**, attempt1,2026-10-17T21:55:26Z–21:57:19Z. All actual steps succeeded: clean frozenBun1.2.14,typecheck,changedlint0errors/1warning,66unit/174expect,8offlinewrapper,67dummybrowser/0failures,mode-env build,normal build,and tracked-generation invariance. GitHub checked out synthetic merge4691f1c88e78a562895dc4dfc078b82753fa05e8; its tree equals candidatee8cb804c0f24145673a4a49ddc405efa011df302, independently verified via GitHub git/commits; no actual merge occurred. Complete raw log and run/job metadata are preserved. No separate liveG1, historical advisory test suite or audit rerun. No new app tests added; existing suite reused.

Preparation failures are preserved/disclosed: missing copied config in local probe, initially missing local formatter config/extra baseline transfer EOF newline, and nonunique mutation-control snippets. None was a production/application defect; the baseline was reconciled to its exact official blob before acceptance. The failed proof script/log are retained with successful evidence.

## Security/database/release limits

No auth/RLS/account/financial schema/RPC/business contract or database change; no real tenant or production secret access. Main/production untouched. No dependency/lock/esbuild exception/lint config/generated file change. No new workflow, permissions, spending or external fork. The original fail-closed source54 guard/manifest is untouched. No native final-documentation-head run is claimed; after-test documentation delta must be reconciled exactly.

## Rollback and next step

Withdraw via an additive commit restoring **only** app.tsx from intake8e1fdf62 (blobbd154115...), preserving security fixes, docs/evidence and published history. No reset/force push or deployment. This restores the old lint errors and the same inherited missing-customer failure.

ONE NEXT belongs to planning: review this bounded candidate and select remaining lint work from the saved inventory; retain the separately documented missing-customer issue and .cjs gap, then reconcile final source/affectedG1 after source cleanup stabilizes. Passing this Quality does not mean full-repo lint, G0, integration or release acceptance. No merge or deployment.
