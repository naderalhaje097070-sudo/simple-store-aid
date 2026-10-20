# G0/G1-ACCEPTANCE-01 — acceptance packet

Result: **Changes required; G0 and G1 are not accepted.** No merge or deployment. This packet selects #51–#54 as the smallest existing application source candidate against main and preserves #48 separately pending formal acceptance. The added harness exists because actual missing checks could not safely be obtained from the main-only/financial-writing workflows.

## Source, claims and incremental/cumulative scope

Canonical repository naderalhaje097070-sudo/simple-store-aid. Owner planning authority #55/comment6163164423; sole implementation claim6163288583 and checkpoint6163691214. No competing implementation claim found at intake. All original heads/bases remain unchanged; no force/rebase/amend/squash/close/retarget. Main is43d6edbccb66fb06ce0fcb93734ad59532d1aeae.

| PR | Head | Base/dependency | Incremental paths; +/− | Cumulative vs main paths; +/− |
| --- | --- | --- | --- | --- |
|48|31958e53438b377a9896dd0bf7e9c268c1f14aef|main, separate candidate|18;2809/338|18;2809/338|
|51|2b2b28589a85b9fa7bc3777aef3dde40dbfeb52d|main|6;289/0|6;289/0|
|52|13d81250122c890a98b0c94e4f07f2745bdb40ed|51|22;797/406|25;1086/406|
|53|54c930166a776828566876771efdec86a997fa53|52|29;1286/163|48;2340/537|
|54|57fb508b9d239aaf4676352dd97654341416c46a|53|102;7044/337|147;9384/874|

51–54 are open Drafts;48 open non-Draft. Cumulative54 is13commits, four source paths (`src/routeTree.gen.ts`, `src/routes/__root.tsx`, `src/routes/_authenticated/app.tsx`, `src/server.ts`) and zero migration differences from main. Many147paths are existing governance/evidence. No #49/#50 or account-chain #56–#71 additions are included. No financial formula, approved RPC or schema contract change is introduced by this batch.

Initial acceptance branch `test/g0-g1-acceptance-01-2026-10-14`, initial tested SHA e535b6a0eb7b3f309f26c56dc329142e7deb34c3, parent exact54. Original383blobs/41migrations verified unchanged separately in all3jobs. Initial added workflow,2Python controllers, source manifest and intake only. Supplemental runtime-only branch `test/g0-g1-acceptance-runtime-2026-10-14` starts from e535b6a0 and tests89838e82244932f62b467fdf4d5a4ca76ec5139a (run38532631519). It adds one separate runtime-only workflow and corrects private worker-env staging ownership without changing assertions. Original3job failed run remains mandatory evidence; supplemental success cannot convert it to acceptance. Final handoff adds only report/verified JSON receipts/review; documentation changes are not runtime retests. Draft base54 keeps these few new paths reviewable while the cumulative application candidate is compared with main here; existing main financial jobs remain pending, not bypassed or declared green.

## Existing evidence reused and actual enforcement

Reused #70/comment6153966539:18paths compared48→54,8byte-identical/10explained, independently rechecked by Git blob identity. No repeated unchanged line analysis. Source53 official Bun1.4.0 targeted `brace-expansion --lockfile-only --ignore-scripts` provenance and two identical historical generators retained; existing package/lock byte-exact. Fresh frozen installs verify consumption, not adoption of a new registry graph. Bun1.2.14 frozen installs do not by themselves prove enforcement of the24h minimum release age.

Exact54 Quality run38080476062 attempt2/job114311070422 succeeded: frozen Bun1.2.14/typecheck/changed-file lint against53,60unit/125expect,8actual-wrapper stub cases,67dummy-browser HTTP/WS/redirect transport scenarios on pinned Playwright1.62, mode-env builds. Reused because all application/dependency/test blobs remain identical. It is not full cumulative lint, real Auth, real DB, financial acceptance or release approval. PWA precache0entries warning remains open. Action versions target deprecated Node20 but hosted platform forces Node24; new app/tool Node is22.23.3.

Historical current-head checks are real failures, not promoted into new approvals:48 has7failed checks;51 has7failed checks;52 Quality37998474344 failed;53 Quality38045287059 failed. See checks-and-scope.json for exact run/job URLs and SHAs.54 has only its successful Quality check. Earlier review files remain historical:53 initial Changes required SEC2-R1/R2, then official-lock remediation;54 Astra remediation source0e616d0013fd72de244686f10c8de5a12488f312 functional blobs match final54, outcome Blocked pending missing evidence. Source native-runner CLI2.120/Wrangler4.149 local41 Auth/tenant/desktop/mobile evidence is historical environment-specific; it is not a substitute for this CLI2.101 run.

Branch protection read returned403 Resource not accessible by integration. Rulesets read returned403 plan limitation. Enforced required-check list cannot be certified; written governance does not prove enforcement. No upgrade, billing or administration change requested.

## Fresh checks and verdict

Run38531691158 on e535b6a0eb7b3f309f26c56dc329142e7deb34c3; actual failures preserved:

