# B-DEP-IDENTITY-01 — independent implementation review

Reviewer: /root/dep_identity_review. Date: 2026-10-22. Scope: unpublished local implementation based on integration59c8a0c7920e58a02cb885b382f6ac5f1cb168f1. This is a draft source review, not final current-head or whole-B acceptance.

## Inspected and independently reproduced

- Inspected request-boundary.ts, server.ts, mcp-request-boundary.test.ts, integrated_identity.py, test_integrated_identity.py and official preparation graph-delta.json.
- Independently executed Python identity fixture suite:16 tests passed.
- Independently reproduced the B-migration rewrite case below in a disposable fixture; no implementation files changed.
- Retrieved the existing official wrapper0.20.1 preparation artifact from GitHub; recomputed baseline.tgz SHA512 and matched the recorded official npm metadata integrity. Extracted57 published package files and inspected real constructors, public declarations and JWT verifier.
- Inspected official SDK1.32.0 source, official SDK1.32.1 release record and exact locked TanStack router-core1.171.34/start-server-core1.169.39 normalization/matching source.
- No live database, app, browser, provider or Windows test was executed by this reviewer. No GitHub writes, implementation edits, production access or secret access occurred.

## Accepted design direction

The handwritten server entry enforces64KiB actual request bytes,256 combined JSON members, depth32 and5s read deadline before dispatching the existing generated MCP handlers. Original bytes, headers and abort signal are replayed for permitted requests. Non-MCP requests remain the same object. The public framework normalizer and case-insensitive route classification cover the active route semantics. No generated route ownership change or library fork is needed. The wrapper has independent jose audience validation, so SDK expectedResource is not the active boundary; acceptedAudiences must remain unchanged and wrong-audience rejection must be tested.

The supported full audit tool is Bun1.3.14, separate from the runtime1.2.14 frozen compatibility baseline. The official-generated lock graph includes expected Vite transitive changes; it is not a four-line-only lock modification. Those changes need exact graph rationale and actual final compatibility/invariance evidence.

## Findings requiring disposition

### BDEP-REVIEW-01 — Medium — early body cancellation

File/contract: src/lib/mcp/request-boundary.ts early rejection before getReader/finally.

Evidence: declared oversize, invalid length and already-aborted requests with an existing body return before the current cancellation path. The stream is neither consumed nor canceled by this helper.

Risk: rejected large/stalled uploads retain an application stream unless hosting behavior happens to clean them up. The boundary should explicitly release input resources without waiting indefinitely for client cancellation.

Required fix: nonawaited bounded body cancellation on those early rejections; focused tests demonstrate cancel invoked and rejection resolves even when cancel never resolves.

### BDEP-REVIEW-02 — Medium — full prior B migration identity

File/contract: tests/g01-acceptance/integrated_identity.py migration anchor.

Evidence: original41 migration map is anchored to frozen A. The other nine prior B migrations match only a new self-declared map. A disposable fixture rewriting049.sql, regenerating its protected blob and integrated_migrations entry and committing is accepted with all_integrated_blobs_match=true and original54_migrations_unchanged=true.

Risk: the new gate independently enforces historical A immutability but does not independently preserve applied B migrations42–50 despite fixed B_BASE_SHA containing all50.

Required fix: compare the complete50 path/blob/mode migration set to immutable B_BASE_SHA, while retaining the independent frozen A/original41 validation. Add a negative control changing a B migration and regenerating the B manifest to match.

## Pending final evidence

Actual published source SHA and B manifest; complete migration/source/mode preservation; new manifest/mode/archive/map negative controls; supported current full audit; frozen final unit/type/lint/build/generation invariance; actual server-entry dispatch/alias/body-bound tests; wrong-audience/valid-auth compatibility and patched SDK contracts. Windows-specific claims require actual Windows execution; old esbuild proof does not become launch-editor proof.

Current outcome: Changes required for the two focused findings and missing final evidence. No introduced Critical/High identified in the inspected request-boundary design; no merge or whole-B acceptance is granted.
