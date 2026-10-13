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

## 2026-10-13 Africa/Tripoli — OWNER-RETENTION-VERIFY-01 tested catalog candidate, Draft PR66

Owner-authorized task received2026-10-12; claim #55/6133382681; live checkpoint6133571113.
Branch test/owner-retention-catalog-2026-10-12 above PR65/f37885b1ff5dcc9ab113e5cbee4516b485cedadd.
Tested runnable source9a5a58f6a8556f009880437c0cf95ac91c38c770. main remains
43d6edbccb66fb06ce0fcb93734ad59532d1aeae; Draft stack unmerged/unreleased.

Actual fixture-free local Supabase catalog run38314670848/job115028337892 SUCCESS:
CLI2.101.0/PG17.6(Auth2.188.1/PostgREST14.10/Storage1.54.1), full43unchanged migrations.
56FK/242triggers/193constraints/51functions/80policies and effective grants inventoried.
239comparison rows:234MATCH +5raw DIFFERENCE preserved. The5initialNOTVALID declarations
are validated on this fresh empty stack by later20260626233231 dynamicVALIDATE block;
source-expectation refinement documented, not a schema fix or239automatic matches.
Public30FK/14apptrigger/42latestbody/58oldpolicy+22restrictivepolicy/66privilege rows checked;
provider/inline/PK/UNIQUE/role/default/schema inventories have no complete prior oracle.
Standalone indexes and actual lifecycle/RLS/trigger execution remain unverified.

authenticatedTRUNCATE on21publictables confirmed by effective privileges; no DELETE/TRUNCATE
executed by the probe, no normal-user API/SQL exploit established. DELETEtenants/finance
not granted to authenticated. Original finance7zero; Auth/tenant fixtures0; public22digests
unchanged (original email_send_state seed only nonempty public baseline). Credential scan,
UIDpsqlunexpectedegress0 andcleanup3/3PASS; complete provider-service egress not claimed.
Artifact11775803747 ZIPsha256da00685345c6ad613c016d702a150cb043168de39d17b1b8bbfd9a36f0793bb0.

Quality38314670777/job115028337953 SUCCESS:66tests/159assertions,8wrapper+67browserboundary
scenarios; merge-ref559d45e tree7037e184 equals tested candidate tree. 13focused offline oracle
testsPASS locally andCI. Independent separate reviewer reproduced13offline tests+239recorded
catalog comparisons, verifiedZIP/hashes and fetched original logs; did NOT replay liveDB/CI.
Accepted evidence/planning handoff only; no merge or populated retention acceptance.

No app/migration/dependency/financial or provider-policy fix, account deletion/ban/financial
fixture. Existing harness reused; only dedicated catalog+Quality actually ran. Final docs/state
commit [skip ci] avoids out-of-scope automatic MCPban; preserves tested runnable blobs.
Exact final SHA/CI state/source-equivalence and closure claim are in PR66/#55final handoff.
Full report/table/limits/review: changes/owner-retention-verify/.

OWNER-RETENTION-01 approved policy remains; no persisted closure state/action proven.
Status: Tested catalog candidate only; closure_verified=false; integration_accepted=false.
**ONE NEXT proposed:** planning scope/authorize OWNER-CLOSURE-IMPLEMENT-01 per NEXT_BATCH.md:
persistent private closure state + existing active-actor predicate + least-privilege self-owner
action, retained store/finance/audit and separate financial fixture/isolation approval.
Resolve account/store scope, idempotent repeat and excessTRUNCATE disposition before implementation.
Retention duration/erasure controls still separate. Stop here; no next implementation/merge/deploy.

---

## 2026-10-12 — OWNER-RETENTION-01 approved policy; documentation handoff

Owner explicitly approved the bounded policy at23:47:15 Africa/Tripoli:
closure stops owner access while preserving the store, financial history and audit links;
no automatic record erasure or change to balances, rights or obligations. Hard-delete,
ownership transfer and new access grants need separate explicit approval. This is not
perpetual personal-data retention; retention duration/erasure controls need a later decision.
Exact owner wording and scope: DECISIONS.md top block; #55/6133251051.

Policy decision blocker resolved; **runtime compliance remains NOT VERIFIED**.
PR65 source audit at41cf1a0d2b7f6dca4d8fc197cdd87f76e00cea3b identifies no verified account-closure UI/RPC.
Owner Auth hard-delete reaches business/audit CASCADE and surviving actor SET NULL;
triggers/CHECKs may abort it. No live deletion or populated-history result exists.
Earlier ban/soft-delete/expiry evidence is limited and does not prove closure retention.

This batch: additive documentation on PR65 branch above PR64/2ae95ed6175e0859b4c0a1d36d1110f99f19c792.
main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae; Draft stack unmerged.
No app/schema/migration/dependency/test/workflow change or DB/runtime action.
Final SHA/path verification and #55handoff are recorded at closure. [skip ci] respects
the no-live-test scope; pending/skipped is not GREEN or a quality-gate waiver.
Previous intake/source checks/review remain historical; no new independent/live review claimed.

