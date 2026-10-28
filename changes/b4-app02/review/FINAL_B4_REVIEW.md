# B4 / APP-02 — final independent review

Reviewer: `/root/foundation_a_independent_review`, independent of implementation. Date: 2026-10-22 UTC. Repository: `naderalhaje097070-sudo/simple-store-aid`.

**Formal outcome: Changes required.** The APP-02 correction is technically accepted within B4 on the integration candidate below, and the scoped B4 review is complete. This is not approval for human merge, main, B5/B6, the whole B package, release or deployment. General DEP-20261021 High findings and the preserved A source-manifest barrier remain open. No new unresolved B4-specific defect was found in the final reviewed scope.

## Exact source and preservation

Reviewed and native-tested executable: **`f3b702440a4ffd17038f3c668a2f446620a97919`**, complete Git tree **`6bc91e3b942dccfa5beab67b57f0c22c15b78917`**. Base: `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0`.

Independent complete-tree comparison records 358 protected paths and 50 migration SQL files. All 47 base migrations and 349 of 350 prior protected path/blob/mode identities remain exact; the intended webhook route is the sole replaced old protected file. Eight protected files are added: the module, three test/harness files, workflow and three migrations. No path is deleted. Existing package/lock, financial/read-state source, B2/B3 corrections and signature helper remain exact. Applied 48 and 49 were retained rather than rewritten.

| Forward migration | SHA256 |
| --- | --- |
| `20261021132651_webhook_persistence_01.sql` | `95b527271e552f20bfb8a0e07627e0195ed681c46e3f8cbcb7d5daaa4a98a66d` |
| `20261021134621_webhook_bootstrap_01.sql` | `c905a149d7deb0cb9b22080142152a5a06aa2c982b4ee7f907c63a434cff3f75` |
| `20261021140746_webhook_errors_01.sql` | `a5cff8d91149a61424f1d6cd62bf60cc42a334623085eec7e706ac3b0f38f955` |

The local source is a blob extraction: 352 available protected blobs match; six binary blobs are unavailable locally and two extracted shell files lack their Git executable bit. Official tree identities/modes establish their preservation. No complete local checkout or local frozen-runtime claim is made.

## Contract assessment

The former route acknowledged failed/missing writes and performed independent subscription/tenant mutations. The new route acknowledges a supported callback only after a named successful result from one transaction containing required subscription, live binding/cache and receipt writes. Errors, zero affected rows, absent/malformed results and bounded uncertainty return 503. Unsupported verified events remain ignored; existing environment-selected SDK verification precedes persistence.

The RPC is service-only SECURITY INVOKER, with explicit PUBLIC/anon/authenticated EXECUTE revocation, pinned catalog search path, UTC and lock timeout. Two private RLS tables retain normalized receipt/identity and live binding state. Ordinary authenticated actors receive no access; service has no destructive private-table grants. Global provider-ID, event and tenant serialization, checked row counts and transaction rollback address duplicate and partial-write boundaries. No raw provider payload or user credentials are stored in the new ledger.

Provider event times retain microseconds. Equal-time contradictory states fail; event IDs do not choose a conflicting winner. Only created can replace a known live binding, ordered by immutable entity creation time; late created for an existing stream projects its latest stored state. Sandbox changes only its environment-qualified subscription state. The global tenant cache is explicitly live-only; the existing billing consumer and entitlement helper read environment-qualified subscriptions. Existing trial, cancellation, financial and retention rules are preserved within this scope.

Legacy arrival clocks are conservative admission barriers, not recovered provider chronology. Ambiguous legacy/UI ordering fails before mutation. Missing updated/canceled streams require created and then explicit replay; full snapshots cannot reconstruct fields deliberately retained by the historical handler.

## Findings disposition

| Finding | Severity / origin | Final disposition and actual evidence |
| --- | --- | --- |
| APP-02 false acknowledgement and partial persistence | High, inherited | Closed on this integration candidate only. The actual old route on schema 47 reproduces false 200 responses. Final errors/zero-row faults on all four required targets produce 503, full data invariance, same-event recovery and one receipt. |
| B4-SOURCE-01 legacy public/UI ordering contradiction | Medium, introduced prototype | Closed. Conservative created guards in both environments and the live projection guard precede writes. Both native legacy display-conflict cases return 503 with unchanged snapshots; normal replacements remain positive. |
| B4-SOURCE-02 missing public row permits retained stream reassignment | Medium, introduced prototype | Closed. Cross-environment receipt history rejects recreation/reassignment of a known missing stream. Later-time tenant/customer and environment regression cases return 503 with invariance; duplicate acknowledgement does not recreate a row. |
| B4-SOURCE-03 unseen updated/canceled bootstrap loses historical fields | Medium, introduced prototype | Closed by 49. Final missing-stream cases return 503 without a receipt, then created and explicit replay preserve the intended plan/price, periods and cancel flag. Earlier conditional full-snapshot bootstrap acceptance is withdrawn in the retained ordering review. |
| Created scheduled-cancel flag differs from original new-row default | Medium, introduced; implementer discovery | Closed by normalizer and 49 SQL. Old-route baseline proves false; final actual row, request and resolved receipt are all false after created, followed by the explicit updated replay. Existing created/canceled retention behavior is checked. |
| B4-SOURCE-04 application SQLSTATE 40001 triggers internal retry/late mutation | High, introduced | Closed by 50 within the tested stack. Its actual installed body exactly matches the reviewed correction, contains no manual 40001 and retains ordinary P0001 errors. No late updated receipt appears before explicit replay; created remains false, then replay applies the update. Earlier failing diagnostics remain failures. |

