# G0-QS-01 — bounded candidate handoff

The qs-only candidate updates6.15.3→6.16.0 and removes the two targeted Moderate advisory IDs. The same actual-installed contracts demonstrate the old defects and patched behavior; ordinary parent compatibility remains covered. **G0 remains open:** remaining audit and inherited lint findings are not waived, and no live G1 acceptance is granted to the new lock.

Canonical repository naderalhaje097070-sudo/simple-store-aid, existing Draft PR72, branch `test/g0-g1-acceptance-runtime-2026-10-14`. Starting head15710d48301e4130ece09c733b1f102ade20501f above PR54/57fb508b9d239aaf4676352dd97654341416c46a. Main43d6edbccb66fb06ce0fcb93734ad59532d1aeae unchanged. Sole claim55/6201151721 closes at the final linked55/70 handoff; no additional PR.

Executed patched source: **fc6d621e955d3666ecc0e7fbc79dd402f39b3ee8**. Final publication after it changes only documentation/evidence/root checkpoints; exact final head and final-head automatic Quality observation are recorded in55/70.

## Cause, official verification and exact graph

The starting graph resolves qs6.15.3 through SDK1.31.0→Express5.2.1, plus Express→body-parser2.3.0. Actual locked and installed manifests show qs ranges^6.14.0 and^6.15.2 respectively; both include6.16.0. Parent versions and SDK/Lovable/Hono are unchanged. Official [tagged manifest](https://github.com/ljharb/qs/blob/v6.16.0/package.json) and [release changelog](https://github.com/ljharb/qs/blob/v6.16.0/CHANGELOG.md) confirm stable6.16.0, unchanged runtime dependencies, and the parser/serializer fixes. The specific [array-limit advisory](https://github.com/advisories/GHSA-x5fp-wj9c-mxmx) and [isBuffer advisory](https://github.com/ljharb/qs/security/advisories/GHSA-4mjr-xmp4-gh2g) identify6.16.0 as patched. Registry generation and actual frozen installation establish availability, not just a tag.

The two defects are: a comma-separated bracket-array input escaping a configured strict limit; and query data retained under plainObjects/allowPrototypes causing stringify to call a non-function constructor.isBuffer. The tests establish these library behaviors, not exploitation of a production application route. arrayLimit is not claimed to be a universal array element cap; the strict comma+throwOnLimitExceeded configuration is explicit.

Only paired qs6.16.0 overrides/resolutions are added to package.json; no direct qs dependency. Official npm @oven/bun-linux-x64-baseline1.4.0, approved SHA512 from LOCK_REGENERATION and revision34cbb9a40, generated the complete lock in a temp directory from exact15710 lock and unchanged bunfig. Command: `bun update qs --lockfile-only --ignore-scripts`,120s timeout,177ms actual; Bun reports959 packages. Root manifest/lock remained unchanged during preparation, so no pre-lock manifest mismatch was introduced.

Adopted lock Git blob **ae751828a88ffb99a782cae124cb8021d1df1c45**, SHA256 **8af21cc34673e16227dc5f53ba06b26692c15f8081b46f09108eb1d2fe7be2ed**. Full lock.diff and graph.json prove only the qs record/version/integrity/registry-default tarball representation and qs override change. All other records/workspaces match the base. No hand editing/splicing of generated entries, no other package or release-age change. No Express/body-parser/SDK upgrade.

## Executed evidence

| Run and exact source | Actual result |
| --- | --- |
| [Baseline/preparation38799321349/job116643907603](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38799321349/job/116643907603), d5a5178369d8506eeaccae1e2640e7d493173987 | Frozen original graph succeeds. Actual qs6.15.3 Node TAP15:12 ordinary cases pass, exactly3 targeted cases fail,0 skipped, raw exit1. Explicit EXPECTED-RED control verifies exact failures and messages, not product acceptance. Official generator/provenance succeeds afterward. |
| [Patched38799630354/job116644968614](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38799630354/job/116644968614), fc6d621e955d3666ecc0e7fbc79dd402f39b3ee8 | Frozen Bun1.2.14, Node22.23.3, exact graph, **15/15 installed Node contracts**,6 guard controls, affected CJS/TS lint and tracked-source invariance PASS. Full audit with supported Bun1.4.0 returns1 for remaining findings, so job is correctly **FAILURE**; no tool/parser failure. |
| [Executed-source Quality38799635683/job116644987451](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38799635683/job/116644987451) | SUCCESS:62unit/133expect including all4 existing MCP adapter cases; typecheck/changed-source lint,8offline server-wrapper cases,67dummy browser containment cases and2 isolated builds. Actual checkout synthetic42c4a6a657f0cf98f6dfefac56e5c6370488acf9 has treebba877db53c61f8355578f132565c06f8a5c11c9, equal to testedfc6. This is not an actual merge or live G1. |

Full raw TAP/stdout/stderr/exit/hash receipts and installed parent/SDK manifests are retained in preparation.zip and verification.zip. The baseline and patched CJS tests differ only in line wrapping/trailing commas; no assertion or expected data was changed to make the patch pass.

The15 tests cover:
- Indexed, bracket and repeated-key arrays; nested values; flat/bracket comma groups exactly at limit3; ordinary flat strict overflow rejection.
- GHSA-x5fp-wj9c-mxmx: four comma values under bracket notation must throw RangeError at configured limit3. It does not throw on installed6.15.3 and does on6.16.0.
- GHSA-4mjr-xmp4-gh2g: two option-specific parse→stringify round trips retain the own constructor.isBuffer string and produce the exact encoded input, with no prototype pollution. Both old runs throw the documented non-callable TypeError; both patched runs preserve data and succeed.
- Ordinary nested boolean/empty/array parse/stringify and Buffer serialization.
- Installed Express and body-parser resolve the identical qs module object; exact parent versions remain5.2.1/2.3.0. Real Express extended GET query and body-parser extended POST form requests return200 with exact expected arrays/nesting on ephemeral127.0.0.1 only, with bounded timeouts and server close in finally.

`tests/unit/dependency-security.test.ts` adds qs only to the existing all-copy stable-major map: major6 with floor6.16.0. The Hono4.13.7, brace-expansion and all other guards remain unchanged. Disposable fixtures accept the patched lock and reject old qs, prerelease, major7, an extra nested vulnerable qs copy, and old Hono4.13.6 (exits0/1/1/1/1/1). These are temporary negative test inputs, not edits to the adopted lock. Existing full unit/MCP tests remain mandatory; four synthetic MCP tests do not prove live app tools/OAuth/tenant behavior.

Two scoped read-only preparation/verification workflows and tests/g0-qs/evidence.py provide missing evidence because local Bun/dependencies are absent. The recorder reuses the existing unchanged Hono command/audit helper with separate output directory and target IDs; raw nonzero audit remains a failing G0 gate. CI Bun1.2.14 proves frozen compatibility; only the audit scanner switches to already verified1.4.0. No credential/service/DB or deployment step. Existing Quality/G0/G1 workflows and lint exceptions are unchanged; explicit lint includes the new CJS fixture despite Quality's existing CJS omission. No broad lint rerun/cleanup.

## Complete fresh audit and remaining blockers

Raw audit-full.json, audit-stderr.txt, audit-receipt.json and audit-summary.json preserve the complete result and exit **1**. audit-comparison.json compares the previous Hono packet's actual eight-ID result with this scan: exactly **GHSA-x5fp-wj9c-mxmx** and **GHSA-4mjr-xmp4-gh2g** disappear. No new ID or Critical/High is reported in this observation. No fixed residual-count acceptance rule is used.

| Remaining package | Severity | GHSA |
| --- | --- | --- |
| @babel/core | Low | GHSA-4x5r-pxfx-6jf8 |
| @hono/node-server | Moderate | GHSA-frvp-7c67-39w9 |
| dompurify | Low | GHSA-c2j3-45gr-mqc4 |
| dompurify | Moderate | GHSA-55q2-fjhq-7xh7 |
| dompurify | Low | GHSA-6688-9rhm-gjv2 |
| esbuild | Low | GHSA-g7r4-m6w7-qqqr |

Observed remainder is6 findings,2Moderate/4Low. None is waived or assumed safe as a development dependency; the whole G0 audit still fails. Historical lint blockers and their prior measurement stay open; no fresh full lint total is claimed or remeasured. Separate engineering/risk decisions remain planning-owned.

## Source identity, affected revalidation and limits

No live G1/database/SSR/Auth/network-counter/cleanup acceptance was rerun or credited to this lock. Prior40/40 belongs to dbc870 and its old dependency graph. The new isolated Node HTTP parent fixtures and unchanged Quality offline/browser boundaries cover only their stated synthetic contracts. They do not prove actual Nitro/Cloudflare app route integration, hostile production request exposure, full dependency reachability, live OAuth/RLS/financial state or later branch tests.

Before accepting future integration on the new lock, explicitly reconcile the source54 manifest/383-blob identity check (currently permits only four historical doc/workflow overrides) against the approved package/lock/security-test/checkpoint changes. Keep the old fail-closed guard unchanged in this batch; do not merely allowlist new files to obtain green. Review/freeze the new source and run affected actual transport/query/form/SSR/Auth/environment proof as selected by the integration scope, including its required isolation/data/counter/secrets/cleanup contracts. No old G1 pass substitutes for this. Hono evidence also stays at its own recorded source.

All app/41SQL blobs and financial/account contracts are unchanged from15710. PR49/50/lifecycle/later MCP branches are not imported, PR48 remains open, main unchanged. No customer/production/Paddle, migration, merge, deploy or launch approval.

## Review, evidence and rollback

Independent focused review is in REVIEW.md; it separates actual reviewer reexecution from logs/artifacts inspected and does not provide human approval. artifact-index.json lists durable ZIP hashes and bounded JWT/provider-key/private-key pattern scans of all uncompressed members. No project credentials or customer data were used; this is not a universal secret detector. Preserve the red baseline rather than relabel it successful security behavior.

Rollback: additive revert of this batch's candidate pins/generated lock/guards/test tooling, then frozen install and parent/MCP/typecheck/build verification. This restores vulnerable qs and is not an acceptable production remedy. Production was unchanged; no data compensation is applicable.

**ONE NEXT:** planning reviews this bounded candidate and selects one separate remaining G0 remediation/risk disposition. The worker closes the claim in55/70 and stops; no automatic next phase or G1 rerun.
