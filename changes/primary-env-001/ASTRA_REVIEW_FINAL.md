# Independent ENV remediation review — 2026-10-10

Outcome: **Blocked pending missing evidence**. This is not approval for human merge or a release, and does not authorize financial harness execution.

The reviewer inspected the original candidate represented locally by `7c9e0ae` and the subsequent bounded browser-containment remediation. Parent-reported original remote candidate: PR54 `f5db53d430648926daa586993abb8b1c35059d36`. The reviewer independently matched all 13 frozen remediation source blobs below before executing the final regression. A resulting remote amendment SHA was not independently verified in this review; reconcile these blobs to that final candidate before attaching exact-head acceptance.

## Findings disposition

| Finding | Original severity | Final disposition and evidence |
| --- | --- | --- |
| ENV-A1: redirects bypass HTTP route predicates | High | Closed for reviewed boundary. `browser_network_guard.py` uses `route.fetch(max_redirects=0, max_retries=0)`, aborts every 3xx, and never continues an intercepted request directly. Live loopback recorder cases cover navigation 301/302/303/307/308 and POST 307/308 across all four harness policies. |
| ENV-A2: WebSockets bypass HTTP routing | High | Closed for reviewed boundary. Shared context WebSocket routing closes each socket without connecting to a server. All four harnesses install the shared guard before creating pages and retain service-worker blocking. Live recorder cases prove no forbidden WebSocket handshake reaches the fixture. |
| ENV-A3: arbitrary loopback write origins accepted | Medium | Closed for reviewed boundary. Auth/destructive HTTP is restricted to application and configured isolated Supabase origins. Visual policy rejects non-read methods. Alternate-origin POST negatives and allowed API POST positives pass. |
| Rereview: Google Fonts dependency creates false containment failure | Medium | Closed. The application's exact stylesheet URL receives an offline CSS response only for non-navigation GET requests whose resource type is stylesheet. Other methods, fetch GET and navigation to that URL are rejected. The live cases pass for all four profiles. No font-provider fetch occurs in this exception. |
| Rereview: dev/HMR prerequisite conflicts with WebSocket blocking | Medium compatibility issue | Addressed by the documented production-build/local-emulator prerequisite and updated runner messages; HMR and Realtime remain deliberately unsupported. This prerequisite has not been verified against the complete application. |
| Rereview: positive popup claim lacked a corresponding case | Test adequacy | Addressed. Four allowed same-origin popup cases now verify fixture content and recorder receipt. |

No unresolved concrete Critical/High ENV source finding was identified in the final reviewed changes. No concrete defect was found in the current public-key exposure guard, Supabase alias validation, production endpoint exclusion, or baked/runtime identity comparison. Public-key decoding is not credential authentication or proof of project ownership.

## Independent verification actually performed

- Original candidate: `bun test tests/unit` — 60 pass, 0 fail, 125 expectations; `bun tests/gate4/sec-env/probe.ts` — target-green; `bun tests/gate4/sec-env/server-boundary.ts` — 8 passing actual-wrapper/stub-entry scenarios; `node node_modules/typescript/bin/tsc --noEmit` — exit 0.
- Initial source defect: AST-executed pure browser predicates accepted alternate loopback POST origins. No harness body or network operation was executed for that proof.
- Initial remediation: actual Chromium transport regression — 47 scenarios, 0 failures; updated E1–E10 probe — target-green; `git diff --check` — exit 0.
- Final frozen remediation: independently verified all 13 Git blob IDs, then executed `tests/gate4/sec-env/browser-network.py` using the scratch Python/Playwright toolchain and recorded executable/arguments — **Chromium 153.0.8010.0, 67 scenarios, 0 failures, exit 0**. The added font and allowed-popup changes justify this final rerun. Subsequently reviewed and hash-verified the README-only correction distinguishing local/CI emulator flows from preview/staging visual production builds; the table records its final blob. The other 12 source blobs were unchanged; no browser rerun was needed for this documentation clarification.
- Final launch-configuration verification, without source changes: independently inspected `browser-launch-strict.json` to confirm removal of the explicit web-security/site-isolation/insecure-content/SharedArrayBuffer overrides, then reran only the browser transport suite with that changed configuration — **Chromium 153.0.8010.0, 67 scenarios, 0 failures, exit 0**. This supersedes the permissive-launch run as final browser evidence; the historical permissive log remains preserved separately.