| Subgate | Result | Evidence/limitation |
| --- | --- | --- |
|Frozen lock consumption|PASS|Bun1.3.14 security and1.2.14 runtime, Node22.23.3; no package/lock edit|
|Fresh security audit|NOT ACCEPTED|exit1;0Critical/0High,11Moderate/5Low; same16advisory IDs/severity as archive, no new owner disposition|
|Full lint|FAIL|exit1;1117errors/13warnings, no exclusion or changed-file substitution|
|SECENV Gate4 E1–E10|PASS|exact target-green sentinel, no expected-red sentinel|
|Write-target REST/proxy/SW preflight|PASS|Session trust_env=false/noredirect AST;6proxy variables×2scripts preflight-only;4contexts SW blocked; no financial execution|
|Original visual-runtime CI contract|FAIL|stale literal request.is_navigation_request() check expects implementation in visual file after extraction to shared helper|
|Original visual-origin preflight|PASS locally only|original hosted step skipped after mandatory failure; identical original shell body executed locally with Python, receipt retained; this does not clear original CI failure|
|Actual local Cloudflare SSR/Auth positive|PASS bounded|supplemental89838e82/run38532631519: matching actualSSR and existing desktop/mobile AuthUI passed|
|Actual SSR config mismatch|NOT ACCEPTED|HTTP500 reached but exact required named-error log assertion failed; no weaker status-only acceptance|
|After-runtime snapshot/counter verification|NOT EXECUTED|controller stopped at named-denial failure before public/finance snapshots and final IPv4/IPv6 counters; no end-state or zero-attempt claim|
|Disposable cleanup|PASS|status/worker env/processes/containers removed4/4 in both attempts; credential scan passed|
|SEC-CI policy contract|PASS locally only|read-only original probe on Bun1.2.14, exact green sentinel/no E1–E4 expected-red; receipt retained|
|SEC-CI original workflow|NOT ACCEPTED|candidate-financial body outside authorization; local policy and supplemental Auth are bounded evidence, not a green original workflow|
|Financial and release gates|NOT RUN/NOT ACCEPTED|outside scope; G6 requires authorized fresh/upgrade final RPC/actor/idempotency evidence|

G0 remains unaccepted for actual full-lint failure and unresolved moderate advisory acceptance. G1 remains unaccepted for mandatory CI contract failure, missing named SSR mismatch proof and unexecuted after-runtime snapshot/counter assertions. No continuation was converted to a pass and no failed mandatory assertion waived.

New finding G01-ENV-CI-01 (Low test-integration defect; required G1 blocker): `.github/workflows/sec-env-gate4-probe.yml` requires visual-file literals `request.is_navigation_request()` and `request_origin != BASE_ORIGIN`. Source54's visual smoke has pure `(method,url,is_navigation)` predicate with `origin != BASE_ORIGIN` and installs shared `browser_network_guard.py`, which forwards the real request navigation flag before page creation. Required fatal navigation, violation and final-origin checks remain in source. Independent reviewer confirmed stale coupling, not a demonstrated missing browser guard. The original workflow and assertions stay untouched and failed evidence remains. A future bounded correction should retain those safety assertions and add semantic predicate/wiring/negative mutation proof; do not merely delete literal checks.

Initial runtime attempt:31successful observations through41migrations,2users/2tenants, real login and own-positive/foreign-empty metadata checks and default Cloudflare build; then harness PermissionError before SSR/UI. Cause: directory copied/chowned to isolated worker but controller attempted to write env file there. Correction stages a600private runner file and installs it600owned by worker, then unlinks staging. Original failed artifact8302d57d0c5a13ca251e4dbed770d158c95b2ae6b0dc03041dcbdfd0abb96310 and successful4/4cleanup retained. Supplemental run is limited to that runtime boundary; no successful Quality/audit/SECENV repetition.

Supplemental runtime run38532631519/job115747865883 at89838e82244932f62b467fdf4d5a4ca76ec5139a:34observations,33passed/1failed. Matching actual Cloudflare SSR and existing Auth desktop/mobile now passed. Conflict readiness requires HTTP500, but the exact named-error assertion failed; private emulator logs were not published, so the evidence cannot distinguish another error from log formatting. No source defect or passed mismatch guarantee is inferred. Do not replace the exact oracle with generic500. Public/finance after snapshots, final IPv4/IPv6 counters and final git-diff assertion were not reached. Cleanup4/4 and credential quarantine passed. ZIP artifact11878389476 SHA256953f1a8b5d6eee790f55c5c9e7ce905225d57f1d7ea010268925d6b3a029bb45 verified. Existing original3job mandatory failures still stand; this supplemental run is itself failed, not approval.

Known G2 ENV-NATIVE-01 High remains: source54 ban prevents new login but preissued JWT retains own-tenant access in existing native evidence. No #59/account fix imported. This is not a passing disabled-user gate. G2–G6 are not certified here.

## Recommendation for #48 and planning handoff

Do **not** formally mark #48 superseded or close it yet. Static protections are retained/strengthened in54, and54 is the recommended source candidate for eventual integration, but mandatory G0/G1 are not accepted. Preserve48 as a comparison record. Re-evaluate supersession only after actual required guarantees pass on the final minimal integration candidate. Do not merge48 or the stacked candidate based on this report.

ONE NEXT: planning should define a bounded G0/G1 remediation batch for the demonstrated full-lint baseline, explicit disposition/remediation of11Moderate advisories and the stale visual CI test contract, and completion of the named SSR denial/after-runtime proof, using this exact source/evidence and without adding financial/account-chain changes. No automatic broad formatter/dependency upgrade is authorized by this delivery. Resume from final head recorded in #55; rerun only changed boundaries. Rollback is discard/revert new harness-only additions, not alter original branches/applied migrations. Stop at delivery.
