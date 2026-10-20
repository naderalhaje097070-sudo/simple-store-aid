# G1-CLI-CLEANUP-01 — bounded handoff, 2026-10-15

**Outcome: Blocked pending missing evidence. All missing runtime checks now executed, but G1 is not accepted.** The current strict blocker is16 blocked native IPv4 packets (not unique connections). No successful external delivery is shown by these counters. No merge, deployment, release acceptance or PR48 closure.

## Source and change

Repository: naderalhaje097070-sudo/simple-store-aid. Existing Draft72 remains on test/g0-g1-acceptance-runtime-2026-10-14 above PR54/57fb508b9d239aaf4676352dd97654341416c46a. Claim #55/6187165138; previous claim was closed. Starting head f2e54d33233ac4ddfa51782b7c1a2534f441eed8; all430 local blobs matched the live nontruncated tree before edits. Main was43d6edbccb66fb06ce0fcb93734ad59532d1aeae.

First executed source d4eeee0d6c392ce19fb0eeac1b69a0d4a9832ddb. Final executed source **819291c85825d73854262d76d2030736470ef92b**. Both contain435 blobs. Relative to the430-blob starting head, only runtime.py, the supplemental workflow, three state documents and their fingerprint file changed;424 original blobs/modes are unchanged. Five new files are the diagnostic/cleanup helpers and two intake/impact documents. Application, generated Auth, package/lock and all41 SQL migrations are preserved. Final handoff adds only documents/evidence and checkpoint fingerprints; reconcile those separately from runtime evidence.

Changed executable files: supplemental g01-runtime-retry.yml checks out the observed official setup-cli SHA, retains action Bun1.3.10/frozen dependencies, runs phase diagnostics and6 cleanup fixtures, and calls cleanup.py. diagnose_cli.py verifies official main SHA2569ab8da10c0e6ac30dc793094383b973604e95598ccd6c81a05a83a3d1a55cd68, adds12 fixed phase markers, bounds execution to120s and terminates its process group. cleanup.py uses a proved user lookup/numeric UID and fail-closed process/container states. runtime.py adds the official Wrangler banner flag, per-phase native counters and deferred-but-finally-fatal collection. No application/API/RPC/DB/financial contract changes. No blind tool version change.

## Proven causes and limits

The old38605846901 cancellation is proven only inside official setup-cli afb1b15109756ea5cf9d8985a359d9095235ca2b / bun src/main.ts before user/firewall/DB/SSR creation. Its underlying cause **remains unproven**. Both new executions complete all12 phases with CLI2.101.0/Bun1.3.10, exit0/no timeout; the first takes about3seconds. Do not relabel the old failure as a Bun download, rate-limit, billing or token problem.

The old cleanup oracle used pgrep by an absent username and accepted only exit1, although nonexistent-user failure returns a different exit. Local reproduction returned2. The new checker accepts KeyError as absent user only, accepts pgrep1 as no processes for an existing numeric UID, rejects pgrep0 as remaining processes and rejects lookup/command/read/timeout errors. Docker -a checks include stopped containers. Six fixtures and actual hosted4/4 receipts prove this bounded fix; absent-user fixtures are not claimed as hosted missing-user execution.

The current blocker is exact: native REJECT counters rose1→25 on the first new run and1→17 on the final run; IPv6 stayed0. Final phase receipts localize8 blocked packets to each emulator startup and none to Auth UI. Primary Wrangler4.149.0 source proves banner output can trigger an npm update check independently of metrics, and the official hide flag returns before that check. The observed reduction24→16 is consistent with partial suppression, **not proof of the destination/stack of the remaining attempts**. Do not weaken the zero-unexpected-packet gate or claim external escape/delivery. See NETWORK_DIAGNOSIS.md.

## Actual verification

