# G0-DOMPURIFY-01 — bounded candidate handoff

DOMPurify alone is upgraded3.4.11→3.4.16 on existing DraftPR72. Actual installed-browser cases show the five targeted old failures and10/10 patched success. The unchanged real invoice exporter produces a valid local synthetic PDF. All three target advisory IDs disappear; **G0 remains open** for three other advisories and inherited lint, and no G1 acceptance is granted to this new lock. This candidate is Implemented/Tested, not Merged/Released.

Canonical repository naderalhaje097070-sudo/simple-store-aid. Branch `test/g0-g1-acceptance-runtime-2026-10-14`, starting5623a6ea09101dfa97f36909a66d8ea3a81956f4 abovePR54/57fb508b9d239aaf4676352dd97654341416c46a. Sole claim55/6202123085 closes only at linked55/70 handoff. Tested final executable source **a5edd17a420814133bba559911efb871f4b0633e**, tree8d8cf609ebeadf485b5f2a3a071b81b7e35a8c33. Later publication is documentation/evidence/checkpoints only; exact final head is in55/70. Main and PR48 are untouched.

## Root cause and scope

Official cure53 advisories identify the three nondefault-config library defects: [custom-element hook policy](https://github.com/cure53/DOMPurify/security/advisories/GHSA-c2j3-45gr-mqc4) fixed3.4.12; [IN_PLACE hook-detached resource subtree](https://github.com/cure53/DOMPurify/security/advisories/GHSA-55q2-fjhq-7xh7) fixed3.4.13; and [IN_PLACE removed rawtext root serialize/reparse](https://github.com/cure53/DOMPurify/security/advisories/GHSA-6688-9rhm-gjv2) fixed3.4.16. Official [release3.4.16](https://github.com/cure53/DOMPurify/releases/tag/3.4.16) and tagged manifest were verified. Audit severity is reported as the registry actually returned, separately from upstream labels.

[Tagged jsPDF4.2.1 manifest](https://github.com/parallax/jsPDF/blob/v4.2.1/package.json) declares optionaldompurify^3.3.1, allowing3.4.16. FrozenBun1.2.14 installs optional dependencies normally; no omit/skip workaround. Baseline3.4.11 and patched3.4.16 both have actual dist and installed manifest evidence. Physical enumeration finds one installed patched copy; the parent resolves the identical distribution. Missing optional package is a failure. Every lock record is guarded, including nested versions.

Existing invoice source uses html2canvas→jsPDF.addImage→save; no direct DOMPurify import, sanitize/hook/IN_PLACE call is present in the inspected app. The library regressions prove corrections under their explicit conditions. They do not prove production application exploitation or universal non-reachability.

## Official generated lock and compatibility

Only dompurify3.4.16 is added to existing paired overrides/resolutions. No direct dependency or jsPDF upgrade. Preparation starts from exact5623lock and unchangedbunfig in a temporary directory. Official npm @oven/bun-linux-x64-baseline1.4.0, approved SHA512 in changes/primary-sec-002/LOCK_REGENERATION.md and build34cbb9a40, runs `bun update dompurify --lockfile-only --ignore-scripts`. Entire output is adopted, never hand-edited. Bun reports959packages/290ms.

Lock Git blob **d630ca04096a126cbeb021d083ee248085f2efea**, SHA256 **ee1f5da0c882776472dd6a074b1c6df8547ca3b37ca1cf7fe1863588ba5c5496**. lock.diff/graph.json prove only DOMPurify record/version/integrity and its override changed. Every other package/workspace record matches baseline, including Hono4.13.7, qs6.16.0, jsPDF4.2.1 and all parents. No release-age exception/config change.

Only existing package.json/bun.lock/security-floor test change. Additional files are two bounded read-only workflows, browser/PDF/evidence fixtures and intake/impact/evidence docs. Existing Quality/G1 workflows, application122files, all41migrations and all43SQLfiles are unchanged. No financial/API/RPC/schema/RLS/auth/tenant/state/business contract change, DB mutation or new PR. All new paths and rationale are in the intake packet and artifact index.

## Actual execution

| Evidence | Exact source/result |
| --- | --- |
| [Preparation38806528259/job116668708545](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38806528259/job/116668708545) | 3f3d2da2bcc17fb6c3bda7f9e3f2f1ff6e282c5a: original frozen install/optional presence PASS; browser3.4.11 has5ordinaryPASS and exactly5targetedFAIL across3GHSA; verified official generator PASS. Expected-red controller exits0 after checking the exact failed set, not raw process exit1. |
| [Final verification38887412161/job116928426043](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38887412161/job/116928426043) | a5edd17: frozen1.2.14/whole graph/actual optional copies+parent/10browser/PDF/8guardmutants/affectedlint/source-invariance PASS. Supported1.4audit returns1 for three residual findings; job correctly **FAILURE** only at audit. |
| Final-source Quality | [38887419454/job116928450006](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38887419454/job/116928450006) **SUCCESS**:63unit/137expect including4existingMCPfixtures; typecheck/changedlint,8stubserver-wrapper and67dummybrowser-containment cases, two isolated builds. Actual synthetic checkout9bc591ac225e24b709f6e224bacada0bd26b2338 has tree8d8cf609ebeadf485b5f2a3a071b81b7e35a8c33, matching testeda5edd. No actual merge or G1 execution. |

Browser: pinnedPlaywright1.62.0/Chromium151.0.7922.34. Two custom-element admission forms (RegExp/function), two detach hooks (before/upon), removedrawtextroot fail-closed exception and five ordinary/control cases. All10cases are the same assertions across old/fixed (initial new fixture line wrapping only). Old five failed expectations are preserved as evidence, never green product acceptance. The rawtext fixed call throws the documented fail-closedTypeError; ordinary in-place and DOM-output controls remain valid.

Security floor: every stable3.x copy>=3.4.16. Eight disposable guard controls have exit0 forpatched,1 forold/prerelease/major4/nestedold/missing/oldHono/oldqs. Existing guards are not weakened. Explicit ESLint covers only new fixtures and affected guard; inherited full lint remains open without a new full-repo measurement.

PDF: test-only bundle imports unchanged `src/lib/invoice-pdf.ts:downloadInvoicePdf`, invokes local dummy Arabic invoice and captures real download. Final exact filename `mongezz-invoice-00017.pdf`, UTF-8 document,110539bytes,1page/1image, SHA256bf4608cc8bd62595790eaedd0910e381731abd05c51be61e88137dce64b1bd97. Original iframe cleanup succeeds. Local `pdfinfo` independently parses PDF1.3, jsPDF4.2.1, one A5page, unencrypted/noJavaScript. No customer/financial/API/DB writes. This is export compatibility, not financial correctness or visual/font parity.

HTTP routes are installed before page creation and only fulfilled/aborted; no fetch/continue can reach external destinations or redirects. WebSockets intercepted, service workers blocked. Three exact CairoCSSrequests fulfilled with empty offlineCSS, fallback fonts; no font-provider contact. Finalnetworkreceipt has zero violations. Payload resources use dataURI/local markers only. These browser fixture guards are not claimed as native packet-counter/G1 evidence.

## Retained failures and independent finding

Initial preparation Quality38806536249 failed on9Prettier diagnostics in the newly added fixture; only that new fixture's formatting was corrected, preserving all assertions. Full raw log remains in job-logs.zip. No broad lint cleanup.

First patched verification38886992955/source8781 and diagnostic38887230718/source584b both reached10/10DOMPurifyPASS then failed exact PDF filename. The diagnostic saved actual name `u-a-a-u-s-u-s-u-u-u-s-invoice-00017.pdf` and211667-bytePDF. Independent reviewerR1 identified missingUTF8charset in the synthetic HTML/JavaScriptresponse. IndependentNodeTextDecoderwindows1252→NFKD reproduction matched this exact corrupted filename; UTF8 yields the originally expected name. The harness alone adds explicitUTF8headers/meta/check; filename/PDF/network/cleanup assertions and app implementation remain unchanged. Sourcea5edd final retest closesR1. Both failed archives/logs are retained, not omitted or relabeled passes.

## Full fresh audit and open gates

Raw audit.stdout/audit.stderr/audit.receipt.json/audit-summary.json preserve actual `bun audit --json`, supported1.4.0+34cbb9a40, complete findings and **exit1**. audit-comparison.json proves exactly the three DOMPurifyIDs removed from the prior qs scan; no new/Critical/High in this observation. No fixed residual count is an acceptance rule and no remaining finding is waived.

| Remaining package | Severity | GHSA |
| --- | --- | --- |
| @babel/core | Low | GHSA-4x5r-pxfx-6jf8 |
| @hono/node-server | Moderate | GHSA-frvp-7c67-39w9 |
| esbuild | Low | GHSA-g7r4-m6w7-qqqr |

No full lint cleanup/acceptance and no liveG1/DB/SSR/Auth/financial rerun. Historical40/40 belongs todbc870/oldlock. Before accepting integration, explicitly reconcile the approved finalmanifest/lock/tests/checkpoints with source54's fail-closed identity guard, freeze/review the new source, and run the affected actual runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof required by that integration scope. The guard is unchanged here and rejects these changes; no silent allowlist expansion. Existing G0/G1/G2 and human release boundaries remain open. PR48 remains open.

## Review, rollback and next

REVIEW.md records the actual independent reviewer, finding/correction, replayed Python/Node/hash/archive/log evidence, and commands not rerun. It does not claim independent Bun/browser/DB execution or human approval. Artifact index records ZIP integrity and checks for secret patterns. Final delivery adds docs/checkpoints/evidence only above testeda5edd source.

Rollback: additive revert of candidate pins/generated lock/guard and fixtures with frozen/security/typecheck/build checks. This restores the vulnerable baseline, so it is not a production security remedy; production is untouched. No migration/data compensation.

ONE NEXT: planning selects the next separate G0 advisory/lint disposition and retains final-lockG1 requirements. Close sole claim at55/70hand-off and stop. No production/customer/Paddle/secrets/newcost/merge/deploy/launch approval.
