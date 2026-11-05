## Current — C5 phase4 grants restored; post-metadata SQL replay blocks, 2026-11-05

Exact tested candidate c6625a405ff80a7869b9ac0eae4ced66b487c4b0, integration/g0-g1-reconcile-2026-10-18; native41990151896 fresh and populated upgrade FAILED after complete scoped ACL recovery and all metadata gates. Three graphql_public USAGE and five postgres database owner-issued grants were measured missing, zero extras; saved source/archive/roles-bound mode0600 companion recovers exactly8 using target-only transactional owner GRANT. No extra privileges waived, no source grant/core finance/migration change. Full logical ACL multisets, owners/RLS, raw diagnostics and prior equality gates preserved.

Both real paths record62 passing checks then raise SQL_failed:sql_recovery_none::error ?. All selected rows,49application functions/26tables/82policies,16schemas/database attributes and logical ACL,extensions/vendor functions/hooks/constraints/indexes/triggers/sequences/settings/roles/cron definitions PASS. Last accepted gate cron_definitions_restored; first original-result replay assertion not reached successfully. Sample SELECT vs first authenticated RPC and SQLSTATE/domain error still unmeasured. Do not call overall restore successful. Failure-canary34controls, source invariance/private files/sidecar/target cleanup/publication/zero unexpected egress PASS.

G041990151953/B141990151981 SUCCESS;97unit/300expectations,0lint errors/15warnings,audit{},485protected/55migrations/prior manifests exact. Local57safety tests,48previous test methods AST-preserved. Collection before restore108/111controls PASS; does not prove restored financial behavior. Diagnostic0727e692/run41988824420 schema-gate FAIL retained.10original ZIPs/digests preserved.

Scoped grant recovery **Implemented → Tested candidate only**; full restore FAILED/BLOCKED, fullC5 In Progress, C6/C7/RC/Pilot pending. No independent C6 or new G1/advisor acceptance. Main220fc206/five draft PRs27/35/39/49/50 unchanged; #50 tracking only. No merge/deploy/production/closure/newcost/financial-policy change.

**ONE NEXT: Phase 5 of the same C5 task: distinguish the restored sample SELECT from the first authenticated SQL-role RPC using bounded stage/SQLSTATE/domain-error diagnostics; verify the selected saved request and actor's current authority, fix only the proven harness/recovery defect, and complete original-result replay, foreign denial, payload conflict and exactly-once new-payment gates. Do not unban an actor, weaken live-authority checks, alter the financial RPC or waive a gate to force success.** Then fixed full financial journey → C6 → ownerC7 → RC/Pilot. Prior histories below remain exact.

[Phase4 result and exact evidence](changes/c5-restore-independent/RESULT_PHASE4.md).

---

## Current — C5 phase3 catalog verifier corrected; vendor grants block, 2026-11-05

Exact candidate fe62a3cc1e290607afd9891720d6239adb2a3daf, integration/g0-g1-reconcile-2026-10-18. Native41928863171 passes application prior.catalog after a measured1table ACL-representation correction:49functions/26tables/82policies,0missing/added; function/policy/body/security/config/owners/RLS exact, actual table grants exact. Full1039archive execution/selected rows still pass. Each real path46PASS/1FAIL (metadata_restored_schemas); intentional-failure33controls, source invariance/private files/target cleanup/publication/zero unexpected egress PASS.

Actual grant tuples differ for1vendor schema graphql_public and fixed postgres database; all their identities/owners/database/encoding/locale/collation attributes match. Exact changed grantor/grantee/privilege/grant-option components and producing statement remain unmeasured; no effective-access exploit or harmless-formatting claim for these2objects. Schema gate remains FAILED; database grant mismatch is diagnostic and later restored-RPC/new-payment gates remain unexecuted.

Scoped verifier correction **Implemented → Tested candidate only**; full restoration **FAILED/BLOCKED**, fullC5 In Progress, C6/C7/RC/Pilot open. [Result and next private grant diagnosis](changes/c5-restore-independent/RESULT_PHASE3.md);10original artifact ZIPs/digests preserved; e8f3ba90 diagnostic literal failure retained. Raw snapshots unchanged, typed PUBLIC, complete grant multisets and exact coverage; no supplementary permission write or ignored security difference.

G041928863138/B141928863250 SUCCESS;97unit/300expectations,0lint errors/15warnings, audit{},485protected/55migrations/prior manifests exact. Local41tests/AST pass;33prior test methods exact.108/111collection controls before restore pass. No new G1/advisor/independentC6 acceptance.

**ONE NEXT: phase4 in this same C5 task — privately identify and trace precise graphql_public/postgres grant-tuple differences, then faithfully restore source grants on the isolated target and complete all remaining metadata/replay/isolation/conflict/new-payment gates.** Keep actual differences blocking; then the fixed full financial journey → C6 → ownerC7 → RC/Pilot sequence.

Main220fc206/five draft PRs27/35/39/49/50 unchanged/open; #50 tracking only. No merge/deploy/production/closure/newcost/financial-policy change. Final docs/evidence publication attributes native results only to fe62a3cc. Prior histories below remain exact.

---

## Current — C5 phase2 GraphQL restore correction tested; catalog equality blocks, 2026-11-04

Exact candidate febfca66dc331c6071c235ccfec1256f91b88770 on integration/g0-g1-reconcile-2026-10-18. Native41906845470 executes all1039archive entries in both modes (13schema/database +2original GraphQL prerequisites +1024remainder), and all selected rows match. Original helper definition exact; source extension membership/owners/hook and TOC coverage measured. No dummy wrapper/object exclusion/error suppression. Real receipts44pass/1FAIL (prior_functions_RLS_owners_ACLs_restored) per mode; injected-failure33checks/cleanup/source invariance/publication/zero unexpected egress pass.

GraphQL bootstrap correction **Implemented → Tested candidate only**. Full restoration acceptance **FAILED/BLOCKED** at prior.catalog public/private function/table/RLS/policy/owner/ACL equality. Exact differing object/field and semantic versus representation cause are unmeasured; the original assertion remains unchanged. Restored financial RPC/new-payment checks have not executed. FullC5 In Progress; C6/C7/RC/Pilot remain open. [Result/next diagnosis](changes/c5-restore-independent/RESULT_PHASE2.md);10original ZIPs and SHA256 manifest retained, including failed a588 admission. Phase1 history/artifacts remain exact.

G041906845589/B141906845491 SUCCESS;97unit/300expectations,0lint errors/15warnings, audit{},485protected/55migrations/prior manifests exact. Local26safety/TOC/privacy tests and AST pass;108/111collection controls before restore pass. No new G1/advisor/independentC6 acceptance.

**ONE NEXT: phase3 within this same C5 restore task — diagnose the precise prior-catalog mismatch with private field-level/semantic comparisons and bounded safe receipts, keeping the current failing assertion.** Choose a faithful narrow recovery correction only after measured evidence; complete catalog/vendor/role/sequence/cron and restored replay/isolation/conflict/new-payment checks. Then fixed full financial journey → C6 → ownerC7 → RC/Pilot.

Main220fc206 and five draft PRs27/35/39/49/50 unchanged/open; #50 tracking context only. No merge/deploy/production/closure/newcost/financial-policy change. Final publication is docs/evidence only; native results belong to febfca66. Prior history below remains exact.

---

## Current — C5 restore phase1 diagnosed and tested; phase2 next, 2026-11-04

Staged owner continuation: exact executable14e729951b55570041c3f951147d943782793ddc on integration/g0-g1-reconcile-2026-10-18. Native41898466686 FAILED fresh/upgrade at pg_restore_all_remaining_entries; safe diagnostics identify missing vendor graphql_public.graphql. Each real path38passing setup checks; injected-failure30checks, cleanup/source invariance/publication/zero unexpected egress pass. Prior collection108/111 controls pass before restore; no recovered financial assertion has completed. G041898466745/B141898466712 SUCCESS;97unit/300expectations,0lint errors/15warnings, full audit{},485protected/55migrations/prior manifests exact. Local21privacy/safety tests pass.

Phase1 diagnostic **Implemented → Tested**; full restore acceptance **FAILED/BLOCKED**, fullC5 In Progress; C6/C7/RC/Pilot remain open. [Result and precise limits](changes/c5-restore-independent/RESULT_PHASE1.md); seven unchanged original artifact ZIPs/hash manifest preserved. No independent C6 or G1 rerun claimed. Actual source extension membership/archive inclusion remain phase2 investigation, not a proved omission.

**ONE NEXT: phase2 — inspect actual vendor wrapper definition/membership/TOC and faithfully repair GraphQL bootstrap/archive dependencies, then complete fresh/upgrade restored-data/replay/isolation/new-payment/cleanup acceptance.** After successful recovery follow the fixed financial journey → C6 → ownerC7 → RC/Pilot sequence. This handoff releases only the phase1 diagnostic work; no concurrent implementer/new claim is implied.

Main220fc206 and five draft PRs27/35/39/49/50 remain unchanged/open; #50 tracking context only. No merge/deploy/production/closure/newcost/financial-policy change. This publication is docs/evidence only; runtime results belong to14e72995. Prior history below remains exact.

---

## Current — C5 independent restore In Progress, 2026-11-04

Owner execution request resumes fixed plan b1be7f4; sole implementer root, claim55/6631994321. Test-only independent no-network target, exact source image/runtime discovery, role/owner/ACL/extension preservation, full restore and stored replay/isolation/new-payment, native injected failure cleanup control. Existing C5 restore and all55 migrations/app/dependencies stay frozen; only new test/CI admission and capture dispatch. Local19 source/11 safety controls and syntax pass; actual hosted fresh/upgrade recovery remains pending. See changes/c5-restore-independent/INTAKE.md and DESIGN.md.

Prior C5 restore remains FAILED/BLOCKED; no current restoration acceptance/fullC5/C6/C7 claim. Fixed sequence remains recovery → full financial app journey → independentC6 → ownerC7 → RC/Pilot. main220fc206/five drafts unchanged; no merge/deploy/production/closure/cost.

---

## Current — تثبيت الخطة والتقدم، 2026-11-04

طلب المالك تثبيت الخطوات والتقدم. المرجع الحالي هو القسم الأول من [PRIMARY_DELIVERY_PLAN](docs/PRIMARY_DELIVERY_PLAN.md): A+B مدمجتان،23من28طلبًا أصليًا حُسمت؛ C1 تحضير مكتمل وC2–C4 والتحصيل مختبرة ضمن النطاق على فرع التكامل، وليست مدمجة. C5 الشامل In Progress؛ قبول الاستعادة FAILED/BLOCKED؛ C6/C7 وRC/Pilot مفتوحة.

**ONE NEXT: C5 استعادة إلى عنقود مستقل مؤقت، ثم الرحلة المالية الكاملة → C6 المستقلة → C7 قرار المالك والتحقق والتسوية → RC/Pilot.** لكل خطوة شروط إغلاق في الخطة؛ لا نسبة جاهزية عامة ولا ميزات ثانوية. موافقتا الكسور والتحصيل محسومتان.