Status: Approved policy / documented candidate; not implemented, live Tested, Merged or Released.
integration_accepted=false; financial/isolation/release gates remain in force.
**ONE NEXT:** planning scope/authorize OWNER-RETENTION-VERIFY-01, isolated catalog-only
verification per changes/account-deletion-safety-intake/OWNER_RETENTION_HANDOFF.md.
Proposal only, not permission to run it. Closure enforcement/populated finance testing and
personal-data retention/erasure design require separate boundaries. Do not start deletion.

---

## 2026-10-12 — ACCOUNT-DELETION-SAFETY-INTAKE, S2.4 documentation candidate

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

## 2026-10-11 — full local TanStack MCP route candidate, draft PR63

Approved task: issue55/6112713277; sole execution claim6112916960.
Branch test/mcp-tanstack-route-2026-10-11 directly above PR62 head26d6e271ad1a50a26390d25d3236edb5ab47fff7.
PR63 is draft/unmerged; main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae.

Local full route was proven on3b1a25fda8a11b27559b0e988a7930e6748972fa:
HTTP -> native Nitro node-server -> src/server.ts -> generated TanStack /mcp
-> SDK0.20.1 -> genuine local Supabase OAuth/PKCE. Run38169721783:71/71 controls,
A4/B4 active -> B ban persistedSQL -> oldB4 exact account_inactive/isError -> A4
after all B attempts. Initialize200/initialized202/stateless exact4catalog passed.
Missing/malformed/clientclaimless bearers401; hostile headers leave trusted issuer
and JWKS local. Build/runtime conflict500 was separately proved with exact cause
and zero downstream. Public22fingerprints unchanged, finance7zero, containment,
credential scanning/quarantine and cleanup passed. Quality38169721803 passed;
its merge-ref2edf3d6501cda70b3bdae4af9965ac65634a40d0 has the identical source tree.
Independent agent fetched original logs and accepted only this local test scope.
This additive final candidate also records metadata/runtime provenance and filter
coverage. Exact final-head gates and independent closure receipts are recorded in
PR63/#55 at batch closure; no source change follows those gates.

PR62 reconciliation: its final26d6e271 result was52controls, with separate review
6112608180 and planning6112713277 scoped acceptance. The51/pending-review notices
below are preserved historical checkpoints, superseded by those final receipts.
PR60/61/62/63 remain unmerged; none is a main fix or release approval.
integration_accepted remains false. Cloudflare/production/nonempty financial or
foreign-tenant data/concurrency/broader lifecycle matrix remain unverified.
Two pre-credential harness failures are preserved; protected runner workspace
was inaccessible to the dedicated UID. Exact preload/standalone build copies
and cmp/hash checks fixed test access only. No application/dependency/migration/
financial-contract/generated-file manual modification.

Packet changes/mcp-tanstack-route/. ONE NEXT: planning reviews PR63 final evidence
and independent receipt to select the next bounded gate. Stop; no merge/deploy or
financial work.

---

## 2026-10-11 — local MCP issuer candidate verified, draft PR62

Bounded result on29af5b34d3c55c6db1c4debc5d93d8587d2c04fe:
MCP run38165648102 GREEN (51 controls); A/B genuine local OAuth/PKCE,
initialize200 + initialized202 + stateless catalog,8/8 active tool calls,
committed B ban verified,4/4 exact account_inactive old-token denials,
A4/4 after ban.22 public hashes unchanged,7 finance counts zero,
external-attempt/SDK counters zero, stack/key cleanup PASS.
Quality38165648142 PASS (66 unit tests /159 assertions, server/browser boundaries,
both builds). Targeted issuer/crypto6/6 /34 assertions; Python6/6 PASS.

This additive receipt commit removes the last unrelated Vite formatting hunks.
Required gates must run on its exact final head; final run IDs/source/independent
review are recorded in PR62 and issue55 without another source-changing commit.
Separate agent independently reviewed security/harness and reran targeted tests;
final-head review is pending. Receipt changes/mcp-local-issuer/evidence/native-29af.json.

Main43d6edb unchanged; draftPR60/61/62 remain unmerged. No release approval,
production action, dependency/migration/financial-contract change. Direct actual MCP
handler is proven; full TanStack HTTP route, nonempty financial/cross-tenant payloads,
cloud deployment and concurrency remain untested. Historical failed attempts retained.
ONE NEXT: planning reviews this bounded evidence and authorizes a separate full
TanStack HTTP-route verification batch if appropriate. Stop here; no merge/deploy.

---

## 2026-10-11 — PR62 bounded local MCP issuer candidate

Owner authorizes this issuer/configuration batch on PR61 head
315751c46678fa18ffc35dae1e8d6e2cb9b30335, stacked on draft PR60. Main remains
43d6edbccb66fb06ce0fcb93734ad59532d1aeae. PR62 / branch
fix/mcp-local-issuer-2026-10-11 is draft, unmerged and not release approval.
Execution claim: issue55 comment6109194766; no competing visible claim.

Actual definition regression failed before repair on3771dcb (run38140972804).
Reuse validated build environment to select issuer/JWKS; preserve direct production,
strict SDK auth and outbound containment. Real local OAuth/PKCE replaces unsuitable
password JWTs only in the test fixture. Do not count empty financial lists as explicit
ban denial. Focused verification and independent review are pending for this candidate;
final exact-source results override this pending note in PR62 and issue55.
No dependencies/migrations/financial policy/production/merge/deploy changes.

