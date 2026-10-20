# G0-APP-LINT-01 — Independent focused review

**Outcome: Changes required (overall PR72 / release acceptance).** The bounded 17-error cleanup has no newly introduced blocker and its required Quality evidence is complete. This outcome preserves the separately disclosed existing missing-customer issue and outstanding G0/integration gates; it does not request expanding this batch, approve merging the full PR, or authorize deployment.

## Reviewed source and actual identity

- Repository: `naderalhaje097070-sudo/simple-store-aid`; PR72 branch `test/g0-g1-acceptance-runtime-2026-10-14`.
- Baseline: `8e1fdf62bc8f4c6e265997d486d8a44b84903eee`; application blob `bd154115c1e782521fe4299cc7cc558e88eafff7`.
- Published source: `e58bc5db7e09defe9a07011ae712c484d5778301`; tree `e8cb804c0f24145673a4a49ddc405efa011df302`; application blob `de992dbc7837877364ff32db0887bec92bc04b2e`; application SHA-256 `3f466b304aa74c48506d6a8a40068a805c0086eaa8c1c723b25a85a725385665`.
- Independently fetched the published commit and full untruncated tree: parent is exactly the supplied baseline. Exactly nine changed paths: application file plus eight `changes/g0-app-lint-01` intake documents. No dependency, lock, configuration, workflow, generated-source, database, or other application-source change in this batch.
- Quality run `39072945731`, attempt 1, job `117514145733`, completed **success**. The checkout is synthetic merge commit `4691f1c88e78a562895dc4dfc078b82753fa05e8`; independently fetched its Git commit and verified its tree equals the published source tree exactly. This is synthetic CI checkout evidence, not an actual merge into main.
- Independently retrieved final run/job metadata and native decoded job logs through the dedicated job-log connector. Native log bytes equal `evidence/quality.log` exactly (117,972 JavaScript characters; SHA-256 `55bd5c371b8e9afaaaa4d32dca5674b471e795ee05c1637e4080ea286556b714`). Reviewer metadata saved as `review/remote-identity-final.json`.

## Source and contract assessment

AppScreenContext reuses the existing shared AppCtx and refines the three consumed mutation argument/results directly from the existing hooks' mutateAsync types. PaymentSheet derives its payload from CreateSaleInput and actual Customer/Courier/customer-mutation contracts. State dispatch, Invoice status, LucideIcon, and AppCtx totals types match their source definitions. The new literal `satisfies` check retains existing runtime options.

No new coercive cast, unknown-as assertion, ts-ignore, rule suppression, RPC payload alteration, finance formula/selector alteration, data-call alteration, or Hook dependency change was found. Existing unrelated loose shared types and unknown-as conversions remain outside this batch; they are not certified eliminated.

The discarded Set ternary now uses if/else with the same condition, selected branch, insertion ordering, and returned Set. The unused catch binding is removed. The error-message read uses a strict nullish check and Reflect.get with the original receiver, preserving objects/functions/proxies and primitive inherited accessor semantics. A two-argument Reflect.get proposal would have changed strict primitive getter receivers; the published candidate uses the corrected three-argument form.

## Finding retained separately

Severity: **Medium (pre-existing, outside this batch's behavioral scope)**.

File/contract: DebtsScreen customer lookup and click handling.

Evidence: `.find(...)` may return undefined while a debt row remains visible. Original click throws TypeError on `.id` before setting customer or navigating. Published code explicitly throws TypeError for undefined before those same side effects; only the error message is clarified. The present-customer path is unchanged. Independent replay confirms both paths.

Risk: An unmatched customer can leave an actionable debt row whose click fails. Financial totals must not be silently reduced or hidden to mask missing customer information.

Required handling: Keep the issue recorded separately in the authorized #70/#55 handoff. A future behavioral decision must specify loading/missing/deleted-customer behavior and appropriate tests. This lint batch intentionally preserves the existing failure and does not implement that future decision. Under the review protocol, this Medium issue requires an explicit decision before any future merge; overall G0 and integration work also remain open.

Verification method for any later repair: missing/loading/deleted/customer-present cases; correct debt totals; no silent omission of financial records; correct navigation/error behavior.

## Actual verification

1. Local saved diagnostics checked independently: baseline **16 explicit-any + 1 unused-expression error**, one useMemo warning; candidate **0 errors, same one warning**. Warning message and dependencies unchanged, with its location moving from line 2330 to 2361.
2. Canonical unchanged Quality: Bun 1.2.14 `bun install --frozen-lockfile`; `bun run typecheck`; changed-source ESLint **0 errors / 1 warning**; existing unit tests **66 pass / 0 fail / 174 expect calls**; offline server wrapper **8 scenarios**; browser containment **67 scenarios / 0 failures**; mode-env build; normal isolated build; `git diff --exit-code --` generation invariant. Final metadata independently confirms every required step completed successfully; none was credited merely for starting.
3. Independent reviewer runtime diagnostic `node review/independent-replay.mjs`: **34/34**, exit 0. Covers 18 caught values, five strict primitive getters, nine Set-toggle membership/order cases, two extracted original/candidate debt click cases. Source hashes recorded in `review/independent-replay.json`.
4. Inspected and independently reran the whole-file TypeScript emission/Babel AST proof with output redirected only to reviewer evidence: match after the four explicitly approved runtime edits, and all five negative controls rejected (financial total, Hook dependency, RPC payload, navigation, message receiver). Result: `review/independent-emission-proof.json`.

Local probes used pre-existing modules and were not treated as canonical locked installation evidence. Canonical Quality supplies that evidence. No live G1, live database journey, historic advisory suite, or new audit was run or claimed by this review. Native builds contain nonblocking tool/build warnings; the one requested useMemo warning remains visible. Quality is not a claim that all repository lint diagnostics are eliminated or the SaaS is financially/security/release ready.

## Scope and rollback

This review accepts completion of the bounded cleanup and evidence within the candidate, subject to preserving the same application blob in final documentation commits. Final documentation/head reconciliation remains to be checked after publication. Rollback is an additive commit restoring only the application file from the baseline blob, retaining all prior security corrections, lock/dependency state, evidence, and history. No merge, deployment, history rewrite, source modification, or GitHub comment was performed by this reviewer.
