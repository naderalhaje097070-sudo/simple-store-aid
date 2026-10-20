# Independent G0/G1 acceptance review — 2026-10-14

Outcome: **Changes required.** G0/G1 are not accepted; this is neither human merge approval nor a release decision. The packet provides a bounded, reviewable acceptance assessment with actual failed evidence. No further unchanged database/CI replay is needed to deliver this assessment.

## Source and independence

The reviewer did not implement the application, workflow, controllers or fixes and did not mutate GitHub, start a database, dispatch CI, access providers/billing, or execute financial bodies. The only file written by this review is this report.

Read directly from GitHub: planning #55/comment6163164423, previous comparison #70/comment6153966539, PR48/51/52/53/54 metadata, project governance, dependency-generator provenance, relevant original workflow/contracts, and exact source trees. Main43d6edbccb66fb06ce0fcb93734ad59532d1aeae; PR54 57fb508b9d239aaf4676352dd97654341416c46a; separate PR48 31958e53438b377a9896dd0bf7e9c268c1f14aef. Initial test source e535b6a0eb7b3f309f26c56dc329142e7deb34c3; supplemental runtime source89838e82244932f62b467fdf4d5a4ca76ec5139a.

Independently compared all18 PR48/PR54 path identities: eight byte-identical and ten differing exactly as the prior comparison. Reused the unchanged line analysis. Independently matched the source54 manifest to all383 remote blobs and recomputed all383 local Git blobs with zero mismatches. Re-read nontruncated remote54/89838e82 trees: all383 original blobs and modes remain intact. Supplemental-vs-initial remote comparison contains only the new runtime-only workflow and private env staging/failure-phase diagnostics in the controller; assertions remain unchanged. This source does not import financial/account-chain candidates or add migrations.

## Evidence independently checked

- PR54 Quality38080476062 attempt2/job114311070422: directly fetched actual steps and logs. Success includes60 unit tests/125 expectations, eight actual-wrapper/stub cases and67 dummy browser transport scenarios. Existing exact-source Quality is reusable; it is not full lint, live account-lifecycle, PWA, audit or financial acceptance.
- Initial run38531691158: directly fetched environment/security job logs115744819101/115744819199. Exact SEC-ENV target-green and REST/proxy/service-worker checks passed; visual-runtime literal check failed. Security frozen install passed; fresh audit and full lint each returned actual exit1.
- Recomputed fresh audit16 records and compared package/advisory ID/severity with the preserved archive: same11 Moderate/5 Low, no Critical/High records. This corroborates scanner results, not exploit reachability or owner risk acceptance. Summed full-lint per-file receipts independently:1117 errors/13 warnings.
- Independently hashed original security ZIP `da70fe35ad8ed47b9d4e3e1b57e1267c78cd9dd49dbdb662595349d66afcb28a` and all four member bytes against retrieved receipts.
- Independently hashed initial runtime ZIP `8302d57d0c5a13ca251e4dbed770d158c95b2ae6b0dc03041dcbdfd0abb96310` and all five member bytes. It contains31 successful observations followed by controller PermissionError before SSR/UI; cleanup4/4 passed. Reviewed the narrow private600 staging/install correction before its affected-boundary retry.
- Supplemental run38532631519/job115747865883: directly fetched actual job logs/API steps. Independently hashed ZIP `953f1a8b5d6eee790f55c5c9e7ce905225d57f1d7ea010268925d6b3a029bb45` and all five member bytes. Recomputed34 observations:33 pass, one fail. Matching actual Cloudflare SSR and existing real desktop/mobile Auth UI passed. Required named config-denial assertion failed, job exit2. Cleanup4/4 and credential scan passed. After-runtime public/finance snapshots, final IPv4/IPv6 counters and final source assertion were not reached.

