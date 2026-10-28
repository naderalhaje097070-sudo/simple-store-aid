# B4 / APP-02 verification ledger

Scope: signed subscription callbacks through the actual route, existing verification helper, locked Paddle3.8.0 and Supabase2.110.5, disposable loopback database. This is neither deployed HTTP/browser testing nor a real provider integration. Original financial, paywall, retention and release gates remain open.

| Contract | Direct evidence required | State |
| --- | --- | --- |
| Original false200/partial persistence | Actual old route on47; each real SQL fault and a missing updated target | Final50 runtime PASS |
| Atomic receipt/subscription/live binding/cache | Error and zero-row triggers on all four targets, full snapshot equality, recovery sameevent | Final50 runtime PASS |
| Deduplication/lost reply/concurrency | Alternate notificationID, exacteventID replay, ID conflict, eight simultaneous duplicate deliveries and concurrent ordered snapshots | Final50 runtime PASS |
| Provider ordering and precision | Adjacent microseconds; equal state/cross eventtype; ambiguous conflict; >6digits rejected | Final50 runtime PASS |
| Subscription binding and old consumer | Missing stream updated/canceled503→created→explicit replay; late created for an existing legacy stream uses newest state; old canceled stream cannot rebind; equal entity times; legacy public-clock guard in both environments | Final50 runtime PASS |
| Legacy floor/recovery | Preserve original timestamp/floor through matching/no-op repair; differing unknown old state503; subsequent known event/stale handling | Final50 runtime PASS |
| Durable identity | Cross-owner/customer/createdAt/environment rejects; retained receipt after public fixture removal cannot reassign identity | Final50 runtime PASS |
| Secret/environment selection | Actual SDK signature; live/sandbox isolation; wrong secret400; invalid environment400; no DB mutation | Local22 and final50 native PASS |
| Least privilege and previous B2/B3 | Real anon/two owners/two staff/disabled staff/banned/closed JWT denial; actual private SQL denial; servicepositive and prior scanner/tenant-write controls | Final50 runtime PASS |
| Source/migration preservation | Existing47 migrations and applied48/49 remain exact;349/350 prior protected paths exact, intended webhook route replacement only;358 protected/50SQL | Final source358/50 verified; final50 runtime PASS; independent final scoped review complete, APP-02 accepted on candidate only; whole-head Changes required |
| Frozen app compatibility | Existing76 unit tests,22 signed handler controls, typecheck/full lint/original wire/build/clean generated files |f3b70244/run39614265434/job119270964453 PASS76+22/types/lint/wire/build/invariance |
| General merge gates | Full dependency audit and preserved A source manifest | Changes required:11 package entries/8GHSA/3High; old manifest rejects B superset |

Original failing source review and its correction addendum remain under review/. Native attempt39608299485 preserves the shallow-history baseline failure; no upgrade acceptance is inferred. The first generated SQL proposal was never applied; generator-final contains the chosen CLI-produced file and hash. No historical suite is relabeled as a current-head result.

Final correction50 removes application40001 to prevent PostgREST14 internal retries. The late-mutation diagnostic failures on d86/f4 are preserved and supersede any early complete-snapshot acceptance. Final no-late-receipt, created defaultfalse, plan/price and canceled period/flag checks must pass. Updated/canceled equal-creation negative cases stop at the missing-stream guard; only created reaches the distinct-stream tie branch. See POSTGREST_RETRY_ROOT_CAUSE and INDEPENDENT_LIMITS.

Final native39614265434 on f3b702440a4ffd17038f3c668a2f446620a97919: fresh206; baseline47 has53 passing reproduction controls; populated after50 has169. All original pre/post fingerprints and old catalog hashes match in exported populated-preservation.json. Cleanup removes private status/state and full stacks; unexpected IPv4/IPv6 rejects0. No financial rows in fixtures. Final independent review is `review/FINAL_B4_REVIEW.md`, with stored-evidence replay and explicit limits; publication preservation is recorded externally in #55; whole-B merge/RC remains blocked.

Final local advisors contain45WARN per artifact (43auth_rls_initplan,2multiple_permissive_policies),0ERROR. These outputs are preserved; they are not a clean-advisor or full-B performance acceptance.
