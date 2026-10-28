# B-DEP-IDENTITY-01 — native refusal lifecycle correction

Independent reviewer: /root/dep_identity_review. Source reviewed:9266f848a03e0e6f700c23518eafd0c7ed750d6b. This record supersedes the earlier recommendation to cancel every refused input immediately.

## Observed failure

Actual native run39871214831 entry job120145831679 built the standalone Node application successfully, passed the actual-entry fixture and29 identity fixtures, and recorded a real existing401 from GET/mcp during readiness. Its first oversized POST then failed with ECONNRESET before recording the required413. The reset remains a failure, not an acceptable rejection or proof of security denial.

## Primary source inspection

- srvx0.11.16 `src/adapters/_node/request.ts` exposes the incoming Node request through Readable.toWeb().
- srvx0.11.16 `src/adapters/node.ts` resolves the async application handler before invoking sendNodeResponse().
- Node22.23.3 `lib/internal/webstreams/adapters.js` implements toWeb.cancel(reason) by destroy(streamReadable, reason). Its readable adapter uses ByteLengthQueuingStrategy at the Node readable highWaterMark, copies each supplied Buffer chunk, and pauses the Node readable when desiredSize<=0. This is bounded backpressure, not an unbounded clone or tee.
- Node22.23.3 `lib/_http_server.js` resOnFinish() calls req._dump() only if the incoming request has not been consumed and no resume is scheduled. This cleanup guarantee does not apply unconditionally after partial body reads.
- The same response-finish handler closes a last response through socket.destroySoon()/socket.end(). A Connection:close refusal therefore allows the response to finish before closing the unread upload connection on the observed HTTP/1 Node runtime.

The observed integration failure is consistent with cancellation destroying the incoming socket before the adapter sends413. The source trace establishes the relevant lifecycle ordering; a packet-level trace was not captured. A separate minimal bare Node server fixture did not reproduce the same reset and is not promoted to a reproduction of srvx/Nitro behavior.

## Corrected contract and required verification

For non-aborted refusals, leave the unread stream with its host and release an acquired reader lock. Do not cancel before returning the rejection. On observed Node HTTP/1 use Connection:close for a rejected request so partial uploads cannot leave a paused persistent connection after the error response. Cancellation after an already-aborted request is distinct; no clean response can be promised to a disconnected client.

Preserve the native413 assertion. Add actual declared-large/incomplete and chunked actual-byte-overflow tests asserting a complete413 response, subsequent socket close and an unaffected fresh connection returning the existing401. No native or deployed HTTP2/Worker refusal portability claim follows from the Node header behavior; such hosts control hop-by-hop header and request stream cleanup. Existing normal Worker acceptance is distinct from this refusal lifecycle test.

The prior early-cancel Medium disposition is reopened as a demonstrated native compatibility issue until the corrected lifecycle passes. No implementation edit was made by this reviewer.

## Independent current audit observation

The supported audit also failed on new current findings: DOMPurify Critical GHSA-cg2g-xh64-v4q7, High GHSA-mrv2-3pqr-j5jr, Low GHSA-c6gr-qvv4-5v3f, and ip-address Moderate GHSA-rxp7-6hxx-x8q5. Earlier13-entry/10-advisory preparation counts are historical; no current clean audit is claimed.
