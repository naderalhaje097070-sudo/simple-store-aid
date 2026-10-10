# PRIMARY-ENV-001 — browser containment remediation

Date:2026-10-10. This checkpoint supersedes the initial packet's browser/reviewer scheduling claims in VERIFICATION.md; the original evidence remains historical. Extended existing draft PR54 from remote head `f5db53d430648926daa586993abb8b1c35059d36`. Main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. Source Git blob IDs and raw proof hashes are in remediation-evidence.json; application dependency blobs are unchanged.

## Defects and bounded corrections

Independent Astra review found three transport defects: browser redirect chains bypassed the initial route check (ENV-A1, High); WebSocket handshakes had no interception (ENV-A2, High); auth/destructive policies accepted unrelated loopback schemes/ports (ENV-A3, Medium). The original actual browser regression reproduced36 failures across47 scenarios; browser-before.log is preserved.

One shared standard-library helper is now installed at context scope before pages. It fetches without redirects or retries, aborts every3xx before a browser response, and closes routed WebSockets without connecting. Auth/destructive HTTP accepts only the exact configured app and Supabase origins. The visual harness stays read-only. Failures produce reason codes, not sensitive request URLs.

Astra's rereview identified a compatibility defect: the existing root page imports a Google Fonts stylesheet, which the stricter policy would mark as a violation. The helper now supplies empty CSS offline for that exact URL only when it is a non-navigation stylesheet GET. POST, navigation and fetch-GET to that URL are blocked. No remote font request is needed; screenshots use fallback fonts and do not prove final Tajawal typography. Documentation now requires the production-built local emulator because Vite HMR would violate the WebSocket policy. Application source, finance, schema and package graph are unchanged.

## Actual verification

| Check | Result and scope |
| --- | --- |
| Original real-browser fixture |47 scenarios;36 failures; exit1; actual legacy handlers/policies, disposable loopback recorders |
| First corrected browser fixture |47 scenarios;0 failures; reviewer independently reproduced this result |
| Allowed-popup expansion |51 scenarios;0 failures; four actual same-origin popup positives |
| Final expanded fixture |**67 scenarios;0 failures; exit0**; adds offline font stylesheet success and POST/navigation/wrong-resource negatives for each profile |
| Gate4 E1–E10 | target-green exit0 after transport source/wiring updates |
| Changed TypeScript ESLint | exit0 for the changed Gate4 probe |
| Python/shell syntax | seven affected Python ASTs and E2E runner bash syntax passed; no financial harness bodies imported |
| Workflow syntax | updated Quality YAML parses; embedded Bash syntax checked; no hosted step execution claimed |
| `git diff --check` | exit0 |
| Prior application/unit/wrapper/type/build evidence | unchanged source baseline60 unit tests/125 expectations,8 wrapper/stub cases, typecheck and two isolated builds; implementation did not rerun unchanged builds; Astra independently checked prior baseline |

The browser test uses Python3.12.14/Playwright1.62.0 with scratch-pinned Chromium153.0.8010.0 from `@sparticuz/chromium`153.0.0 after the matching Chromium151 CDN archive failed. Version/hash/alternative are explicit in browser-toolchain.json. CI installs the pinned Playwright browser normally; this local alternative does not establish matching hosted compatibility. No app dependency or lock regeneration occurred.

Redirect cases cover301/302/303/307/308 navigation and307/308 POST. Recorder hit counts detect escape; redirect reason codes are asserted. Other cases cover unrelated-origin POST, blocked WebSocket handshake, forbidden popup, permitted app navigation/popup and permitted dummy local API POST. Font tests use the real browser's stylesheet resource classification. All traffic bodies are dummy; fixture ports8080/54321 and a random sink are disposable and must be free. No application, Auth, Supabase, RLS, tenant, SQL or financial writes were exercised.

An intermediate failed after-test was a disposable page navigation race, preserved in browser-after-intermediate.log. The fixture now closes each aborted navigation page before the next case; containment assertions were retained. browser-after-47.log preserves the earlier passing run; the51-case success was observed in the tool result but its raw file was superseded by the67-case expansion. browser-after.log is the final67-case run; no raw51 log is claimed.

## Review, acceptance and rollback

See ASTRA_REVIEW_INITIAL.md, ASTRA_REVIEW_FINAL.md and REVIEW.md for independent findings and bounded disposition. Release acceptance remains **Blocked pending missing evidence**: real isolated database/migrations/auth/RLS/tenant/financial integration, matching hosted browser/required checks, prior security/full-lint disposition and actual rollback rehearsal. Remaining11Moderate/5Low audit findings are not waived.

Rollback before release is an additive revert of this remediation through the reviewed branch; never use the original unsafe harness to bypass a failing boundary. No data rollback ran or was needed because no app/DB writes occurred. Next execution is the isolated environment sequence in ISOLATED_STACK_READINESS.md. No merge, deploy, production access or financial acceptance.
