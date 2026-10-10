# PRIMARY-ENV-001 — verification and completion checkpoint

Date:2026-10-10. Repository:naderalhaje0970-droid/simple-store-aid. Candidate only; main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Remote parent is PR53 head54c930166a776828566876771efdec86a997fa53; reuse source is PR48 head31958e53438b377a9896dd0bf7e9c268c1f14aef. Exact tested application/config/test/workflow Git blob fingerprints and raw proof hashes are in evidence.json. The new PR body records resulting immutable remote commit.

## Outcome and root cause

Prepared fail-closed environment isolation by reconciling existing PR48 implementation onto the unchanged generated PR53 dependency candidate. Baseline probe proved implicit production fallback: E1/E2/E3 exit42. Two additional safety gaps were found during implementation self-check: privileged-public-key formats were accepted (three failing synthetic regressions), and page-only interception did not cover other context pages/popups. Reconciliation also fixed a test-fixture issue: inherited Proxy variables correctly blocked safe preflights, producing E7; safe fixtures now remove routing and explicitly test all six proxy variables as negative cases.

This is not independent review or accepted delivery on main. Astra was attempted once and stopped at usage limit before reviewing source. Outcome: **Blocked pending missing evidence**.

## Changed paths and reasons

| Paths | Reason |
| --- | --- |
| .env.example; config/supabase-build-config.ts | Explicit deployment target, dedicated environment identity, alias/URL validation and public-key exposure guard |
| vite.config.ts; src/server.ts | One Lovable wrapper, validated browser defines, baked/runtime match before lazy app entry, binding conflicts fail closed |
| .github/workflows/{quality,isolated-auth-smoke,sec-ci-gate4-probe,sec-env-gate4-probe}.yml | Reuse PR48 explicit isolated fixtures/negative probes; add offline real-wrapper probe to Quality |
| tests/unit/supabase-build-config.test.ts; supabase-public-key.test.ts | Changed fail-closed contract and before/after privileged-key negatives; financial/dependency tests retained |
| tests/gate4/sec-env/{probe,server-boundary}.ts | E1-E10 inventory/preflight matrix, proxy negatives/context wiring, actual wrapper integration with stub app |
| tests/e2e/{README.md,isolated-auth-smoke.py,rapid-click-sale.py,run.sh,sale-dashboard-close.py,write_harness_guard.py} | Preflight before credentials/network, write intent/loopback/proxy/psql checks; context routing |
| tests/financial-rules/run.sh; tests/visual/mobile-rtl-smoke.py | Reuse isolated PostgreSQL routing and canonical visual production exclusion |
| PROJECT_STATE.md; TASKS.md; DECISIONS.md; changes/primary-env-001/* | Current checkpoint, blockers, review status, impact/design/rollback/provenance and actual raw evidence |

No package, lock, finance-domain, RPC, schema, applied migration or financial policy change in this packet. Public-key formats are an exposure guard, not provider credential authentication. Legacy anon JWT and modern publishable formats remain supported; opaque offline fixtures are not evidence of valid provider keys.

## Commands actually executed

Commands below ran in the separate isolated worktree with Bun1.2.14, Node24.19.0 and installed PR53 dependencies. No install/audit regeneration was needed; package/lock blob IDs remained unchanged. Logs under proof/ retain baseline and intermediate failures.

| Command/check | Actual result |
| --- | --- |
| Original `bun tests/gate4/sec-env/probe.ts` before PR48 reuse | exit42; E1/E2/E3 expected-red; no connection |
| `bun test tests/unit` immediately after reuse | 56 pass/0 fail;120 expectations |
| Initial reused Gate4 probe | exit1/E7; inherited Proxy variables contaminated positive fixtures; preserved |
| `bun test tests/unit/supabase-public-key.test.ts` before fix | 3 fail/1 pass; synthetic secret/privileged JWT accepted |
| Final `bun test tests/unit` | **60 pass/0 fail;125 expectations**, five files |
| Final `bun tests/gate4/sec-env/probe.ts` | **exit0 target-green E1-E10**, only pure resolver/preflight paths |
| `bun tests/gate4/sec-env/server-boundary.ts` | **8 pass** using actual server wrapper + stub app entry; no network/database |
| `node node_modules/typescript/bin/tsc --noEmit` | exit0 |
| ESLint for config,server,vite,Gate4 probe/wrapper probe and both environment unit files | exit0; full repository lint not claimed |
| `node node_modules/vite/bin/vite.js build` with a minimal clean env and synthetic ci loopback values | exit0 |
| Same build with `--mode sec-env-contract`, values loaded from temporary mode env file, process config unset | exit0; fixture file removed |
| Python AST parse of all E2E/visual files; `bash -n tests/e2e/run.sh tests/financial-rules/run.sh` | five Python files/two shell runners pass; no harness bodies executed |
| `git diff --check` | exit0 |
| YAML parse of all five workflows and `bash -n` for embedded bash run steps | passed; syntax only, not hosted execution |
| Git blob hash checks for package.json,bun.lock | match verified PR53; no dependency mutation |

Build commands ran through a Python subprocess wrapper to supply only PATH/HOME and fixture values, capture return codes/logs and remove the temporary mode file. Existing warnings remain: large chunks and PWA glob/precache mismatch/empty precache; builds do not prove offline release behavior. No repeated hosted jobs were triggered manually.

## Acceptance and remaining evidence

Passed locally: missing/unsafe config fails closed; non-production rejects known production identity; aliases/target and baked/runtime mismatch denied; privileged public-key fixtures rejected; positive/negative harness preflight and explicit proxy routing tests; wrapper rejection before stub app response; syntax/type/lint/build checks above.

**Not verified:** independent exact-candidate review; hosted five required checks; real isolated database existence and migration chain; real Playwright popup/interception behavior; outbound browser/WebSocket/redirect containment; application auth/RLS/tenant/disabled-user behavior; service-role ownership; financial stored values/atomicity/concurrency/idempotency; deployment/rollback/PWA behavior. Existing PR53 security/full-lint acceptance blockers and11Moderate/5Low audit findings remain open. Local E1-E10 assertions include source wiring and are not substitutes for browser/database execution.

GitHub billing clarification from the preceding authorized account inspection: October billed$0, no payment history/outstanding invoice observed, Actions budget$0 with stop-usage. Quota/spending restriction is supported; an unpaid invoice was not proven. No account payment/spending settings changed.

## Rollback and next task

Before merge, close this new draft candidate if rejected; preserve PR48/PR53/main. After authorized human merge, revert the additive ENV commit through a reviewed PR and rebuild a prior accepted environment-specific artifact. No data rollback is necessary because no writes/migrations ran; actual release rollback still needs rehearsal.

**ONE NEXT:** independent review of the exact candidate when reviewer capacity is available, followed by any fixes and required isolated integration/CI evidence. Write-capable financial tests remain blocked. No production access, merge or deploy performed.