The browser probe loads actual pure policies and the shared transport helper without executing application, database or financial harness bodies. Recorder traffic uses dummy data only. Tests measure destination receipt, not only guard return values. The source-wiring assertions supplement direct review but are not end-to-end application evidence.

## Frozen remediation source fingerprints

| Path | Git blob |
| --- | --- |
| `.github/workflows/quality.yml` | `c6c5cb1e66ceb3f2be0ef22de0af6f5f9cc1c92d` |
| `.gitignore` | `0ae00ce43b9dcb0a4c256eab27ae8cbcd06cc38c` |
| `tests/e2e/README.md` | `dec7e4848e5f45f8ad2cdd3c856bd55b80575073` |
| `tests/e2e/isolated-auth-smoke.py` | `a89e812bebed660e7ef29be962807906bdb3bfa0` |
| `tests/e2e/rapid-click-sale.py` | `4d5c2c669cad99f4749f3b179161b26f3ffdd45e` |
| `tests/e2e/run.sh` | `bb21340a1614fcc2e161c6342a501dfb14a88e13` |
| `tests/e2e/sale-dashboard-close.py` | `1a63ea92fe5f6eb9e0d30841954f6742b7ee0de9` |
| `tests/e2e/write_harness_guard.py` | `5cb2435fe47ef5ca5777318643754e5f26c3a3b0` |
| `tests/gate4/sec-env/probe.ts` | `992d3fa7cf62047e823818405cb4ca4e081f6d4b` |
| `tests/visual/mobile-rtl-smoke.py` | `8f9f976654934990414aa15fd6881af1c0fce19c` |
| `tests/e2e/browser_network_guard.py` | `ddebad5aba645cff1aae59b9d1c1e373c51bf598` |
| `tests/gate4/sec-env/browser-network.py` | `8dcd2113208201485ce1b49be509bea457090963` |
| `tests/gate4/sec-env/requirements.txt` | `cecdc6c3450a494085ded0e124ed5c3f7767d843` |

## Acceptance limitations and one next action

Local execution used Python 3.12 / Playwright 1.62.0 with substitute Chromium 153.0.8010.0. Matching Playwright Chromium 151 was unavailable after a failed CDN archive download. The historical substitute run included explicit disabled web-security/site-isolation flags; those overrides were removed for the independently passing final strict-launch run. The final launcher still uses `--no-sandbox`, `--disable-setuid-sandbox` and substitute executable/rendering settings, so it is not evidence of Chromium sandbox protection or an identical hosted runtime. Results prove the exercised interception boundary under that runtime, not matching hosted CI or complete browser egress containment across untested protocols.

The offline font response intentionally yields fallback typography; screenshots do not validate Tajawal or provider availability. Blocking all HTTP redirects and WebSockets is an intentional harness constraint, not production browser behavior. Existing cleanup-RPC usage, financial behavior, dependency acceptance and full-repository lint debt remain outside this remediation and are not newly introduced ENV findings.

Still missing: final remote source reconciliation; successful hosted required checks and matching browser; isolated database/migration/auth/RLS/tenant/disabled-user evidence; complete application and financial correctness/atomicity/concurrency/idempotency evidence; deployment and rollback rehearsal. No tests or approvals are promoted from another environment or earlier head. No production access, database operation, financial harness body, merge or deployment occurred during review. Only this review document was written by the reviewer.

ONE NEXT: reconcile and preserve the final amendment's source/evidence, then obtain the required isolated integration and hosted-check evidence in a capable environment before requesting acceptance. Keep financial write harnesses and release actions blocked meanwhile.
