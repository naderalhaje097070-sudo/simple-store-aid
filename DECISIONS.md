## 2026-10-13 — OWNER-CLOSURE-IMPLEMENT-01 blocked before implementation

Owner approved planning #55/6151090438 and instructed this worker to execute; sole
claim6151326852. Source PR68/00923287d804f99faa1b70d28cece17f9f33eac3;
main observed43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Branch
`docs/owner-closure-blocker-2026-10-13`; final SHA/PR and claim closure will be recorded in #55 at handoff.

Confirmed OC-FIXTURE-01: the planning card requires product/order/items/payment/audit
via approved RPCs, but selected source creates products through authenticated REST
with price/cost/stock; no product creation RPC exists. No fixture shortcut/new RPC/
financial repair or borrowingPR49/50 taken. Owner authorization already exists; this
is an allowed-surface mismatch, not another missing generic approval.

48 selected exact Git blobs and43 historic migration digests match; all44 migration
sources searched and relevant effective definitions reviewed. Native43 catalog is historical structure, not a new live44 receipt.
Existing16 privilege-oracle tests PASS; not closure proof. Separate non-implementing
reviewer confirmed the blocker; no reviewer live DB/CI/test rerun.

No application/schema/workflow/financial contract change, closure action or financial
fixture. No merge/deploy. Closure remains Planned / implementation Blocked;
closure_verified=false; integration_accepted=false. Account scope, actual standalone
indexes, retry exception and all live implementation acceptance remain open.

ONE NEXT for planning: resolve OC-FIXTURE-01 by considering explicit permission for
one synthetic product via the existing owner REST/RLS path on the disposable stack,
while order/items/payment/audit remain on existing approved RPC/trigger paths only.
This is proposed, not approved or executed. Resume this same task/packet after resolution
and source/claim recheck; no repeated SEC-TRUNCATE or assumption that drafts are main.
Evidence, exact boundary, limitations and independent review:
`changes/owner-closure-implement-01/`. OWNER-RETENTION-01 policy is unchanged.

## 2026-10-13 — SEC-TRUNCATE-01 tested candidate, unmerged

Planning #55/6139631421; execution claim6144887293. Resumed after checking
existing branches/PRs/comments: no prior SEC-TRUNCATE-01 execution or duplicate fix.
Base PR66/9d30064d0d42667bf4b1de6469c319e625b9f33d; branch
fix/sec-truncate-01-2026-10-13. Runnable source tested:
c233f156220b4551e82edccec3eaff9161c20ba3. main remains
43d6edbccb66fb06ce0fcb93734ad59532d1aeae. No merge/deploy.

One CLI-generated forward migration20261013120223_sec_truncate_01.sql revokes
only client TRUNCATE on22 application tables and postgres/public table defaults.
authenticated21→0/22; anon/PUBLIC0/22. Other rights, service/owner/maintenance,
roles/memberships, provider schemas/defaults and43 prior migrations preserved.
Future-default protection is scoped to postgres-created public tables; unexpected
global client table-default grants (including inherited grants) outside public
stop the migration; remaining effective inherited table grants fail acceptance.

Fresh44 and upgrade43→44 passed in run38394692253. Dedicated push Quality job
115286889333 ran the existing13 Quality steps (only push BASE_SHA differs):
66unit/159assertions,8wrapper and67browser containment scenarios passed.
16focused oracle tests passed. The original PR workflows were deliberately not
run: final docs [skip ci] avoids historical lifecycle suites outside this batch;
a skipped docs head is not a green live-tested head or a merge-gate waiver.
CLI2.101.0; PG17.6/image17.6.1.106; Auth2.188.1; PostgREST14.10; Storage1.54.1.

All22 public fingerprints stable; original finance7, auth users and tenants empty.
No TRUNCATE/DELETE or financial fixtures executed by the test. Only empty default
probe CREATE TABLE inside ROLLBACK; cleanup3/3 and credential screening passed in
both environments. UID unexpected egress0; not a complete provider-egress audit.
Initial pre-DB generator failure38394158093 is preserved, corrected generation
38394370225 succeeded. Artifacts, matrix, hashes and limits:
changes/sec-truncate-01/REPORT_AR.md, RUNS.json and INDEPENDENT_REVIEW.md.

