# G0-HONO-01 — bounded candidate handoff

Hono alone is patched from4.12.27 to4.13.7 on existing Draft PR72. Its eight targeted advisory IDs are absent from the fresh audit. Existing adapter compatibility and protection checks pass. **G0 and the whole PR remain blocked:** full lint violations and eight other audit findings are not waived. No merge, release or deployment approval.

Repository naderalhaje097070-sudo/simple-store-aid; branch `test/g0-g1-acceptance-runtime-2026-10-14`; base89606268234724241065fdd0a8abe84467dd8b51 above PR54/57fb508b9d239aaf4676352dd97654341416c46a. Main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Sole claim55/6199980098 closes only in the final linked issue handoff. No additional PR.

## Exact source and verification

Executed final source: **e38cf18d007ebaa6f9a9c0e314283a33960d89db**. Final delivery adds only documentation, root checkpoints and evidence; all executable files/package/lock match that tested source. The final publication head is recorded in55/70, not inferred from an ancestor check.

| Evidence | Actual result and identity |
| --- | --- |
| [Preparation38790485483/job116613440057](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38790485483/job/116613440057) | SUCCESS on c460c1dcf0f6ae434f28bf91885a8f5bb2cf9a1d; official npm @oven/bun-linux-x64-baseline1.4.0 integrity matches LOCK_REGENERATION; revision34cbb9a40. Temp-directory `bun update hono --lockfile-only --ignore-scripts`,120s timeout,148ms actual,959 packages reported by Bun. |
| [Final bounded38791526145/job116617020439](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38791526145/job/116617020439) | Executed e38cf18d. Frozen Bun1.2.14/Node22.23.3, exact graph, five guard mutation cases, vendor manifests/import scan, detailed lint measurements all PASS. Audit scanner1.4.0 supported/verified; audit exit1 and job FAILURE due solely to eight remaining findings. No parser/tool error in this run. |
| [Final executed-source Quality38791533893/job116617047729](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38791533893/job/116617047729) | SUCCESS:61 units/129 expectations including all four unchanged MCP adapter tests; typecheck, changed-source lint,8 offline wrapper cases,67 dummy browser containment cases, both isolated builds. Actual checkout synthetic569cae5b46337fe5a364d3a455a1156feb2fe399 has the same Git tree as e38cf18d. This is not an actual merge. |
| [Audit-only38791274700/job116616149653](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38791274700/job/116616149653) | Supported official Bun1.4.0 audit on3a94c86d4a9c1fef75b3f93520e35db54fa84586, same package/lock/security test as final. Same eight remaining IDs, exit1/FAILURE retained. |
| Preserved failed preparation checks | Quality38790489064/job116613453570 failed frozen install while the manifest preceded generated lock; no false success. First bounded38790980313/job116615137571 passed frozen/graph/mutations/vendor/lint but Bun1.2.14 lacks audit (`Script not found "audit"`), then JSON parsing failed. This was a tool failure, not a scan or clean result. The verified supported scanner corrects it without package upgrades. |
| Earlier compatible source check | Quality38790990927/job116615172750 SUCCESS on synthetic8aaf5696354a24e674e8f398428d08af7ecfec49, tree equal ce5da9ef3fe9a966f1e01011ef23cd52471e1831. Only audit workflow/config changed afterward. Automatic Quality38791282341 is also retained; no historical manual rerun. |

## Proven cause and minimum correction