| Check | Actual result |
| --- | --- |
| Local cleanup regression |6 cases PASS, including four required states plus lookup/command/timeout negatives |
| Existing named-receipt/visual mutations |17 cases PASS; generic500/alternate guard/wrong status still rejected |
| Actual local read-only pgrep | Current UID correctly classified remaining/false; unused UID no-process/true |
| Official source checksum/mutation | Exact9645-byte source accepted; altered source rejected;12 markers |
| AST/YAML/source identity/diff | PASS; original383 manifest permits only four explicit historical CI/state exceptions;41 migrations |
| Final hosted runtime | **39 checks,38PASS,1FAIL**, after all final checks collected |
| Exact named mismatch | Only build_runtime_supabase_mismatch; complete expected message and HTTP500 PASS |
| Real matching SSR/Auth | PASS, actual local Cloudflare build and desktop/mobile login |
| Tenant fixtures | Two real temporary users; own metadata positive/cross-tenant empty in tested cases |
| After-state | All22 public-table counts/digests identical before/after; no comprehensive financial acceptance inferred |
| Finance zero | orders/order_items/products/payments/expenses/financial_audit_log zero at end; no financial flow |
| Native outbound condition | **FAIL**: IPv4+16, IPv6+0; blocked attempts remain |
| Tracked-source preservation | PASS on executed819291c8 after build/runtime |
| Credential-free receipt + artifact scan | PASS; raw private logs/credentials not published |
| Cleanup |4/4 PASS on both new runs; no processes, no stopped/running target containers, worker/status files absent |

Actual commands: python test_cleanup.py; python test_g1_contracts.py; read-only pgrep positives/negatives; AST/YAML/identity/diff checks; exact official frozen installer and diagnostic wrapper; existing frozen application install, CLI/help/preflight/fresh-stack commands and unchanged controller/build/Auth flow through hosted workflow. No new full lint/audit/financial suite or account-chain replay.

## Durable evidence and hosted runs

- First scoped run: https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38701706724 — runtime job116311206661 FAILURE; environment116311206421 SUCCESS. Runtime ZIP SHA256209d083d73713333e7dc6fe918ceca090c0b6f726ba07def7d6ad319901b9507.
- Final scoped run: https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38702788681 — runtime job116314775547 FAILURE; environment116314775366 SUCCESS. Runtime ZIP SHA2569fbd455504f0b2bd2181ce6df8e0844fc37f32d0797f21585386d133444a4a10.
- First automatic Quality: https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38701712301 / job116311226831 SUCCESS. Checkout synthetic7ceda29be1788096d6e882c6fb2f612a92a0f9a7, complete tree identical to d4eeee0d.
- Final executable Quality: https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38702796165 / job116314798867 SUCCESS. Checkout synthetic451036ff8392ba617b89bf87658a0c529fbe9f41, complete435-blob tree identical to819291c8.60 unit/125 expectations,8 actual-wrapper/stub cases,67 dummy browser transport scenarios, typecheck/changed-source lint/builds. Synthetic checkout is not an actual merge or main acceptance.

Raw runtime ZIPs preserve every member, including progress receipts; selected parsed JSONs and archive hashes are stored under evidence/. Historical prior failed packets remain unchanged. New raw artifacts have seven-day hosted retention; committed copies are the durable packet. No secrets are included in raw ZIPs: credential scan passed before upload and local receipt pattern scan passed.

## Review, remaining gates and resumption

Independent reviewer g1_review did not implement the changes, reran6+17 local fixture cases and actual read-only pgrep, independently fetched official source/live GitHub logs/trees and checked retrieved artifacts. Exact re-execution and final outcome are in REVIEW.md. Review is an independent agent assessment through the shared connector, not a human-account approval. No independent database/Auth/financial replay or new CI dispatch by the reviewer.

G0 remains separate and unaccepted: inherited1117 lint errors/13 warnings and11 Moderate/5 Low advisories; no replay or waiver. Inherited G2 preissued banned-JWT access on54 remains unaccepted and untouched. No #49/#50 or account-lifecycle chain imported. #48 stays open, without formal supersession. No new PR, protected merge, deployment, production/customer access, Paddle/provider call, new subscription or financial-policy change.

State: implemented/tested draft harness, **G1 acceptance failed**, not Merged or Released. ONE NEXT is a planning decision for a separate bounded emulator-startup connect/DNS attribution under the same reject firewall. Do not execute it in this batch. Revert only this batch additively if needed; no schema/data compensation. Close the sole claim only in the final linked #55/#70 handoff, then stop.

Publication checkpoint: documentation/evidence commit127efa113402844f77ccd14439f4f4aad0f82de3 follows executed819291c8. This final report-save changes no executable. The final branch head is recorded in the linked #55/#70 handoff, rather than recursively embedding its own commit ID here. No runtime gate was rerun or waived by publication.