Independent reviewer /root/sec_truncate_review reran16 offline tests, reconciled
raw catalog/ACL/data and verified original GitHub logs/ZIPs; no live DB or Quality
replay. Final documentation preserves the tested runnable blobs.
closure_verified=false; integration_accepted=false. OWNER-RETENTION-01 policy
remains approved; actual closure and nonempty financial retention remain unproved.

ONE NEXT: planning reviews this security candidate, then defines one separate
owner-closure batch with account/store/idempotence and isolated fixture acceptance
criteria. No closure implementation, automatic regrant rollback, merge or deploy
is authorized by this completed batch.

## 2026-10-13 Africa/Tripoli — OWNER-RETENTION-VERIFY-01 evidence disposition

OWNER-RETENTION-01 remains the owner's approved closure policy from the block below;
duration/erasure of personal data still requires a separate decision. Owner's later task
authorized one isolated database catalog verification plus tools/tests/docs/review only;
claim #55/6133382681, Draft PR66 above PR65/f37885b1. That authorization did not approve
closure implementation, financial fixtures, deletion, production, merge or deployment.

Observed source9a5a58f6a8556f009880437c0cf95ac91c38c770, catalogrun38314670848:
owner->tenant/business/audit CASCADE and surviving actorSETNULL confirmed structurally;
all30reviewed public FKs and14apptrigger declarations match. 5initialCHECK validation
expectations refined by later dynamicVALIDATE; raw234MATCH/5DIFFERENCE retained.
authenticatedTRUNCATE on21publictables is an effective privilege concern, not a proved
ordinary-userAPI exploit; no destructive statement executed by the verification probe.
Existing active-actor body lacks persisted closure state. Structure != closure behavior.

Decision disposition: accept recording verified catalog observations, no policy expansion
or runtime compliance approval. Independent reviewer accepts evidence/planning handoff;
13offline tests+recorded reconciliation rerun, originalCI logs read, no independentlive run.
closure_verified=false; integration_accepted=false. Full limitations/report/review and
one proposed next implementation intake: changes/owner-retention-verify/.

**ONE NEXT proposal, not implementation authorization:** OWNER-CLOSURE-IMPLEMENT-01.
Persistent private closure marker + existing active-actor guard + scoped owner action;
resolve account/store cardinality, idempotence and destructive privilege scope first.
Nonempty fixture testing remains gated and must preserve exact balances/rights/obligations/
audit links. No hard-delete/transfer/new access/retention duration is silently approved.
The historical policy/pending/source notices below remain preserved, not current scheduling.

---

## 2026-10-12 — OWNER-RETENTION-01: سياسة إغلاق حساب المالك معتمدة؛ التنفيذ غير مثبت

