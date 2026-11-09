## Current — RECOVERY-02, 2026-11-07

1. [Done] Production hotfix `20261107214500_sec_email_queue_service_only` (verified ACLs after apply).
2. [Done 2026-11-08] Rollback test (full script, rolled-back txn) vs CURRENT production (43, email fix kept): md5 33/33, ACL 35/35, policies 59, lab unchanged after (evidence r02_rollback_test_20261108). Not a backup/restore proof.
3. [FROZEN] Apply the 9 October migrations to production — only after rollback test, backup/restore proof, independent review and explicit owner approval of that scope.
4. [Open] Independent financial/security review (not this agent); CI/browser tests blocked by the suspended GitHub account.
5. [Done 2026-11-09] True concurrency in the lab via parallel pg_cron sessions (evidence r02_concurrency_20261109).
   - C1 last-unit sale, C2 double collection, C3 duplicate webhook, C4 double settlement: all PASS (no double financial effect).
   - Findings: (a) settle_courier_orders accepts an already-settled order (courier_id NULL bypasses the custody check), 0 collected, no money effect, low severity; (b) the webhook's SELECT tenants FOR UPDATE with lock_timeout 2s times out (retryable) while a long transaction on the same tenant holds FK KEY SHARE; consider FOR NO KEY UPDATE.
   - [Pending owner confirmation] Lab cleanup of synthetic tenant d1000001 and helper recovery_evidence.r02_run (the DELETE confirmation was unanswered).
6. [Owner decision] Day close counts returned courier orders in `sales` (pre-existing behaviour).
7. [Open] Supabase default privileges still grant EXECUTE on new public functions to `authenticated`; every new SECURITY DEFINER function must revoke explicitly. Consider changing the default.

---

## Current — Phase 1 remaining, 2026-11-06

