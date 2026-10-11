# Full local TanStack MCP verification — bounded test-only batch

Planning authorization: [#55/6112713277](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6112713277).
Claim [6112916960](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6112916960).
Draft [PR63](https://github.com/naderalhaje097070-sudo/simple-store-aid/pull/63), basePR62 final26d6e271ad1a50a26390d25d3236edb5ab47fff7. Main unchanged43d6edbccb66fb06ce0fcb93734ad59532d1aeae.

## Proven source and commands

Source3b1a25fda8a11b27559b0e988a7930e6748972fa, [native route run38169721783/job114559594661](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38169721783).
Exact head checkout, bun1.2.14 install --frozen-lockfile, CLI2.101.0 disposable Supabase,
existing43migrations and built app command NITRO_PRESET=node-server bun run build.
Native Node22 serves the real .output/server/index.mjs with Node --import containment preload.
The dedicated UID cannot traverse protected hosted workspace (ROUTE_ORIGINAL_WORKSPACE_READABLE=false).
Only exact standalone .output copied to /tmp/monjez-tanstack-route/.output, module SHA256 matches;
preload copy cmp matches. No custom /mcp or metadata server/adapter call in harness/preload.
Source contract markers + actual metadata/MCP route + observed src/server.ts exact runtime
conflict establish entry/router/adapter provenance. Generated files are unchanged by build.

The original proof and receipts are saved under evidence/native-3b1a25f-*.
This additive candidate adds runtime/metadata receipts and complete consumed-file path filters.
Final exact-source route/Quality/review results are recorded in PR63/#55 after this commit.
No source edits after final required gates; preserve every earlier attempt.

## Results on the proven source

| Scenario | Observed result |
| --- | --- |
| Credential-free OS/preload native redirect self-test | redirect manual302; native follow refused; UID REJECT packets observed; IPv6 deny rule present |
| Normal protected resource and issuer | actual generated metadata200; local resource54325/mcp and issuer54321/auth/v1 |
| Missing/malformed/clientclaimless bearer | explicit401/unauthorized + correct Bearer local metadata challenge |
| Host/forwarded header adversarial requests | metadata issuer pinned; initialize/initialized/catalog success; no issuer/JWKS outbound attempt |
| A and B sessions | initialize200, initialized202 empty, no stateful session required, exact4unique tool catalog |
| A4 then B4 |8/8 successful MCP payloads; HTTP status alone not oracle |
| B ban | actual local Auth admin ban stored; SQL banned_until>now verified |
| Same preban B JWT |4/4 HTTP200 MCP isError=true, exact account_inactive content; never empty/500/timeout proof |
| A after all B attempts |4/4 successful MCP payloads |
| Runtime/build conflict |500; exact configuration error observed twice; no downstream/remote calls; not ban acceptance |
| OS/post-bundle network attempts |app and conflict IPv4/IPv6 reject deltas0; preload unexpected blocked0 |
| Data |22public before/after fingerprints equal after fixture setup;7finance tables0 |
| Secrets and cleanup |known plus generic JWT/key scans clean; fail-closed artifact quarantine tested;3cleanup predicates true |

71/71 controls,16ordered lifecycle observations. SDK actual JWKS requests30 to fixed local path,
REST16; no administrative key in app process. Admin fixtures/ban and SQL are observations,
not substitutes for user MCP path. integration_accepted=false.

## Required checks

[Quality38169721803](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38169721803):
PASS,66unit tests/159assertions, typecheck, changed-source lint selection,
offline server boundary, browser redirect/WebSocket/origin containment and both builds.
Quality used merge-ref2edf3d6501cda70b3bdae4af9965ac65634a40d0;
its tree20988a95488313ffe108e4128264058f3cad18a0 exactly equals candidate tree.
Those offline/stub boundary checks are separately labelled Quality; they are not the full route.
Focused Python shared oracle6/6 and new route9/9 PASS; issuer/crypto6/6 with34assertions PASS.
Local node --check preload and workflow YAML parse PASS. Do not re-run historical210/212/78 suites.
Existing direct handler real-stack workflow was not used as new full-route proof.

## Failed attempts retained

First b6713a2 [run38169531260](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38169531260)
and second df59536 [run38169591638](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38169591638)
failed at credential-free preload import ERR_MODULE_NOT_FOUND; isolated UID lacked hosted
workspace access. Stack/build/MCP steps skipped; cleanup passed. Second was already queued
during security-evidence correction, not a repeated claim of success. Reproduction:
sudo -u mcp-route test -r original workspace guard is false while runner reads same tracked file.
Correction copies exact preload/native build only, keeps all isolation/semantic controls.
No actual application defect was observed; no application repair is proposed or implemented.

## Files, contracts, review, limits and rollback

New tests/account-lifecycle/tanstack_route_build.py: validated native app build, standalone copy/provenance.
New tanstack_route_guard.mjs: containment only, credential-free redirect canary and pre-bundle barrier.
New tanstack_route_probe.py: subclass reuses real fixtures/oracle/init; HTTP protocol/auth/lifecycle/conflict/data/evidence.
New test_tanstack_route_probe.py: adversarial ordering/catalog/denial/secret-quarantine oracle tests.
New .github/workflows/mcp-tanstack-route.yml: exact-source isolated CI, consumed entry/config/test filters, cleanup/artifacts.
New changes/mcp-tanstack-route intake/eight impact files/failure receipts/verification/review/evidence: durable scope and truth.
Additive PROJECT_STATE/TASKS/DECISIONS: current outcome and PR62 final52control reconciliation; preserved history.

Application/API/RPC/schema/migration/dependency/financial/state contracts: no changes.
Independent implementation-separate agent retrieved raw GitHub logs and reran local focused tests.
Medium pre-CI findings (native counters, broad secret scan, artifact quarantine) were fixed; no unresolved
Critical/High/Medium source finding on3b1a25f. Final head review must consume final receipts.
This is separate-agent scoped review, not native human GitHub approval or owner merge permission.

Unverified: Cloudflare/worker binding runtime, public/reverse-proxy policy, production, nonempty
financial data/foreign payload isolation, financial correctness, concurrency/in-flight behavior,
hard-delete/cascades/natural expiry and the broader integration matrix. No integration_accepted=true.
Rollback: close draft or remove test assets via new revert commit; stop UID/server/stack --no-backup
and remove private status; no production/schema rollback. No force/rebase/amend.
ONE NEXT: planning reviews final PR63 evidence and independent closure receipt to select next bounded gate.