Packet: changes/mcp-local-issuer/. ONE NEXT: inspect focused acceptance and required
Quality on the final candidate, retain any blocker, and submit to planning review.

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

## Current checkpoint — ENV-NATIVE-01 clean baseline, 2026-10-11 Africa/Tripoli

Active repository: `naderalhaje097070-sudo/simple-store-aid`.
Main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`; this candidate
is stacked on draft PR57 `fd2bed16a051a6d4de44f8b97c1a5ba9a36e50fc`.
Branch: `test/env-native-01-clean-baseline-2026-10-11`. No merge or release.

The owner replied «انت المسؤول» to the concrete PR57 approval request.
Recorded as delegated technical approval for Gates0–3 / L01–L15 isolated scope,
not merge, deployment, cost or core financial-contract approval. Issue #55 records
the sole implementer's claim. This bounded batch builds a focused nonfinancial
Gate4 baseline on an existing GitHub runner with pinned Supabase CLI2.101.0.
Five new local harness safety tests pass; hosted evidence is pending.
See [execution record](changes/env-native-01/CLEAN_BASELINE.md).

A named expected-red baseline demonstrates the old-JWT defect; it never accepts
an authorization fix, broad lifecycle isolation, financial tests or release gates.
Actual pg_catalog and provider schema must be captured before implementation.
MCP/admin, nonempty history, expired/deleted actors and broad writes remain open.
ONE NEXT: execute the clean focused baseline, reconcile its actual catalog/results,
then design the minimum forward-only enforcement correction with independent review.

Prior checkpoints below are preserved historical candidate records.

---
## Current checkpoint — ENV-NATIVE-01 preparation, 2026-10-10

Active repository: `naderalhaje097070-sudo/simple-store-aid`.
Main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`; baseline is draft
PR56 `b9aa56bc3bb30948d95961c06fd493dfb866f476`. This batch is a candidate,
not Merged or Released. Branch: `test/env-native-01-lifecycle-intake-2026-10-10`.
Packet: [ENV-NATIVE-01](changes/env-native-01/CHANGE_INTAKE.md);
results: [VERIFICATION](changes/env-native-01/VERIFICATION.md).

S2.4a preparation is implemented: focused Gates0–3, pinned migration/policy/RPC/app
discovery map and offline evidence regression oracle. The archive remains22 passes/
2 seed conflicts; pre-ban own-tenant access is detected as regression, not accepted.
No authorization fix/migration/app financial change or live database execution here.
Source-only discovery is not the effective pg_catalog; catalog reconciliation required.

ONE NEXT: owner review/approve the concrete lifecycle intake and L01–L15 execution
scope, then clean isolated Gate4 baseline on a verified disposable runner. This is
the required intake gate under AGENTS/NAADF-CMF, not merge/deploy authorization.
ENV-NATIVE-01 High candidate, independent review and broad isolation gates stay open.
Financial write/concurrency/idempotency/rollback suites remain blocked by isolation.
Quality342 attempt2/343 success remain historical exact-head evidence; no reruns.

All previous checkpoints below are retained history, with accepted rules preserved.

---

## Current execution checkpoint — PRIMARY-RESUME-001, 2026-10-10