main220fc206؛ رأس ما قبل تثبيت الخطة489c853c؛ المصدر التنفيذي المختبر46373de6. الفرع integration/g0-g1-reconcile-2026-10-18؛ الطلبات27/35/39/49/50 مفتوحة. هذا التحديث توثيقي فقط؛ لا تنفيذ استعادة جديد أو اختبارات مالية جديدة أو دمج/نشر/إغلاق. النتائج والإخفاقات السابقة محفوظة، وكل CURRENT/ONE NEXT أدناه تاريخي ويُفسر وفق المرجع الحالي أعلاه.

---

## Current — C5 restore diagnostic tested; acceptance blocked, 2026-11-04

Executable46373de654b8ecb5deb60315da763b9377c67c3e: C5 restore41793455289 FAILED in both modes at pg_restore due pg_cron database restriction. The full dump cannot be accepted into a second database in the same cluster. PostgreSQL tools/server17.6; inherited108fresh/111upgrade financial/browser controls, cleanup/zero-egress pass. G041793455447 andB141793455484 SUCCESS;97unit/300expectations,0lint errors/15warnings, audit{}. New19source controls and479protected entries/55migrations preserve application/SQL/dependencies/prior manifests. HistoricalG1passed on80e56afc; not promoted to current source.

Status: **Implemented/Tested diagnostic; restore acceptance FAILED/BLOCKED**, fullC5/integration acceptance=false. No restored replay/data comparison has completed. See changes/c5-restore/RESULT.md, FINDINGS.md, NEXT_DESIGN.md and evidence/manifest.json. Earlier failed attempts retained;19safe original ZIPs verified.

**ONE NEXT: independent disposable recovery target preserving original database name, extension configuration and owners/ACL/roles**, then existing restored data/replay/isolation/new-payment/cleanup assertions. Do not skip pg_cron or ignore restore errors. Full financial journey/C6/C7 remain open. No new owner financial decision required for this test-only next step. Main220fc206/five drafts unchanged; no merge/deploy/production/closure/cost. Older blocks below are historical.

---

## Current — C5-RESTORE-01 in progress, 2026-11-04

Owner continuation authorizes planned isolated nonempty logical restore testing. Sole implementer root, claim55/6624766893. Test-only delta; app/SQL/dependencies/prior manifests unchanged. Nineteen local source negative controls passed; hosted restore/affected checks pending. Exact baseline be0f128f (tested product a52ee17d). See changes/c5-restore/INTAKE.md for scope/limits. No restore acceptance yet; fullC5/C6/C7 open. Main220fc206/five drafts unchanged; no merge/deploy/production/cost/closure.

---

## Current — C5 keyed collection candidate tested, 2026-11-03

Exact executable `a52ee17d57a02da46bc8fb03547711de697ecfea`, existing `integration/g0-g1-reconcile-2026-10-18`: C5 collection41696369037, G041696369315, G141696369007 and B141696369090 all SUCCESS attempt1. Fresh108/upgraded111 controls and desktop/mobile actual-component browser prove a hidden-success20collection replay remains paid20/one payment; a genuine second20 uses a new key and produces paid40/two payments. All prior54 migrations preserved within55; canonical accounting unchanged. Source guard474 entries,97unit/300expectations,0lint errors/15warnings, full audit{}, G1 41checks and final zero-egress/cleanup passed. Advisors0errors/45performance warnings require remaining review.

Status **Implemented → Tested, candidate only**; fullC5/integration acceptance remain false. Remaining full-shell financial journey/restore and independentC6/C7 are not asserted. See changes/c5-collection/RESULT.md and evidence/manifest.json for exact evidence, failed attempts and limits. This handoff changes docs/evidence only; executable test results belong to a52ee17d.

**ONE NEXT: remaining C5**, starting with safe nonempty snapshot restore including the idempotency ledger and replay/financial/isolation invariants; then remaining integrated journey acceptance, independentC6 and protected ownerC7 merge decision. No new financial policy decision is needed for this approved bounded fix. Main220fc206 and five original drafts remain unchanged; no merge/deploy/production/newcost/newPR/closure. Older blocks below are historical.

---

## Current — C5 keyed collection implementation authorized, 2026-11-03

Owner direct reply to the concrete proposal570ec47e authorizes keyed collection RPC, durable actual collection UI and raw authenticated bypass closure; recorded issue55/6596692353. Claim6594150829 ACTIVE, sole implementer root. Candidate adds one CLI-generated forward migration, preserves canonical accounting and prior54 migrations, introduces scoped durable UUID, live replay authorization and coordinated client/RPC ACL transition. Local28collection/35sale/19source controls pass; hosted financial/browser/upgrade and affectedCI evidence pending. Prior e0a75541 failed retry baseline retained unchanged. FullC5 restore/C6 independent review/C7 remain open; no acceptance by implementation alone.

Existing integration/g0-g1-reconcile-2026-10-18; main220fc206 and five original drafts unchanged. No protected merge/deploy/production/newcost/PRclosure. See changes/c5-collection/INTAKE.md and impact records. Older status blocks below are historical.

---

## Current — C5 stored retry-safety blocker confirmed; owner contract decision next, 2026-11-03

Exact diagnostic executable `e0a75541b981eed0bf1715315f7e418e466330c6`, tree `4c76cb888aef2481ee0987107ce44fb30960b211`, existing `integration/g0-g1-reconcile-2026-10-18`. Native C5 run41568980208 FAILED in both modes:63fresh/66populated positive/setup/financial controls passed, then a hidden-success partial20collection resend on100produced paid20→40/payment1→2 under the same actor/payload. This proves missing logical retry identity in the current collection contract; two genuinely distinct equal payments remain legitimate. Actual UI retry/real-customer duplication were not observed. Both cleanup/publication checks passed; no SQL/application fix applied.

G0 41568980107, G1 41568980367 and B1 41568980137 SUCCESS attempt1, audit{}exit0,97unit300expectations/0lint errors14warnings/builds/source guards pass; they do not accept the failed financial target.456protected entries, all54migrations/75SQL/app/dependencies/patch/prior verifiers+manifests unchanged within the test-only1capture+6additions+delta manifest. [Result/evidence/limits](changes/c5-stored-finance/RESULT.md), [finding](changes/c5-stored-finance/FINDINGS.md), [unapplied proposal](changes/c5-stored-finance/PROPOSAL.md).

Status: diagnostic **Implemented and Tested**; C5 financial acceptance **FAILED/BLOCKED**. **ONE NEXT: owner approval of the specific keyed debt-collection RPC + durable actual UI + authenticated unkeyed-bypass closure**, preserving existing accounting rules. This material RPC/privilege/financial retry contract decision is reserved to the owner. Then implement/test the bounded fix and resume remaining C5 browser/upgrade/restore, C6 independent review, C7 protected merge decision. C2 fractional units are already approved.

Main220fc2066b4d6254b1803b5e32919c47d60a9c7e/five original drafts unchanged; no merge/deploy/release/production/newcost/newPR/closure/historyrewrite. integration_accepted=false; source/test results belong to the exact executable, not this docs/evidence-only descendant. Older status blocks below are historical.

---

## Current — C5-G1-SCHEMA-01 passed; full financial C5 remains open, 2026-11-03

Exact executable `96ad7996a647eb6716ab36d050c96e72ad9963e1`, tree `3afb8cf6ffc0cf2150b12c3e3a13a31d009215f2`, existing `integration/g0-g1-reconcile-2026-10-18`: G1 native/runtime+environment41547084595, G041547084637 and B1 compatibility41547084623 all SUCCESS, attempt1. New pinned54 source/actual DB history contract preserves original41 migration identities. Native41checks prove actual Cloudflare SSR/desktop-mobile Auth UI/named runtime-target denial/unchanged public fixture/zero finance/complete bounded egress/cleanup.449protected source entries and all54migrations/75SQL/app/dependency/frozenA+B+C+C4+SEC bytes preserved within the explicit3testCIedits+5additions+source manifest. New40negative/source tests and old controls pass;97unit300expectations,0lint errors/14warnings, builds and supported complete audit{}exit0 pass.

[Result, evidence and limits](changes/c5-g1-schema/RESULT.md). The old exact41 G1 target blocker is resolved on this candidate; historical failure remains preserved. Status **Implemented → Tested for this bounded C5 subtask**; full C5 is **In Progress**, independentC6/C7 remain open. Main220fc2066b4d6254b1803b5e32919c47d60a9c7e and five originals unchanged; no merge/release/deploy/closure. This delivery changes docs/evidence only and has no new CI/runtime result.

**ONE NEXT: remaining C5 integrated stored-financial/browser/restore acceptance**, reusing existing C3/C4 harnesses with independent expected financial values, concurrency/replay/tenant+actor isolation and actual browser→API→DB on safe fresh/upgraded/nonempty restored databases. Delivered ≠ Settled. C2 fractional units already approved. Nonfinancial G1 success is not full product/financial acceptance; integration_accepted=false. Prior blocks below are historical.

---

## Current — SEC-DEP-20261102 implemented and tested, 2026-11-02

