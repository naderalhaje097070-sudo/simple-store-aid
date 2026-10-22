# B4 / APP-02 — final runtime verified on candidate only

Exact executable: `f3b702440a4ffd17038f3c668a2f446620a97919`, tree `6bc91e3b942dccfa5beab67b57f0c22c15b78917`. Native run39614265434 and all four jobs succeeded. Independent final scoped review is complete: `review/FINAL_B4_REVIEW.md` (SHA256 `4fd405bcd876882d94162dbfc73cd71562477276b753d8e8f73c11a8e3f0ecb8`) accepts APP-02 on this integration candidate only. Formal whole-head verdict remains **Changes required**. The docs-only publication preservation receipt is recorded externally in issue #55 after publication. Main remains18700dee8ecdda2e457c0aa18c4f83a81b042019; no B correction is claimed released.

The original signed handler returned200 after subscription/tenant persistence failures and could leave partial writes. The route now acknowledges a supported event only after one service-only SECURITY INVOKER transaction confirms its durable receipt and required subscription/live binding/cache state. SQL errors, zero affected rows, missing results and bounded persistence uncertainty return503. Existing selected-secret verification remains unchanged; explicit invalid environments and invalid normalized inputs fail before persistence. Logs contain fixed reason labels.

Exact event replay is idempotent; notificationID is not the deduplication key. Provider event time retains microseconds. Stale state does not roll back current billing state; conflicting equal timestamps and ambiguous legacy clocks fail safely. Only created replaces a known live binding, using immutable provider entity creation order. Sandbox cannot change the global live cache. New public rows use provider createdAt; old public clocks remain unchanged, with consumer-order ambiguity rejected. Non-current receipts do not promise cache/UI agreement. Retained stream identity cannot be reassigned after its public row disappears.

Updated/canceled require a prior public stream row; a later full snapshot cannot reconstruct the original plan, periods or scheduled-cancel history. Missing streams return503 without a receipt, created establishes the row, and an explicit replay applies in provider order. Created retains its original new-row cancel flag defaultfalse, while later cancellation preserves stored periods/flag. Application-domain errors useP0001 so PostgREST14 does not internally retry a refused request after the route times out. See POSTGREST_RETRY_ROOT_CAUSE and the retained failing diagnostics; driver-level/CPU traces are not claimed.

| Boundary | Actual result on the exact executable |
| --- | --- |
| Fresh full50 migration chain |206 unique passing native controls |
| Populated upgrade |53 baseline47 reproduction controls,169 after47→50; exported original data/catalog fingerprints match |
| Frozen compatibility |76 original unit tests/221expectations,22 signed handler controls, types/full lint/original wire/build/clean generation |
| Fault/atomicity | Real SQL errors and RETURNNULL on all four required write targets; all-data invariance and sameevent recovery |
| Ordering/replay | Adjacent microseconds, equal-state/conflict, missing-created recovery, legacy binding/display/identity, concurrent duplicates and ordered updates, deliberately discarded response |
| Authorization | Actual anon/owner/two-staff/disabled-staff/banned/closed JWT denials, private SQL denial, service positives and B2/B3 boundary controls |
| Local advisors |45 WARN (43 auth_rls_initplan,2 multiple_permissive_policies),0 ERROR in each final artifact; raw output retained, no clean-advisor claim |
| Cleanup/egress | Both stacks/status/private state removed; credential-free canary rejected, unexpected IPv4/IPv6 rejects0 |

Three CLI2.101.0-generated forward files preserve every applied predecessor:

- 48 `20261021132651_webhook_persistence_01.sql`: SHA256 `95b527271e552f20bfb8a0e07627e0195ed681c46e3f8cbcb7d5daaa4a98a66d`.
- 49 `20261021134621_webhook_bootstrap_01.sql`: `c905a149d7deb0cb9b22080142152a5a06aa2c982b4ee7f907c63a434cff3f75`.
- 50 `20261021140746_webhook_errors_01.sql`: `a5cff8d91149a61424f1d6cd62bf60cc42a334623085eec7e706ac3b0f38f955`.

All47 original migrations and applied48/49 are exact.349/350 prior protected paths are exact; the intended webhook route is the sole replaced old path. Current identity:358protected/50SQL. The extra paths are the new module, three test/harness files, one workflow and three migrations. Existing package/lock/signature helper/B2/B3 functions and grants are unchanged. DECISIONS records the engineering contract; no financial/trial/cancellation/retention policy or provider API fallback was added.

Earlier188/151-check successes lacked the subsequently discovered cases and remain historical/scoped. d86/f4 failures and independent source findings remain failed rather than relabeled. The final native report, actual function body/ACL and safe pre/post preservation data are under evidence/final-native. No financial rows, production data/secrets, provider call, deployed HTTP/browser acceptance, real late-commit network fault, rollback deployment rehearsal, B5/full-B/RC/release approval or production reconciliation is claimed. See INDEPENDENT_LIMITS and COVERAGE.

General merge verdict remains **Changes required**: DEP-20261021 full audit has11package entries/8distinct GHSA/3High, exit1 on byte-identical dependencies; the preserved A manifest also rejects the B superset. Neither gate was weakened. ONE NEXT is dependency remediation and source-identity reconciliation before B5/B6 acceptance under the canonical plan. B7 requires the owner decision after successful gates. No merge/deploy/PR closure/history rewrite/new spending occurred.