**الحالة: Approved policy / documentation only.** أقر المالك هذا القرار صراحة في
المحادثة الحالية، 2026-10-12، Africa/Tripoli (وقت الرسالة 23:47:15 +02:00).
سجل التفويض والمطالبة: [#55/6133251051](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6133251051).
هذه الإضافة تحسم وصف «Pending OWNER-RETENTION-01» في السجل التاريخي أدناه؛
لا تمحو تاريخ التدقيق أو تعني أن السياسة منفذة على main أو الفرع.

### النص المعتمد وحدود القرار

> أعتمد OWNER-RETENTION-01 بالحدود التالية:
> إغلاق حساب المالك يوقف وصوله، مع حفظ المتجر والسجل المالي وروابط التدقيق.
> لا يؤدي الإغلاق إلى محو تلقائي للسجلات أو تغيير الأرصدة والحقوق والالتزامات.
> الحذف النهائي ونقل الملكية ومنح وصول جديد إجراءات منفصلة تحتاج موافقة صريحة.
> هذا القرار لا يحدد احتفاظًا أبديًا بالبيانات الشخصية؛ مدة الاحتفاظ وضوابط المحو تُحسم لاحقًا بقرار مستقل.
> وثّق موافقتي في DECISIONS.md وحدّث الحالة والمهمة ونقطة الاستئناف في #55. ميّز بوضوح بين السياسة المعتمدة والسلوك الحالي غير المثبت.
> سلّم لمحادثة التخطيط الفجوة بين السياسة والكود، واقتراح أصغر دفعة تحقق معزولة بمعايير قبول واضحة. هذه الموافقة تخص السياسة والتوثيق فقط؛ لا تبدأ تنفيذ حذف أو تعديل برمجي، ولا تدمج أو تنشر.

الإغلاق يوقف وصول المالك ويحفظ المتجر والسجل المالي وروابط التدقيق، دون محو
تلقائي للسجلات أو تغيير الأرصدة والحقوق والالتزامات. الحذف النهائي ونقل الملكية
ومنح وصول جديد إجراءات مستقلة تحتاج موافقة صريحة. هذا **ليس احتفاظًا أبديًا**
بالبيانات الشخصية؛ مدة الاحتفاظ وضوابط المحو تُحسم بقرار مستقل لاحق. لا نختار
حقول هوية شخصية جديدة أو مدة احتفاظ أو صلاحيات قراءة إضافية بهذا القرار.

### السياسة مقابل الكود

الاعتماد هنا لسياسة العمل فقط. تدقيق PR65/41cf1a0d2b7f6dca4d8fc197cdd87f76e00cea3b مصدرّي:
لا مسار UI/RPC لإغلاق/حذف الحساب مثبت، وAuth hard-delete للمالك يصل إلى
tenant/business/audit CASCADE وإلى actor SET NULL في صفوف باقية؛ قد تُفشل
triggers/CHECKs العملية. نجاح الحذف أو فقد البيانات أو حفظها في التشغيل غير مثبت.
أدلة ban/soft-delete/expiry بمالية خالية لا تثبت سياسة إغلاق المالك ذي سجل مالي.
الحذف النهائي ليس تنفيذًا مقبولًا للإغلاق؛ لا يُعتمد فشل FK عرضي كحارس للسياسة.

تفويض هذه الدفعة: التوثيق وتسليم فجوة السياسة/الكود وتصميم تحقق فقط؛ **لا حذف،
تعديل برمجي/مخطط، DB query/write، fixture مالية أو اختبار حي، دمج أو نشر**.
لا يفتح القرار بوابات المالية/العزل ولا يوافق على الاختبار المقترح تلقائيًا.
integration_accepted=false؛ مدة الاحتفاظ/المحو وتنفيذ الإغلاق وإثباته ما زالت منفصلة.

**ONE NEXT للتخطيط:** تحديد/تفويض OWNER-RETENTION-VERIFY-01 وفق
[التسليم ومعايير القبول](changes/account-deletion-safety-intake/OWNER_RETENTION_HANDOFF.md):
مطابقة catalog معزول دون إجراء lifecycle أو fixtures مالية، لإثبات الحواف الفعالة
فقط. اختبار الإغلاق بمالية غير فارغة وتصميم الإصلاح يحتاجان نطاقًا وتفويضًا منفصلين.

---

## 2026-10-12 — Owner deletion contract is pending, not inferred

Task #55/6125519471; sole claim6125791464. Branch
`docs/account-deletion-safety-intake-2026-10-12` directly above Draft PR64
`2ae95ed6175e0859b4c0a1d36d1110f99f19c792`. Source-map checkpoint
`f03ae6563243956bf82986485eac09094950414c`, #55/6125888048.
Final head/PR/independent factual verdict are recorded in this batch's PR/#55closure.
main remains`43d6edbccb66fb06ce0fcb93734ad59532d1aeae`; draft stack unmerged.

Implemented documentation / offline source checks only:139fetched blobs match Git,
43ordered migrations,30retained public FKs,14source trigger declarations; original41
catalog migration hashes preserved. Catalog proves prior function/policy/grants,
not effective current FK/trigger rows. No fresh DB queried; no deletion/fixture/financial
write or live/history suite run. Prior soft-delete/ban/expiry receipts remain bounded
historical evidence, not hard-delete retention proof.

Owner hard-delete reaches tenant/business/audit CASCADE plus surviving actor SET NULL
references. Financial audit trigger append to deleted tenant can abort deletion;
customer/courier CHECKs can block SET NULL. Success/data loss is untested.
Non-owner deletion, role unlink, soft-delete and ban differ; raw audit UUID retention
is not retained human identity. No account/store deletion UI/RPC exists. Later DELETE
revoke defeats early owner DELETE grants; historical authenticated TRUNCATE needs
catalog/reachability reconciliation without executing it. No production incident inferred.

**Pending OWNER-RETENTION-01:** decide owner/store/financial-audit identity retention
and post-closure access. Existing employee disable/unlink rule and pending employee
hard-delete identity decision do not decide owner policy or retention period.
Proposed test in`changes/account-deletion-safety-intake/TEST_SPEC.md` is DESIGN ONLY;
nonempty fixtures/destructive action require a separately approved boundary.

Final docs commit uses`[skip ci]` because unchanged MCP workflow would launch live tests
for state-file edits, outside this batch. No workflow/test modification or gate waiver;
skipped/pending is not GREEN. No merge/deploy/production/cost/contracts/history rewrite.
Status: Implemented documentation candidate, offline checked, not live Tested/Merged/Released.
Broader isolation/integration_accepted=false and financial/release gates remain blocked.
**ONE NEXT:** concrete owner decision OWNER-RETENTION-01; do not execute deletion/test yet.

---

## 2026-10-12 — L13 natural provider token expiry candidate, Draft PR64

Task #55/6119851247; sole implementer claim6119904934.
Branch test/auth-natural-expiry-2026-10-12 above PR63 final3cb0d82afe31eb2d81538fd7ae631c10fdfa0357.
main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae; the entire stack remains unmerged.

Tested candidate source44a0d221e635340b8450334ed9484c3f39f48205:
Auth Natural Expiry run38227740249/job114739300263 PASS,79/79 controls/35 ordered requests.
B genuine OAuth/PKCE initially succeeds7/7 (own REST, read-only summary RPC, initialize and4tools).
Actual signed exp-iat180; SDK0.20.1 default tolerance30, PostgREST14.10 skew30, Auth2.188.1 leeway0.
Real wait to exp+35 with wall/monotonic agreement: same unchanged B token gives7/7 expired denials,
fresh A7/7 successful, new B7/7 successful, original B still7/7 expired denials.
REST/RPC401/PGRST303/JWT expired. MCP public401/invalid_token is generic; causal proof adds
same-token signature/identity/exp-specific cryptographic error, locked verifier source correspondence
and zero downstream user/tool access. Do not claim MCP publicly exposed ERR_JWT_EXPIRED.
Accounts remain active and original B session exists;4password/3authorization_code/0refresh requests.
Public22 fingerprints unchanged,finance7empty,zero unexpected IPv4/IPv6/fetch,secret scan+cleanupPASS.

Quality367/run38227740311 PASS on merge-ref0ce34c6 with tree equal to candidateeeaa24e5.
12expiry+4consent fixture offline tests pass. Independent agents re-ran focused offline checks and
reviewed original receipts; final-head closure verdict lives in PR64/#55. No independent live replay.
All application/dependencies/43migrations/Auth policy/proxy/financial code untouched.
Shared PKCE test helper alone now supports Auth's existing-consent autoapproved ConsentResponse;
callback/state/code/PKCE/client verification preserved. Configured MCP consumer regressions ran
automatically for this helper change (not added to expiry counts), bothPASS. No historical210/212/78 reruns.

Four failed attempts preserved: two pre-credential source inspector assumptions, token_type scheme
misclassified as credential and quarantined, then existing-consent fixture shape mismatch.
None accepted as natural-expiry success; no application defect or test weakening.
Evidence packet changes/auth-natural-expiry/evidence/native-44a0; permanent final source/run/review
receipts are in PR64/#55. This additive checkpoint preserves every earlier source/evidence statement;
final-source gates must be reconciled at closure, never inferred from this ancestor run.

Status: Implemented/Tested candidate; not Merged/Released; integration_accepted=false.
Broader L13/lifecycle,nonempty finance/foreign data,concurrency,Cloudflare/proxy/production/release unverified.
ONE NEXT: planning reviews PR64 final evidence/review and selects the next bounded lifecycle gate.
Stop after closure; no merge/deploy/finance/production/cost/history rewrite.

---

## 2026-10-11 — local full TanStack route proof is a separate acceptance

PR63 tests the native built Node preset of the unchanged application, including
src/server.ts and generated routing/adapter. Installed Nitro NITRO_PRESET selects
node-server only in isolated harness; default Cloudflare deployment is unchanged.
No direct createMcpProtocolHandler test server is used for this full-route claim.
OAuth/PKCE fixture, initialize sequence and strict account_inactive/body oracle
are reused from PR62. Test metadata under hostile Host/forwarded headers without
inventing proxy policy: advertised resource can reflect trusted forwarded host;
issuer/JWKS stay pinned and outbound attempts remain forbidden.
OS UID containment is established before credentials, then preload barrier records
firewall baselines before bundle import and requires zero later IPv4/IPv6 deltas.
Detected credential evidence is quarantined outside the always-upload directory.
On3b1a25f:71 controls passed,22public hashes stable and finance7empty; independent
review accepted that bounded evidence. Final exact-source receipts live in PR63/#55.
Broader integration_accepted=false; no financial correctness/nonempty isolation,
Cloudflare runtime, production or release inference. Main and unmerged lineage stay
unchanged. PR62 final52controls/6112608180 supersede historical51/pending notes below.
ONE NEXT: planning review of final PR63 evidence, not automatic merge or expansion.

---

## 2026-10-11 — focused local MCP proof, no release decision

Real local OAuth/PKCE meets the unchanged SDK client-claim requirement. On29af5b,
all four banned old-token calls gave explicit account_inactive, while the other tenant's
four calls remained successful; no empty result accepted as denial.51 controls passed.
Actual runtime Authv2.188.1 independently confirms public authorization IDs are32
ASCII alphanumeric, not UUIDs. This is direct handler proof only. Final CI and separate
review receipts belong to PR62/#55; owner/planning controls the next batch.

---

## 2026-10-11 — validated MCP issuer selection (draft PR62)

Use the existing approved Supabase build/runtime endpoint contract for MCP issuer
selection; do not construct a remote host from project ID, request Host or JWT.
Pin JWKS to that validated provider issuer; retain authenticated audience and strict
SDK0.20.1 OAuth-client binding. Real local code/PKCE tokens are test prerequisites.
Empty finance results do not prove explicit tool denial after ban. Direct handler
proof is distinct from full TanStack route proof. Draft/unmerged; no release decision.

---

## 2026-10-11 — MCP L10 verification candidate

Owner «قم بالاختبار» authorizes the next bounded test-only batch after PR60 evidence
closure. Base e4ee6bafc8adec292826769ec37ad1d21e97ae95; source of truth issue55.
Root owns tests/account-lifecycle/mcp_* and focused workflow/packet. No app,
migration, dependency, financial-contract, production, cost, merge/deploy change.

Actual application four tools/locked protocol with real local Auth JWT are the
scope; administrative Supabase MCP is a different trust boundary. Local3 oracle
methods PASS. New focused one-stack CI is pending. Active controls must pass before
ban testing; source-derived cloud issuer versus approved local URL is a potential
configuration blocker, not proof of correct ban denial. Record all observed status
and stored hashes; no timeout/5xx/generic auth failure treated as acceptance.
Do not repeat prior210/212/78 workflows or claim full isolation/financial release.

Packet: changes/mcp-lifecycle-01/VERIFICATION_PLAN.md. Actualsource/jobs/results and
blocker saved in draftPR/#55 after execution; independent acceptance not performed.
ONE NEXT: inspect actual focused result; if active is blocked, scoped issuer/config
repair intake with retained failing regression before any application change.

---

## 2026-10-11 — PR60 second failure retained; signature classifier diagnosed

Candidate9cc230b7f17de92f69a7ec2d59f0e0f3735a6dde: Quality350 SUCCESS; focused4
run38120549060 attempt1 correction fresh210/210 andupgrade212/212 PASS. Independent
steps both FAILED at tampered_jwt_reason: actual issuerES256/providerGET200,
future signedHS256 fixture200 andexpired401 passed, tampered401 received but old
exactbody was not retained. No soft-delete/fullindependent receipt claimed.
Raw progress/failure preserved under changes/env-native-01/evidence/hardening-followup.
Actual pinned PostgREST14.10/jose-jwt0.10.0 decode contract explains strict harness
expectation mismatch: failed individual key verification yields KeyError with
exact None-of-keys details. Reviewer-owned additive classifier correction accepts
ONLY401/PGRST301/exactmessage+details, with same-token future200 control; missing
configured-key details remain denied. Sanitized allowlisted constants are now
retained. Fifteen focused units PASS locally; new source actual CI and
independent replay receipt are required before bounded approval. No unchanged
rerun, application/migration/dependency change, merge or deployment.
ONE NEXT: inspect exact-source new controls and independent reviewer replay,
then reconcile explicit remaining lifecycle/isolation gates in PR60/#55.

---

## Forward verifier correction after actual issuer mismatch — 2026-10-11

InitialPR60 source7f6a6c991c7de4767c13f38485709e01ac0b1bf8: Quality349 SUCCESS,
focused3/run38120052208 attempt1 originalcorrection fresh210/210/upgrade212/212 PASS.
Both independent steps FAILED after44 controls because actual Auth issuer signing
is asymmetric; initialHS256-assumption was false. No independent expiry/softdelete
or acceptance is claimed. Failures/progress retained under evidence/hardening-initial;
ZIP digests verified and cleanup succeeded. No unchanged historical rerun.

Forward test-only correction verifies originalJWT through Auth GET/user exactidentity
and uses CLI-source-verified combined JWKS legacyHS key for clean-header signedfixture
twins. Mandatory futurepositive /expired303 /tampered301; provider-verification,
local-signing and naturallyelapsed-token limitations explicit. No new dependency
or cryptographic implementation; real softdelete remains gated on actual freshresult.
Artifact names include run_attempt for distinct independent replay evidence.

Final source/job/counts/independent receipt and protocolverdict recorded in PR60/#55;
no selfapproval/pending-as-pass. All43 migrations/application/finance/main unchanged.
ONE NEXT: complete currentfocusedverification and independentlyinitiatedreplay, then
reconcile remaining L01–L15 isolation requirements before financial execution.

Earlier checkpoints below remain historical evidence.

---

## Verification hardening after independent review — 2026-10-11

Owner «قم بذلك» approves bounded PR59 review followup. Independent review5482207278
completed on fd95ad2e1966362719965ef282de1e2eb66cb070: Blocked pending missing evidence,
no introduced Critical/High code defect found. This candidate addresses E1 advisor
pre/post exact-schema provenance and ERROR checks, E2 trusted stored foreign no-effect
window and E4 consumed workflow paths. Separate reviewer oracle supplies ban/active,
real softdelete/history and valid signed expiry controls plus independent live replay.

Branch test/env-native-01-review-evidence-2026-10-11, stacked on unmerged PR59.
No application/migration/financial/dependency change; all43 migrations and old evidence
preserved. Eight scoped implementer unit methods pass locally. Final actual jobs,
source SHA, reviewer receipt and verdict are authoritative in the batch PR / issue55.
Do not promote pending results or implementer evidence to independent acceptance.
Packet: [VERIFICATION_HARDENING](changes/env-native-01/VERIFICATION_HARDENING.md).

Main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. MCP/harddelete-cascade/nonempty
financial history/concurrency/active financial effects/production performance/prior
queue-scanner authorization remain unverified. Financial/release gates stay closed.
ONE NEXT after this bounded batch: reconcile final independent live receipt and
remaining L01–L15 gaps before financial execution. No merge/deploy/cost/production.

Earlier checkpoints below are historical; review-unperformed notices are superseded.

---

## Forward compensation after isolated profile failure — 2026-10-11

Initial correction source `0c9689dd814e5ce8220d15ed5dcad6b0deb75efe`:
Quality347 passed, but focused run38092565324 failed in BOTH fresh/upgrade modes.
Fresh stopped after25 controls; upgrade after117. Neither is a green correction.
Raw sanitized progress/failure evidence is retained under evidence/correction-initial.

Candidate root cause: profiles' existing UPDATE check selects profiles; adding a
SELECT SubLink in its restrictive ALL policy triggers PostgreSQL17 recursive RLS
expansion. Verified source: postgres/postgres REL_17_STABLE rewriteHandler.c,
hasSubLinks / activeRIRs / ERRCODE_INVALID_OBJECT_DEFINITION. New live regression
must prove exact42P17 + profiles recursion, rather than assume the masked500 code.

Migration42 is immutable after isolated application. Add generated migration43,
20261010225012_avoid_profile_policy_sublink_recursion.sql, changing ONLY the new
profiles policy to the same direct private predicate. Preserve all58 prior policies.
Fresh43 and representative41→43 upgrade now required; no history rewrite/retry of
historical source. Upgrade/rollback apply both additive migrations. Add real active
profile edit, safe SQLSTATE-only diagnostics, lookup plan/runtime image/advisor
capability records. No5xx is permission success and no linked/cloud advisor fallback.
Exact final results are recorded in PR59 and #55; Gate6/broad isolation remain open.

Prior candidate descriptions below are retained chronological evidence.

---

## Current correction candidate — ENV-NATIVE-01, 2026-10-11 Africa/Tripoli

Owner explicitly «قم بذلك» authorizes the concrete database-policy/RPC correction
and isolated tests after the PR58 clean baseline. Active repository is
`naderalhaje097070-sudo/simple-store-aid`; main remains
`43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. Baseline draft PR58 is
`b8fd5e95ab1f6eee07bb6198da3169cd46916962`.
Branch: `fix/env-native-01-live-account-2026-10-11`. Candidate only, never Merged/Released.

One forward-only migration adds a private live Auth-account predicate,22 restrictive
authenticated ALL policies and guards30 exposed definer /3 internal assertion
functions. Preserve existing policies, ACLs, RPC signatures and financial bodies.
No rows/backfill/applied-migration/app/dependency/config change. Static generator and
human-gated rollback are pinned to the reconciled catalog; baseline oracle unchanged.
Five new local contract tests pass; actual fresh42 and41→42 upgrade/denial/active/
rollback tests are recorded on the exact source in the batch PR and issue #55.
Consult those final run records; do not infer hosted results from this checkpoint.

Design/limits: [CORRECTION](changes/env-native-01/CORRECTION.md).
Gate6 independent review, MCP/expired/deleted actors, concurrent/nonempty financial
history and production-scale performance remain open. Broader financial writes and
release stay gated. Existing active-user email/scanner privilege concerns require
separate review; this lifecycle guard does not accept those contracts.
ONE NEXT after candidate tests: independent adversarial review plus missing isolation
coverage. Merge/deployment/cost/financial-policy changes still require owner approval.

Prior checkpoints below remain historical evidence.

---

## Completed focused baseline — 2026-10-11 Africa/Tripoli

Draft PR58 `test/env-native-01-clean-baseline-2026-10-11`, based on PR57; main remains
`43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. No merge or release.
Tested runtime SHA: `15d30f3794aaab8c04b1dc17ddbfc4d99c4099bd`.

Quality345/run38091180062 attempt1 SUCCESS:60 unit tests,8 server wrapper
scenarios,67 browser scenarios, typecheck/lint and both build stages.
Account Lifecycle Baseline1/run38091180122 attempt1 SUCCESS as a named
EXPECTED-RED regression:57 controls passed;10 denial targets failed, showing
banned owner AND staff retain old-JWT protected own data/summary and direct RLS.
Fresh Docker stack: CLI2.101.0, PostgreSQL17.6,41 exact migrations; four dummy
actors/two tenants, zero finance rows; public history checksums unchanged.
All cleanup steps succeeded. No foreign tenant read/update/reassignment succeeded.

Effective catalog:40 public functions,58 policies,432 table grants. The tenant
owner policy bypasses a helper-only fix; existing role/tenant/admin assertions
contain no live Auth-ban check. Catalog and exact raw sanitized results are
archived under changes/env-native-01/evidence/clean-baseline; infrastructure/job
identity and limitations are in execution.json and CLEAN_BASELINE.md.

This closes the focused harness/baseline batch, not ENV-NATIVE-01 or broad
Gate4/6 acceptance. All previous failed evidence and unverified coverage remain.
ONE NEXT: use this catalog to implement the minimum forward-only caller-bound
live-account enforcement across direct policies and exposed definer entry points,
extend missing lifecycle tests, then obtain independent review. Financial writes,
merge/deployment remain gated. Later docs/evidence-only commits preserve runtime;
their check statuses must be stated on their own exact SHA.

---

## DEC-ENV-NATIVE-01-BASELINE — Delegated approval and bounded execution

2026-10-11 Africa/Tripoli. Owner «انت المسؤول» delegates technical responsibility
after review material in PR57; Gates0–3 / L01–L15 isolated scope are approved for
routine implementation, without merge/deploy/cost/financial contract approval.
Use the existing GitHub runner, repository-pinned CLI2.101.0, separate temporary
CLI config and exact41 migrations. No production identity/config or source changes.
Keep the harness fail-closed before credential reads; real loopback Auth tokens
are distinct from SQL RLS checks. Expected-red is a named regression, never green
authorization acceptance. Preserve all prior failed evidence and missing coverage.
This batch changes only tests, workflow and documentation. Enforcement migration
and independent acceptance follow actual catalog reconciliation. Rollback: revert
these additive candidate commits; no database correction has been applied.

---
## DEC-ENV-NATIVE-01-PREP — Lifecycle intake candidate

2026-10-10. Routine owner-authorized preparation only; proposed authorization design
awaits intake approval under AGENTS/NAADF-CMF. Use Auth ban as the existing defect's
live lifecycle signal after pinned-schema validation; do not add client-writable
disabled state, delete identities/history, or adopt the separate finance stack.
An old JWT reading own tenant is the confirmed historical failure. A tenant-helper-
only change leaves direct owner policies open. Source discovery and offline tests
are not isolated acceptance or independent review. Preserve22/2 fixture evidence.
No production, migration implementation, costs, merge or deployment. Candidate scope
and rollback: changes/env-native-01. ONE NEXT: approve intake/L01–L15 scoped baseline.

---

## DEC-PRIMARY-RESUME-001 — Owner transfer and evidence reconciliation

- Date: 2026-10-10 (Africa/Tripoli).
- Status: owner-instructed source identity; documentation candidate, not merge approval.
- Active repository: `naderalhaje097070-sudo/simple-store-aid`, stable repository ID1281463067.
  Prior `naderalhaje0970-droid/simple-store-aid` links identify transferred history;
  separate `mongezz` repository is not authorized as a fallback.
- main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. Existing PR51-54 candidates are not accepted on main.
- Observe workflow attempt and real steps: Quality #342 attempt2 is green on
  `57fb508b9d239aaf4676352dd97654341416c46a`; retained attempt1 failure must not be rewritten or
  used to claim a current runner block for that successful job.
- Only bounded Quality execution is proven. No account spending change or release,
  database, disabled-account or financial acceptance follows from it.
- Preserve the existing six-stage plan, all accepted DEC-001 through DEC-014
  financial/security boundaries, raw failed evidence and Lovable history.
- ENV-NATIVE-01 remains a blocker requiring focused lifecycle intake/safety tests
  and independent review; do not approve it through UI-only or login-only proof.
- Routine safe candidate preparation is authorized by MONJEZ v2.2. Protected
  merge/deploy/destructive/cost/core-contract/security-bypass decisions stay with
  the owner. No new financial policy is introduced by this record.
- Rollback: close this draft before merge; if later human-merged, use an additive
  documentation revert and retain issue/PR evidence. Never force-push.

---

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