1. [In progress] release-finance.yml: 8 jobs green on one SHA (collection, sale x fresh/upgrade/populated; journey x fresh/upgrade).
1a. [Done] release-finance.yml 8/8 green on 76273d4 (run 42306255829).
2. [Implemented, effective after merge] Trusted gate release-gate-trusted.yml (pull_request_target, base code, objects mode). Owner settings: docs/RELEASE_GATE_SETTINGS.md.
3. [Done] Independent review of gate + workflow (verdict on b2c9dc7: not closable). Findings F1-F5 and minor items fixed; see PROJECT_STATE.md and docs/RELEASE_COVERAGE.md.
3a. [In progress] release-finance (9 jobs incl. quantity), B1, G0, C5 green on one SHA after the fixes.
3b. [Planned, before the first Phase 2 PR] Port the durable c3 controls (idempotency table RLS deny, direct table denial, same-key replay without writes) into release-finance; review b2-b4 coverage.
3c. [Planned, after the gate is proven on main] Retire the stage identity chain from integrated-quality and the old stage workflows (separate owner-visible decision).
3e. [Planned, after PR #74 merges] Update PR #73 on the new main: both edit tests/g01-acceptance/integrated-b-source.json; recompute blobs, rerun main's identity and all PR checks; PR #73's earlier results do not count.
3f. [Blockers, documented] c3 durable controls before the first Phase 2 PR; restore with synthetic data before Pilot.
3g. [Blocked: owner decision] Rulesets/branch protection unavailable: private repo on GitHub Free ("Upgrade to GitHub Pro or make this repository public"). Recommended: GitHub Pro (cost decision); do not make the repo public. Until resolved, checks are advisory only; no integration merge; Phase 1 not complete.
3h. [Done 2026-11-07] Gate verified on GitHub (PR #75, test only): head fetch with one-shot credential OK, gh api label events OK, 45/45, RELEASE_GATE_FAILED "Base migration changed". PR #76 (test only) awaits the owner's gov-ok-4e36fbf... label to verify approval binding and performed_via_github_app; this works without rulesets.
3d. [Owner] Apply docs/RELEASE_GATE_SETTINGS.md in two stages (A: trusted-release-gate after PR #73; B: full 11 checks incl. suite (quantity, fresh) after the integration merge); check Lovable sync under the PR-required rule; run the two verification PRs.
4. [Planned, Pilot condition] Restore of real financial data (backup -> restore -> balances match) in the Phase 5 rehearsal. Restore suites are kept, not deleted; Pilot is blocked until this passes. Use realistic synthetic or de-identified financial data, never real customer data.
5. [Backlog, low] Self-host the Cairo invoice font (production InvoiceDetailScreen calls fonts.googleapis.com).

---

## Current — profit contract ADOPTED under specific owner delegation, 2026-11-06

The owner explicitly delegated the pending choice to the lead assisted by financial/programming agents. Two actual fresh independent read-only advisers (/root/financial_decision and /root/engineering_decision) reviewed source1c8f43c76471332bb80248929a47a66a1c80af8e and both returned ADOPT. Root adopts C5-PROFIT-BASIS-01: preserve legacy recorded before-expense margin, add explicit gross alias and net=saved margin−saved expenses once (fixture135−5=130), via SELECT-only invoker projection. No rounding/clamp/backfill or old API/data meaning change. This is an operational collection-based measure, not audited statutory profit.

**The prior owner-adoption blocker is RESOLVED for this specific contract.** This is scoped delegated adoption, not general permission to alter other financial policies, merge/deploy, incur cost, destroy data or bypass governance. Implementation C5-PROFIT-CONTRACT-IMPLEMENT-01 is Planned/ready; the decision alone is not implementation/testing.

Adopted presentation conditions: expose existing realizedRevenue through totals/types for the invoice-period estimate equation; collected remains a separate payment-date cash fact. Remove false profit-gap=debt+custody equality and universal close_day-equivalence comment; label admin legacy margin before expenses. Preserve financial algorithms. Carry view read-state/errors/retry into affected day-close/pilot controls and validate required values rather than null-to-zero. Explicit layered source admission/new55→56 acceptance must preserve all old55 proofs.

Decision records: changes/c5-profit-contract/DECISION_ADOPTED.md, REVIEW_DELEGATED_FINANCIAL.md, REVIEW_DELEGATED_ENGINEERING.md, IMPLEMENTATION_INTAKE.md, evidence/delegated-decision.json. Current batch is documentation/source decision only. Decimal135−5 and counterexample (profit gap30, debt50) checked; no SQL/view/RLS/native/type/build implementation tested here. Original failed archives/oracle/executable source remain unchanged; fullC5/integration=false, C6/C7/RC/Pilot pending.

**ONE NEXT: execute the approved bounded isolated implementation and explicit safety-net/admission delta, then exact-source fresh/populated/security/history/read-state/desktop/mobile verification and independent implementation review. No repeat request for adoption of this split.** Then remaining C5/network → full independent C6 → protected owner C7/main verification/settle original5drafts → RC/Pilot. Existing branch integration/g0-g1-reconcile-2026-10-18; main220fc206/five drafts unchanged. Claim6687511352 pauses at final decision handoff; no concurrent implementer. Prior records below preserved as history.

---

## Current — concrete profit-contract proposal reviewed; owner adoption OPEN, 2026-11-06

C5-PROFIT-CONTRACT-DESIGN-01 completes the fixed next design batch on source4f7aec69, existing integration/g0-g1-reconcile-2026-10-18. Source inventory130code files+55SQL,7consumer files; exact recommended SQL/ACL/typed-consumer/history/rollback plan and phased acceptance matrix prepared. NineDecimal arithmetic vectors PASS; two actual separate read-only reviewers accepted proposal/design scope. No SQL/view/RLS/native/implementation acceptance claimed.

PROPOSED C5-PROFIT-BASIS-01: preserve old day_closes.realized_profit135 before expenses and all oldRPC/DTO meanings; add SELECT-only security-invoker reporting projection with explicit realized_margin_before_expenses135 and realized_net_profit130 (=135−5). No stored-row mutation/backfill/reallocation. Historical/manual provenance remains unverified; net derived from recorded v1 values, not retroactively audited. Separate invoice-period estimate and payment-date snapshot scopes; admin135label clarified without cross-tenant scope change. Old failing130oracle/archive remain unchanged until exact split is adopted and implemented with stronger gross135+net130 checks.

Owner adoption of this precise financial-report contract remains OPEN under AGENTS/user protected-decision rules. Broad continuation instructions authorized concrete design/docs, not choosing a protected financial meaning on owner's behalf. Implementation is Planned, not Implemented/Tested/Merged/Released. See `changes/c5-profit-contract/DESIGN.md`, `RESULT.md`, `REVIEW.md` and eight impact records/evidence.

**ONE NEXT: owner adopts the exact preserved-gross135/separate-net130 split, or specifies another reviewed meaning. Then execute the specified isolated additive implementation (generated forward-only migration, typed reader/clear labels) and exact-source fresh/populated/desktop/mobile/security/history tests without repeating routine permission.** Remaining C5 network/journey → full independentC6 → ownerC7/verified main/settle five drafts → RC/Pilot remain the fixed path. No early PR closure or broad feature expansion.

All executable/financial/SQL/test-oracle/dependency source unchanged in this documentation-only delivery. No new CI/native run, no transferred acceptance from earlier sources; fullC5/integration=false, C6/C7/RC/Pilot unaccepted. Main220fc206/five original drafts unchanged. Claim6672249212 pauses at final55handoff pending owner decision; no active parallel implementation. No merge/deploy/production/newcost/financial-policy adoption. Earlier state/history below remains exact.

---

## Current — first failed C5 assertion extracted; stored/UI profit semantics differ, 2026-11-06

Read-only diagnosis `C5-FIRST-FAILED-ASSERTION-01`, original executable122d8aa4/native42125234643. Original fresh13460626236 and upgrade13460512159 ZIPs downloaded with newly available artifact capability; SHA256 exactly matches recorded GitHub digests. First and sole false row `desktop_final_day_close_independent_oracle`: ordinal58fresh/59upgrade; all57/58 earlier rows PASS. Stored sales275/collected225/expenses5/debt0/custody0 match. Only realized_profit differs: expected130, actual135, difference5. Prior actual profit-display-after-expense, return/settlement and close_day_success controls PASS. No new native run or executable/SQL/test expectation change.

Full55migration trace and actual independent reviewer confirm last close_day body in20261010223557_enforce_live_account_state.sql (189–274), no later definition/mention. It stores payment-weighted item margin before expense subtraction, with expenses separate. UI app.tsx370 and2546–2553 subtracts expense. Fixture225collected−90allocatedcost=135margin;135−5expense=130net. Confirmed stored/UI semantics mismatch, not proof of missing cash or failed collection. Reviewed decisions/intake do not explicitly select a new persisted-field meaning; neither SQL nor oracle is silently changed.

Diagnosis/extraction verified and independently accepted in scope only. FullC5/In Progress, acceptance blocked, integration=false; fullC6/C7/RC/Pilot pending. Mobile and later network assertion remain unexecuted/unaccepted; blocked-external attempts unresolved. Original ZIP bytes are now durably preserved in this packet (earlier metadata-only notices remain historical). See `changes/c5-journey/RESULT_FIRST_ASSERTION.md`, `REVIEW_FIRST_ASSERTION.md`, `evidence/first-assertion/`.

**ONE NEXT: prepare a bounded contract-alignment design defining whether stored realized_profit is before-expense margin or net after expenses, including UI/API/history compatibility, before selecting and implementing the reviewed resolution.** Preserve the failing evidence and130 expectation while unresolved; any later SQL correction must be forward-only. No approval of a new financial policy or history rewrite is inferred.

Main220fc206/five original drafts unchanged. This publication is documentation/original evidence only, no new CI result claimed for its SHA. Sole/root claim6671950951 pauses at final55handoff; no next active implementation claim. No merge/deploy/production/PR closure/newcost/financial modification. All prior state/history below remains exact.

---

## Current — C5 customer selector repaired/tested; later assertion blocks, 2026-11-06

Existing `integration/g0-g1-reconcile-2026-10-18`. Diagnostic source `a91369a7e628e4d9eeec277a8248cd9894c0c7e0`/native42124180329 narrows the old wait to grouped advanced checkout, after desktop quarter-sale/hidden-response/reload/replay controls. Frozen app picker button includes customer name plus phone/بدون رقم; the old exact button-name selector is incompatible. Corrected `122d8aa4f33ba1e54a08ce90a5c2db16a4ab5560` chooses a button containing the exact customer-name child and retains strict ambiguity failure. Fine checkpoints/count-only sanitized diagnostics remain; no financial assertion/application/SQL/dependency/guard change. Cumulative5source paths only; all55SQL/original23test methods/19browser+3native control ASTs preserved.

Corrective native42125234643:24admission tests and actual2-case customer selector contract PASS in each fresh/upgrade mode (old0/new1 match; independent per-case click required). Actual app journey bypasses the old timeout and later FAILS at coarse `desktop_day_close`, HarnessFailure after58fresh/59upgrade recorded controls (includes setup and may include failed row). Exact failing downstream assertion/expected-observed values unestablished; that stage may remain from earlier actions and is not proof that close_day SQL failed. Last diagnostic counts are earlier sale snapshots, blocked_external2 unresolved and unwaived. Both cleanup/private-file+stack removal/publication and zero unexpected egress PASS. Corrective G0 `42125234639` audit+quality and B1 `42125234641` SUCCESS. Diagnostic G0 `42124180395` SUCCESS belongs only to a91369a7; no result transferred across sources or to later documentation SHA.

Actual separate read-only sale_review accepts diagnosis/selector repair only after source/tests and independent native log inspection; no fullC6/merge approval. Repair **Implemented → Tested candidate only**; fullC5/In Progress, acceptance blocked, integration=false, C6/C7/RC/Pilot pending. Main220fc206/five drafts unchanged; recovery77/77 and earlier evidence retained without rerun. See `changes/c5-journey/RESULT_SALE_SELECTOR.md`, `REVIEW_SALE_SELECTOR.md`, `evidence/sale-selector.json`. Raw artifact references/digests are metadata, not newly archived ZIP claims.

**ONE NEXT: identify the first failed downstream control from saved safe journey evidence, then compare expected/observed UI/API/stored values against the approved contract. Add only a bounded assertion identifier if needed, retain failures and all financial/network assertions, then correct the measured cause and verify affected fresh/upgrade desktop/mobile paths.** Do not infer the cause from the coarse stage, waive a gate or repeat an unchanged run. Fixed path remains C5 → independentC6 → ownerC7 → RC/Pilot.

Sole/root pauses this bounded batch after final55handoff; no next active execution claim. No merge/deploy/production/PRclosure/newcost/core-financial-policy action. All prior complete state/history below remains verbatim.

---

## Current — C5 inventory repair tested; actual desktop sale timeout blocks, 2026-11-05

Exact executable `14f00488bba4b2ad0b08103444c2521d6c6585e5`, existing `integration/g0-g1-reconcile-2026-10-18`. Native C5 `42112588038` reaches the actual app journey in both fresh and populated54→55 modes. The old unexpected cache-path digest identifies `supabase/.temp/cli-latest`; CLI discovery now runs outside the source checkout. Strict source guard unchanged; no cache ignore/deletion/waiver. Only workflow/test/declared manifest identities changed; all55SQL/application/dependencies/old21test ASTs preserved. Local and each native admission23/23 PASS; native497protected/55migrations/reviewedHEAD PASS. Independent read-only reviewer accepts this inventory correction only.

The full journey remains FAILED/BLOCKED: `desktop_sale` TimeoutError after18fresh/19upgrade setup/behavior controls. Exact waiting locator/runtime cause remains unestablished; no financial defect or successful financial scenario inferred. Populated seed/forward upgrade, both cleanup/publication/private-file+stack removal and zero unexpected egress PASS. B1 `42112588006` SUCCESS. G0 `42112587955` audit and quality SUCCESS (all executed required steps pass or normal conditional skips); results belong to executable14f00488, not later documentation commits.

Inventory correction **Implemented → Tested candidate only**. FullC5/integration acceptance=false; full independentC6/C7/RC/Pilot pending. Main220fc206 and five drafts27/35/39/49/50 unchanged. Existing recovery77/77 evidence retained, not rerun. Report/review/safe receipts: `changes/c5-journey/RESULT_INVENTORY.md`, `REVIEW_INVENTORY.md`, `evidence/inventory-repair.json`. Raw artifact IDs/digests are linked metadata; no downloaded ZIP archival claim.

**ONE NEXT: diagnose the exact desktop_sale waiting step/locator/runtime state using bounded safe receipts and the existing private-publication scanner; retain the failing assertion, fix only the proven cause, then verify affected fresh/upgrade desktop/mobile paths.** Do not repeat an unchanged run, waive identity/isolation gates or change core financial contracts. Then fixed full-journey → independentC6 → ownerC7 → RC/Pilot.

Sole implementer/root pauses this completed inventory batch at handoff; no concurrent implementation claim remains active after final55handoff. No merge/deploy/production/PRclosure/newcost/financial-policy action. Prior complete state/history below is preserved verbatim.

---

## Current — C5 independent logical recovery/replay PASSED; fixed-plan step2 next, 2026-11-05

Exact tested a88d4fba6942500d3c999b1475961bff8d652501, integration/g0-g1-reconcile-2026-10-18; native41993105090 SUCCESS fresh and populated upgrade.77/77 checks each: complete selected rows/application catalog/owners/ACL/RLS/schema/database/all remaining metadata/roles/cron definitions, oldest inactive saved-key atomic denial, active saved-key original-result replay/no effects, active foreign denial, payload-conflict denial, new payment replay and exactly one effect, source unchanged and private dump/roles/ACL companion/target cleanup.1039TOC entries exactly once;8scoped owner grants restored; SQL-role only, not restored HTTP/Auth/password/key/PITR acceptance.

Root cause measured at diagnostic56ce610e2a7286c2c0a461cfe26094dba484b42a/41992098519: sample SELECT succeeds, subject matches, canonical actor_is_active=false; original_replay denied42501/account_inactive. Harness incorrectly treated the oldest intentionally blocked actor's saved request as a positive. That original request is now a mandatory negative; no unban/account-state/security/financial SQL/migration change.10eligible saved requests:9active/1inactive; oldest selected for denial. Failed diagnostic evidence retained.

G041993105190/B141993105424 SUCCESS;97unit/300expectations,0lint errors/15warnings,audit{},485protected/55migrations/prior manifests unchanged. Local69safety cases,61prior diagnostic test methods AST-preserved. Collection before restore108/111PASS; intentional-failure34controls per path, publication and zero unexpected egress PASS. Available CLI advisor on disposable source:45WARN (43auth_rls_initplan,2multiple_permissive_policies),0ERROR; not independent G1 reacceptance.

Independent recovery subtask **Implemented → Tested candidate only**. Fixed-plan step1's scoped lab blocker closed; fullC5/In Progress, integration_accepted=false, C6/C7/RC/Pilot pending. No independent C6 review or Merged/Released claim. Main220fc206/five drafts27/35/39/49/50 unchanged; #50 tracking only. No merge/deploy/production/PRclosure/newcost/core financial-policy change.10original ZIPs/digests preserved; results attributed only to executable a88d4fba6942500d3c999b1475961bff8d652501.

**ONE NEXT: Step2 of the fixed delivery plan: close gaps in the full C5 financial journey. Map and reuse existing evidence; verify actual desktop/mobile UI → API → database with independent expected amounts for fractional sales, full/partial collections and debt, courier delivery/custody/settlement, returns/stock, concurrency/replay/lost replies, authority and tenant isolation. Run only uncovered or affected checks on the fixed acceptance candidate; then independent C6 → owner C7 → RC/Pilot. Delivered is not Settled. Do not rerun all historical suites or claim restored HTTP/Auth/password/key/PITR acceptance from this SQL-role drill.**

Prior current notices and fixed-table step1 pointers below are preserved history and do not override this current step2 selection.

[Phase5 result and evidence](changes/c5-restore-independent/RESULT_PHASE5.md).

---

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

## SEC-DEP-20261029 — dependency remediation and affected G0 checks passed on candidate, 2026-10-30

Owner explicitly authorized package-name/version disclosure to npm (55/6509972254), resolving the prior automatic review blocker. Existing integration tested executable 5dcc330ee5c43cbd76b3e33f3e854ca8b009f9c7/tree7f1d37b57f31e93cfc96a9bdb38786bae1a3245d; main220fc2066b4d6254b1803b5e32919c47d60a9c7e and original five financial drafts unchanged. Official seroval1.6.11/node-server2.1.3 with generator-owned lock (2/1099records changed), unchanged age rule/vendor; no suppression/manual lock edit.

Final IntegratedG0 40967812727 SUCCESS quality+supportedBun1.4audit(raw{}actualexit0), B1compat40967812714 SUCCESS, SECcontracts40967812725 SUCCESS. Normal frozenBun1.2.14 consumer, C414identity/all54SQL/frozenA+B, B29+C18mutationtests,94unit291expectations, types/lint0errors13warnings, actual callback10+7/bridge3/clock4+2controls, browser containment/financial-readUI, both builds/source invariance pass. Earlier request-boundary40966773248/B7regressions40966773290 pass ondb4; unchanged dependency/control blobs verified, not rerun claimed. Failed AST comparison/formatter/clock harness runs and final receipts preserved in changes/sec-dep-20261029.

Only test harnesses/explicit C inventory extended for known C2; all application src/54SQL/frozenA+B/originalB verifier/tests preserved byte-exact. Full C financial/production acceptance and independent review NOT performed. Incidental originalG1runtime40966773360 FAILED old exact41_migrations contract; environment and complete cleanup passed, public artifacts retained. This remains an open integrated-C5 target/migration contract, not waived or retried unchanged. C3 legacy sale stays revoked; current UI/typeddb still needs C4 idempotent bridge. overall integration_accepted=false.

ONE NEXT: C4/FIN-03 durable unresolved sale identity and typedRPC/UI transport/outcome bridge, preserving fractions and server idempotency; then C5 integrated54schema/browser/restore acceptance, C6 independent financial/security/dependency/source review, C7 owner merge decision. No merge/deploy/production/newcost/newPR/closure/historyrewrite. Old notices below are historical.

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

> Deferred Low — OC-EVID-02 historical naming/count precision: retain old reports and explicit current denominators; future documentation cleanup only. Not a new product fix or additional acceptance gate.

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

> CURRENT — B4 / APP-02 technically accepted on integration only; delivery 2026-10-22 (native tests 2026-10-21).
> Exact executable `f3b702440a4ffd17038f3c668a2f446620a97919`, tree `6bc91e3b942dccfa5beab67b57f0c22c15b78917`; accepted main remains `18700dee8ecdda2e457c0aa18c4f83a81b042019`, where B corrections are absent.
> Native39614265434: fresh50 has206 passing controls; populated47 baseline53 reproduces old-handler failures; corrected50 has169. Frozen compatibility passes76 original tests plus22 signed-handler tests, types/lint/wire/build/generated-file invariance. Both disposable stacks are removed. Each artifact retains45 advisor WARN and0 ERROR; no clean-advisor claim.
> Independent final review accepts APP-02 only and completes the scoped B4 technical review. Formal current-head verdict: **Changes required**, because DEP-20261021 High and the preserved A source-manifest barrier remain open. No whole-B/B5/B6/RC/release acceptance.
> Current source identity358 protected paths/50SQL;349 of350 prior protected paths and all47 original SQL remain exact, with only the intended old webhook route replaced. Applied48/49 remain exact; CLI-generated50 changes only application refusal SQLSTATE40001 toP0001. Dependencies/signature helper/B2/B3 protections remain unchanged.
> ONE NEXT: separately claim dependency remediation and B source-identity reconciliation, then satisfy B5/B6 under canonical #70/comment6263266625. No suppression, manifest weakening or inherited-A waiver.
> No merge, deployment, PR closure, provider call, production operation or new spending;20 original draft heads/bases remain unchanged. B4 claim #55/comment6312231207 is completed/released through the final handoff in #55; no next execution claim is implied.
> See `changes/b4-app02/RESULT.md`, `COVERAGE.md`, final native evidence and `review/FINAL_B4_REVIEW.md`. The docs-only publication SHA and independent preservation receipt are recorded in #55 after publication, without altering tested source.
> This notice supersedes older CURRENT / ONE NEXT notices below; historical evidence follows unchanged.

> CURRENT — B3 / AC-02 runtime verified on integration only, 2026-10-21.
> Exact executable `117f59289a01c56aeb764be27acfbb45663ec439`; accepted main remains `18700dee8ecdda2e457c0aa18c4f83a81b042019`, where B2/B3 are absent.
> Native39568502042: fresh47 has240 passing controls; populated46 baseline52 reproduces client trial/billing writes and entitlement-helper bypass; corrected47 has211 passing controls. Existing346 protected paths and46SQL are exact; current350/47. Legitimate onboarding/settings/default14day trial and trusted service rights remain supported.
> Independent scoped review accepts AC-02 and completes B3 technical review. Formal current-head merge outcome: Changes required due to DEP-20261021 High; no package-B merge/RC approval.
> General merge blocker DEP-20261021: current G0 full audit exits1 with8 distinct advisories/3 High on unchanged dependencies. The old A manifest also rejects the B protected-source superset. No audit/identity waiver or whole-B/RC acceptance; B4/B5/B6/B7 remain open.
> ONE NEXT: B4 / APP-02 subscription-event persistence acknowledgment, no real provider calls. Resolve current dependency findings and source-identity reconciliation before B5/B6 final acceptance.
> No merge, deployment, new/closed PR or production action;20 original draft PR heads/bases remain unchanged. Claim #55/comment6311099521 is completed/released at final handoff; no new execution claim implied.
> See `changes/b3-ac02/RESULT.md`, `COVERAGE.md`, `DEPENDENCY_AUDIT_BLOCKER.md`, native receipts and independent review.
> This notice supersedes older CURRENT / ONE NEXT notices below; historical evidence follows unchanged.

- [x] B3 / AC-02 bounded client INSERT/UPDATE correction: exact source117f, fresh240/upgraded211 and baseline52; scope-specific review result in packet.
- [ ] DEP-20261021 / High general merge blocker — current implementation stream must remediate/report actual reachability and rerun full current audit on the final candidate before B5/B6; no suppression or inherited-A waiver. See changes/b3-ac02/DEPENDENCY_AUDIT_BLOCKER.md.
- [ ] B4 / APP-02 ONE NEXT under the canonical #70/comment6263266625 plan; fresh repository/head/claims check before implementation.

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
> See `changes/b1-composition/RESULT.md` and `changes/b1-composition/INTAKE.md`; the full original B71 document is archived beside it as `historical-B71-TASKS.md`. Existing A history follows unchanged.

## FOUNDATION-A — A1–A8 complete on main; B1 next, 2026-10-20

- [x] A8 owner approval received and PR72 merged at0c138a970a03d00084631f1fe51fd3713c424874, preserving additive history and the exact approved tree.
- [x] Verify actual main coverage before settlement:288source identities/modes,manifest/41SQL,28original documents,PR48matrix18/18,78acceptance files/77hashes;51–54heads are ancestors. Post-merge Quality39448069522 SUCCESS.
- [x] Settle all8Arequests:72merged;51automatically merged via72;32/33/48/52/53/54closed superseded/incorporated with evidence. Actual open count28→20.
- [ ] B1 next: reconcile existing56–71 chain over accepted A, inspect sibling67 coverage and preserve A security/dependency/runtime guards. Use existing71; no new feature expansion. B2–B7 and C1–C7 remain as in the canonical70plan.

Completion receipts: docs/foundation-a-merge-2026-10-20. The frozen source51 acceptance capsule and historical failures remain unchanged. Current documentation-only checkpoint/claim disposition and main Quality are recorded in55/70. No deployment, production mutation, new policy/spending or B/C merge approval. No active implementation claim is implied by the next-task entry. Earlier pending A8 entries below are historical.

## FOUNDATION-A — final A8 candidate51, 2026-10-20

- [x] A1–A6 requirements and current-source acceptance: source51b09a6f33a672704f8424cbf2bbed7a2be682ca, G0run39444611013/G1run39444611354 attempt1 SUCCESS. Native43read/10UI/40G1,full audit/frozen/lint/typecheck/build/generation/identity/cleanup receipts retained. The application is unchanged from reviewed421; stored close_day remains truthfully onfabb with its independent arithmetic bridge.
- [x] A7 current source51 supplemental review: Approved for human merge within A. Historical esbuild workflow's accidental current-head rerun is corrected by manual fixed73e133 proof, without changing assertions or weakening current gates; original failure39396201730 retained. Exact source/main inventory865paths and eight-PR coverage are durable.
- [ ] A8 protected owner decision: merge existing PR72/package A only after final automatic Quality and source-preserving documentation confirmation. Verify each coverage row on main, settle all8requests and update open count; then B. No closure based only on branch tests.

ONE NEXT is that owner merge decision. Exact final publication/PR head, PR checks, independent preservation confirmation and claim6286335135 release are recorded at final55/70handoff. main43d6edb unchanged;28open. B1–B7/C1–C7/overall integration/release remain pending. Earlier state below is retained history, not the active ONE NEXT.

## FOUNDATION-A — A1–A7 source acceptance complete; A8 owner decision, 2026-10-20

Authoritative checklist70/comment6263266625, same integration branch, package representative PR72. Executable source421774f4bb2f6e541be8ca03faf3714e7c81bab8. Actual commands/results, failures, source provenance, independent review and rollback are in docs/foundation-a-acceptance-2026-10-20. Documentation publication and PR head are recorded in55/70; main43d6edb remains unchanged.

- [x] A1 APP-01 incomplete financial reads: preserve cached known amounts with status, require complete reads for healthy zero and dependent actions; missing-customer protection retained.
- [x] A2 APP-03 fetch actual trial expiry and distinguish loading/error/expiry without changing trial policy.
- [x] A3 APP-04 refresh day/zone basis and memo dependencies; actual stored close_day nonempty three-zone proof plus unchanged final arithmetic/SQL and independent bridge. Unknown settings protect daily summaries/close/Pilot, while debt/collection/week/month remain independently available.
- [x] A4 CI-1 fail on Git discovery errors, cover six source extensions and real lint failures; terminate ESLint options before path arguments. Original failing controls preserved.
- [x] A5 preserve all eight requests:28original historical Markdown files from32/33; PR48 matrix7exact/11reconciled;52/53dependency/security and54isolation lineage preserved; full source delta vs main saved.
- [x] A6 final421 native G0/G1 pass:43read/10Chromium/40G1, frozen/audit/full lint/typecheck/build/generation/288blob/41SQL/cleanup evidence retained. No promotion of old823results.
- [x] A7 independent focused source review: all three in-scope blocking findings repaired and independently reverified; verdict Approved for human merge within A. Final docs preservation receipt accompanies the publication.
- [ ] A8 owner decision: merge PR72/package A only after explicit permission. Verify accepted source/coverage on main, then settle all8requests and update actual open count. No request closes based solely on branch tests.

ONE NEXT: the A8 owner merge decision after current PR Quality/docs checks. Routine preparation updates existing72 without new PR/history rewrite; no auto-merge/deployment. Claim6286335135 is released in55at handoff, with no hidden execution continuing. B1–B7 and C1–C7 remain pending; the older32financial design acceptance stays C5, not satisfied by the bounded close_day probe. Overall integration/release acceptance remains false. Preserve rollback/failure history and all owner-controlled merge/policy/spending boundaries.

## FOUNDATION-A checkpoint — 2026-10-19

Standing owner instruction: finish the existing28PRs through A8/B15/C5; no routine reconfirmation, protected merge/deploy/policy decisions remain owner-only. Canonical simple-store-aid on naderalhaje097070-sudo.

- [x] A1 APP-01 candidate source preserved;34actual-source local read cases pass.
- [x] A2 APP-03 candidate source preserved;13query/projection/billing cases pass.
- [x] A3 APP-04 candidate source preserved;4stable-data clock/timezone cases pass.
- [x] A4 CI-1 candidate source preserved;5Git/real-ESLint cases pass.
- [x] A5 candidate regression wiring,288-path snapshot and unchanged41SQL/package/lock reconciliation recorded.
- [ ] A6 exact fabb481 native G0/G1/browser/build/generation evidence; queued runs39281934875/39281934868. Stored isolated close-day result comparison also remains.
- [ ] A7 fresh independent review including updated runtime compatibility proof; no self-approval.
- [ ] A8 owner merge decision, then evidence-backed disposition of A's8PRs.
- [ ] B15andC5 remain queued under70/6263266625; no accepted closure/release claimed.

ONE NEXT: A6 only. Full report and actual failure/success receipts in docs/foundation-a-2026-10-19. Local browser403block and nonlocked build/invariance limits are explicit; do not reuse823native PASS for changed source.

## REVIEW-ALL — 2026-10-19

- [x] Complete fresh independent scoped reviews and28PR source/dependency ledger. Outcome: **Changes required**; no merge/release approval. Reports: docs/integration-g0-g1/reviews/2026-10-19.
- [ ] **ONE NEXT: FIN-READ-FAIL-CLOSED-01 / APP-01 High.** Propagate financial read loading/error/completeness; retain known cached amounts with clear status; no healthy zero/no-debt state for incomplete reads. Actual container/screen regressions, no formula change.
- [ ] APP-02 High before paid billing: durable, error-aware, retryable/idempotent webhook persistence; no200after failed required work. Test partial failure, replay, event order and environment separation.
- [ ] FIN-01 High: decide/enforce whole-unit quantities or approved fractional inventory; prove persisted stock/line/return reconciliation on fresh and populated upgrade.
- [ ] FIN-02 High: forward integration migration preserves both canonical courier transitions and live-actor checks; same effective body/ACL on fresh+upgrade; reject backward state/custody decrease without settlement.
- [ ] FIN-03 High before Idempotency acceptance: unresolved logical sale key survives30minutes/reload/ambiguous result; explicit reconciliation/new-operation lifecycle; real isolated single-effect tests.
- [ ] APP-03 Medium: truthful trial projection, loading/error/expired states.
- [ ] APP-04 Medium: day-close timezone/date memo inputs and parent dependencies; compare preview with stored close.
- [ ] AC-01 Medium: scanner trusted-caller/admin guard survives SECURITY DEFINER; preserve approved service/cron and inactive-account denial.
- [ ] AC-02 Medium: reserve trusted billing/trial columns, including onboarding INSERT; trace consumers before claiming paywall protection.
- [ ] CI-1 Medium: fail changed-file discovery on git errors; preserve valid no-source diffs and all six source extensions.
- [ ] Compose accepted account/financial candidates, then prove one frozen RC: fresh/populated upgrade, concurrency, restore, operations and Pilot gates. No merge/deploy/closure approval; integration_accepted=false.

Five High and five Medium distinct findings; the financial peer addendum does not double-count FIN-01/02. Exact source, evidence levels, actual tests, rejected hypotheses and rollback/limits in the four reports and findings.json. Native G0/G1 remain valid on823cbcaf only. Historical records below are preserved.

## INTEGRATION-RESUME checkpoint — 2026-10-18

- [x] Candidate-only G0: native full lint0errors/13warnings and fullaudit exit0 on823cbcaf; locked contracts/types/generator/build invariance and mjs/cjs coverage; run39172903511.
- [x] Candidate-only affected G1: native40/40, stable279source/41SQL,22data fingerprints, fixed counters, full traces/secrets/cleanup4/4; run39172903470. Historical failed39/40 preserved; exact old observer error unknown.
- [ ] **ONE NEXT / Gate6:** fresh independent adversarial review of823cbcaf and inheritedDraft72 scope using docs/integration-g0-g1/REVIEW_REQUEST.md; no implementation self-review accepted as independent. Resolve findings before merge proposal. Current original72/main unchanged.
- [ ] After review, traceable promotion to existing72 without a duplicatePR; protected main merge/deploy still owner-controlled. No PR closure until accepted coverage documented.
- [ ] Reconcile downstream account-chain/G2; old54preissuedbannedJWT access remains known here. Preserve prior59–71 evidence without claiming integration on this candidate.
- [ ] Financial49/50 + October effectiveRPC/ACL/RLS: fresh and populatedupgrade, independent persisted balances, duplicate items/retries/concurrency/partialfailure/returns/settlement/storeisolation; preserve Sale≠cash and Delivered≠Settled.
- [ ] Review13visible lintwarnings (10refresh,AddProductSheet initial/app tenantTz Hooks,1unuseddisable); Hooks not declared harmless. Track inherited build/precache/offline/performance warnings beforePilot.
- [ ] Restore/operations/provider/subscription/retention decisions and fullsingleSHA RC/Pilot gates remain unverified; integration_accepted=false.

Report/rollback/source and sanitized receipts: docs/integration-g0-g1. Historical records below retained; this block supersedes older ONE NEXT selections.

## G0-LINT-FORMAT-03 — bounded batch, 2026-10-18

- [x] Ten accepted handwritten files117formatter→0/0warnings; no new whole-repository classification/count. Saved ranking reused; guide unmodified/excluded after failed method proof, onboarding replacement freshly linted. Initial133 not final117; raw baseline assembly/failures preserved.
- [x] Exact pinned formatter/source-types/runtime/comments/meaningfulJSX proof and independent nine-control review PASS; suppressions2+2 unchanged/not approved. Existing completed/app/generated/dependency/config/tests/workflow bytes fixed.
- [x] Local frozen/typecheck/targetlint PASS; unchanged native Quality39123211326 SUCCESS on8916bec5ed6f14159b9323d860ee388b3b485a27, all19steps success perAPI. Rawlog download exit1/0bytes/no establishedHTTPcode; native counts/runnercheckout not claimed, no rerun. Current synthetic tree equals source, not actual merge.
- [x] Source/claim reconciliation before upload, sole claim55/6249300481; final docs-only delta/manifest checked and linked70/55delivery/closure recorded there. No G1/historicalsecurity/audit/merge/deploy.
- [ ] Lower saved formatter candidates, guide proof, mixed rules/Hook warnings/inherited suppressions/generated/.cjs and G0/finalsource/affectedG1/integration/release acceptance remain open. No remaining global total inferred.

Report/table/exclusion/evidence/review/rollback in docs/g0-lint-format-03. Additive restore only ten accepted paths from3b4a312 to withdraw, preserving prior fixes. ONE NEXT belongs to planning remaining bounded cleanup, then stable-source identity/affectedG1. Stop after delivery; older checkpoints retained as history.

## G0-LINT-FORMAT-02 — bounded batch, 2026-10-18

- [x] Saved handwritten ranking reused, no global reclassification. Fresh five-file diagnostics186formatter→0, other errors/warnings0→0; files/counts in docs/g0-lint-format-02/REPORT.md.
- [x] Exact locked formatter/source-type/runtime AST/meaningful JSX/comments/idempotence proof, unchanged inherited suppressed diagnostics and independent batch review. app.tsx and generated files excluded; no application tests/workflow/config/rule/dependency changes.
- [x] Local frozen/typecheck/targetedlint PASS. Existing native Quality39121437943 SUCCESS on dcd3688de41cd3aef422eb22792566c9b9434d10; all steps metadata successful. Native raw-log download failed, exact native counts/checkout not claimed; current synthetic tree equals source, no actual merge.
- [x] Sole claim55/6248999708 after live head/claim verification; final docs-only source reconciliation and linked55/70 handoff/closure recorded there. No merge/deploy or G1/advisory/audit rerun.
- [ ] Remaining lint/.cjs/generated/other-rule work and G0/final-source identity/affectedG1/integration/release acceptance remain separate/open. No whole-project remaining count inferred from186.

ONE NEXT: planning chooses remaining bounded G0 cleanup after this handoff. Additive rollback restores only the five table paths froma9915102 and preserves all earlier security/UI fixes. Stop after delivery; no next batch automatically. Historical checkpoints below are retained.

## APP-DEBT-MISSING-CUSTOMER-01 — bounded candidate delivered, 2026-10-18

- [x] Owner-authorized missing-customer UI remedy on existing Draft72: executable82623c7189de21c0a03c5e4b3b6539ff5c74320e; known debt60 retained, clear loading/unavailable states, invalid navigation/collection blocked, no invented ID/zero.
- [x] Before-fix actual React/Chromium reproduction; local9/9 + independent9/9 regression; affectedlint0errors1useMemowarning/typecheck/66unit/8wrapper/67containment/twoisolatedbuilds/generationinvariance.
- [x] Existing Quality39120188797 SUCCESS, every required step successful per API; native raw-log storage403 and count/checkout evidence limits explicit. Current synthetic tree equals tested source, no actual merge. No app/test changes after source826.
- [x] Source/claims reconciled after API recovery before upload; sole claim55/6248860942. Linked55/70 handoff carries final documentation head and closure; no merge/deploy.
- [ ] Main-branch/integration/release acceptance NOT granted. Remaining lint/.cjs coverage and separate incomplete invoice-read handling remain open. No G1/historical advisory/audit rerun.

See docs/app-debt-missing-customer-01 for actual source/evidence/review/rollback and changes/app-debt-missing-customer-01 for scope. New component tests are standalone, not wired into unchanged CI. ONE NEXT: planning chooses remaining bounded G0 lint; no automatic expansion or source/G1 reconciliation in this batch. Older missing-customer deferral below is historical; this candidate supersedes it only within the reviewed UI scope, not on main.

## Current queue checkpoint — G0-APP-LINT-01, 2026-10-17

- [x] Bounded draft candidate removes17app errors(16any+1expression), retains1useMemo warning; actual types derive from existing contracts, no financial calculations/calls/Hook deps changed.
- [x] Source e58bc5db7e09defe9a07011ae712c484d5778301/appblobde992dbc; Quality39072945731 attempt1SUCCESS: frozen/typecheck/changedlint/66unit174expect/8wrapper/67browser/twoisolatedbuilds/generationinvariance. Synthetic checkout tree equals source.
- [x] Independent focused review/replay and exact before/after/raw evidence/rollback in docs/g0-app-lint-01; no new source blocker for this bounded lint candidate, wider approval remains Changes required.
- [ ] **Separate existing Medium: APP-DEBT-MISSING-CUSTOMER** — DebtsScreen find can return undefined for a visible debt row; click fails TypeError before navigation on both versions (new explicit diagnostic message only). Decide loading/missing/deleted-customer behavior and add targeted regression independently. Never silently drop debt rows/totals or assert an unproved invariant. No behavioral fix in this batch.
- [ ] Existing useMemo tenantTz warning, remaining whole-repo lint and .cjs coverage remain separate. No new global count;887 was previous baseline only.
- [ ] G0/final-source reconciliation/affectedG1/integration/release acceptance remain open; source54 guard unchanged. No automatic G1 or merge/deploy. Main/production and dependencies/lock unchanged.

ONE NEXT: planning reviews this bounded handoff, selects remaining lint work and disposition of the separate missing-customer finding; stable-source identity/G1 follows cleanup. Final head/claim closure in #70/#55; stop after handoff.

## G0-LINT-FORMAT-01 — bounded formatter candidate, 2026-10-17

Owner-approved one-file formatting on Draft72: intakeff7a0daa; preparation source6e1bb937 / post-format appblobbd154115c1e782521fe4299cc7cc558e88eafff7; published3c6d611ce3f616c2c519a3acdc2a9f743837fab2 tree059dcc3cdd4898b0ae9c463159fd6ffae97fe783 equals reconstructed preparation tree+that app. LockedPrettier3.8.3 only in src/routes/_authenticated/app.tsx. Current full lint1210→887errors,13warnings unchanged; prettier1148→825, app323→0format with17othererrors/1warning unchanged. Source/type/runtime JSX AST/comments and all other diagnostics preserved; no types/Hooks/logic/rules/ignores/dependencies/lock/esbuild exception/generated-source change.

Preparation39071094844 SUCCESS: frozen1.2.14/typecheck/66unit174expect/twoisolatedbuilds/post-generation blob invariant. Published-source Quality39071253858 **FAILS** at inherited17nonformat app errors; frozen/typecheckPASS, subsequent stepsSKIPPED. Do not credit preparation results to skipped Quality steps. First comparator failure retained. Independent focused review finds no introduced formatter blocker; broader acceptance Changes required. Full raw archives, receipts, actual logs/review/rollback: docs/g0-lint-format-01. Temporary preparation workflow retired; final metadata-only identity in70/55/PR72, no native final-doc-head run claimed.

G0/integration remain open for lint, .cjs coverage and final-source reconciliation/affectedG1 later. No historical security or liveG1 rerun; source54guard/manifest, finance/account/SQL/main/production preserved; no merge/deploy/newPR/billing change. ONE NEXT: planning selects next bounded lint batch from current inventory; stabilize cleanup before identity reconciliation/G1. Claims55/6233216181 and6233219827 close at linked final70/55 handoff; stop.

## G0-ESBUILD-COMPAT-PROOF-01 — bounded candidate tested, 2026-10-17

Owner explicitly authorized exact esbuild0.28.1 override beyond unchanged mcp-js0.20.1^0.27.0; this is project compatibility evidence, not publisher support. Start1b7a1a01; tested source73e133b25a8a5167c6730eb82cf364268ad44373/tree0704600984e277d6090d87c5d3c53777f6cf86f7. Official complete Bun1.4-generated lock8db84562 changes only esbuild+26platforms plus override; all prior security fixes/SDK/app/SQL preserved. Final delivery identity is in70/55/PR72, documentation/evidence plus one no-behavior EOF blank-line restoration in the retired SEC-CI workflow after tested source; app/graph/test bytes unchanged.

Native Windows0.27.7 baseline39025616246:5cases3PASS/2specific traversalFAIL, rawexit1/controller0. Final Windows and Linux39026053191 each5/5, clean frozen1.2.14, real resolved/native versions,57officialMCPfilehashes/wholegraph/source invariance pass. Linux3actual MCP generator/CLI contracts,4adapter/SDK contracts,11guardcontrols/affectedlint pass. Quality39026056460 SUCCESS:66unit/174expect,8stubwrapper/67dummybrowser,typecheck/changedlint/twoisolatedbuilds/post-generation sourceinvariance. Synthetic Quality checkout tree equals tested source; not actual merge. Full supported audit raw{} exit0; exactly last esbuild advisory removed/no new. Missing-rg preparation and new-fixture formatting failures retained. docs/g0-esbuild contains report/raw/source/run/review/rollback.

Targeted dependency advisory item proved on draft only. G0/integration remain open: inherited full-repo lint not accepted, liveG1 not rerun, source54 fail-closed identity guard/manifest untouched; final-source reconciliation and remaining affected runtime/transport/SSR/auth/isolation/state/counter/secrets/cleanup proof need separate packet. No finance/account/SQL/production/main/merge/deploy/fork publication or billing configuration changes. ONE NEXT is planning that remaining evidence packet; close current claim after70/55 handoff and stop.

## G0-MCP-JS-COMPAT-01 — official decision checkpoint, 2026-10-17

Completed the owner-authorized read-only version investigation using exactly one diagnostic run39011125934/attempt1/SUCCESS on56170b8792337649458c3cbb6bc1aee7a8d03bc3. Official HTTP200 metadata contains33 newer stable+48 newer prereleases; all81 requireesbuild^0.27.0 and reject published patched0.28.1/0.28.2. No compatible official candidate exists in this captured snapshot. No candidate archive/install or binary comparison was performed. docs/g0-mcp-js/REPORT.md and exact raw official-inspection.zip preserve receipts, commands, source/run/artifact identity and limits.

Project package/lock and all prior security floors remain unchanged. Diagnostic trigger and temporary scripts are retired in this delivery; normal SEC-CI workflow restored to0540e266. No Quality/G1, finance/account/SQL, main, merge/deploy or billing configuration change. Decision investigation complete; remediation/G0/integration remain blocked. ONE NEXT for planning: a separately authorized design/source-inspection packet for a narrowly scoped parent contract patch/upstream option, not broad mcp-js/SDK upgrade or silent override. Stop after55/70 handoff.

## Current queue checkpoint — G0-NODE-SERVER-01, 2026-10-16

- [x] Existing Draft72 adapter1.19.14→1.19.15 only; official npm availability/tarball/fix and SDK1.31.0/Node/Hono compatibility proved. No2.x/SDK/app upgrade. Paired constraints and generator-owned complete lock1a0791b4 preserve all other graph records and prior fixes.
- [x] Native Windows old baseline8 cases,6PASS+2specific securityFAIL; patched Windows8/8 and Linux8/8 on tested15688194725fdb2c25e53d55d63cfe605295ec68. Actual installed adapter/SDK HTTP/errors, all-copy inventory, frozen/graph,10 Bun guard controls/affected lint/source invariance pass. Harness encoding/lifecycle/checkout failures retained, no weakened oracles.
- [x] Source Quality38952653426 SUCCESS65unit/145expect,4 MCP,8wrapper,67dummybrowser,typecheck/two builds; matching synthetic tree. Independent review with actual replay limits and complete raw evidence in docs/g0-node-server.
- [x] Full supported audit removes exactly target GHSA-frvp-7c67-39w9; only esbuildLow remains, no new/CH. Raw exit1 and audit jobFAIL preserved; no G0 waiver.
- [ ] G0 acceptance: separate esbuild remediation/disposition and inherited lint work remain. No current full-repo lint total inferred.
- [ ] Integration on final lock: explicitly reconcile unchanged source54 identity guard/manifest and rerun affected actual runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof. Old40/40 is historical, not this lock's evidence; no automatic live G1 run.
- [ ] Merge/release/production/finance/account/migration changes are not authorized or performed. PR48 remains open.

ONE NEXT is planning of a separate remaining G0 task while retaining G1 prerequisites. Sole claim55/6222380561 closes in final linked #55/#70 handoff; worker stops there. Earlier queues below are historical.

## Current queue checkpoint — G0-BABEL-01, 2026-10-16

- [x] Draft72 root @babel/core7.29.0→7.29.7; existing safe7.29.7 copies retain version and deduplicate. No Vite/TanStack/Workbox or non-Babel package changes. Approved necessary Babel dependency minima/223path hoisting explained in docs/g0-babel; zero new versions, exact6old removals.
- [x] Official complete lock9d67e2d under paired constraints; all-copy stable7.x>=7.29.6 floor, prior Hono/qs/DOMPurify guards retained. Frozen1.2.14/graph/80parent ranges/9guard controls/affectedlint/sourceinvariance PASS.
- [x] Actual local installed behavior: baseline18tests16PASS/2outside-rootFAIL; corrected6/6 on1deduplicated distribution, all5parents same7.29.7, zero skips. Legitimate sibling/within-package-parent/inline/plain maps preserved; inputSourceMap/config unchanged.
- [x] Audit target removed exactly,2remaining1Moderate/1Low/noNew/CH; rawexit1/job38896279667FAIL preserved. Quality38896289565SUCCESS64unit/141expect,4MCP/8wrapper/67dummybrowser/two builds/typecheck. Tested1e80a33d5f0c766c89259aad9b9db4fce2492fdd.
- [x] Actual separate reviewer static/Python/Node/semver/hash/receipt/log checks saved; no independent Bun/Babel/compiler/browser/DB rerun. No new engineering finding in this batch.
- [ ] G0 acceptance: node-server/esbuild and inherited lint require separate engineering/risk disposition; no waiver/cleanup here.
- [ ] Final-lock G1: explicitly reconcile/review/freeze source54 identity against approved manifest/lock/tests/checkpoints; execute affected runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof. No silent guard expansion or historical40/40 credit.
- [ ] Merge/release/pilot remain protected and unapproved. PR48 open; app/financial/account/SQL excluded.

ONE NEXT belongs to planning: select one separate remaining G0 disposition and preserve G1 requirements. Close sole claim55/6214726307 at linked55/70 handoff and stop. Older queues remain historical.

## Current queue checkpoint — G0-DOMPURIFY-01, 2026-10-16

- [x] Draft72 DOMPurify-only3.4.11→3.4.16 approved paired constraints/generated wholelockd630ca04; no jsPDF/Hono/qs/other graph change. Testeda5edd17a420814133bba559911efb871f4b0633e.
- [x] Optional package actually present on both graphs; installed all-copy+parent contract. Baseline5ordinaryPASS/5specificFAIL, fixed10/10actualbrowserPASS; no inferred app exploitability.
- [x] Real unchanged synthetic invoice PDF110539bytes/1page/1image/exactfilename/UTF8/iframecleanup/network0. IndependentR1 harnesscharset defect resolved without changing assertions or app; retain bothfailedPDF runs and initialnewfixturelintfailure.
- [x] Frozen/graph/8guardcontrols/affectedlint/sourceinvariance PASS; Quality38887419454SUCCESS63unit/137expect,4MCP/8wrapper/67dummybrowser/two builds/typecheck. Full audit exactly3DPIDsremoved,3others2Low/1Moderate/noNew/CH; rawexit1/job38887412161FAIL preserved.
- [x] Independent focused review and actual replay scope saved in docs/g0-dompurify/REVIEW.md; static/Python/Node/hash/rawreceipts/log review, no independent Bun/browser/DB execution.
- [ ] G0 acceptance: Babel/node-server/esbuild advisories plus inherited lint remain separate engineering/risk decisions; no waiver or new full-lint total.
- [ ] New-lock G1 integration: explicitly reconcile unchanged source54 identity guard/manifest against approved final package/lock/tests/checkpoints, then affected actual runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof. No silent allowlist expansion or reuse of old40/40 as this lock's acceptance.
- [ ] Merge/release/pilot: not authorized or performed. PR48 remains open; financial/account chain excluded.

ONE NEXT belongs to planning: choose one separate remaining G0 disposition, preserve G1 requirements. Sole claim55/6202123085 closes at linked55/70hand-off; stop there. Older queues remain historical.

## Current queue checkpoint — G0-QS-01, 2026-10-15

- [x] Draft72 qs-only6.15.3→6.16.0 pins and officially generated lockae751828; no Express/body-parser/SDK/Hono/other package change. Testedfc6d621e955d3666ecc0e7fbc79dd402f39b3ee8.
- [x] Actual installed baseline15cases12PASS/3specificFAIL with rawexit1 retained; patched15/15PASS includes both advisory defects, ordinary parser/serializer and real loopback Express/body-parser compatibility. No mocks/live app/DB.
- [x] Every-copy stable6.x floor and sixguardcontrols including retained Hono floor; frozen/graph/affected-new-test lint/source-invariance PASS.
- [x] Full supported audit: both qsGHSA absent;6others2Moderate/4Low remain, noNew/CH in scan, actualexit1 and38799630354FAIL retained. No fixed residual-count rule or waiver.
- [x] Quality38799635683SUCCESS62unit/133expect,4MCP/8wrapper/67dummybrowser/two builds/typecheck; matching synthetic tree. Independent static/hash/receipt/log review completed, no independent Bun/DB replay; docs/g0-qs.
- [ ] G0 acceptance: six other advisories and inherited lint remain separate engineering/risk decisions. No lint cleanup here.
- [ ] Future new-lock G1/integration acceptance: explicitly reconcile source54 identity baseline and execute affected real transport/runtime/isolation proof, rather than reusing old40/40. Guard remains unchanged fail-closed.
- [ ] ONE NEXT: planning chooses one separate G0 batch/disposition after55/70 handoff. Claim6201151721 closes there; worker stops. No finance/lifecycle/migration/production/merge/deploy.

## Current queue checkpoint — G0-HONO-01, 2026-10-15

- [x] Bounded Draft72 candidate: Hono4.13.7 paired pins and generator-owned lock53af322, no SDK/Lovable/other package changes. Tested e38cf18d007ebaa6f9a9c0e314283a33960d89db.
- [x] All-copy stable4.x security guard plus four negative mutations; frozen/graph/MCP/typecheck/build/environment fixtures verified, Quality38791533893 SUCCESS61unit/129expect.
- [x] Full audit saved: eight targeted GHSA gone; eight others4Low/4Moderate remain, no new/CH in this scan. Final38791526145 retains audit exit1/FAIL. Initial unsupported Bun1.2 audit and manifest-before-lock frozen failures preserved.
- [x] Missing CJS/app measurement:16+41 format errors; app main/current340/1 with matched diagnostics except fix ranges. No full-lint acceptance or code formatting.
- [x] Independent focused review and permanent evidence in docs/g0-hono; reviewer replay is static/Python/hash/raw-evidence, not independent Bun/DB execution.
- [ ] G0 acceptance: inherited lint and eight remaining advisories require separate scoped engineering/risk decisions; no waivers here.
- [ ] Before any future G1 on the new lock: explicit baseline/identity reconciliation and affected-runtime proof. Old40/40 is not promoted; legacy guard retained fail-closed.
- [ ] ONE NEXT: planning reviews this handoff and chooses one next separate G0 batch. No implementation starts automatically. Claim55/6199980098 closes through final55/70 handoff; no merge/deploy, finance/account/migration changes.

## Bounded handoff — G1-EGRESS-TRACE-01, 2026-10-15

Executed affected G1 on dbc870fcc278781b650860273ac4e1116f629f85:38742289056 PASS40/40, cleanup4/4 and zero unexpected native packet delta. Official cf-fetch opt-out removes proved workers.cloudflare.com DNS attempts; same firewall and acceptance, actual-vendor3case fixture PASS. Prior diagnostic+16 and two precredential oracle failures preserved. Quality38742298220 PASS; independent focused review/evidence in docs/g1-egress-trace. No application/financial/account/schema/dependency change. G0/G2 and #48 disposition remain separate, no merge/deploy or release acceptance. Claim6188008835 closes at linked delivery. ONE NEXT planning review only; stop.

## Final bounded result — G1-CLI-CLEANUP-01, 2026-10-15

Implemented/tested on Draft72, not merged/released. Installer now bounded and operational in both new runs; historical root cause unresolved. Absent-user/process-error cleanup oracle fixed with6fixtures and hosted4/4 receipts. Final source819291c85825d73854262d76d2030736470ef92b executes39checks/38PASS; only native zero-outbound conditionFAIL(+16blocked IPv4packets,0IPv6). Full named mismatch+500,after-state/finance-zero/source/secret pass; Quality38702796165 PASS. docs/g1-cli-cleanup/REPORT.md and REVIEW.md hold actual evidence and limits. No G1 acceptance, no G0 waiver, no account/financial imports, no #48 closure, no merge/deploy. ONE NEXT for planning, not this worker: separately scoped emulator-startup attribution under unchanged firewall. Close claim6187165138 at final #55/#70 links and stop.

## Final handoff — G1-ACCEPTANCE-REPAIR-01, 2026-10-14

Existing Draft PR72 retained; main43d6edbccb66fb06ce0fcb93734ad59532d1aeae and original48/51–54 unchanged. Tested source7d30e65c7bfb454fda4bf6bc6224e8510174c200: semantic CI17tests/6safechecks and automatic Quality PASS. Runtime38605846901 CANCELLED during CLI setup before DB/SSR; cleanup receipt3/4, process oracle failed for a user never created. No new liveSSR/after-state/native-counter acceptance. Exact reports, raw receipts and independent review: docs/g1-acceptance-repair/REPORT.md and REVIEW.md. These supersede the intake status below.

Outcome: Blocked pending missing evidence; G0/G1 unaccepted. #48 stays open without formal superseded. All application/auth/dependency/41SQL/financial contracts preserved. Delivery is metadata/evidence only above tested7d; root fingerprints updated explicitly, no executable test change or failure waiver. #55/6173791297 closes only in the final linked handoff. ONE NEXT: bounded installer diagnosis plus absent-user cleanup-oracle proof and exact SSR/after-state/counter execution; no blind version upgrade, account/financial expansion, merge or deploy.

## Current queue — G1-ACCEPTANCE-REPAIR-01, 2026-10-14

Owner-authorized continuation claim #55/6173791297 on existing PR72. ONE NEXT: semantic visual CI proof plus exact named SSR/after-state evidence and independent review only; no unrelated tests, financial writes, dependency updates or blanket formatter. G0 full lint/advisory disposition and known G2 remain open. Do not treat previous root queue/source checkpoints as a new authorization; all prior entries below are historical.

## Current queue checkpoint — PRIMARY-ENV-001 real native runner, 2026-10-10

- [x] Exact PR54 head84c3444 snapshot: all356 blobs match GitHub before/after execution.
- [x] Capable disposable non-root runner; fresh experimental native CLI2.120.0 stack applied41 migrations. No production credentials/data.
- [x] Bun1.2.14 frozen install, Gate4/Auth preflight,60 unit/125 expectations, typecheck/build; matching Playwright1.62.0/Chromium151 desktop/mobile Auth UI passed.
- [x] Two dummy tenant/user metadata checks executed using real user JWTs:22 pass,2 fixture-role conflicts preserved and independently explained by existing owner trigger.
- [x] Evidence/screenshots retrieved with secret redaction; source integrity verified; provider confirms sandbox stopped. No snapshot/public route or financial test.
- [ ] ONE NEXT: independently review the packet and resolve **ENV-NATIVE-01** through a focused account-lifecycle change gate: pre-ban JWT still reads own tenant after Auth ban, despite new login denial. Preserve history and require direct API/RLS/RPC denial proof.
- [ ] Complete broad authorization and matching hosted checks; external native evidence does not approve Docker/CLI2.101.0 CI or replace independent isolation acceptance.
- [ ] Financial write/concurrency/idempotency/rollback suites remain blocked until accepted isolation proof. Prior security/lint/PWA and11Moderate/5Low findings remain open.

Evidence: changes/primary-env-001/NATIVE_RUNNER_VERIFICATION.md and native-runner/. Older queues remain historical.

## Current queue checkpoint — PRIMARY-ENV-001 runner feasibility, 2026-10-10

- [x] Re-read PR54 head `0e616d0013fd72de244686f10c8de5a12488f312`, PR53 base and unchanged main directly from GitHub.
- [x] Cloud metadata: old validation project INACTIVE; organization Free. No accepted schema/data provenance or restore suitability; no cloud action.
- [x] Container prerequisites absent; user namespace creation denied; UID/GID mappings only permit root and non-root transition fails.
- [x] Discovered official native-stack alternative; scratch CLI2.120.0 archive SHA256 verified and actual help inspected. Clean default native bootstrap exits1: PostgreSQL cannot run as root. No database service or migration started.
- [x] Re-read latest Quality job: failure, runner_id0, steps[]. No blind rerun or spending change.
- [ ] ONE NEXT: capable disposable Docker runner using existing CLI2.101.0, or separately evaluated experimental native non-root runner. Execute fresh exact-candidate migration/Auth/tenant/RLS/disabled-user proof before requesting isolation acceptance.
- [ ] Required hosted checks, isolation gate and financial tests remain blocked; existing security/lint/PWA blockers unchanged.

Evidence: changes/primary-env-001/{RUNNER_FEASIBILITY.md,runner-feasibility.json}. Older checkpoints remain history.

## Current queue checkpoint — PRIMARY-ENV-001 Astra remediation, 2026-10-10

- [x] Independent Astra source review resumed; original ENV-A1/A2/A3 findings recorded.
- [x] Shared context guard: redirect/retry blocking, WebSocket interception, exact configured auth/destructive HTTP origins.
- [x] Rereview fixes: exact offline font stylesheet with fallback-font limitation; production-build/no-HMR prerequisites; real positive popup coverage.
- [x] Actual browser regression: original47/36 failing cases; final67/0. Astra independently reproduced67/0 and closed the bounded findings; no overall acceptance.
- [x] Changed-source Gate4/lint and seven Python/shell/YAML/diff checks; final source/evidence fingerprints saved in existing draft PR54.
- [ ] ONE NEXT: provision a capable isolated runner, then validate fresh local stack/migrations and production-built Auth/tenant/RLS/disabled-user behavior on the exact candidate.
- [ ] Matching Playwright browser/hosted required checks: current local substitute browser is explicit; GitHub quota/spending startup remains blocked. No blind retries or account spending changes.
- [ ] Financial acceptance after isolation gate: stored values, stock/custody/transaction boundaries, concurrency/idempotency and rollback; no financial harness execution yet.
- [ ] Previous security/full-lint/PWA gates and11Moderate/5Low findings; no merge/deploy/pilot acceptance.

Evidence: changes/primary-env-001/{REMEDIATION_VERIFICATION.md,ASTRA_REVIEW_FINAL.md,ISOLATED_STACK_READINESS.md,remediation-evidence.json}. Earlier queues below are historical.

## Historical initial ENV queue — 2026-10-10

- [x] Local ENV reconciliation: reuse current PR48 source on PR53, preserve dependencies; explicit environments, matching build/runtime, guarded harnesses.
- [x] Candidate fixes: privileged-public-key negative regression; deterministic proxy fixtures + explicit proxy rejection; context routing for auth/destructive harnesses.
- [x] Offline verification:60 unit tests/125 expectations; Gate4 target-green;8 actual server-wrapper cases with stub entry; typecheck/changed lint/two isolated builds/syntax.
- [ ] ONE NEXT: independent exact-candidate review. Astra was attempted but stopped at usage limit before review; no approval.
- [ ] ENV acceptance: hosted/current-head checks and isolated DB/auth/RLS/tenant/browser containment evidence. No write-capable financial flow before proof and acceptance.
- [ ] Security acceptance: PR53 final review, prior CI/lint gates and remaining11Moderate/5Low findings remain open.
- [ ] Release/PWA: retain and investigate existing build warnings including empty glob/precache; do not claim offline release readiness from these builds.
- [ ] GitHub Actions startup: no invoice observed; $0 stop-usage budget/quota blocks execution. No account spending change; no blind retries.

Evidence: changes/primary-env-001. The old queue below is historical and does not schedule new work.

## Current queue checkpoint — 2026-10-10

- [x] PRIMARY-SEC-002 local candidate: Critical/High audit triage and compatible dependency corrections prepared; audit now reports 0 Critical and 0 High records; native frozen install/typecheck/unit/build/changed-file lint/diff-check evidence saved. Candidate only; not on main.
- [x] PRIMARY-SEC-002 PR packaging: draft PR #53 stacked after PRIMARY-SEC-001; hosted Quality attempts failed before runner steps (`runner_id:0`, empty steps).
- [x] PRIMARY-SEC-002 source/evidence review of PR #53 head `4a5dda42d6470ded52edfb667d582d04d2a28165`: Changes required; see `changes/primary-sec-002/REVIEW.md`. This is not a GitHub approval or final-head merge acceptance.
- [x] PRIMARY-SEC-002 compatibility evidence: four synthetic Lovable/MCP runtime checks passed; clean Bun generation independently matched all four brace-expansion entries. No application tenant/finance proof claimed.
- [x] SEC2-R2 candidate remediation: generator-owned Bun 1.4.0 update from the verified original PR52 lock; independent regeneration matches byte-for-byte. Unsupported brace paths removed; Lovable MCP stays at 0.20.1. Frozen installs, 44 unit tests, typecheck, isolated build, changed-source lint and audit verified; final review still pending.
- [x] SEC2-R1 startup diagnosis: GitHub run 38035862590 visibly reports failed recent account payments or a spending-limit restriction. The account must resolve it; no billing/spending change was made.
- [ ] ONE NEXT — owner resolves GitHub Billing & plans; then execute required CI and review the final candidate. Preserve failed evidence; no blind retries while billing is unchanged.
- [ ] PRIMARY-SEC-002 acceptance: final-candidate review and required checks remain open; do not waive remaining Low/Moderate findings or previous lint/CI blockers.
- [ ] PRIMARY-ENV-001 after security PR evidence is stable: reconcile fail-closed environment isolation before write-capable financial tests.
- [ ] Track remaining security maintenance: Moderate/Low findings remain for `@babel/core`, `@hono/node-server`, `dompurify`, `esbuild`, `hono`, and `qs`.
- [ ] Financial gates remain blocked until environment isolation and canonical financial write evidence are proven.

Evidence: changes/primary-sec-002/VERIFICATION.md. Earlier PRIMARY-SEC-002-as-next statements below are historical.

## Current queue checkpoint — 2026-10-09

- [x] PRIMARY-SEC-001 candidate preparation: official transport/serializer patch verification, generated lock, three negative/positive advisory guards, minimal ErrorComponentProps compatibility, native29 tests and typecheck/build evidence saved. Candidate only; not on main.
- [ ] PRIMARY-SEC-001 acceptance: independent review; hosted CI evidence; disposition/fix of pre-existing lint gates. No checks waived.
- [ ] ONE NEXT — PRIMARY-SEC-002: triage2Critical and33High audit records by package chain, runtime/tooling exposure, exploit condition and compatible correction. Do not interpret65 scanner records as65 exploited product defects. Resolve security before real-store use.
- [ ] Track tooling/CI: Bun1.2.14 lacks release-age resolution support; Node>=22.12 required by the new framework but Quality does not pin Node; PR51 job runner_id0/empty steps cause remains unproved.
- [ ] PRIMARY-ENV-001: reconcile PR48 and prove fail-closed isolation before write-capable tests.

Evidence: changes/primary-sec-001/VERIFICATION.md. Earlier PRIMARY-SEC-001-as-next statements below are historical planning state. Financial contract, PR49 and PR50 gates remain in force.

# Governed Tasks

## Current queue — 2026-10-09

See [primary plan](docs/PRIMARY_DELIVERY_PLAN.md) and the current block in PROJECT_STATE.md.
Only this queue schedules new work; the preserved August queue below is history.

| Task | Status | Acceptance |
| --- | --- | --- |
| PRIMARY-GOV-001 | Documentation candidate prepared | Identity/state/task/decision links agree; diff limited to docs; no release acceptance implied |
| PRIMARY-SEC-001 | ONE NEXT: preparation | Official advisory + compatible lock/build + required final-head evidence and review |
| PRIMARY-ENV-001 | Follows security candidate and prerequisites | Reconcile PR48/current SEC-CI; prove isolated targets before write tests |
| FIN-COURIER-001 | Existing gate/contract retained | Diagnose current Gate4 and evaluate PR49; backend -> reports -> UX |
| FIN-IDEM-001 | Depends on canonical financial write | Evaluate PR50; all relevant writes, concurrency/replay/lost response |
| PILOT-RC-001 | Blocked by release gates | One accepted source with recovery, security, finance and complete journeys |
| PILOT-000 / commercial | Not started | Actual stores, reconciliations, costs and accepted billing lifecycle |

Do not mark old mongezz B01–B20 as accepted here. Preserve original finding/task IDs,
map dependencies, and use additive history. No full rewrite, speculative transfers,
financial-policy changes or new product scope in the initial dependency packet.

## Historical task snapshot

The content below is preserved as historical evidence; old Active/queue headings
do not schedule the current branch. Actual acceptance is verified from the
relevant current source, review and result, never a historical checkbox.

---

# Governed Tasks

## Active

### RELEASE-BASELINE-RECON-002 — Current main reconciliation before Pilot RC1

- Priority: P0 sequencing prerequisite.
- Change type: Governance / source-of-truth synchronization only.
- Reconciliation-start `main`: `a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`.
- Accepted current Phase-0 baseline after human merge of PR #44: `975a34a854c510f3da7dbe45caa9791bb0375e2d`.
- Previous P0 Gate-4 baseline: `983b746e5c6639dcdc5e6557381ad5619abaa046`.
- At reconciliation start, `main` was 11 commits ahead / five changed paths relative to the old Gate-4 baseline.
- After concurrent repository history and PR #44, the accepted current `main` is 21 commits ahead / nine net changed paths relative to that old baseline.
- Net current drift categories:
  - sale UI `busy`/`saving` duplicate-click guards;
  - `@lovable.dev/vite-tanstack-config` `2.7.7` → `2.9.1` plus lockfile changes;
  - Lovable plan relocation/update;
  - rapid-click sale QA result/script artifacts;
  - isolated Auth Smoke compatibility-date containment from PR #44.
- Rapid-click artifact classification:
  - `docs/rapid-click-sale-results.md` reports 6/6 UI duplicate-click scenarios passed;
  - this remains UI evidence only and does not close FIN-IDEM-001;
  - `tests/e2e/rapid-click-sale.py` reads target configuration/session context and performs financial writes, so it is **not authorized for production execution** and future use must be isolated/fail-closed.
- Out of scope:
  - production financial logic;
  - workflow hardening implementation;
  - environment resolver implementation;
  - migrations/RPC/RLS changes;
  - deployment or pilot execution.
- Done when:
  - `PROJECT_STATE.md`, `TASKS.md`, and the reconciliation record agree;
  - final PR #41 diff relative to accepted `main` is documentation/governance only;
  - required checks on one exact final head are reviewed;
  - a human explicitly merges PR #41;
  - the resulting `main` SHA is recorded before Phase 1 begins.

## Fixed P0 execution queue

### P0-1 — SEC-CI-001: deterministic and secret-safe CI

- Issue: #29.
- Design PR: #32.
- Gate-4 PR: #37.
- Status:
  - Gates 0–3: owner-approved;
  - Gate-4 probe: reached real execution and passed;
  - Quality previously failed on formatting in `tests/gate4/sec-ci/probe.ts`;
  - Gate 4: **NOT APPROVED**.
- Required next actions after RELEASE-BASELINE-RECON-002 merge:
  1. branch/reconcile SEC-CI Gate 4 from the accepted release baseline;
  2. preserve exact policy sentinels;
  3. fix only test-quality/format issues required for Quality;
  4. validate the final stable Supabase CLI candidate on a real runner with fresh migrations + T1–T15 + auth smoke;
  5. prove concise/redacted reporting and least-privilege permissions;
  6. independent evidence review;
  7. explicit human Gate-4 approval;
  8. focused SEC-CI implementation PR;
  9. exact-head verification and explicit human merge.
- Exit:
  - release-blocking workflows are deterministic, isolated, secret-safe, and distinguish infrastructure failure from assertion failure.

### P0-2 — SEC-ENV-001: fail-closed environment isolation

- Issue: #30.
- Design PR: #33.
- Gate-4 PR: #38.
- Status:
  - Gates 0–3: owner-approved;
  - Gate-4 probe: reached real execution and passed;
  - Quality previously failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`;
  - Gate 4: **NOT APPROVED**.
- Approved contract:
  - `MONGEZZ_DEPLOY_TARGET = local | ci | preview | staging | production`;
  - non-production requires explicit non-production Supabase configuration;
  - missing configuration fails closed;
  - non-production rejects the known production project;
  - production requires explicit production intent and explicit configuration;
  - no source-code production fallback.
- Additional current evidence requirement:
  - financial-write test harnesses, including `tests/e2e/rapid-click-sale.py`, must be prevented from running against production or ambiguous targets.
- Required next actions:
  1. reconcile Gate 4 from the accepted release baseline;
  2. correct test-quality issues without weakening sentinels;
  3. verify client, SSR, build-time, runtime, and financial-write test-harness resolution paths share the approved fail-closed contract;
  4. exact-head Gate-4 evidence;
  5. independent review;
  6. explicit human Gate-4 approval;
  7. focused resolver/build implementation PR;
  8. exact-head verification and explicit human merge.
- Exit:
  - local/CI/preview/staging and write-capable test harnesses cannot silently target production Supabase.

### P0-3 — FIN-COURIER-001: courier sale/customer/custody correction

- Issue: #22.
- Gate-4 PR: #27.
- Gates 0–3: owner-approved and merged through PR #24.
- Current exact-head evidence on `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:
  - Quality: GREEN;
  - Ephemeral Financial Rules / T1–T15: GREEN;
  - Isolated Auth UI Smoke: GREEN;
  - UI Gate-4 contract: GREEN;
  - backend Gate-4 contract: real execution failed with exit code `3`.
- Rapid-click main-branch artifact reports 6/6 human-style duplicate-click scenarios passed, but it is UI-only evidence and does not alter the approved FIN-COURIER contract.
- Classification: real Gate-4 evidence blocker, not runner failure.
- Gate 4: **NOT APPROVED**.
- PR-A / PR-B / PR-C: **BLOCKED**.
- Required next actions after SEC-CI and SEC-ENV are closed:
  1. reconcile #27 assumptions against the accepted release baseline, including the UI `saving`/`busy` guards and rapid-click artifacts;
  2. identify the exact backend sentinel producing exit `3`;
  3. determine whether the cause is probe defect, stale baseline assumption, false evidence, or a genuine current contract mismatch;
  4. correct Gate-4 test/evidence only if required; do not implement financial behavior while the gate is unapproved;
  5. rerun Quality + T1–T15 + Auth Smoke + backend/UI Gate-4 on one exact final head;
  6. independent financial review;
  7. explicit human FIN-COURIER Gate-4 approval.

#### FIN-COURIER implementation after Gate-4 approval

**PR-A — canonical financial write**

- forward-only constraint/schema changes;
- `create_sale_with_items_v2`;
- atomic `update_courier_outcome_v2`;
- same-tenant customer validation;
- legal/monotonic courier state transitions;
- custody/debt/stock transaction correctness;
- SQL/concurrency/backward-compatibility/rollback safety tests.

**PR-B — reporting/financial-health alignment**

- outcome-aware reporting;
- canonical debt/custody/store-cash separation;
- regression proof against PR-A semantics.

**PR-C — sales UX**

- Advanced Sale primary on desktop/mobile/post-sale;
- Quick Sale secondary direct/cash/fully-paid/customer-free shortcut;
- courier-specific wording/statuses;
- mobile RTL + desktop exact-flow tests;
- preserve loading/failure states and client-side duplicate-click guards as defense in depth.

### P0-4 — FIN-IDEM-001: financial retry safety

- Issue: #31.
- Design PR: #35.
- Gate-4 preparation PR: #39.
- Status:
  - Gates 0–3: owner-approved;
  - full target behavior intentionally dependency-blocked until FIN-COURIER PR-A provides canonical `create_sale_with_items_v2`;
  - current UI duplicate-click guards and rapid-click 6/6 result are not accepted as server-side idempotency.
- Required target contract:
  - key scope = `tenant_id + operation + idempotency_key`;
  - same key + same canonical request returns original result with no second financial effect;
  - same key + different request returns deterministic conflict;
  - concurrent same-key calls produce exactly one committed financial effect;
  - failed transaction does not poison the key;
  - authorization/tenant isolation still applies on replay.
- Required tests before implementation:
  - sequential replay;
  - same-key conflict;
  - concurrent duplicate calls;
  - lost-response retry;
  - failure-then-retry;
  - tenant isolation;
  - result fidelity;
  - exactly-one stock/payment/debt/custody effect.
- Exit:
  - explicit human Gate-4 approval and focused server/database implementation verified on exact head.

### P0-5 — PILOT-RC-001: one exact release candidate

- Master tracker: Issue #34.
- Dependency: P0-1 through P0-4 complete and human-merged.
- Create one exact `PILOT_RC1_SHA` and freeze it for release verification.
- Required proof on that same SHA:

Financial:
- T1–T15 GREEN;
- FIN-COURIER approved contract GREEN;
- idempotency/retry/concurrency GREEN;
- debt/courier-custody/store-cash reconciliation matches canonical rules;
- returns and stock restoration GREEN;
- day close/reconciliation GREEN.

Security/environment:
- local/CI/preview/staging cannot target production;
- write-capable test harnesses cannot target production or ambiguous configuration;
- tenant isolation GREEN;
- no raw credentials/secrets in CI output or artifacts;
- least-privilege release workflows.

Reliability:
- frozen dependency install;
- typecheck/lint/unit/build GREEN;
- fresh isolated migration chain GREEN;
- authenticated UI smoke GREEN;
- failure/retry paths verified.

UX:
- Advanced Sale primary;
- Quick Sale secondary only;
- mobile RTL and desktop core flows GREEN;
- loading/error/retry states verified.

Operations:
- release notes;
- known limitations;
- environment and secret inventory;
- backup procedure;
- restore procedure tested;
- rollback/compensation procedure reviewed;
- incident checklist.

- Exit: explicit human RC1 approval. No automatic deploy.

### P0-6 — PILOT-000: owner-only controlled pilot

- Target: 3–5 owner-operated stores under direct supervision.
- No employee-account dependency.
- Pilot mode: fix-only for release-critical defects; feature requests are collected but not automatically implemented.
- Measure:
  - activation and time-to-first-sale;
  - daily sales/expenses/debt/day-close/courier-settlement usage;
  - reconciliation variance;
  - failed/duplicate writes;
  - D1/D7/D14/D30 retention;
  - willingness to pay.
- Exit: pilot evidence reviewed and accepted before deciding the next product roadmap.

## Deferred until after owner-only pilot evidence

### EMP-001 → EMP-005 — Team/employee edition

Employee identity, RBAC, assignment, personal custody, employee UI, and employee E2E remain deferred until the owner-only financial core has real pilot evidence and the corresponding change gates are approved.

### Other deferred scope

- payroll;
- attendance;
- automatic commissions;
- GPS tracking;
- internal chat;
- custom per-button permissions;
- multi-branch expansion;
- broad analytics expansion;
- AI product features.

## Completed

### BASELINE-RUNTIME-001 — Auth Smoke local runtime containment

- Issue #42.
- PR #43 tested a dependency rollback and was closed without merge after exact-head evidence reproduced the failure.
- PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937` passed Quality, T1–T15, and real Playwright Auth Smoke.
- PR #44 was explicitly human-approved and merged as `975a34a854c510f3da7dbe45caa9791bb0375e2d`.
- Scope was one local emulator command-line compatibility-date pin only.
- No deployment or production access occurred.

### OPS-GHA-001 — GitHub-hosted Actions execution restoration

- Issue #36.
- Resolved 2026-08-01 after monthly Actions quota reset.
- Hosted runner reached real shell steps/logs.
- No weakened tests, public-repo workaround, unmanaged self-hosted runner, merge, or deploy was used.

### FIN-COURIER-G0-G3

- PR #24.
- Owner-approved and merged.
- Establishes the financial/customer/courier/primary-sale contract.

### AUDIT-001

- PR #23.
- Reviewed and merged.
- Restored a governed pilot baseline before the later drift recorded by RELEASE-BASELINE-RECON-002.

### GOV-001

- PR #19.
- Governance bootstrap merged.

### EMP-000

- PR #20.
- Employee-account baseline/decomposition merged; no implementation authorization.

### PR17-PROTOTYPE

- Closed without merge as superseded oversized prototype.

## Permanent financial invariants

- Sale != Cash.
- Delivered != Settled.
- Customer debt != Courier custody.
- Returned => zero debt/custody + approved stock restoration.
- Customer required only when customer debt is created.
- Courier-collected money remains custody until settlement.
- No UI-only authorization or UI-only duplicate-write protection is accepted as the financial safety boundary.