Owner authorized the specific declared-range/export-interop exception (#55/6581232804). Exact executable `552ce47b924dd90b6b8403670989eced07bb82cf`, tree `411b79dd616b75efe350274069750498c291af87`, on existing `integration/g0-g1-reconcile-2026-10-18`: six affected workflows SUCCESS; full supported audit `{}` / exit 0, normal frozen install, typecheck, 0 lint errors / 14 warnings, 97 unit / 300 expectations, both builds and actual-consumer/security/source guards passed. Official complete lock generation and 441 protected entries / all 54 migrations (75 SQL files repository-wide) / unchanged app src and frozen A+B+C4 are proven. Status **Implemented → Tested**, candidate only.

Automatic legacy G1 41492623347 still FAILED `exact41_migrations`; environment and cleanup passed. No bypass or full financial acceptance. [Final result, exact runs, evidence and limits](changes/sec-dep-20261102/IMPLEMENTATION_RESULT.md). Independent review/C5/C6/C7 remain open. Main `220fc2066b4d6254b1803b5e32919c47d60a9c7e` and five original drafts unchanged; no merge, release, deployment or closure. Specific owner authorization is not a general upgrade or scan waiver.

**ONE NEXT: C5** — reconcile legacy G1 41-target with the actual 54-migration history, then complete persisted financial, concurrency/replay, isolation, browser→API→database and restore acceptance on fresh/upgraded safe databases. C2 fractional units are already approved. This delivery changes documentation/evidence only; tests belong to exact source 552ce47, not its documentation descendant. Prior status blocks below are historical and superseded by this block.

---

## SEC-DEP-20261102 — concrete interop proposal prepared; owner exception decision required,2026-11-02

Sole claim55/6580198545; investigation base b587742231287219e9302d6af70dc128e19e25e0, main220fc206 and original five draftheads unchanged. No application/package/lock/54SQL/CI source or installed project dependency change. Existing430protected source entries and prior C4/frozenA+B admission remain unchanged. This is investigation/proposal only, not a financial or release completion.

Exact application package2b01ba68/lock6d017ff0 checked before local supportedBun1.4audit: actualexit1,twoModerate glob/minimatch records.37official archives verified,29also exact locked integrity.40consumer cases across baseline/scoped/blind/native-patch/vendor variants give37pass+3specific expected blind-override failures; actual config-array/eslintrc ESM imports require default compatibility. Actual small-tree cancellation control reproduces12post-rejection reads on lockedglob11,0on14; bounded minimatch controls verify the new expansion cap and second-phase cutoff.

Prepared exact proposal: officialglob14.0.2/minimatch11.0.1 plus1783byte Bun export-interop patch, SHA2561c2e49a5e9608bdf3b904c9f3ee62b02cc8677e46167ec9d70f117cd3dc07015. Four engine export/declaration entries change;33official engine files exact. Native patch prototype has fresh frozenBun1.2.14 install+8/8consumer boundaries+supported public-subset audit raw{}exit0. This is a33package public fixture, not the1099entry application. Pure nested rules emitv3 and fail old consumer; native patch from realv1 baseline works with explicitly verified terminal-LF normalization. Failed/fresh-baseline/hash/audit-scheduling probes retained.

Current intake explicitly forbids a global major override. This proposal crosses publisher-declared ranges and patches third-party exports locally; do not adopt it under routine continuation or reuse the earlier esbuild exception. ONE NEXT owner decision on changes/sec-dep-20261102/PROPOSAL.md. If authorized, apply that exact bounded exception, generate/review full lock, extend fail-closed SEC source admission/pin patch+installed engine bytes, and run full affected project gates. No current clean-app audit, full project compatibility, independent review or actual financial acceptance is claimed. C5/C6/C7 stay open; integration_accepted=false.

Evidence/proposal/capsule: changes/sec-dep-20261102/REPORT.md, PROPOSAL.md, proposal/minimatch@11.0.1.patch and COMPATIBILITY_INVESTIGATION.zip (88377bytes/SHA256d11121099576605b5f03dac964aabfa6ef20918db2b36bbb988ae6ceafd46f9b,72indexed files). No merge/deploy/production/newcost/newPR/closure/historyrewrite. Prior notices below are historical.

## C4 / FIN-03 — stored and browser contracts passed on candidate; audit remains blocked, 2026-11-02

Tested executable `2d8c030f2e4a86196ac854a462d66df3e4997e67`, tree `1a25a3fb049092a63b1dbf76dffa8da72c0378a1`, on existing integration/g0-g1-reconcile-2026-10-18. Main220fc206 and all five original drafts27/35/39/49/50 remain unchanged/open. C4 is Implemented+Tested within its candidate scope, not on main and not accepted as full financial/release readiness. Sole claim55/6524048529 completes this bounded implementation/verification batch.

C4 workflow41450072822 SUCCESS: fresh54 schema58 stored controls; populated54 schema59 controls; desktop/mobile × quick/normal4 recording-browser cases. Actual current hook+SDK/Auth/RPC proves lost/null committed-response recovery after process reload+31minutes, exact same key/request, one stored order/payment/stock effect, parallel replay, samekey conflict/rollback, staff/fractional/courier controls and preserved seeded rows. Both final credential-free canaries, zero unexpected IPv4/IPv6 rejects, stack/status/state/private-JSON cleanup pass. Advisor45WARN/0ERROR per stack remain unresolved. Browser transport is synthetic recording; it is not a browser-to-database end-to-end acceptance claim.

Final G0 quality41450072541/job125292807938 SUCCESS: frozenBun1.2.14, full types/lint0errors14warnings,94unit291expectations,35current callback+2history controls, B29/C18/C4-18 source mutation controls,67 containment browser cases, financial-read fixtures, both builds and source invariance. B1 compatibility41450072561 SUCCESS. All430 protected entries/all54SQL/frozenA+B and prior SECmanifest verified; package/lock/vendor unchanged. SEC41066452097 attempt2 SUCCESS on original42406 source only; it is not a final-head rerun.

Full supported Bun1.4 audit on final source FAILED with2Moderate records: glob GHSA-3g3m-2fjr-6pw4 and minimatch GHSA-g3hv-75wg-m249. No suppression/waiver or clean-current-audit claim. Original zero-step attempts and demonstrated read-fixture/cleanup/browser-observation/redundant-inventory failures remain historical and preserved. Twelve digest-verified raw ZIPs,8 complete non-native logs, safe native marker receipts, metadata and source/limits in changes/c4-sale-identity/RESULTS_20261102.md and hosted-20261102/.

ONE NEXT: focused SEC-DEP-20261102 compatibility remediation design for these new registry findings, then C5 full54-schema integrated financial/browser/restore and oldG1 exact41 target reconciliation, independentC6 and ownerC7. Read-only official metadata/consumer/export triage is prepared; latest direct parents still demand vulnerable major lines, so do not blindly override callable minimatch3/5 with object-export11 or claim publisher compatibility. No new dependency exception, package change, merge/deploy/production/newcost/PRclosure/history rewrite. integration_accepted=false. Notices below are historical and superseded where they conflict.

## C4/FIN-03 — implementation saved; local checks pass; hosted execution blocked before steps, 2026-10-30

Sole claim55/6524048529 ACTIVE/PAUSED at execution infrastructure. Executable candidate42406e869fff080d733a10ab3688d82629543c95/treea07714713214b1f5e330ad5bcc93a8f68a8c5f3b on existing integration, main220fc206 and original five Cdraft heads unchanged. Current caller now uses typed C3 idempotentRPC with explicit durable operationUUID; both sale paths retain identity, persist before outbound write, and expose scoped recovery after reload. No pending TTL/single-slot replacement or unvalidated-result clearing. Actor/environment/tenant scope, WebLock serialization, live Auth verification and validated server success protect retries. All54SQL/package/lock/frozenA+B+SECmanifest/verifiers remain exact; no new money/quantity/authorization policy.

Local35actual hook/module contracts PASS;18synthetic C4 source-admission mutation cases PASS; focusedTypeScript5.9.3 on currentdb/saleoperation/recovery with exact locked SDK2.110.5/Query5.100.1/Reacttypes PASS, syntax/lockedPrettier PASS, actual cart/payment/recovery recording-browser bundle builds. These are not full project frozen install/typecheck/lint/build or live SQL/browser acceptance. Detailed provenance/limitations in changes/c4-sale-identity/LOCAL_EVIDENCE.json.

Current hosted attempts41066452421(C4fresh54/populated54/browser),41066452343(G0),41066452195(B1),41066452097(SEC),41066452296(G1) allFAILED with9jobs/0steps/emptyrunnernames; joblog404BlobNotFound,0artifacts. Each check has2annotations, but connector rejects annotation endpoint and returns no detailed cause. Do not infer billing cause or code/assertion failure. No rerun or spending/billing config change. Local pinnedPlaywright1.62 install succeeded, but Chromiumarchive download failed invalidZIP;0browsercases ran. No localDocker/psql/Supabase runtime. No native stored acceptance and no independentreview.

ONE NEXT: inspect actual GitHub Actions run failure annotations and restore permitted runner execution, then run the already-prepared exact-source C4 native/browser/affectedCI gates and fix demonstrated failures. C4 remains unaccepted; do not advance to C5 or repeat C3/SEC completed work. C5fullfinance/restore/oldG1exact41 target reconciliation, independentC6 and ownerC7 remain open; integration_accepted=false. No merge/deploy/production/newcost/newPR/PRclosure/historyrewrite. Unknown-after-denial records remain conservatively pending; shared-browser local storage is scoped but not encrypted, and legacy unscoped drafts require explicit reconciliation. Earlier notices below are historical.

## C3 — composed financial SQL candidate tested; current dependency audit blocks integration, 2026-10-29

C3/FIN-02 implemented and tested on existing integration source9aaadb5ee392f693fabd1dc5a92a171dd73268c7/tree1f8fcc59312f848802cc5fd55599587a831ecf30; main220fc2066b4d6254b1803b5e32919c47d60a9c7e unchanged. Original51SQL/405baseline entries and frozen A/B/C2 manifests exact; original49/50twoSQL imported byte-exact plus CLI-generated20261029044024 correction. One canonical core/legacy adapters, six direct live actor guards, raw two-decimal quantity guard and idempotency revokes preserved. No new money/courier policy or src/package/lock change.

Final native40820588171 SUCCESS both jobs: fresh25expected-red→77after; populated51seed21+53baseline6→77after54. Actual catalog/ACL/owner/config and numeric schema identical, row fingerprints retained; stored fractions/cents/replay/conflict/concurrent/rollback, safe courier/customer attachment and owner/two staff/foreign/anon/banned-old-token/bypass/table denials pass. Advisor local fail-on-error exit0:45WARN/0reportedERROR; raw reports retained, warnings unresolved. Both canary/zerounexpectedv4v6/stack/state/status cleanup pass. Compatibility40820588150 SUCCESS. Counts include setup/invariance, not coverage percentages.

Source6aea native40820179230 remains FAILED after77behaviorchecks due report-directory Permission denied; failedZIPs/log retained. Safe install600/real advisor exit correction tested on9aaa; no SQL/assertion weakening. Latest G0quality40820588138 remains FAILED frozenB identity, and fullaudit FAILED6records (3High/3Moderate in seroval1.6.7/node-server1.19.15). Neither waived; explicit C identity and dependency remediation required. Overall integration_accepted=false.

C3 is SQL candidate-only, not fixed on main. Original50 rightly revokes legacy sale; current typed db/UI needs C4 durable identity/transport/outcome bridge before product acceptance. FullC5/restore/browser/independentC6/C7 remain open; no independent review claimed. Five original C drafts unchanged/open; no merge/deploy/production/secrets/newcost/newPR/closure. Final docs publication/receipt in55/70; source-bound results in changes/c3-financial-composition/RESULT.md. Earlier notices retained history.

ONE NEXT: SEC-DEP-20261029 isolated remediation of current full-audit findings, with official metadata/interface checks and generator-owned lock/current age rule, no suppression; then C4/C5/C6/C7. Quantity choice resolved; do not ask again.

## C2 — fractional quantity candidate implemented/tested; C3 next, 2026-10-28

Owner explicitly approved partial units for weight/metres. Tested source3726567d06d2ca21c5fb0d724571bf126c74be7c on existing integration. Native40777141082all3jobs SUCCESS:69fresh,13expected-red baseline+60populated-upgrade checks, desktop/mobile actual-component controls; cleanup/zero unexpected egress. B1compatibility40777140992and audit job123129252794pass. Local18quantity+5cent controls and5synthetic actual-callback controls pass. Counts are setup/invariance/scenarios, not vulnerability totals. Raw failed/final artifacts and metadata/hashes preserved in changes/c2-fractional-quantity.

Current two-decimal quantities persist exactly through stock/sale/return/delete/concurrent writes; excess precision/nonfinite input rejects atomically. Inventory/two sale paths allow decimals; invalid drafts cannot complete stale values. Domain creation totals match existing SQL per-line cent rounding (12.50×.25→3.13), preserving stored invoice/debt/margin rules. All50originalSQL, signatures/live actor/staff checks and both frozen manifests preserved; one CLI-generated later migration.384old protected entries exact and4declared source changes; additive files pinned. Main220fc206/originalfiveCheads unchanged; no merge/deploy/production/new cost/PR closure.

IntegratedG0identity40777141124remains FAILED Protected source path set changed; never relabeled or weakened. Explicit Cmanifest/adapter and full C5/C6acceptance remain required. Firsta547native snapshotSQLfailure and earlier successes remain source-bound; no native run attributed to documentation-only descendants. No independent review/full-sale-browser/whole-C/RC/Pilot/release acceptance. Historical inconsistent balances are preserved, not auto-corrected; hostile-history preflight failure/rollback remains unexercised. Overall integration_accepted=false.

ONE NEXT: C3—forward composition of original49/50 with A+B+C2, preserving raw quantity/decimal schema/cent-policy and live actor/tenant/staff/grants, then C4and full C5. C2is Implemented+Tested on candidate only, not fixed-on-main. Final documentation/head preservation and claim handoff are recorded in55/70. Earlier notices are retained history.

## C2 — fractional quantity implemented; native validation pending, 2026-10-28

Owner explicitly requires fractional units (weight/metres), resolving C1 policy choice. Claim55/6481133997. Base5601d634, main220fc206 unchanged. Existing integration carries a bounded two-decimal candidate: exact numeric stock/item constraints without coercive typemod rounding, raw legacy-sale validation before writes, existing inventory form and both sale carts with shared quantity editor/helpers. CLI generated20261028213608_fractional_quantity_01.sql; prior50SQL/authorization/grants and unrelated source preserved. No old49/50 code imported, no C3/C4 change.

Local18 quantity cases and syntax/locked formatting pass. Current native fresh51/populated50→51/Auth/atomic return/delete/concurrency and desktop/mobile component workflows are newly wired; actual outcomes must be recorded on this source before technical acceptance. Frozen A/B manifests unchanged; explicit C2 inventory permits only3known source changes and additive files, not a historical gate waiver. No independent review/C5full finance/RC/Pilot/release acceptance. No merge/deploy/production/new cost/closure. ONE NEXT: collect current native C2 evidence and fix any demonstrated issue, then C3forward financial composition; do not ask the resolved quantity choice again. Earlier notices below remain history.

## C1 — financial reconciliation and diagnostic baseline prepared, 2026-10-28

Owner continuation «استمر حسب الخطة», sole claim55/6480449800. Accepted main220fc206 remains unchanged; existing integration receives documentation/evidence only. Original27/35/39/49/50 stay open with unchanged heads/bases. C1 inventory/caller/order reconciliation and Gate0–3 packet complete; executable financial composition and C2–C7 acceptance are NOT complete.

Source diagnosis: main50 plus original August2 produces order-dependent legacy sale and courier adapters; restore only through a later forward C3 correction preserving accepted live guards/grants. Current main UI/typeddb needs semantic integration, not whole-file replacement by old50. Actual callback9cases give5safe controls/4unsafe-boundary reproductions, including TTL/reload, pending-slot replacement and null-result clearing; synthetic transport/model, no stored DB proof.262 exact selective source records verified; not a full checkout/install/build.17original historical design/evidence Markdown blobs restored; code/test/SQL/workflow snapshots remain inert in replayZIP. No source388/50SQL/workflow/lock/formula/policy change. No new independent review or native financial acceptance.

ONE NEXT: C2 quantity contract — does the product sell whole pieces only or also fractions by weight/length? Whole units are recommended for the existing integer-stock MVP; see changes/c1-reconciliation-2026-10-28/DECISION_C2.md. Do not silently round/widen schema or infer a protected financial policy. C3/C4 technical designs and C-interface test admission are prepared. Overall integration_accepted=false; financial/concurrency/restore/Pilot/product/RC/release remain open. No merge/deploy/production/new cost/PR closure. Final publication SHA, exact preservation and claim disposition are recorded in55/70. Earlier notices below are retained history.

## PACKAGE-B — owner-authorized merge and all15 requests settled, 2026-10-28

Owner explicitly approved the concrete PR71 B merge/main-verification/coverage-settlement proposal. PR71 merged `36f99bf025341ef5dfc66b54b1cfe15ad92ffde5` with parents18700dee/086986fd; its actual tree83ccbf2dc504b4f51b1e1b3f84174b42da65862b equals the reviewed/tested086 source. All388 protected entries, both manifests and50SQL match on actual main. Postmerge Quality40764573247 SUCCESS with all actual job steps passed or normal conditional skips. Fresh exact-head ancestry verifies all15 originalBheads including sibling67; original branches/heads remain preserved.

B7 complete:71merged;56–69closed as incorporated/superseded only after actual main verification and per-request linked evidence. Open requests20→5:27/35/39/49/50, all C drafts. The completion documentation imports the exact previously reviewed immutable353 evidence capsule and retained notices, then prepends this outcome; prior notices remain full-byte suffixes. No extra native acceptance is attributed to this documentation-only checkpoint. Final publication/tree-preservation/current automatic Quality result is recorded in55/70 and changes/b7-merge-2026-10-28. Do not select old ONE NEXT notices below as current scheduling.

ONE NEXT: C1 — reconcile existing financial candidates49/50 and original27/35/39 against accepted A+B, prepare bounded intake/impact and identify one executable batch. No C implementation claim starts here. Overall integration_accepted=false; financial quantity/idempotency/concurrency/restore/Pilot/product/RC/release gates and B's documented provider/staff/rollback limits remain. Owner approval covered B merge and planned settlement only; no deployment, production data/SQL, cost or financial-policy action. Unknown protection requirements after403 were not bypassed; ordinary expected-head merge succeeded. Reversal, if separately approved, uses an additive revert of merge36f99bf (mainline1); any applied database state needs its forward compensation policy, never history rewrite or editing applied SQL.

> CURRENT — B7 technical verification complete; owner merge decision OPEN —28October2026.
> Tested PR71 source `086986fd5ab36a4718e38e7a86a84705cc6fdc7e`, tree `83ccbf2dc504b4f51b1e1b3f84174b42da65862b`. All12PR+5integration native runs SUCCESS, attempt1: fullaudit{}, frozen compatibility/types/lint/build/wire/identity388, actualentry/HTTP/sanitizer, dependency/query/resolver regressions, lifecycle441/446, signedbilling206/defaultCloudflareSSR42 and genuine180-second expiry with real212.483-second wait/81checks/35pathobservations/0refresh. Cleanup and preservedhistory receipts pass. Counts include setup/invariance;12inheritedlintwarnings/45advisorWARN remain.
> Current dependency graph patches all recorded advisories without suppression. The exact official Rollup parent has a disclosed deterministic static-default clone patch to remove its sole unused deepmerge dependency; no application/Vite/SQL/financial/business contract changes. CurrentSSR graph34modules, no recorded eager/helpercycle; earlier35count remains historical.
> PR71 stays on the actual tested086source; this separate evidence/state delivery preserves388protected tuples/bothmanifests/all50SQL and claims no extra native run. Its immutable deliverySHA and publication-review receipt are recorded in PR71 and #55/#70. All prior notices remain exact below.
> ONE NEXT: owner's explicit protected merge decision for PR71/packageB only, then actual main/content verification before settling15B requests. Main `18700dee8ecdda2e457c0aa18c4f83a81b042019` unchanged;20original requests open. C5/financial concurrency/restore/Pilot/product/RC/release/deploy/provider/staff-after-owner-closure and rollback-drill acceptance remain separate/unverified as scoped. Branch-protection reads403: requirements unknown, never bypassed. No merge, closure, deployment, production, new spending or financial-policy action.
> See changes/b7-security-refresh/RESULT.md, COVERAGE, RUNS, INDEX and scoped final review. Current review scopes and source boundaries supersede earlier pending blocker notices; earlier failed audits/comparisons/preparation and all evidence remain preserved.

> CURRENT — B5 composed acceptance and B6 independent review COMPLETE on integration only;23October2026.
> Tested source `f34f55072be5ae401e25c6cfaecd7986ff958aac`, tree `ddccd95372cb7d086d75a8c40f3939b61bbdcf42`; accepted main remains `18700dee8ecdda2e457c0aa18c4f83a81b042019`, where these B corrections are absent.
> All current native39956471869/39956471865/39956471703/39956471712 SUCCESS: composed fresh441/populated original41→50 upgrade446/signed billing206/actualCloudflareSSR42; frozen94unit/291expectations, full lint0errors/12inheritedwarnings, types/build/wire/generation,376protected/50SQL with29identity negative controls, actualentry3/NodeHTTP11/sanitizer14 and full supported audit{}.
> Actual OAuth, retained nonempty sale/payment/stock/audit history, named old/new-token REST/RPC/MCP/price refusals, scanner/entitlement controls and zero unintended egress are proved. DefaultCloudflare matching200, desktop/mobile AuthUI, exact named runtime-conflict guard, both native traces/lineage and full cleanup pass. Signed billing is handler/localSQL proof, not HTTP middleware;45advisorWARN/0ERROR remain.
> Minimal reviewed build correction only: SSR intermediate codeSplitting:false prevents the observed eager CommonJS-helper cycle; package/lock/handlers/generatedroutes/security/business/financial policies and all50SQL remain unchanged. Controlled variants preserve49public file hashes; server bytes+4,566/cold-start and deployment limits unmeasured. Failed attempts and exact-source attribution are retained.
> Independent B6: Approved for human merge within bounded package-B technical scope; no unresolved introduced Critical/High/Medium finding. Review SHA256 `6bbf070336fbc2e9673bcfa257651a6eae5724be3fb010b5c9190b8fc112ccf8`; receipt `53c19110e180345df62b4e5852f003b02a7d8c81371f39256de9b0e22cf32fff`. Current441/446/42 are named setup/behavior/invariance controls, not distinct vulnerabilities or complete product coverage. OC-EVID-02 Low historical label/count precision remains deferred documentation debt.
> ONE NEXT: B7 — prepare the existing PR71 against main with exact preserved source/coverage and checks, then the owner's concrete protected merge decision; only after authorized merge verify and settle15B requests. C5requests/product/RC/release remain separate. No merge/deploy/originalPRmutation/closure/provider/production/new spending/history rewrite occurred in B5/B6;20originaldrafts remain.
> Claim6354262307 completes/releases through final55 handoff after independent docs-only publication preservation. No native rerun is attributed to the later evidence/documentation SHA. See `changes/b5-lifecycle/RESULT.md`, COVERAGE/ARTIFACTS/RUNS/INDEX and final review. This notice supersedes older CURRENT/ONE NEXT below; their complete texts remain exact.

> CURRENT — B-DEP-IDENTITY-01 verified on integration only;23October2026.
> Exact tested source `2de022a5e50a2e1d1761bfad92344505d146a750`, tree `5ed3276420424cd5ed5536d49b269be27a46ef5b`; accepted main remains `18700dee8ecdda2e457c0aa18c4f83a81b042019`, where these B corrections are absent.
> Current native39872844085/39872844063/39872844084 all SUCCESS: frozen compatibility94unit/291expectations, full supported audit{}/exit0, types/full lint/wire/build/generation,369protected/50SQL identity with29negative controls, actual entry3/realNodeHTTP11, offline sanitizer14, current webhook4+22 and foundation/browser regressions.
> Official whole-lock patches SDK1.32.0/Hono4.13.11/launch-editor2.14.2/Vite8.1.6/DOMPurify3.4.17/ip-address10.7.4; explained Vite build graph delta, no advisory suppression or release-age exception. Handwritten MCP request limits precede existing dispatch; generated routes/auth audience/business/financial contracts remain unchanged.
> The new exact B inventory preserves frozen A/original41; all50 applied SQL anchor independently to fixed B base59c8a0c. Historical failed audits, socket reset, lazy-Request replay and webhook comparison remain preserved with explicit dispositions.
> Independent final review accepts this dependency/request-boundary/B-identity technical batch only; no unresolved introduced blocking source findings in scope. Formal whole-head verdict: Blocked pending missing evidence (B5/B6). See review/FINAL_SCOPED_REVIEW.md and FINAL_SCOPED_RECEIPT.json; final docs-only preservation is recorded externally after publication.
> Whole-head/B5/B6/B7/B/RC acceptance remains blocked pending composed runtime evidence. Prior9266G1 run39871214992 fails exact41_migrations before scenarios against B50; successful cleanup/credential scan is preserved. No new G1green or current authenticated lifecycle is claimed.
> ONE NEXT: separately claim B5 fixed-source fresh50 and populated-upgrade account/REST/RPC/MCP/server-entry acceptance, reconcile effective50 runtime assertions while preserving original41, then B6 independent review. B7 owner merge/settlement and C remain open under canonical #70/comment6263266625.
> No merge/deploy/original draft mutation/closure/provider/production/new spending/history rewrite;20 original drafts remain (B15/C5). Claim6348079134 completes/releases through final #55 handoff after publication preservation; no next execution claim is implied.
> See `changes/b-dep-identity/RESULT.md`, coverage, provenance/index and final independent review. Native evidence belongs to2de022a5; docs-only publication is source-preserved, not a new native test run. This notice supersedes older CURRENT/ONE NEXT blocks below; their full history remains unchanged.

## B4 / APP-02 — final scoped evidence and next gate (22 October 2026)

Final50 source `f3b702440a4ffd17038f3c668a2f446620a97919` supersedes the interim49 verification status below. Run39614265434 passed fresh206, populated baseline53/corrected169 and frozen76+22 compatibility controls. Independent scoped review accepts APP-02 on this integration candidate only; the formal whole-head outcome remains Changes required because dependency High findings and the preserved A manifest barrier are open. The earlier complete-snapshot assumption and failing diagnostics remain withdrawn/failed in the retained history. Docs-only delivery must preserve358 protected identities/50SQL. The next separately claimed step is dependency remediation and source-identity reconciliation before B5/B6; no merge or deployment follows from this decision.

## B4 / APP-02 — application refusal and database retries (21October2026, candidate only)

Do not use engine SQLSTATE40001 for billing-domain ambiguity. Supabase documents that PostgREST14 can retry it internally, even after the HTTP client times out. Our diagnostic observed an absent stream, followed by created receipt request/statefalse, then a storedtrue flag consistent with the previous updated callback running later. The source normalizer was correct. All ten domain refusals use P0001 in a new CLI-generated50 forward function replacement; the route maps that RPC error to503 for explicit replay. Driver-level traces were not captured, so the mechanism is attributed to the official source and the observed ordering witness.48/49 stay immutable and new native stacks start without old pending requests. See POSTGREST_RETRY_ROOT_CAUSE.md for primary sources and exact evidence.

## B4 / APP-02 arrival-order correction —21October2026 (candidate only)

The initial complete-snapshot bootstrap assumption is withdrawn: the old handler deliberately preserves original plan/price and prior periods/cancel flag, which a later updated/canceled snapshot cannot reconstruct. Such callbacks now return retryable503 when their public subscription stream is absent; created establishes original fields, followed by replay in provider order. This preserves the business contract instead of inventing historical state. A created scheduled-change payload retains the old new-row cancel flag defaultfalse; existing flags remain preserved.

Migration48 was already applied in disposable verification and remains byte-identical. The correction uses a second CLI-generated forward migration49, replacing only the newly introduced function. Existing47 migrations, old public functions/grants and live signature helper remain exact. Earlier188-check runs do not cover the newly found cases and are retained as limited historical evidence, followed by final49 verification.

## B4 / APP-02 — transactional subscription callback persistence (2026-10-21, candidate only)

The existing signed handler acknowledges database failures and partial writes. Supported callbacks therefore use one service-only SECURITY INVOKER database transaction for subscription, required live cache/binding, and private durable receipt. Exact event retries are idempotent; ambiguous ordering, legacy clocks, missing identity and SQL errors return retryable failure. Provider occurredAt remains a microsecond string, and timestamps beyond database precision are rejected. No provider API lookup or raw payload logging is introduced.

Existing billing readers use environment-qualified subscriptions ordered by created_at. New rows use the immutable provider entity creation time; existing legacy rows keep their arrival timestamps, with conservative ambiguity rejection in both environments. Only created can replace a non-null live binding; non-current updates remain durable without rebinding. Sandbox never mutates the global tenant live cache. Existing canceled-period, trial, financial and retention contracts are preserved. No backfill, historical migration rewrite, rollout, merge or whole-B acceptance is implied. See changes/b4-app02 for limitations and native proof status.

> CURRENT — B2 / AC-01 corrected on the integration candidate, 2026-10-20.
> Exact executable source `7a4fb5811c35a053109860c3155074087b930489`; accepted main remains `18700dee8ecdda2e457c0aa18c4f83a81b042019`, where this correction is absent.
> Final native fresh46:95 checks; populated45-to46 upgrade:48 baseline controls reproduce the old bypass and59 corrected-state checks pass. All original B1 paths and45 SQL remain byte/mode exact.
> Independent scope is AC-01 only; B3/B4/B5/B6/B7 and the owner merge decision remain open. Early Medium B2-EVID-UPLOAD-01 is corrected; original failure and its review remain preserved.
> ONE NEXT: B3 / AC-02 — protect client INSERT/UPDATE trial/billing fields while preserving legitimate onboarding/settings and the existing business policy.
> See `changes/b2-ac01/RESULT.md` and its coverage/native/review packet. No B merge, deployment or PR closure occurred;20 requests remain open.
> This notice supersedes every older CURRENT / ONE NEXT notice below; historical A/B1 material follows unchanged.

> CURRENT — B1 composition complete, 2026-10-20.
> Accepted A remains on main `18700dee8ecdda2e457c0aa18c4f83a81b042019`. B is staged for review only.
> This notice supersedes older ONE NEXT notices below and in imported B documents.
> Scope: compose PR56–71 plus sibling67 without losing A; preserve all41 original migrations and four exact B additions.
> B2 AC-01, B3 AC-02 and B4 APP-02 corrections remain pending, followed by B5 lifecycle validation and B6 independent acceptance review.
> No B merge, deployment, production operation or PR closure is authorized by this composition step.
> ONE NEXT: B2 / AC-01 — scope the privileged security scan correction and verify regular-user denial with admin/service positive controls.
> Native frozen composition run39452262035 passed76 unit tests, original wire regression and build; lifecycle acceptance remains pending.
> See `changes/b1-composition/RESULT.md` and `changes/b1-composition/INTAKE.md`; the full original B71 document is archived beside it as `historical-B71-DECISIONS.md`. Existing A history follows unchanged.

## FOUNDATION-A — owner-authorized merge and evidence-based closure, 2026-10-20

Owner «اذا كل شي تمام ادمج» authorized the concrete PR72/A8 proposal after final independent approval and all exact-head checks. Fresh head/base/clean checks passed. Use merge_method=merge and expected headad73a947; actual merge0c138a970a03d00084631f1fe51fd3713c424874 preserves the published history. Actual main tree equals the approved tree; protected288/manifest/41SQL and archived coverage/evidence are present. Existing post-merge Quality39448069522 passed.

Only after that main verification, close32/33/48/52/53/54as superseded/incorporated; GitHub automatically recognized51merged via72. No claim that the three stacked security requests were separately merged into their old bases. Historical32financial design acceptance remains C5. Eight A requests are settled,20remain (B15/C5); preserve branches and failed evidence.

The acceptance capsule is frozen; this outcome/root-state follow-up is documentation only, preserving every protected source blob/mode and manifest/migration identity. Canonical70plan records A8 complete and B1 next. Overall integration/release acceptance stays false; owner approval covered A merge and its planned coverage settlement, not deployment, B/C merges, production access or financial/commercial policy. No B source change begins in this completion record.

## FOUNDATION-A — preserve bounded proofs across source evolution, 2026-10-20

Final51 acceptance supersedes421 only for the proposed current-source snapshot, with actual new G0/G1run39444611013/39444611354 and independent supplemental approval. Do not relabel earlier native or stored-finance runs. Source51 alters one protected historical workflow and its matching manifest entry; app/tests/lock/package/SQL and existing current gates remain unchanged.

A one-off exact-change verifier must not be presented as a general current-head gate after unrelated approved manifest scripts evolve. Preserve its original assertions and failed rerun, label it historical, require manual invocation and pin the actual accepted73e133 checkout. No adjustable source input, assertion relaxation, current Windows claim, ignored dependency advisory or bypass of current gates is introduced. Review verified both native failure logs, the scripts-only manifest difference, all-copy security guards and new integrated acceptance.

The A8 proposal remains the existing PR72 against main via fast-forward, with documentation-only descendants inheriting review only after exact source/blob/mode/manifest preservation checks. Owner merge approval remains mandatory under the standing plan; no merge/deploy/closure/production/spending/policy authority is inferred from technical approval. Main43d6edb and28open requests remain unchanged until explicit decision. Main coverage precedes each conditional closure; B/C and product release stay open.

## FOUNDATION-A — scope of accepted evidence and owner merge boundary, 2026-10-20

Standing plan70/comment6263266625 and owner «استمر وفق الخطة» authorize routine completion of A1–A7 and concrete A8 preparation on the existing integration branch/PR72, without another PR or rewritten history. The earlier A6-only original72-untouched restriction is superseded for fast-forward PR preparation, not for main/merge/deploy/closure. Explicit owner approval remains required to merge; Review Protocol approval does not perform that action.

Final executable source421774f has native G0/G1 evidence and an independent Approved for human merge verdict bounded to package A. Treat timezone settings query availability as part of the daily read basis; never substitute a default after a failed settings fetch. Preserve known cache/status and independently available non-daily actions. Use the same boundary for Pilot and close callback/UI. Terminate changed-lint options before Git-derived file paths. No formula/RPC/SQL, trial policy, provider or dependency change was needed for these demonstrated repairs.

The stored close_day run is truthfully attributed to fabb481. Exact final arithmetic memo/41SQL identity plus independent fixture replay supports the bounded arithmetic comparison; it is not a new SQL run on421 or proof of financial REST/concurrency/populated-upgrade acceptance. These remain C gates. Actual source43-case, Chromium10-case and G1-40 results apply to421, not arbitrary later code.

Documentation-only descendants preserve288protected blobs, the manifest and41SQL, restore28original32/33Markdown documents and retain all failed evidence. Restoring a historical design preserves its content without declaring every old proposed financial acceptance complete. PR48's7exact/11reconciled paths and remaining A ancestry have explicit coverage; every closure waits for owner-approved merge and actual main verification. B/C findings and overall integration_accepted=false remain visible. Final head/check/claim disposition is recorded in55/70/PR72; no production, cost or policy approval is inferred.

## FOUNDATION-A — preserve acceptance boundaries during resume, 2026-10-19

Owner authorized resuming the existing A/B/C plan after Work stalled. Recovered local APP-01 is verified against canonical remote blobs and continued on the existing integration branch, without altering original72/main or creating another PR. Four bounded functional corrections have separate source commits; the final source snapshot/regrression wiring is fabb481. Evidence is additive.

A source snapshot and local passing tests are not independent review, native acceptance or main completion. Whole-file equivalence is no longer claimed for intentionally changed read/trial/clock declarations: keep unchanged declarations/arithmetic/wire checks, targeted actual-source regressions and independent review of that proof change. Lock/dependencies and all41SQL remain unchanged. Native queue/browser availability and stored close-day comparison remain visible blockers. A6→A7→ownerA8 remains mandatory before B; no merge/deploy/policy/spending approval is inferred.

## 2026-10-19 — independent review disposition

Owner requested review of previous work. Three fresh independent scoped reviewers and the lead financial/dependency review recorded **Changes required** (5High,5Medium after deduplication) under docs/integration-g0-g1/reviews/2026-10-19. No approval for human merge or release. Current mechanical G0/G1 results remain valid on823cbcaf, while inherited defects and untested composition keep integration_accepted=false.

Missing financial reads must not imply zero; successful webhook HTTP must not imply durable persistence; a same-key server contract does not prove that clients preserve unresolved logical keys; separate green migrations do not prove compatible final functions. Preserve explicit quantity/stock and courier-transition contracts. Static/catalog/offline fixtures are not new SQL/production execution. Reject direct-DML, unconditional integer duplicate oversell and permission-resurrection hypotheses where effective revokes/checks/ACL contradict them.

ONE NEXT is bounded FIN-READ-FAIL-CLOSED-01 under standing owner execution authorization. That task must not change formulas, SQL, providers or quantity policy. Other findings require their own scope and gates. Medium dispositions must be explicit; High findings block their scoped acceptance. No quantity/trial/retention/provider policy, protected merge/deploy or new spending decision was made. Original PRs/main and runtime source/lock are untouched; publication is reports/evidence/state only and does not imply a new native CI run.

## 2026-10-18 — Candidate integration mechanics, no protected policy change

Standing owner authorization allows routine preparation on isolated integration/g0-g1-reconcile-2026-10-18; no merge/deploy authorization. Candidate823cbcaf passes native mechanicalG0/affectedG1 on oneSHA, but is not on main and has no freshGate6independent review. integration_accepted=false.

Use exact committed279blob integrated source snapshot instead of expanding legacy383path overrides; validate original41SQL unchanged. Existing54manifest/history preserved. Scope label reviewed_integrated_source is source reconciliation, not independent acceptance. Any source change requires a new exact manifest and affected evidence.

Nine known generator outputs normalized by reviewed hash pairs/pinnedPrettier after successful realVite build; unknown output fails before writes, nonzero build/postprocess exits preserved. This is explicit output postprocessing, not a patch to the upstreamLovable generator. Real tracked-source invariance remains mandatory. API/SQL/finance/authority/dependencyversions unchanged; same-wire types plus truthful nullable stored references and explicit nullTypeError diagnostics are reviewed candidate changes.

ProcessMap terminal/liveworker repair preserves sticky failures/unmappednonloopback/network/trace/secret/cleanup gates. EarlierfailedG1 retained; its exactreadcause unknown despite reproduced observer bug and later40/40success. Nofinancial/account lifecycle/production/Pilot acceptance inferred. Fresh independent review required before a highriskmerge proposal; ownerretention/subscription/financial/merge/deploy approvals unchanged. See docs/integration-g0-g1 for rationale,actualresults,remainingrisks and additive rollback.

## G0-APP-LINT-01 — preserve behavior while tightening local screen contracts

2026-10-17 owner task authorizes17inherited app lint fixes only, on existing Draft72. Refine local shared context mutation signatures from actual hooks instead of changing shared AppContext or coercing data. Derive payment/status/icon/totals contracts from current sources. Keep tenantTz Hook warning and existing conversions outside scope. Explicit Set if/else preserves discarded-expression semantics. Unknown thrown-value message access preserves original receiver/nullish behavior. Strict types expose an existing missing-customer click failure; retain explicit TypeError before navigation with clarified message, and record APP-DEBT-MISSING-CUSTOMER separately rather than inventing an invariant or filtering financial rows. No financial/business/API/schema change or release approval. Evidence Quality39072945731 on e58bc5db plus scoped independent review; G0/integration remain open. Final metadata in70/55.

## G0-ESBUILD-COMPAT-PROOF-01 — bounded candidate tested, 2026-10-17

Owner explicitly authorized exact esbuild0.28.1 override beyond unchanged mcp-js0.20.1^0.27.0; this is project compatibility evidence, not publisher support. Start1b7a1a01; tested source73e133b25a8a5167c6730eb82cf364268ad44373/tree0704600984e277d6090d87c5d3c53777f6cf86f7. Official complete Bun1.4-generated lock8db84562 changes only esbuild+26platforms plus override; all prior security fixes/SDK/app/SQL preserved. Final delivery identity is in70/55/PR72, documentation/evidence plus one no-behavior EOF blank-line restoration in the retired SEC-CI workflow after tested source; app/graph/test bytes unchanged.

Native Windows0.27.7 baseline39025616246:5cases3PASS/2specific traversalFAIL, rawexit1/controller0. Final Windows and Linux39026053191 each5/5, clean frozen1.2.14, real resolved/native versions,57officialMCPfilehashes/wholegraph/source invariance pass. Linux3actual MCP generator/CLI contracts,4adapter/SDK contracts,11guardcontrols/affectedlint pass. Quality39026056460 SUCCESS:66unit/174expect,8stubwrapper/67dummybrowser,typecheck/changedlint/twoisolatedbuilds/post-generation sourceinvariance. Synthetic Quality checkout tree equals tested source; not actual merge. Full supported audit raw{} exit0; exactly last esbuild advisory removed/no new. Missing-rg preparation and new-fixture formatting failures retained. docs/g0-esbuild contains report/raw/source/run/review/rollback.

Targeted dependency advisory item proved on draft only. G0/integration remain open: inherited full-repo lint not accepted, liveG1 not rerun, source54 fail-closed identity guard/manifest untouched; final-source reconciliation and remaining affected runtime/transport/SSR/auth/isolation/state/counter/secrets/cleanup proof need separate packet. No finance/account/SQL/production/main/merge/deploy/fork publication or billing configuration changes. ONE NEXT is planning that remaining evidence packet; close current claim after70/55 handoff and stop.

## G0-MCP-JS-COMPAT-01 — official decision checkpoint, 2026-10-17

Completed the owner-authorized read-only version investigation using exactly one diagnostic run39011125934/attempt1/SUCCESS on56170b8792337649458c3cbb6bc1aee7a8d03bc3. Official HTTP200 metadata contains33 newer stable+48 newer prereleases; all81 requireesbuild^0.27.0 and reject published patched0.28.1/0.28.2. No compatible official candidate exists in this captured snapshot. No candidate archive/install or binary comparison was performed. docs/g0-mcp-js/REPORT.md and exact raw official-inspection.zip preserve receipts, commands, source/run/artifact identity and limits.

Project package/lock and all prior security floors remain unchanged. Diagnostic trigger and temporary scripts are retired in this delivery; normal SEC-CI workflow restored to0540e266. No Quality/G1, finance/account/SQL, main, merge/deploy or billing configuration change. Decision investigation complete; remediation/G0/integration remain blocked. ONE NEXT for planning: a separately authorized design/source-inspection packet for a narrowly scoped parent contract patch/upstream option, not broad mcp-js/SDK upgrade or silent override. Stop after55/70 handoff.

## DEC-G0-NODE-SERVER-01 — prove published 1.x patch and native Windows boundary

2026-10-16 owner task authorizes the smallest adapter correction above PR72/5cbf198. Official npm packument and verified actual tarball prove1.19.15 is available, so the permitted2.0.5 fallback is unnecessary. SDK1.31.0 accepts1.19.15 without any SDK/app change; adapter engines/peer/exports unchanged. Use paired1.19.15 constraints and approved official whole-lock generation; byte-exact lock1a0791b4 changes only adapter and override. Preserve Hono/qs/DOMPurify/Babel/esbuild and every other package.

Windows URL-prefix/decoded-backslash behavior must be proved on native Windows with real installed package and dummy files, not inferred from Linux. Same8 cases give old6PASS+exact2specificFAIL and patched8/8 on both OSes, with benign auth/static/HEAD/range/negative paths and actual SDK Node HTTP/errors. Static library reproduction does not prove application exploitation. Preserve real old Node exit1 and complete scanner exit1; audit leaves esbuildLow, so G0 stays open.

Harness failures are evidence: explicit UTF8 corrects Windows collection; fresh per-request server/transport follows the locked SDK's single-use stateless contract; disposable Windows checkout retains canonical LF while keeping strict byte assertions. No assertion weakening, SDK upgrade or application workaround. Tests, graph, frozen,10 Bun guard controls and Quality38952653426 pass on source1568819. Independent review states actual hash/raw-evidence/Node-adapted guard replays and limits.

No live G1 rerun or old40/40 promotion. Before integration acceptance, explicitly reconcile unchanged source54 identity guard/manifest to reviewed final source/lock and run affected real runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof. All app/SQL and financial/auth/state contracts unchanged. No merge, deployment, production or further implementation; hand off in #55/#70 and stop for planning.

## DEC-G0-BABEL-01 — preserve safe copies and source-map behavior

2026-10-16 owner task authorizes GHSA-4x5r-pxfx-6jf8 remediation on PR72 starting86d5. Official first fixed7.29.6 is not a valid shared global pin because existing safe7.29.7/TanStack^7.29.7 would regress. Use paired7.29.7 constraints and the approved official whole-lock generator; retain stable7.x guard floor7.29.6. No new direct dependency, lockformat/CI toolchain change or safe-copy downgrade.

Necessary Babel internal changes were explained before adoption: generator reuses existing patched versions, removes exactly six obsolete versions and moves/hoists Babel paths; no new versions, retained metadata changes or non-Babel package changes. Exact inventory and independent graph invariants are saved, not hand-edited generated entries. Vite/TanStack/Workbox/node-server/esbuild versions remain fixed.

Actual transform tests leave automatic inputSourceMap enabled and sourceMaps true; two outside-root dummy-map disclosure oracles fail only on old7.29.0, legitimate map/plain controls pass. Same6cases per distribution pass on corrected shared7.29.7;18→6tests reflects3→1physicaldistributions, not weakened coverage. No application sourcemap config or financial/schema/auth contract change.

Tested1e80 source passes frozen/graph/installed/all-copy/affectedlint and Quality64unit/141expect. Full audit still exits1 for two other findings; G0 stays open. Independent review actually reruns Python/Node adapter/semver/hash/receipt/log checks, not actual compiler/Bun/browser/DB. LegacyG1 source54 identity stays fail-closed; explicit final-lock/source reconciliation and affected real-runtime proof are required before integration acceptance. No release or merge approval.

## DEC-G0-DOMPURIFY-01 — prove optional sanitizer correction and original PDF compatibility

2026-10-15 authorization, 2026-10-16 handoff. Owner approved DOMPurify3.4.11→3.4.16 alone on PR72 starting5623. Official jsPDF4.2.1 optional^3.3.1 accepts3.4.16; no direct dependency, parent upgrade or unrelated graph delta. Approved Bun1.4.0 generates the whole lock under paired constraints, with every-copy stable3.x floor>=3.4.16 and all Hono/qs/previous guards preserved. Package absence cannot stand in for remediation.

Actual browser contracts distinguish five old targeted failures from five ordinary successes and require all10 on patched package. Original src/lib/invoice-pdf.ts is imported unchanged in a browser-only synthetic bundle; actual export, output structure/exactfilename/cleanup and offline networking are checked separately from the library defect. Independent reviewer reproduced missing-charset mojibake filename in the harness; explicit UTF8 response/meta/check corrects only that fixture. No weakened filename/security assertion or application/financial change.

Testeda5edd17 source passes bounded frozen/graph/installed/browser/PDF/guards/lint and Quality63unit/137expect. Supported full audit still returns1 with Babel/node-server/esbuild findings, so G0 stays open. No financial/schema/auth/tenant contract changed, production or G1 live execution. Legacy source54 identity stays fail-closed; explicit reviewed final-lock reconciliation and affected runtime proof are required before future integration acceptance. Preserve failed runs, full audit and exact independent reexecution scope; no release or human-merge approval inferred.

## DEC-G0-QS-01 — demonstrate library defects before bounded patch

2026-10-15; owner explicitly authorized qs6.15.3→6.16.0 only on PR72 starting15710. Actual installed old graph must fail exactly the three targeted contracts while normal cases pass; the same assertions must pass on patched graph. Full encoded round-trip preservation and actual parent resolution/loopback query/form parsing prevent no-throw/version-only compatibility claims. OfficialBun1.4.0 generates the complete lock under paired overrides/resolutions; whole graph comparison permits only qs, preserves all Hono/other floors and parent versions. No direct dependency or manual generated entries.

Testedfc6 with15/15 and Quality62unit/133expect passes covered compatibility, but full audit still returns1 with six non-qs findings. Preserve raw expected-red baseline and complete scanner failures, no fixed count/waiver or inferred application exploitability. No G1 live rerun or source54 allowlist expansion; new-lock integration requires explicit identity reconciliation and affected proof. All app/41SQL/finance/account/production remain unchanged. Independent review/impact/rollback/evidence docs/g0-qs; planning owns the next batch and risk acceptance. No merge/deploy.

## DEC-G0-HONO-01 — bounded dependency patch with separate scanner failure

2026-10-15; explicit owner authorization after70/6198453113. Pin only Hono4.13.7 using the paired existing override pattern; generate the whole lock with approved official Bun1.4.0 from current8960 base, never manually edit generated entries. Review proves one package entry changed; retain SDK/Lovable/security floors and stable-major guards. Final e38cf18d source passed covered compatibility/protection tests; eight target GHSA absent. Use CI Bun1.2.14 for frozen/runtime compatibility, supported verified Bun1.4.0 for audit; preserve initial unsupported-command and frozen failures. Complete scanner exit1 and remaining findings stay failed G0 evidence, not waived success.

Reuse G1 only at original dbc870/old-lock identity. Do not widen source54 identity allowlist merely to approve a dependency update; current new-lock G1 is unaccepted and future baseline reconciliation must be explicit. Lint diagnostics are measurement only. No app/SQL/finance/account/source-rule/production/Paddle/merge/deploy change. docs/g0-hono records exact evidence, limits, review and additive candidate rollback. Planning owns the next batch and any risk acceptance.

## Bounded decision — G1-EGRESS-TRACE-01, 2026-10-15

Treat blocked packet counts, syscall calls, resolver invocations and unique connections separately. Diagnostic16 IPv4 packets are Node/getaddrinfo resolver attempts to127.0.0.53:53 for public hostname workers.cloudflare.com, not demonstrated external delivery. Pinned Miniflare setupCf source identifies optional cf.json metadata fetch and official CLOUDFLARE_CF_FETCH_ENABLED=false early fallback. Apply only that literal in isolated test env; no destination allow/reset/DNS stub/version or app change. Actual installed-vendor3case fixture and dbc870/run38742289056 PASS40/40 prove zero delta with unchanged named500/SSR/Auth/data/source/secrets/cleanup. Preload control retains same16 in diagnostic; corrected untraced execution is not claimed. Preserve failed evidence and all coverage limits. No global gate/release approval; hand off then stop.

## DEC-G1-CLI-CLEANUP-01 — preserve failed network gate and source identity

2026-10-15; owner-authorized bounded continuation on existing Draft72. Use the observed immutable official setup-cli source, unchanged CLI2.101.0/actionBun1.3.10, checked source hash, phase-only instrumentation and120s process-group timeout. Two successful installs do not prove the cause of old38605846901. Distinguish missing user from unreadable user/process state; all read errors remain failed verification. Official Wrangler banner suppression is a test-tool setting; measured packet delta24→16 is partial, with16 remaining blocked IPv4packets. Do not call REJECT counts successful deliveries or unique connections. Collect final invariance/source/secret evidence after a failed native gate but preserve final job failure. Nozero waiver, network allowance, application/financial/schema change, dependency upgrade, merge or deployment. Final runtime819291c8 remains unaccepted; planning owns the next bounded startup trace. docs/g1-cli-cleanup contains preserved raw failed archives, evidence and independent review.

## Final handoff — G1-ACCEPTANCE-REPAIR-01, 2026-10-14

Existing Draft PR72 retained; main43d6edbccb66fb06ce0fcb93734ad59532d1aeae and original48/51–54 unchanged. Tested source7d30e65c7bfb454fda4bf6bc6224e8510174c200: semantic CI17tests/6safechecks and automatic Quality PASS. Runtime38605846901 CANCELLED during CLI setup before DB/SSR; cleanup receipt3/4, process oracle failed for a user never created. No new liveSSR/after-state/native-counter acceptance. Exact reports, raw receipts and independent review: docs/g1-acceptance-repair/REPORT.md and REVIEW.md. These supersede the intake status below.

Outcome: Blocked pending missing evidence; G0/G1 unaccepted. #48 stays open without formal superseded. All application/auth/dependency/41SQL/financial contracts preserved. Delivery is metadata/evidence only above tested7d; root fingerprints updated explicitly, no executable test change or failure waiver. #55/6173791297 closes only in the final linked handoff. ONE NEXT: bounded installer diagnosis plus absent-user cleanup-oracle proof and exact SSR/after-state/counter execution; no blind version upgrade, account/financial expansion, merge or deploy.

## DEC-G1-ACCEPTANCE-REPAIR-01 — preserve safety oracles and failed evidence

2026-10-14; owner continued after PR72 handoff. Reuse the existing PR/source/evidence. Replace the stale visual-file literal coupling with actual pure policy, shared navigation forwarding, context wiring before pages and fatal before/after origin checks, protected by negative mutation cases. Runtime accepts only the same complete named config mismatch AND500; formatting normalization may remove ANSI/whitespace only. Drain logs and publish static categories/hashes; keep private logs/credentials private. A mismatch failure may collect final snapshots/counters but must still fail the job. No app/auth/dependency/SQL/financial contract change, original history rewrite, merge or deployment. G0/G2 acceptance is not granted.

## DEC-020 — Runtime feasibility and unchanged cloud boundary (2026-10-10)

- Status: authorized runner investigation; documentation candidate only.
- Current public documentation adds an experimental native runtime requiring CLI >=2.119.0, so absence of Docker is not a universal Supabase limitation. Existing repository CLI2.101.0 and Docker CI remain unchanged.
- A scratch CLI2.120.0 native probe failed before PostgreSQL startup; the environment only maps UID/GID0, cannot transition to a non-root account and cannot create a user namespace. Do not patch PostgreSQL to run as root, bypass host restrictions or label an unavailable stack as tested.
- Free-plan metadata for the old validation project does not establish fresh schema/data isolation or exact-candidate compatibility. Preserve DEC-PRIMARY-ENV-001-R: do not restore it as a shortcut. No cloud project restore/creation or cost is approved by this record.
- Select a capable disposable runner and preserve exact source/runtime identity. A native runner would need explicit experimental-toolchain assessment and cannot replace matching hosted acceptance by inference. Financial write harnesses remain blocked until real isolation proof and gate acceptance.

# Engineering Decisions

## DEC-PRIMARY-ENV-001-R — Preserve reviewed remediation before integration

- Date: 2026-10-10; authorized continuation of PR54.
- Astra source review resumed and closed the recorded transport/font findings; outcome remains Blocked pending missing evidence. The earlier reviewer-capacity note below is historical.
- Reconcile the 13 reviewed source blobs and preserve raw proof in an additive commit on PR54. Do not rewrite published history or mark bounded transport evidence as application/database isolation.
- No capable local stack is available. The old cloud validation project is inactive and unverified; do not restore or use it as a shortcut. Obtain the documented fresh isolated runner before financial write tests.


This file records decisions that govern Mongezz until replaced by an approved ADR or later decision entry.

## DEC-PRIMARY-ENV-001 — Continue isolated local candidate work

- Date:2026-10-10; owner explicitly authorized implementation and continuation.
- Decision: reconcile existing PR48 current source with immutable PR53 security source on a separate draft branch. Local implementation/probes continue despite hosted Actions quota; they do not substitute for hosted or independent release evidence.
- Contract: explicit deploy target and Supabase public identity; non-production cannot select approved production; runtime matches baked configuration before application entry; public fields reject known privileged formats. Write harnesses remain restricted and require isolated-stack proof before execution.
- Review: Astra attempt failed on usage capacity, so review is pending. Do not substitute self-checks for independent approval or silently change the requested reviewer.
- Consequence: no merge, deploy or financial write harness execution in this packet. Keep PR48/main and dependency artifacts unchanged; preserve raw failed evidence and exact-source fingerprints. Human-controlled release gates remain effective.

## DEC-001 — Delivery methodology

- Status: Accepted
- Decision: Use NAADF for new projects or independently designed subsystems and NAADF-CMF for changes to the existing Mongezz application.
- Consequence: No implementation begins before the required intake, baseline, impact, design, and safety gates are completed.

## DEC-002 — Repository documentation is the source of truth

- Status: Accepted
- Decision: `PROJECT_STATE.md`, `DECISIONS.md`, `TASKS.md`, approved specifications, migrations, tests, and source code override conversational memory.
- Consequence: Project state must be updated before ending a material work session.

## DEC-003 — Financial state ownership

- Status: Accepted
- Decision: Financial rules belong in approved domain functions and authorized server-side/database transaction boundaries, not duplicated UI calculations.
- Consequence: Debt, remaining balance, courier custody, settlement, returns, and margin calculations require central ownership and regression tests.

## DEC-004 — Delivery and settlement are distinct states

- Status: Accepted
- Decision: `Delivered` does not mean `Settled`. Money collected by a courier remains custody until an authorized settlement records it in store receipts.
- Consequence: No UI, report, RPC, or migration may collapse these states.

## DEC-005 — Returned orders

- Status: Accepted
- Decision: A returned order must not create customer debt or courier custody and must restore inventory only through the approved return transaction.
- Consequence: Return behavior requires database and financial regression tests.

## DEC-006 — Tenant and employee isolation

- Status: Accepted
- Decision: Tenant and assignment restrictions are enforced server-side and by RLS using deny-by-default and least privilege.
- Consequence: Hiding UI elements is not authorization. Negative authorization and cross-tenant tests are mandatory.

## DEC-007 — Database migration policy

- Status: Accepted
- Decision: Applied migrations are immutable. Corrections use new forward-only migrations.
- Consequence: Breaking changes require expand-and-contract, compatibility analysis, and rollback or compensating migration planning.

## DEC-008 — Production boundary

- Status: Accepted
- Decision: Automated agents and isolated tests do not access production data, production secrets, or destructive production controls.
- Consequence: Destructive actions, merge, and deployment require explicit human action.

## DEC-009 — Pull-request scope

- Status: Accepted
- Decision: One coherent feature or change per PR. Broad refactoring, global formatting, and unrelated dependency upgrades are separate work.
- Consequence: PR #17 is not a release candidate and must be baselined and decomposed before employee-account implementation proceeds.

## DEC-010 — Lovable-linked history

- Status: Accepted
- Decision: Do not force-push, rebase, amend, or otherwise rewrite published history connected to Lovable.
- Consequence: Corrections are additive commits, merge commits, or new branches and PRs.

## DEC-011 — Pilot before employee expansion

- Status: Accepted
- Decision: Validate the owner-only financial core with a controlled pilot before implementing employee accounts.
- Preconditions:
  - a synchronized and release-verified `main` baseline;
  - non-production environments cannot silently connect to production;
  - financial write operations have approved retry and idempotency protection;
  - CI reports do not expose environment credentials and use deterministic tool versions;
  - support, rollback, and reconciliation procedures are documented.
- Consequence: PR #17 is superseded and closed without merge. Employee work remains deferred until pilot evidence confirms priority and Change Gates 2–4 are approved.

## DEC-012 — Pilot blockers are release blockers

- Status: Accepted
- Decision: `FIN-COURIER-001`, `SEC-ENV-001`, `SEC-CI-001`, and `FIN-IDEM-001` must be completed and release-verified before any real-store pilot data is accepted.
- Consequence: Pilot planning may proceed, but pilot execution remains blocked. A build or smoke-test success alone does not waive these controls.

## DEC-013 — Current role model is descriptive, not final authorization design

- Status: Accepted
- Decision: The current database enum is `owner | staff`. This records existing schema reality only; it does not authorize broad employee access or define the final employee/courier role model.
- Consequence: A future restricted employee capability model requires an approved authorization matrix, RLS design, negative tests, and backward-compatibility analysis.

## DEC-014 — Courier sale, customer, custody, and primary sale flow

- Status: Accepted
- Approval record: FIN-COURIER-001 Gates 0–3 were explicitly approved by the product owner on PR #24 head `a652de164e3efeae707038f1769aee12a9e2474a` after the required Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke checks passed on that exact head. The documentation contract was merged through PR #24 as merge commit `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.
- Decision:
  - customer identity is required when a transaction creates customer debt, not merely because delivery uses a courier;
  - a courier order still pending delivery may exist without a customer and remains outside financial settlement;
  - money explicitly recorded as already collected by a courier is stored as courier custody, not store cash;
  - a fully collected courier sale is represented as `delivered_full` and is immediately eligible for settlement;
  - a partially collected courier sale is represented as `delivered_partial`; the collected amount is custody and the remainder is customer debt, therefore a customer is mandatory;
  - delivery without collection that creates debt requires a customer;
  - advanced sale is the primary sale workflow on desktop, mobile, and post-sale navigation;
  - quick sale remains an explicit secondary shortcut for direct, cash, fully-paid, customer-free sales.
- Consequence:
  - effective database constraints and RPC validation must be corrected through a forward-only migration;
  - the UI must use courier-specific states rather than ambiguous direct-payment labels;
  - existing T1–T15 plus new financial, state-transition, mobile, and desktop tests are mandatory;
  - `Delivered` remains distinct from `Settled`;
  - Gate 4 safety-net work is the only next FIN-COURIER stage authorized for preparation; PR-A, PR-B, and PR-C remain blocked until Gate 4 evidence is independently reviewed and explicitly approved;
  - after the baseline-synchronization PR is merged, the Gate 4 branch must be cut from the verified resulting `main` head rather than from a stale earlier SHA.

## Pending decisions

- Employee assignment source of truth: existing `orders.courier_id` versus a dedicated assignment model.
- Employee historical identity and hard-delete invariant after unlinking.
- Final restricted employee/courier capability model beyond the existing `owner | staff` enum.
- Audit event model for employee order-state and custody changes.
- Final billing enforcement and expired-subscription behavior.
- Final backward-compatibility treatment for existing courier orders that are `pending` but contain inconsistent legacy financial fields.


## DEC-015 — Original-project source and pinned execution plan

- Status: Owner-directed planning/governance; documentation candidate on a review branch.
- Owner instruction on 2026-10-09: consolidate instructions from both repositories,
  define the final-product plan, then pin starting steps so work can begin.
- Source: `naderalhaje0970-droid/simple-store-aid`; verified main `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
- Current plan: `docs/PRIMARY_DELIVERY_PLAN.md`; one current state/task queue.
- `mongezz` and PR137 retain historical evidence only; transfer candidates require
  source comparison and new verification. Plan1.2 identifiers are mapping history.
- Scheduling adjustment: prepare PRIMARY-SEC-001 dependency-security work before
  environment acceptance and financial write verification; reconcile SEC-CI and
  existing PR48/49/50 rather than repeat them from stale August instructions.
- This record does not approve an unreviewed financial policy, waive NAADF-CMF,
  close a release gate, merge, deploy, or authorize production access.

## DEC-016 — Framework transport and serializer candidate pins (2026-10-09)

Within the owner's authorized security batch, use the official minimum patched react-start1.168.60 graph with matching react-router1.170.41/router-plugin1.168.42. Preserve Lovable2.9.1. Pin Seroval1.6.7 in its direct declaration, overrides and resolutions because the old lock is affected and the new framework requires ^1.6.7. Retain seroval-plugins policy and all unrelated root declarations.

Use provider ErrorComponentProps in the two error boundaries; retain behavior and accept error:unknown without casts. Generated route/lock files come from their generators. Lock resolution uses Bun1.3.14 with the existing24-hour release-age policy; the current CI Bun1.2.14 was tested for frozen-install compatibility but its supply-chain enforcement gap is not claimed fixed.

Candidate status only: native29 tests/typecheck/build pass; existing lint, broader audit, hosted CI and review block global acceptance. PRIMARY-SEC-002 is prioritized by newly proven audit evidence before PRIMARY-ENV-001. No financial rule, schema, release approval, merge or deployment decision is changed. See changes/primary-sec-001/VERIFICATION.md.

## DEC-017 — Critical/High dependency advisory floors (2026-10-10)

- Status: Candidate decision in the owner's authorized security batch; not merged or released.
- Decision: preserve explicit patched floors for current Critical/High audit groups: `@modelcontextprotocol/sdk` 1.31.0, `proxy-addr` 2.0.8, `shell-quote` 1.11.0, `brace-expansion` 1.1.21 / 2.1.7 / 5.0.12 by major line, `browserslist` 4.29.3, `fast-uri` 3.1.8, `ip-address` 10.7.3, `js-yaml` 4.3.2, `nanoid` 3.3.19, `postcss` 8.5.29, and `source-map-js` 1.2.2.
- Rationale: `bun audit` on the prior candidate still reported 2 Critical and 33 High package/advisory records. After these floors, current audit has 0 Critical and 0 High records.
- Tooling note: Bun 1.3.14 did not apply nested overrides for the three `brace-expansion` major lines, so the lockfile carries the compatible major-specific entries and the unit guard enforces them. Frozen install was verified with Bun 1.3.14 and Bun 1.2.14.
- Consequence: future dependency refreshes must keep the dependency-security guard green and must not silently reintroduce the vulnerable floors. Remaining Moderate/Low audit records, hosted CI, independent review, runtime auth/MCP, financial gates, merge, and deployment remain outside this decision.

## DEC-018 - Generator-owned PRIMARY-SEC-002 lock remediation (2026-10-10)

- Status: Candidate implementation under the owner's authorized review-remediation request; final review/hosted CI remain open.
- Supersedes the manual-lock procedure described in DEC-017, preserving its patched security floors.
- Use verified Bun 1.4.0 transitive update support on the original PR52 lock and the final manifest/config. Do not hand-edit generated lock entries. See `changes/primary-sec-002/LOCK_REGENERATION.md` for source blobs, commands and graph impact.
- Pin `@lovable.dev/mcp-js` to the already-tested/resolved 0.20.1 to avoid an accidental downgrade during regeneration. Remove unsupported brace-expansion resolution paths; preserve the major-aware dependency guard and frozen installations.
- Keep the existing 24-hour resolution-age configuration and exclusions unchanged. The regenerated lock remains version 1 and installs with Bun 1.2.14 and 1.3.14; no CI toolchain or application runtime upgrade is made here.
- Put the synthetic MCP adapter compatibility tests in `tests/unit` so existing Quality includes them. These tests do not approve application JWT, tenant isolation or financial behavior.
- Hosted execution is blocked by the observed GitHub account payment/spending annotation. No billing change, spending increase, merge or deployment is authorized by this engineering decision.

## DEC-019 — Isolated browser transport policy (2026-10-10)

- Status: candidate remediation in existing draft PR54 under the owner's continuation request; independent bounded findings closed, global acceptance blocked.
- Install one context HTTP/WebSocket guard before creating any page. No direct continuation: fetch without redirects/retries, reject all3xx, close WebSockets without connecting. Auth/destructive requests use exact configured app/API origins; visual policy stays read-only.
- Fulfill the existing exact Google Fonts stylesheet URL offline with empty CSS only for GET/stylesheet/non-navigation; reject other uses. This intentionally uses fallback fonts and does not approve final typography. No provider request, app or package change.
- Use production-built artifacts for browser smoke; local/CI uses the isolated Cloudflare emulator, explicit preview/staging visual targets remain supported. HMR and Realtime are outside these harnesses because WebSockets are blocked.
- Preserve live before/after recorder evidence and substitute-browser/toolchain limitations. Passing dummy transport cases does not establish isolated Auth, migrations, RLS, tenants, finances or matching hosted execution.
- No financial write harness before accepted isolation proof; no production access, billing/spending change, merge or deployment. Continue with the isolated runner sequence in changes/primary-env-001/ISOLATED_STACK_READINESS.md.

## DEC-020 — Bounded experimental native runner evidence (2026-10-10)

- Status: experimental external validation evidence in draft PR54; no CI-toolchain, schema, merge or release acceptance.
- Use one fresh disposable non-root Vercel sandbox for exact simple-store-aid source; enable only local PostgreSQL/Auth/PostgREST and explicit matching ci identities. No production/cloud data, public routes, snapshots, new paid plan or billing change. Preserve repository Docker/CLI2.101.0 workflow.
- Record actual41 fresh migrations,60 unit tests/125 expectations, isolated build, bounded two-tenant metadata and matching-browser desktop/mobile Auth results. Preserve two fixture-role conflicts; separately verify the existing owner trigger rather than rewriting failed results.
- ENV-NATIVE-01: a banned account's old JWT still reads its own tenant. Strict disabled-account acceptance is not met; no exception or UI-only mitigation is approved. A focused gated server/database lifecycle fix and independent review are next.
- Stop the temporary runner after retrieving sanitized evidence. Do not promote bounded tests to comprehensive tenant/RPC/financial or hosted-check acceptance. Financial write tests remain blocked until the isolation gate is accepted.