Repository: `naderalhaje097070-sudo/simple-store-aid`.
Verified main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae` (unchanged).
Candidate baseline: PR54 `57fb508b9d239aaf4676352dd97654341416c46a` (draft, unmerged).
Batch branch: `docs/primary-resume-001-2026-10-10`.
Evidence: [PRIMARY-RESUME-001](changes/primary-resume-001/VERIFICATION.md).

Status: documentation candidate Implemented and locally Tested; not Merged or Released.
Final published SHA/PR and check status are recorded in issue #55 and the batch PR.

GitHub access now works through the new owner connection. The connected GitHub App
installation is 170077393; repository permission read reports pull/push/admin.
This is access evidence, not approval to merge or change billing.

Quality #342 / run38080476062, **attempt2**, completed successfully on the exact
PR54 baseline above. Latest job114311070422 reached checkout, frozen install,
typecheck, changed-source lint, unit tests, offline server boundary, browser
containment and both isolated builds; all returned success. The earlier attempt1
runnerless failure remains historical evidence. No rerun was requested in this batch.
Quality does not prove real database/RLS/RPC/disabled-user/financial acceptance.

Reviewed the existing PR51 plan diff: one additive commit, six Markdown paths,
289 additions, zero deletions. Accepted rules and prior source were preserved.
This continuing agent's source reconciliation is not an independent review approval.
PR51 -> PR52 -> PR53 -> PR54 remains a draft/unmerged stack; the finance
PR27 -> PR49 -> PR50 candidates remain separate and unaccepted.

**ENV-NATIVE-01 remains open:** the prior real dummy-account probe recorded a
pre-ban JWT reading its own tenant after Auth ban. No cross-tenant exposure was
observed in that bounded probe; broad isolation acceptance remains missing.
No lifecycle fix, migration, application test, finance write, merge or deployment
was performed in this documentation batch.

ONE NEXT: `S2.4a / ENV-NATIVE-01` — prepare the focused account-lifecycle
intake, current RLS/RPC dependency map and negative regression safety net on this
candidate lineage, before implementing a forward-only authorization correction.
Independent review of the real isolation packet and security candidates remains
required; financial write testing stays blocked until isolation acceptance.

All previous current/ONE NEXT blocks below are preserved historical checkpoints.
Their accepted financial and release boundaries continue to apply.

---

## Current execution checkpoint — PRIMARY-ENV-001 real native runner, 2026-10-10

A capable disposable Vercel sandbox executed exact PR54 source `84c3444fcdf5fa2825809192cda5b15561c950cf`, preserving reviewed implementation0e616d0013fd72de244686f10c8de5a12488f312. All356 tracked blobs matched before and after execution. Main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae; no merge/deployment occurred.

Fresh experimental Supabase CLI2.120.0 native PostgreSQL/Auth/PostgREST stack applied all41 migrations on a non-root runner. Initial Auth users/tenants/orders were0. Bun1.2.14 frozen install, Gate4, Auth preflight,60 unit tests/125 expectations, typecheck and isolated production build passed. Existing Auth UI smoke passed on desktop1440/mobile390 with Playwright1.62.0/matching Chromium151 and strict browser containment. Screenshots and redacted logs are saved in changes/primary-env-001/native-runner; details in NATIVE_RUNNER_VERIFICATION.md. Repository CLI2.101.0/Docker workflow remains unchanged.

Actual Auth/tenant probe:22 passed checks and2 retained duplicate owner-role seed conflicts. Existing tenant trigger already created the roles; independent aggregate proves exactly2 correct rows. Own/foreign tenant metadata cases passed for both real user JWTs. No comprehensive tenant/RPC/financial acceptance is inferred.

**ENV-NATIVE-01 blocks acceptance:** banning fixtureB rejected new login400 but its previously issued JWT still read its own tenant via PostgREST200. This violates the strict disabled-account baseline; no cross-tenant exposure was observed. No account-lifecycle fix was implemented. Existing isolated write-test gates stay closed.

Final aggregates:2 Auth users/2 tenants,0 orders/products/customers. No financial harness, production access, old cloud-project restore, billing/payment change, migration edit, merge or deploy. The sandbox was stopped after retrieval; no snapshot/public route. This removes the earlier database-runtime availability blocker only. Experimental native tooling and external execution do not replace matching hosted CI, independent gate acceptance, full authorization evidence, existing security/lint/PWA blockers or remaining11Moderate/5Low findings.

ONE NEXT: independent review of this real isolation packet and a focused gated resolution of ENV-NATIVE-01, then remaining authorization/hosted evidence before financial write tests. Older checkpoints below remain historical.

## Current execution checkpoint — PRIMARY-ENV-001 runner feasibility, 2026-10-10

Source verified directly from GitHub: draft PR54 head `0e616d0013fd72de244686f10c8de5a12488f312`, base PR53 `54c930166a776828566876771efdec86a997fa53`; main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. No merge/release occurred. This read-only/runtime-feasibility packet supersedes the older assumption that Docker is the only possible local runtime, without approving a toolchain change.

The old `mongezz-pr35-validation` cloud project is INACTIVE in a Free organization. Metadata does not expose pause date, schema/data provenance or exact-candidate migration compatibility. No restore, keys, SQL, backup download or cloud provisioning was performed; it is not accepted as a test target.

Current official Supabase documentation supports experimental native local stacks in CLI >=2.119.0. Downloaded scratch CLI2.120.0 was verified against the official release SHA256 and its help. A clean-environment/default-config native bootstrap failed before starting PostgreSQL: **PostgreSQL cannot be run as root**. This runtime maps only UID/GID0; both non-root transition and user-namespace probes fail. No container runtime/socket exists either. A new CLI executable alone cannot overcome these runtime restrictions; the repository CLI2.101.0 pin and application source remain unchanged.

GitHub Quality run38073032780/job114274195972 on the reviewed head is failure with runner_id0 and empty steps. No new retry was requested; current specific startup annotation remains unverified. Prior billing/quota evidence remains historical, not a new billing inspection.

Evidence: changes/primary-env-001/RUNNER_FEASIBILITY.md and runner-feasibility.json. No new unit/browser/application/database/financial test passed in this packet; preserve the previous bounded67-case evidence without promoting it to integration acceptance.

ONE NEXT: run the exact candidate on a capable disposable runner: preferably the existing Docker/CLI2.101.0 workflow once hosted capacity returns; alternatively assess CLI2.120.0 native on a supported non-root runner as an explicit experimental tooling change. Prove fresh migrations/Auth/RLS/two-tenant/disabled-user isolation and obtain its gate acceptance before financial write tests. No new cost, production access, merge or deployment.

## Current execution checkpoint — PRIMARY-ENV-001 Astra remediation, 2026-10-10

This top checkpoint supersedes the initial ENV review/capacity status below. Existing draft PR54 is extended additively; main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Only naderalhaje0970-droid/simple-store-aid is active.

Independent Astra review resumed and found three browser transport gaps: redirected requests escaped routing, WebSockets were unintercepted, and auth/destructive policies allowed unrelated loopback origins. The shared context guard now blocks redirects without retries, intercepts/closes WebSockets before pages, and pins the exact app/API HTTP origins. Rereview also corrected the existing font dependency with an exact offline stylesheet stub and standardized local/CI prerequisites on the production-built emulator. Screenshots use fallback fonts. No application, schema, financial or dependency change.

Actual browser evidence: original47 cases/36 failures; final67 cases/0 failures on recorded substitute Chromium153. Astra independently reproduced67 passing cases and closed the three initial findings and font compatibility defect for the reviewed source. Outcome remains **Blocked pending missing evidence**, not release/merge approval. Source fingerprints and logs are in changes/primary-env-001/remediation-evidence.json; final review in ASTRA_REVIEW_FINAL.md. Initial60 unit/125 expectations,8 wrapper/stub cases, typecheck/build evidence remains applicable to unchanged application source; changed Gate4/lint/Python/shell/YAML/diff checks passed.

No working Docker/Podman/Supabase/PostgreSQL tooling is present; the loopback fixtures are not an application/database stack. Real migration/Auth/RLS/tenant/disabled-user and financial/concurrency/rollback evidence is missing. Hosted checks still lack runner execution under the quota/spending blocker. Prior security/full-lint/PWA gates and11Moderate/5Low findings remain open. No database writes, migration, production access, merge, deployment or payment/budget change occurred.

ONE NEXT: obtain a capable isolated runner and execute the exact candidate's fresh stack/production-build Auth and tenant-isolation sequence in ISOLATED_STACK_READINESS.md, then obtain matching hosted checks and gate acceptance before financial write tests. Preserve main and current draft history.

## Historical initial ENV checkpoint — 2026-10-10

This checkpoint supersedes older scheduling below. Work continues only in naderalhaje0970-droid/simple-store-aid. main remains 43d6edbccb66fb06ce0fcb93734ad59532d1aeae. The owner authorized local ENV implementation despite hosted Actions limits; security/release acceptance gates remain open.

Prepared an isolated reconciliation candidate by reusing PR48 head31958e53438b377a9896dd0bf7e9c268c1f14aef on PR53 head54c930166a776828566876771efdec86a997fa53. Removed implicit production fallback, enforce explicit build/runtime target identity, guarded write preflights and context browser routing. Corrected privileged-public-key acceptance with before/after regression, proxy-contaminated positive fixtures with explicit proxy negatives, and page-only auth/destructive interception. Package/lock match PR53 unchanged.

Local evidence: 60/60 unit tests,125 expectations; Gate4 E1-E10 target-green; eight real server-wrapper cases with a stub entry; typecheck, changed-source lint, explicit-env build and mode-file build passed. Python/bash syntax and diff evidence are in changes/primary-env-001/VERIFICATION.md/evidence.json. Builds retain existing PWA glob/precache/chunk warnings; no offline/PWA release acceptance.

Independent Astra review was attempted but failed at usage limit before reviewing source. No independent acceptance. Hosted checks, real isolated database/browser/auth/tenant/financial execution and previous security/full-lint gates remain unverified. No database test writes, production data access, migration, merge or deployment occurred.

Billing clarification: earlier startup annotation listed payment failure OR spending limit; subsequent account inspection showed no outstanding invoice, October billed $0 and Actions budget $0 with stop-usage. A quota/spending restriction is the supported explanation, not proof of an unpaid invoice. No payment/budget changes were made. Do not repeat runnerless jobs while this remains unchanged.

ONE NEXT: independent exact-candidate ENV review when reviewer capacity is available; then close findings and obtain isolated integration/required CI evidence before financial write tests. Safe planning may continue meanwhile.

## Current execution checkpoint — PRIMARY-SEC-002, 2026-10-10

This top block supersedes older current checkpoints below. Application main still remains unmodified at `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. A second focused security candidate batch is prepared in this working tree, continuing from PRIMARY-SEC-001, and is not merged or released.

