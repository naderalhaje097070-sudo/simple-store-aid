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

## Current queue checkpoint — PRIMARY-RESUME-001, 2026-10-10

Repository: `naderalhaje097070-sudo/simple-store-aid`.
Verified main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae` (unchanged).
Candidate baseline: PR54 `57fb508b9d239aaf4676352dd97654341416c46a` (draft, unmerged).
Batch branch: `docs/primary-resume-001-2026-10-10`.
Evidence: [PRIMARY-RESUME-001](changes/primary-resume-001/VERIFICATION.md).

This resumes the six-stage plan and issue #55; it does not create a second roadmap.

- [x] S1.1a: re-read main, PR54, required files, live open PRs and execution claims.
- [x] S1.1a: review PR51 scope/preservation; six Markdown paths, one additive commit,
  289 additions and zero deletions. No independent approval is inferred.
- [x] S1.1a: reconcile active repository identity and current/historical notices.
- [x] S2.1 bounded evidence: Quality #342 attempt2 actually executed and passed
  on PR54 head57fb508; prior attempt1 failure is historical. No billing change
  or blind rerun. Other required checks are not inferred from this one workflow.
- [x] S1.1a documentation candidate: path/content/blob/link/whitespace validation;
  source/migrations/lock/workflows are preserved. Publication details in issue #55.
- [ ] S1.1 full acceptance: genuinely separate review and explicit human merge.
- [ ] S2.2/S2.3: remaining toolchain/security review, exact-head checks and residual
  11 Moderate/5 Low dispositions; Quality alone does not close these gates.
- [ ] ONE NEXT: `S2.4a / ENV-NATIVE-01` — prepare the focused account-lifecycle
  intake, dependency map and regression safety net; preserve historical records.
- [ ] S2.4 isolation acceptance: pre-disable JWT direct API/RLS/RPC denial,
  active-account positive control, foreign-tenant denial and preserved history;
  independent exact-source review and required hosted proof.
- [ ] S3/S4 financial write, concurrency, idempotency and rollback execution remain
  blocked by isolation acceptance. PR27/49/50 stay unmerged.
- [ ] S5/S6 RC1, real-store pilot and commercial deployment remain blocked.

Earlier active queues and ONE NEXT statements below are historical; do not schedule
duplicate dependency/ENV implementation or billing retries from them.

---

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