All Medium findings above have the explicit decision to accept their evidenced corrections; none is silently deferred. The late-mutation diagnostic is observed evidence. Its PostgREST/Hasql retry explanation is a source-backed inference from official documentation/source and the runtime version class, not a captured backend/CPU trace. The correction changes exactly ten application-domain error codes in the 49 body and preserves guards, transaction and grants. Engine-generated serialization/deadlock behavior is not changed. See the retained `SQLSTATE_RETRY_REVIEW.md` for primary sources and the earlier review gap.

## Final native evidence independently replayed

GitHub API confirms run **39614265434**, attempt 1, exact source above, and all four jobs successful. I matched both retained ZIP bytes to API artifact digests and their extracted members, checked unique named controls/results, and independently recomputed the exported populated preservation equalities.

| Evidence | Identity / result |
| --- | --- |
| Fresh 50 | job `119271111233`, artifact `12351144140`, 206 passing controls; ZIP SHA256 `d37f0592131e6b96f6ce5bf9d20ecec2105a8bbf59f12df451c5638f6412a95f` |
| Populated 47→50 | job `119271110943`, artifact `12350993751`, 53 baseline reproduction controls plus 169 corrected controls; ZIP SHA256 `9543465e1b88a5743b51159b73d2f7c3cfcb59e6259c9cf2fddaafd2cf2941e1` |
| Frozen compatibility | job `119270964453`; API log shows Bun 1.2.14 frozen install, Node 22.23.3, 76 original tests / 221 expectations, 22 signed-handler tests, typecheck, full lint (0 errors / 12 inherited warnings), four original OC_APP wire round trips, build and clean tracked generation |

The baseline uses the final harness with the actual **base** route and schema 47; its `source` field is not a claim that the old handler is the final app. Runtime reports PostgreSQL 17.6 / gcc 15.2; final image receipts include PostgREST v14.10.

The exported upgrade receipt has 23 original data fingerprints and five old catalog components (cron, policies, triggers, functions, relations). Actual before/after values match, including the baseline fingerprints. This final artifact supports independent equality replay; earlier attempts without the pair do not. It does not cover every possible catalog property or populated financial history.

Both runs retain 45 advisor WARN records: 43 `auth_rls_initplan` and two `multiple_permissive_policies`; zero ERROR. These warnings are not waived or called clean. Cleanup receipts confirm rejected credential-free canary, zero unexpected IPv4/IPv6 rejects, and removed stacks/status/private state. Native safe-publication checks inspect actual secret values before deletion; uploads require the successful guard and cleanup output. My replay additionally checks credential patterns and member identity, but cannot repeat the deleted-secret-value comparison. An initial reviewer advisor parser incorrectly read the first object inside the array; its output is retained separately and the corrected replay preserves all 45 warnings.

## Verification limits and next gate

I independently inspected source/diffs, API identities/logs, permissions and oracle reachability; ran source-derived ordering witnesses and a focused local actual-SDK normalization check; and replayed stored final native evidence with `final_native_replay.py.txt`. That local SDK check used Node 24.19, not the frozen native environment. I did not run an independent live Supabase stack, deployed HTTP/browser flow, real provider callback, production operation or historical suite.

Counts include setup and invariance controls, not distinct vulnerabilities. Eight simultaneous duplicate calls replay an already committed event; they are not eight racing first inserts. Updated/canceled equal-creation negatives stop at the missing-stream guard; only created reaches the distinct-stream creation tie branch. Lost-response evidence deliberately discards a committed response; the deadline unit stubs an unresolved dependency. Neither proves a native commit-after-timeout network fault. Financial tables are empty. Legacy reconciliation, production volume/performance and a deployed rollback rehearsal remain unverified. The reviewed forward containment revokes the new service RPC while preserving data and retryable failure; it was not executed.

General dependency audit evidence remains failed: 11 package entries / eight distinct advisories / three High on unchanged dependency bytes. This is carried evidence from earlier exact audit runs, not a new audit execution at f3. The preserved A manifest separately rejects the B superset. Neither is weakened or closed by B4. ONE NEXT is their separately claimed remediation/reconciliation before B5/B6 acceptance under the canonical plan.

Fresh read-only API observation on 2026-10-22 confirms main `18700dee8ecdda2e457c0aa18c4f83a81b042019` and all 20 original draft head/base identities unchanged from independent B4 intake. No implementation, merge, publication, provider or database action was performed by this reviewer.

The forthcoming docs-only handoff still requires a bounded complete-tree comparison against this tested source: all 358 protected path/blob/mode identities, 50 migrations, evidence/index/report hashes and truthful current-state notices. That preservation gate must not add executable changes or promote this formal **Changes required** outcome to whole-head approval.