Resolved the remaining current Critical/High dependency-audit groups by pinning compatible patched transitive versions for MCP SDK, proxy address parsing, shell quoting, brace expansion, browserslist, URI/IP/YAML parsing, PostCSS, NanoID and source-map parsing. `bun audit` changed from 65 package/advisory records with 2 Critical and 33 High records to 16 records with 0 Critical and 0 High records. Remaining findings are Low/Moderate only and are not release-accepted.

Native evidence: Bun 1.3.14 frozen install passed; Bun 1.2.14 frozen install passed; typecheck passed; unit tests passed at 40/40 with 86 expectations; build passed using local Supabase fixture values; changed-file lint for the dependency guard passed; `git diff --check` passed. Hosted Quality attempts on PR53 failed before runner execution (`runner_id:0`, empty steps), so they are infrastructure evidence only. Details: `changes/primary-sec-002/VERIFICATION.md` and `evidence.json`.

Known limits: no successful hosted CI, accepted final-candidate review, application MCP/auth/tenant test, financial write test, migration, merge, or deployment ran. PRIMARY-SEC-001 acceptance blockers still apply until exact-head PR/CI/review evidence exists.

Review checkpoint (2026-10-10): draft PR #53 already exists, stacked on PR #52, with reviewed head `4a5dda42d6470ded52edfb667d582d04d2a28165`. The manifest, lock and dependency guard were matched to that remote tree by Git blob hashes. A separate source/evidence review is recorded in `changes/primary-sec-002/REVIEW.md`; outcome: Changes required. Four isolated Lovable/MCP compatibility checks passed, but they do not prove application authorization or tenant isolation. The original manual brace-expansion lock edits conflict with the generated-file rule; independent clean generation reproduces all four entries, while a full regenerated graph has broader changes that were not adopted. Hosted CI still has no executed steps; its specific cause remains unverified.

