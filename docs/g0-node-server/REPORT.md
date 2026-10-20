# G0-NODE-SERVER-01 bounded handoff

Implemented and tested on existing Draft PR72; not merged or released. The
targeted dependency criterion passes. G0 and integration acceptance remain open.
Final publication head is recorded in #55/#70 after documentation delivery.

## Source and change

- Start: `5cbf198d88b0f091a30371676fb09abf92903dc8`.
- Authoritative tested source: `15688194725fdb2c25e53d55d63cfe605295ec68`.
- Tested tree: `a2405b8051fbeeba6e966188369c180c7e3e57c6`.
- Complete generated lock blob: `1a0791b4bfb849e2345d087ddfebde2c33a59f74`.
- Lock SHA256: `540c5f2823b0116ab497819432ba54246dde1b7c9ad6cd085338829d85bde8d8`.

The old adapter decodes a single encoded backslash before Windows filesystem
resolution. The URL router still treats it as one segment, so prefix middleware
does not run while the file resolver enters the protected subtree. This is a
library authorization bypass inside the static root, not proof of application
exploitability or a demonstrated escape outside the root.

Official npm HTTP200 packument and verified actual tarball prove 1.19.15 exists
and is the smallest available fixed stable 1.x. The official reviewed advisory
and published CJS/ESM patch agree. SDK1.31.0 range `^1.19.9 || ^2.0.5` accepts it;
Node requirement stays `>=18.14.1`, Hono peer stays `^4`, exports stay identical.
No 2.x fallback, SDK upgrade or application change was necessary.

Paired overrides/resolutions pin only `@hono/node-server` 1.19.14→1.19.15.
Approved official Bun1.4.0+34cbb9a40 generated the complete lock after checking
the approved tool integrity. Every other graph record is identical. Hono4.13.7,
qs6.16.0, DOMPurify3.4.16, Babel7.29.7 and esbuild are preserved. No direct
dependency, new allowlist exception or manual generated entry.

## Actual verification

| Check | Result and evidence |
| --- | --- |
| Native Windows old1.19.14 | Run38951595338 / source80d2b11b: 8 cases, 6 PASS, exactly 2 specific security FAIL, 0 skipped. `%5C` and `%5c` return200/protected-marker with zero prefix calls. Raw Node exit1; expected-red controller/job0 only after validating the exact failure set. |
| Native Windows fixed1.19.15 | Run38952644379 / job117147589438 SUCCESS, 8/8, 0 skipped. Both encoded variants404, no protected bytes and zero prefix calls. Node22.23.3, platformwin32, real filesystem and installed adapter. |
| Linux fixed1.19.15 | Same run / job117147589979: 8/8 before audit. Linux is supplementary and is not credited as Windows proof. |
| Compatibility | Public/authorized files, ordinary401, HEAD and range206, traversal/missing/malformed paths, POST201 JSON/headers, handled500 then recovery. Real SDK Node transport initializes, lists/invokes a dummy tool, rejects invalid arguments without invoking it, and returns400 for malformed JSON. Per-request stateless lifecycle and cleanup. |
| Physical and locked copies | One real adapter copy on both OSes, same root/SDK resolution, all lock records inventoried, actual SDK parent and Hono/Node compatibility checked. Absence is a failure. Actual SDK source hashes match the diagnostic read. |
| Frozen and graph | Bun1.2.14 frozen on both OSes; exact whole graph allows only adapter and its override. Canonical source bytes and tracked source unchanged. Windows checkout explicitly retains LF; byte assertion stays strict. |
| Security guard | Stable reviewed1.x floor>=1.19.15 for every nested copy; actual Bun10 mutation controls pass, including missing/nested-old/prerelease/unreviewed-major and regressions of all four prior patches. |
| Affected lint | Both new CJS fixtures and modified unit guard pass without writing source. No broad lint cleanup or current full-repo lint total claimed. |
| Quality | Run38952653426 / job117147620305 SUCCESS: typecheck, changed lint,65 unit tests/145 expectations including4 existing MCP fixtures,8 stub wrapper cases,67 dummy browser containment cases, both approved isolated builds. Synthetic checkout7cdcfd1871a9f54a533567f7ef308908cb0c35af has tree exactly equal to tested a2405b80; no actual merge. |
| Full audit | Verified Bun1.4 scanner, actual `bun audit --json` exit1. Target GHSA-frvp-7c67-39w9 absent; exactly one remaining esbuild Low GHSA-g7r4-m6w7-qqqr, no new/Critical/High. Ubuntu job remains FAIL at audit; no waived scanner success. Raw records, streams, receipts and delta retained. |

Fixtures use dummy files/tools and loopback HTTP only; no application orders,
accounts, database, external tool endpoints or financial operations are invoked.
This is not a fresh G1 network-counter/isolation measurement.

## Preserved failures and review

All failures remain in named ZIPs/logs. Initial Windows collection used cp1252
against UTF8 SDK source and stopped before contracts. The next run had both
expected bypass failures plus an unexpected SDK fixture failure: a stateless
transport had been reused. The locked SDK's explicit one-request guard and its
published example justified a fresh server/transport per request; no package or
application workaround. Fresh CI source hashes confirm the diagnostic source.
The corrected baseline then has exactly the intended two failures.

The first patched Windows run stopped after successful frozen install at a
strict config byte assertion because Git converted LF to CRLF. Disabling that
checkout conversion only on the disposable Windows runner preserves the strict
assertion. It does not alter the security oracle. Source1568819 reruns both OSes
and Quality; successful first-source Linux/Quality are separately retained and
are not promoted as this source's evidence.

Independent read-only reviewer report and actual replay limits: `REVIEW.md`.
The reviewer recomputes archive/tarball/receipt/source hashes, graph/audit deltas,
and Node-adapted guard controls, and reviews raw hosted executions. Hosted
Windows/Bun/adapter/SDK/build/browser executions are implementer CI evidence,
not independently rerun by that reviewer.

## Scope, risks and rollback

Changed files: paired package constraints and complete lock; one unit guard;
three focused fixture/evidence scripts; preparation, native baseline and verify
workflows; this intake/impact/evidence packet and three root handoff checkpoints.
`source-delta.json` enumerates the executable-source change. All122 application
blobs,41 migration blobs and43 SQL blobs are identical to start. No application API/RPC,
financial/state/tenant policy, schema, migration, data or production change.

Remaining: esbuild Low, inherited lint, integrated verification and other
previously recorded release gates. G0 is not accepted. No live G1 rerun and no
reuse of the old40/40 on this lock. Before integration acceptance, explicitly
reconcile the unchanged fail-closed source54 guard/manifest to the approved final
source/lock and rerun affected actual runtime/transport/SSR/Auth/isolation/state/
counter/secrets/cleanup checks. This batch does not silently expand its allowlist.

Rollback is additive reversion of only this batch's constraints/complete lock,
guard/fixtures and checkpoints to starting5cbf198, preserving earlier fixes and
all evidence. Re-run frozen/graph/affected checks after any reversion. Restoring
a vulnerable candidate is not authorization to deploy it; no data compensation
is needed. No merge, deploy, production, PR48 closure or next implementation.

ONE NEXT: planning disposition of the separate remaining G0 work while retaining
the final-source G1 prerequisites. Close claim55/6222380561 only with final linked
#55/#70 handoff, then stop.

Provenance, commands and full evidence: `OFFICIAL_AND_GRAPH.md`,
`ci-identities.json`, raw scanner streams/receipts, full preparation/baseline/
verification ZIPs, hosted logs and `REVIEW.md`.