Actual independent re-execution was limited to two read-only local probes: cached Bun1.2.14 `tests/gate4/sec-ci/probe.ts` returned0 with the exact target-green sentinel and no expected-red sentinel; the unchanged original visual canonical-origin preflight shell body returned0/`SEC_ENV_VISUAL_HARNESS_CONFIRMED`. Its body SHA256 is `4cbcfda14d46ccf270614541f2137becac2a0aa1512727981349b0d307022e6b`, stdout SHA256 `5c479f8c30d3e20fd3600262795e8fadaffa2b43f61d5b4528ee38b047a4b1aa`. No browser/Auth/database/financial body was executed by these reviewer reruns.

## Findings and gate disposition

| Finding / contract | Severity / status | Required disposition |
| --- | --- | --- |
| Fresh11 Moderate/5 Low advisories | Existing scanner findings, not accepted | Explicit applicable risk disposition/remediation before acceptance; scanner severity alone does not establish exploitation. |
| Required full lint | Existing quality gate, failed | Preserve1117/13 actual diagnostics; define bounded remediation rather than replacing full lint with changed-source lint. |
| G01-ENV-CI-01, original visual-runtime workflow | Low test-integration defect; G1 blocker | Reconcile the stale literal oracle with the shared guard while preserving navigation, fatal-error, final-origin and negative assertions. |
| Named actual SSR config-mismatch evidence | Required proof failed/unverified | Diagnose and retain a sanitized precise guard receipt; generic500 cannot establish the intended denial. Complete remaining end-state/counter assertions after this boundary is proven. |
| ENV-NATIVE-01, disabled preissued JWT | Existing High G2 OPEN | Keep outside this foundation implementation. Existing historical native observation remains unresolved on54; do not silently import59 or call disabled-account protection accepted. |

G01-ENV-CI-01 evidence: the original workflow expects `request.is_navigation_request()` and `request_origin != BASE_ORIGIN` in the visual file. That file now uses a pure `(method,url,is_navigation)` predicate and installs the shared helper before page creation; the helper forwards the real navigation flag. Off-origin navigation, violations, fatal goto failures and final-origin checks remain present. The failure demonstrates stale test coupling, not a proven missing browser protection. A later correction must prove semantic predicate/wiring behavior and meaningful negative mutations, not simply remove the failed literals. The finding is recorded in the delivery report/issue handoff and remains a required failed gate regardless of its Low severity.

The mismatch retry reaches a500 readiness response but does not prove its cause. Private emulator logs were not included, so another guard error versus log formatting cannot be distinguished from the delivered receipt. Do not infer a source defect, accept a weaker oracle, or claim after-state invariance/zero outbound attempts. The bounded positive SSR/Auth result is valid within the recorded case only.

G0 is **not accepted**: full lint failed and remaining advisories lack new acceptance disposition. G1 is **not accepted**: original mandatory visual CI contract failed, named runtime mismatch proof failed and subsequent invariance/counter assertions did not execute. SEC-CI policy-only/local preflight success does not approve the original financial-writing workflow; its financial body is outside this authorization and remains unmet. Failed mandatory checks were not waived. Branch-protection403 responses do not prove the enforced required-check list.

## Recommendation and limits

PR54 is the strengthened existing source candidate supported by the unchanged18-path comparison. **Keep PR48 open; do not formally mark it superseded, merge it, retarget it or close it on this evidence.** Formal supersession awaits passing required guarantees on a final minimal integration source. No new Critical/High defect was identified in the bounded new acceptance controllers; inherited High G2 and unresolved gates remain explicit.

Reviewed RESULT.md and checks-and-scope.json against the receipts. The packet distinguishes static preservation, positive runtime observations, failed assertions and unexecuted checks. It is sufficient for a blocked planning handoff, not a ready-to-merge recommendation. No production, broader authorization, financial write/concurrency/idempotency, upgrade, PWA/offline, provider or release acceptance is inferred. Final documentation-head source identity and PR/check metadata must still be reconciled at publication without replaying unchanged runtime suites.

ONE NEXT: planning defines a bounded G0/G1 remediation packet covering the actual lint baseline, remaining advisory disposition, semantic visual CI contract and named SSR/after-runtime evidence. Preserve original branches and failed artifacts; rerun only changed boundaries. Stop at handoff without merge/deployment.