Remediation checkpoint (2026-10-10; after PR53 head `479b0cef278497d8d7d455facd4aa797aa2af30b`): replaced the manually edited lock with Bun 1.4.0 generator output starting from the verified original PR52 lock. Removed unsupported brace-expansion resolution paths and pinned the already-resolved Lovable MCP version 0.20.1. Independent regeneration produced the identical lock; retained package versions/metadata are unchanged versus the previous candidate. Generator pruning removed 30 unique optional/orphan package versions; see `changes/primary-sec-002/LOCK_REGENERATION.md`. Moved the four synthetic MCP checks into `tests/unit` so the existing Quality job includes them. Bun 1.2.14 and 1.3.14 frozen installs passed; Bun 1.2.14 ran 44/44 tests with 94 expectations; typecheck, isolated build, changed-source lint and diff check passed. Audit remains 0 Critical / 0 High / 11 Moderate / 5 Low. SEC2-R2 is remediated in the candidate, pending final review.

CI diagnosis is now proven from the signed-in GitHub run page for run `38035862590` / job `114166024458`: GitHub prevented startup because recent account payments failed or the spending limit needs increasing. The annotation does not distinguish these two conditions. No account billing or spending setting was changed. Actual hosted execution is still missing; SEC2-R1 remains an acceptance blocker.

ONE NEXT: owner resolves the GitHub Billing & plans blocker; then run required checks and independent review on the final candidate. Do not repeat runnerless jobs while billing is unchanged. PRIMARY-ENV-001 follows stable security evidence; no financial write-capable tests before isolation proof.

## Current execution checkpoint — PRIMARY-SEC-001, 2026-10-09

This top block supersedes the planning-only status below. Application main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. A focused security candidate is prepared on sec/primary-sec-001-tanstack-2026-10-09, stacked on PR51's planning branch. It is a draft, not accepted on main or released.

Pinned compatible TanStack transport/router/plugin and Seroval1.6.7; generated lock/route tree; corrected two provider error-boundary prop annotations. Native frozen install, typecheck and isolated build pass;29/29 unit tests pass. Full lint remains1117errors/13warnings; changed-file lint fails on340pre-existing errors/1warning in app.tsx, with zero added diagnostics proven by text comparison.

Wider audit:65 package/advisory records (2Critical/33High/25Moderate/5Low),25 fewer than baseline and no new records. These are untriaged scanner reports, not proof of deployed exploitation. Hosted runners still lack usable evidence; CI Bun1.2.14 cannot enforce minimumReleaseAge and Node is unpinned. Independent review and runtime/auth/finance validation remain pending. Details and source fingerprints: changes/primary-sec-001/VERIFICATION.md and evidence.json.

ONE NEXT: PRIMARY-SEC-002, triage remaining Critical/High dependency chains and exploit conditions into focused fixes. Security gate is open; PRIMARY-ENV-001 follows. No financial write harness, migration, merge or deployment ran.

# Project State

Last reconciled: 2026-10-09 (Africa/Tripoli).

## Current state — authoritative within this review branch

- Repository: `naderalhaje0970-droid/simple-store-aid` (original Lovable project).
- Verified main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
- Packet: `PRIMARY-GOV-001` — start plan pinned as documentation candidate.
- Plan: [PRIMARY_DELIVERY_PLAN.md](docs/PRIMARY_DELIVERY_PLAN.md).
- Code baseline remains a functional MVP with financial/security blockers.
- This branch contains documentation only; no runtime, dependency or DB fix is accepted.
- Historical main/PR statuses below are not current task instructions.
- No main merge, release, pilot or production-data authorization is granted by this packet.

## ONE NEXT

`PRIMARY-SEC-001`: prepare a focused TanStack dependency-security candidate.
Start by re-reading live main, applicable governance, package/lock resolution,
Lovable compatibility and open PRs. Follow the detailed four-step task and
applicable intake/safety requirements in the plan. Native verification gaps
keep the candidate blocked; no security override or unsafe environment fallback.

Following dependency: reconcile PR48/environment isolation, then financial gate
and PR49, followed by PR50/idempotency. No financial write test before isolation proof.

## Current evidence limits

Main confirmed at the SHA above; PR48/49/50 metadata re-read, all unmerged.
No application tests, database runs or dependency upgrade performed in this
documentation session. CI and independent review results belong to the actual
PR head and must be recorded separately, not inferred from earlier green runs.
Detailed audit and remaining acceptance conditions are summarized in the plan.

## Historical state — superseded scheduling, retained evidence

The following 2026-08-09 snapshot is retained verbatim as history. Its headings
such as Current stage / Immediate next task do not override the current block.
Existing financial invariants and release controls remain effective.

---

# Project State

Last updated: 2026-08-09

## Current stage

