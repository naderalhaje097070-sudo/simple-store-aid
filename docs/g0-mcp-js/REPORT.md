# G0-MCP-JS-COMPAT-01 — official compatibility decision
Date: 2026-10-17 (Africa/Tripoli). Decision investigation completed; remediation remains blocked.

## Result and one recommendation
No officially published newer mcp-js version in the captured npm registry snapshot admits a patched esbuild. **Retain mcp-js0.20.1 and plan a separately reviewed, narrowly scoped correction to this parent's esbuild contract.** Do not upgrade the SDK/framework or adopt3.1.0 to address this advisory: that upgrade does not change the esbuild range.

The next design packet should inspect the existing0.20.1 tarball and choose a traceable parent patch/fork or upstream patch to permit0.28.1, followed by actual compatibility proof. This is a recommendation for planning, not authorization to force an override, publish a fork, send an upstream message or waive the advisory.

## Official evidence and exact scope
One authorized diagnostic Actions run:39011125934, attempt1, event pull_request_review, executed source56170b8792337649458c3cbb6bc1aee7a8d03bc3. Job117333693079 SUCCESS. Start06:46:02Z, completion06:46:13Z. Node22.23.3/npm10.9.9/Linux Ubuntu24.04.5; semver7.7.4 from existing npm tooling. Ordinary policy/financial/auth jobs SKIPPED; no Quality/G1 or package installation. Review5556693204 was an operational trigger only, not independent review or approval.

Both official HTTPS registry requests returned200, no retries:
- @lovable.dev/mcp-js:107 total published version entries; raw728825 bytes, SHA2560c15631d1c7bd4c205443fbb23eb6c1d269ee71d303f760c27a2b5a57602e3dc.
- esbuild: raw1264676 bytes, SHA25604b9a374d0710d1771d08cb1fbed62e834621a689f116c87f7f514cdd0bb21c1.

The runner scanned all33 stable releases newer than0.20.1, from0.21.0 through3.1.0. All33 require esbuild^0.27.0. A separate local recheck of the captured complete metadata also scanned48 newer prereleases, including4.0.0-rc.0: all48 require the same range. **All81 newer releases reject both officially published stable patched versions0.28.1 and0.28.2.** This is a snapshot result at06:46Z, not a prediction about future releases. Latest tag3.1.0; rc tag4.0.0-rc.0.

Root metadata identity, raw receipt hashes, artifact digest, and source-file Git hashes independently recalculated locally; this was a second analysis by the implementer, **not independent-agent review**.

## Dependency and used API assessment
Existing0.20.1 and nearest stable upgrade0.21.0 have identical published dependency, peer, engine, export-map and bin fields. Both require SDK1.28.0, esbuild^0.27.0 and jose^6.2.2; current approved SDK override remains1.31.0. Neither declares a Node/Bun engine; absence of a declaration does not prove support for every runtime.
2.x introduces Node>=20 and @modelcontextprotocol/server2.0.0. 3.1.0 adds core/client2.3.0 while retaining SDK1.28.0 and esbuild^0.27.0. These are metadata observations only; no binary/source compatibility of those ineligible releases was claimed.

Required project contracts already inspected: auth/defineMcp/defineTool/ToolContext and verified-bearer forwarding; TanStack mcpPlugin; MCP/OAuth handler exports; /mcp plus legacy list/invoke routes; manifest extraction/generation. No eligible candidate exists, so **no candidate archive was downloaded, no SHA512 candidate verification or candidate auth/transport/generation comparison was possible or claimed**. The diagnostic stopped correctly after proving no qualifying declared range. unpack exit0 means no archive was present; it is not an archive-inspection success.

Current locked esbuild inventory remains one0.27.7 record and26 platform records. Its only required pulling edge is root→mcp-js0.20.1→esbuild^0.27.0. Vite8.0.16 optional peer^0.27.0 || ^0.28.0 and unplugin3.4.0 optional peer* accept0.28.1. A parent-only update to any observed version keeps the conflicting required edge. No new candidate graph was generated or installed.

Project manifest/lock/bunfig and existing SDK1.31.0/Hono4.13.7/node-server1.19.15/qs6.16.0/DOMPurify3.4.16/Babel7.29.7 floors are unchanged. No dependent update is justified by this investigation.

## Bounded alternatives and engineering cost
- Upstream compatibility release: smallest local ownership burden; external response/release timing unbounded. An upstream message was not sent.
- Traceable patch/fork of0.20.1 declaring patched esbuild after source/API validation: moderate engineering scope, plus integrity/provenance/license/maintenance and future upgrade obligations. Must preserve runtime/auth/transport and generator behavior. Recommended next **design** investigation if work must proceed without waiting.
- Explicit out-of-range override: not adopted; requires a separate documented compatibility decision and tests, not silent enforcement or an automatic security exception.
No defensible numeric effort estimate exists before0.20.1 package source inspection.

Minimum later tests: native-Windows same benign/hostile esbuild servedir cases old/fixed; actual MCP extraction/build and generated manifest/routes diff; existing four synthetic adapter contracts plus affected auth/origin/metadata/forwarded-host negatives; all-copy installed/locked graph checks, existing CI Bun frozen, typecheck, two isolated builds, changed lint/Quality and full audit retaining raw exit. Final-lock G1/source reconciliation remains a separate later gate.

## Durable evidence, execution accounting and cleanup
official-inspection.zip is the exact Actions artifact12093116552:424119 bytes, SHA256ee18cd440730dc025ae8227c4589b5618270df7cfea4131b107888c5f301223a, matched both GitHub digest and local bytes. It preserves both complete raw packuments, HTTP receipts, commands, version table, script/workflow sources, identities and stdout/stderr/exit codes. All three raw inspect/unpack/source-invariance exits0. The result is NO_QUALIFYING_DECLARED_RANGE, not a repaired dependency.

Diagnostic script Git blobs4b0d7ee521e9d26c3f846fcbf88ff4a352c1543f and50ee66967ca1ca0f98cb0bb5b22884bec5d00e06, workflow blobef203c59e83aed392ffa7d9cdeb6ddeb4f3c0d3a all match archived bytes. local-semver-recheck.json preserves the additional81-release analysis. diagnostic.log preserves raw job logs with GitHub's credential masking.

Exactly1/1 authorized executions consumed; no rerun. Final delivery restores SEC-CI workflow byte-exactly to0540e266 blob a9b792109d47ce28cb9eaa1c8ded51862aea68b4 and removes only this investigation's two temporary diagnostic scripts. Their exact executed versions remain in the immutable source and raw artifact. Final publication uses[skip ci], no Quality/G1. Main/PR48/financial/account/SQL/source identity guard unchanged; no merge/deploy or billing configuration change.

Status: official-version investigation complete, **no compatible official upgrade exists in this snapshot**; esbuild remediation/G0/integration still open. No independent implementation review, archive compatibility, Windows runtime, fresh frozen/build/audit or application exploitability proof is claimed. Handoff in55/70 closes the claim; stop for planning.