The existing graph resolves one vulnerable Hono4.12.27 through Lovable MCP0.20.1→SDK1.31.0, whose dependency accepts ^4.11.4. The tagged [official Hono4.13.7 release](https://github.com/honojs/hono/releases/tag/v4.13.7) is stable, published2026-09-04; tagged manifest has no runtime dependencies and requires Node>=16.9. Official registry generation and frozen install prove availability/integrity, rather than relying only on a release tag. Existing node-server1.19.14 peer accepts Hono^4.

`package.json` adds only paired hono4.13.7 overrides/resolutions, no direct dependency. The complete generator-owned lock is adopted byte-for-byte, never hand-edited or spliced. Lock blob53af3224f706081966e756916c155a6874ce613e; SHA2562d43c022595374bbef83cada6c2cdac265086e36cd58c91fc3f7b097ce7f06aa. Full diff in lock.diff: override addition and one package entry (version/integrity/registry-default tarball representation). Every other package record and workspace remains identical; no SDK/Lovable/other dependency upgrades or release-age changes.

`tests/unit/dependency-security.test.ts` adds Hono only to the existing per-major all-copy map: major4 floor4.13.7, stable three-part versions. Existing floors and brace-expansion major guards are unchanged. The disposable-copy test accepts patched graph and rejects4.13.6, prerelease4.13.7-rc.1, major5, and a nested old4.12.27 copy. These are guard mutations, not manual edits to the adopted lock.

Three branch/path-scoped CI workflows plus `tests/g0-hono/verify.py` provide generator, missing diagnostics and supported audit evidence because local Bun was absent and the registry probe previously403. Preparation and audit-only runs preserve their exact purposes; the reusable bounded verifier now keeps CI Bun1.2.14 for frozen compatibility and switches only the scanner to verified1.4.0 before audit. Contents-read permissions, no persisted checkout credential, no project/service credentials or database. Existing Quality/G0/G1 rules, lint exceptions and acceptance criteria are untouched.

## Complete audit, no waiver

Full raw final JSON is audit-full.json, unfiltered stderr audit-stderr.txt, raw exit/hash receipt audit-receipt.json, structured IDs audit-summary.json. Same raw files remain in verification-final.zip. Scanner exit **1** remains a real failing gate; report does not require a fixed total. No Critical/High or newly reported GHSA appears relative to the archived sixteen-ID baseline in this scan.

Removed targeted IDs: GHSA-8j4g-w8fx-2239, GHSA-f23p-vx2j-j53r, GHSA-79qm-7rj5-m7r9, GHSA-54fx-42gc-7vw4, GHSA-gqvv-2mrq-wpjv, GHSA-g6gw-c38x-mqfc, GHSA-crvj-82cr-hjcx, GHSA-hxh3-vqpv-xpqv. **All eight absent**, no Hono finding remains in this result.

| Remaining package | Severity | Exact GHSA |
| --- | --- | --- |
| @babel/core | Low | GHSA-4x5r-pxfx-6jf8 |
| @hono/node-server | Moderate | GHSA-frvp-7c67-39w9 |
| dompurify | Low | GHSA-c2j3-45gr-mqc4 |
| dompurify | Moderate | GHSA-55q2-fjhq-7xh7 |
| dompurify | Low | GHSA-6688-9rhm-gjv2 |
| esbuild | Low | GHSA-g7r4-m6w7-qqqr |
| qs | Moderate | GHSA-x5fp-wj9c-mxmx |
| qs | Moderate | GHSA-4mjr-xmp4-gh2g |

No dev dependency is assumed safe, no exploitation/absence of exposure is inferred from the scanner alone, and no risk acceptance is granted.

## Used paths and limits of compatibility

Installed manifests prove Hono4.13.7, SDK1.31.0, node-server1.19.14 and Lovable0.20.1. App imports use the existing Lovable TanStack adapters and Vite plugin; no direct application Hono import was added. The installed Lovable protocol chunk references SDK `server/mcp.js` and `server/webStandardStreamableHttp.js`. Observed Hono/cors imports occur in SDK Hono examples, and Hono MIME utilities in node-server serve-static. vendor-imports.json is a bounded textual import inventory, which can include comments; it is **not** a whole-program reachability or bundle exclusion proof.

The unchanged four MCP fixtures actually exercise the installed Lovable adapter/SDK: initialize200, tools/list plus synthetic echo call, invalid input with no handler invocation, and missing bearer401 without contacting an issuer. They do not invoke application tools, validate live OAuth/tenant state, or exercise Hono SSR helpers. Typecheck/build and existing environment wrapper/browser fixtures found no regression within their covered boundaries. Later PR62/64 MCP route fixes, lifecycle branches and PR49/50 are not part of this candidate or credited as tests here.

No G1 database/SSR/Auth runtime was rerun. Prior40/40 belongs to dbc870fcc278781b650860273ac4e1116f629f85 and its old lock. Unchanged harness/firewall facts can be reused only within that identity. Legacy `capture.py identity` still compares383 PR54 blobs and allows only four original doc/workflow overrides: it intentionally rejects the newly changed package/lock/security-test content. Its manifest and guards are not widened to make this patch look like G1 acceptance. Before any future integrated G1 run, planning must approve a bounded baseline/identity reconciliation and affected runtime proof; this is a future G1 blocker, not evidence of a Hono regression.

## Lint measurement only

Detailed per-message output and raw exit1 receipts are retained as lint-detail.json inside both verification archives; no write/format flag or rule change. `app.tsx` is restored byte-for-byte after a temporary same-path main comparison on the disposable runner.

| Measured file/version | Errors | Warnings | Composition |
| --- | ---: | ---: | --- |
| tests/g01-acceptance/dns_trace.cjs |16|0|16 prettier/prettier |
| tests/g01-acceptance/test_cf_fetch.cjs |41|0|41 prettier/prettier |
| candidate app.tsx |340|1|323 prettier,16 no-explicit-any,1 no-unused-expressions;1 hooks warning |
| main43d6edb app.tsx, same config/tools/path |340|1|same composition and message locations/text; only formatter fix byte ranges shift with the two-line type/import change |

All341 app diagnostic records compare equal after omitting only fix byte-offset ranges. This closes the requested bounded measurement gap; it is not a current full-repository lint execution. Historical1117/13 plus these57 CJS formatting errors is not presented as a fresh full count. Existing broad lint and remaining audit findings keep G0 open. Quality changed-file lint success does not replace them.

## Evidence, review, rollback and next

artifact-index.json lists five permanent ZIP archives and SHA256 values. It includes failed tool/frozen evidence and complete job logs. Every archive member was scanned for JWT/provider-key/private-key patterns before publication; no matching credentials. This bounded scan is not a universal secret detector. No production/customer/Paddle or DB connection/secret was used. All application and41 SQL blobs match8960; original history and PR48 are retained.

Independent review is in REVIEW.md: distinguish commands the reviewer actually ran from hosted logs/artifacts reviewed. It does not provide human release approval. See separate impact records and INTAKE for authorized scope.

Candidate rollback: additive revert of this batch followed by frozen install and adapter/typecheck/build verification; no schema/data compensation. It restores vulnerable Hono and is not an acceptable production remedy. Production was never changed.

**ONE NEXT:** planning reviews this bounded result and chooses the next separate G0 remediation/risk disposition, preserving remaining audit/lint and future G1 identity requirements. The worker stops after55/70 handoff; no automatic next phase, merge or deploy.