`RELEASE-BASELINE-RECON-002` — reconcile the effective `main` branch with the fixed Pilot RC1 plan before any new P0 implementation is authorized.

Reconciliation start `main`:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

Accepted current Phase-0 baseline after human merge of PR #44:

`975a34a854c510f3da7dbe45caa9791bb0375e2d`

The current P0 Gate-4 workstreams were created from or stacked on the older governed baseline:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

At reconciliation start, `main` was 11 commits ahead of that older baseline and changed five paths. Before PR #44 was merged, additional direct repository history landed. The accepted current `main` is now 21 commits ahead of the older Gate-4 baseline with net changes across nine paths:

- `.github/workflows/isolated-auth-smoke.yml`
- `.lovable/plan.md` removed/moved into a dated plan file
- `.lovable/plan/اختبار-الضغط-المتكرر-على-زر-بيع-وحفظ-الفاتورة-mobile-390px-2026-08-09.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`
- `docs/rapid-click-sale-results.md`
- `tests/e2e/rapid-click-sale.py`

The application source drift still consists of the client-side sale-save guards already classified as defense in depth. The later rapid-click files are test/planning/evidence artifacts; they do not provide server-side idempotency and are not authorized for production execution.

The project remains a Functional MVP being stabilized into a reproducible, financially safe owner-only release candidate. No pilot or production-release authorization exists yet.

## Current release freeze

Until Pilot RC1 is explicitly approved:

- no new product features enter the release critical path;
- no employee accounts, payroll, attendance, GPS, chat, commissions, multi-branch, AI, or broad analytics;
- no direct product/dependency change to `main` outside a reviewed PR path;
- no automatic merge or deploy;
- no production data/secrets are used by isolated verification;
- any Critical/High financial-correctness or tenant-isolation defect blocks pilot;
- published Lovable-linked history is not rewritten;
- applied migrations remain immutable and corrections use forward-only migrations.

## Completed / resolved

### Governance and financial design

- Governance bootstrap merged through PR #19.
- Employee-account prototype PR #17 was superseded and closed without merge.
- AUDIT-001 baseline restoration merged through PR #23.
- FIN-COURIER-001 Gates 0–3 were owner-approved and merged through PR #24.
- SEC-CI-001, SEC-ENV-001, and FIN-IDEM-001 Gates 0–3 were owner-approved on 2026-07-28; their implementation remains gated.

### OPS-GHA-001 / Issue #36

Resolved on 2026-08-01. GitHub-hosted Actions again reaches real workflow steps and logs after the monthly Actions quota reset. Remaining failures are repository/test evidence, not runner acquisition failures.

### BASELINE-RUNTIME-001 / Issue #42

Resolved by explicit human merge of PR #44 as `975a34a854c510f3da7dbe45caa9791bb0375e2d`.

Evidence sequence:

- Phase-0 PR #41 originally reached a successful isolated Supabase start, QA seed, and production build, then failed before Playwright because the generated Worker compatibility date was `2026-08-09` while the local workerd binary supported through `2026-08-08`.
- PR #43 tested a dependency rollback hypothesis and reproduced the same failure, so it was closed without merge.
- PR #44 changed one local Auth Smoke command only, passing `--compatibility-date 2026-08-08` to `wrangler dev`.
- On PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937`, Quality, Ephemeral Financial Rules / T1–T15, and Isolated Auth UI Smoke all passed; Playwright executed successfully.
- No application logic, financial logic, dependency rollback, production access, or deployment was performed.

## Current P0 workstreams

### 1. SEC-CI-001 / Issue #29

Goal: deterministic and secret-safe release CI.

Current evidence:

- Gate-4 PR #37 is Draft and unmerged.
- SEC-CI Gate-4 policy probe reached real execution and passed.
- Standard Quality reached lint/format validation and failed on formatting in `tests/gate4/sec-ci/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Required before implementation:

- reconcile the Gate-4 branch to the accepted current release baseline;
- correct test-quality failures without weakening the contract;
- prove the final stable Supabase CLI/tool pin on a real runner;
- preserve T1–T15 and Auth Smoke;
- independently review exact-head evidence;
- explicit human Gate-4 approval.

### 2. SEC-ENV-001 / Issue #30

Goal: local/CI/preview/staging must fail closed and must not silently target production Supabase.

Current evidence:

- Gate-4 PR #38 is Draft and unmerged.
- SEC-ENV Gate-4 isolation probe reached real execution and passed.
- Standard Quality reached repository validation and failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Approved target remains:

`MONGEZZ_DEPLOY_TARGET = local | ci | preview | staging | production`

Non-production requires explicit non-production configuration and rejects the production target. Production requires explicit production intent and explicit approved configuration. No source-code production fallback is accepted.

The newly landed `tests/e2e/rapid-click-sale.py` reinforces this requirement: its historical evidence says it used an injected owner session and could leave undeletable paid test orders. The script is not wired into an approved release gate and must not be run against production; future execution must use an isolated tenant and fail-closed environment proof.

### 3. FIN-COURIER-001 / Issue #22

Priority: P0 financial workflow blocker.

Approved business contract remains unchanged:

- direct fully paid: customer optional;
- direct debt: customer required;
- courier pending: customer optional and outside settlement;
- courier fully collected: customer optional; collected money is courier custody and becomes immediately settlement-eligible;
- courier partial/none that creates customer debt: customer required;
- courier-collected money does not enter store receipts before settlement;
- Advanced Sale is primary; Quick Sale is a secondary direct/cash/fully-paid shortcut;
- Delivered is not Settled.

Current exact-head evidence on PR #27 head `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- FIN-COURIER UI contract: GREEN;
- FIN-COURIER backend contract: real execution reached the consolidated safety net and failed with exit code `3`.

This is a real Gate-4 evidence failure, not infrastructure failure. Gate 4 is **NOT APPROVED**. PR-A / PR-B / PR-C remain blocked.

The effective `main` contains client-side sale-save guards in BottomNav, Quick Sale, and PaymentSheet. The rapid-click QA artifact reports 6/6 human-style duplicate-click scenarios passed on one injected session, but this remains UI evidence only and does not alter the approved financial or idempotency contract.

### 4. FIN-IDEM-001 / Issue #31

Priority: P0 financial retry-safety blocker.

Current state:

- Gates 0–3: owner-approved.
- PR #39 is preparation/readiness only and remains dependency-blocked by the canonical FIN-COURIER sale v2.
- Current UI `saving`/`busy` guards and rapid-click results do not satisfy server-side idempotency.

Required contract:

- scope key by `tenant_id + operation + idempotency_key`;
- same key + same canonical request returns original result without a second financial effect;
- same key + different request fails deterministically;
- concurrent same-key calls commit one financial effect;
- failed transaction does not poison the key;
- replay still requires normal authorization and tenant isolation.

## Baseline drift impact

Compared with old Gate-4 baseline `983b746e5c6639dcdc5e6557381ad5619abaa046`, accepted current `main` `975a34a854c510f3da7dbe45caa9791bb0375e2d` is 21 commits ahead with nine changed paths. Material categories are:

1. client-side duplicate-click/save guards in the sale UI;
2. `@lovable.dev/vite-tanstack-config` `2.7.7` → `2.9.1` and lockfile changes;
3. planning-history relocation/update;
4. rapid-click sale QA script/results artifacts;
5. isolated Auth Smoke local-emulator compatibility-date containment merged through PR #44.

Therefore no P0 Gate-4 approval may rely solely on stale exact-head evidence. Each workstream must reconcile its relevant assumptions to the accepted release baseline and run authoritative checks on its final exact head.

Client-side duplicate-click protection remains defense-in-depth only. It does not replace `FIN-IDEM-001`.

## Fixed critical path

1. Complete `RELEASE-BASELINE-RECON-002` and human-merge it.
2. Record the resulting `main` SHA.
3. SEC-CI Gate 4 reconciliation → exact-head proof → independent review → human approval.
4. SEC-CI focused implementation → exact-head verification → human merge.
5. SEC-ENV Gate 4 reconciliation → exact-head proof → independent review → human approval.
6. SEC-ENV focused implementation → exact-head verification → human merge.
7. FIN-COURIER Gate 4 backend-failure diagnosis/reconciliation → exact-head proof → independent financial review → human approval.
8. FIN-COURIER PR-A → PR-B → PR-C, each focused and release-verified.
9. FIN-IDEM Gate 4 against canonical sale v2 → human approval → focused implementation.
10. Create one exact Pilot RC1 commit and run all financial/security/reliability/UX/recovery gates together.
11. Explicit human RC1 approval.
12. Controlled owner-only pilot with 3–5 stores.

## Financial decisions that must not change

- Sale is not Cash.
- Delivered is not Settled.
- Customer debt is not Courier custody.
- Returned orders create no customer debt and no courier custody and restore stock only through the approved return transaction.
- A customer is required only when an operation creates customer debt.
- Money explicitly recorded as collected by a courier is custody, not store cash, until settlement.
- Pending courier delivery remains outside settlement until an outcome is recorded.
- Financial writes use authorized server-side/database transactional boundaries.
- Tenant isolation is enforced server-side and with RLS.
- No UI-only control is accepted as the sole protection for financial correctness or authorization.

## Pilot scope

The first pilot remains owner-only and targets 3–5 directly supervised stores. Employee accounts remain deferred until owner-only pilot evidence is reviewed.

Pilot entry is blocked by:

- FIN-COURIER-001;
- SEC-CI-001;
- SEC-ENV-001;
- FIN-IDEM-001;
- final exact-head Pilot RC1 verification;
- explicit human release approval.

## Immediate next task

Complete exact-head checks on Phase-0 PR #41 after synchronizing its tree to accepted `main = 975a34a854c510f3da7dbe45caa9791bb0375e2d`, preserving all concurrent repository history. Then require an explicit human merge. After that merge, record the resulting `main` SHA and begin SEC-CI reconciliation from that exact baseline.

Do not begin SEC-CI implementation, SEC-ENV implementation, FIN-COURIER PR-A/B/C, FIN-IDEM implementation, pilot execution, or deployment before their stated gate is satisfied.

## Standard verification

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

When a change affects financial or authenticated application behavior, the appropriate isolated financial and authenticated UI suites are additionally mandatory. GitHub checks on the exact final PR head are the authoritative verification source.


