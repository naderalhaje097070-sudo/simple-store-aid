# B4 / APP-02 initial independent design review

Reviewer: `/root/foundation_a_independent_review`, separate from the implementation owner. Date: 2026-10-21 UTC.

**Outcome: Blocked pending missing evidence for B4 acceptance.** This is an early design review, not a tested-source approval. The current whole integration head remains **Changes required** because DEP-20261021 High and the explicitly failing old A identity gate remain unresolved. Neither a B merge nor B5/B6 acceptance is granted.

## Authority and source actually inspected

Canonical repository: `naderalhaje097070-sudo/simple-store-aid`. Read-only GitHub checks observed main `18700dee8ecdda2e457c0aa18c4f83a81b042019`, integration `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0`, and 20 original open draft requests. B4 claim #55/comment6312231207 names the sole implementer and the same base. Responses are retained in `initial-authority.json`.

I read the actual original webhook, signature helper, billing subscription query, subscription schema/triggers, latest entitlement helper, B3 grant correction, repository review/database/security policies, B4 intake and impact documents, and the offline baseline script/result. The proposed SQL and final route do not yet exist as an exact candidate reviewed here. No DB, provider, credential, deployed HTTP, browser, historical suite, or production operation was run by this reviewer. The implementer's supplied-error baseline was inspected, not independently relabeled as a live database or signature test.

The original route ignores returned errors from both subscription and tenant writes, acknowledges 200 after zero-row updates, and performs those writes independently. Its update/cancel tenant filter omits environment. The inherited APP-02 severity is **High**, as recorded in the canonical original findings register; the supplied-error baseline demonstrates the false-success branch within its stated offline boundary.

## Design direction supported within this scope

A single service-only SECURITY INVOKER transaction for subscription state, any required live cache projection, and its receipt addresses the actual failure boundary. A committed exact duplicate or explicitly durable stale/non-current outcome can return 200. A database error, missing required row, conflicting identity, malformed/null result, or uncertain response must remain non-200. An unimplemented queue or an in-memory task is not durable acceptance.

Retaining the existing globally unique provider subscription ID and failing closed on cross-environment collision avoids a larger public-schema change. Use both the global subscription identity and environment/event identity when serializing; the tenant row lock serializes shared projections. All paths need one consistent lock order and bounded contention. Receipt insertion must be in the same transaction as required writes, and a raised fault must roll back every mutation.

Live-only tenant billing metadata is a defensible technical cache contract **within the inspected repository**: billing selects subscriptions by tenant and environment; the entitlement helper uses environment-qualified subscriptions plus the existing trial. No runtime reader of the tenant billing metadata was found outside the old webhook. This search does not establish external-consumer absence. Document the cache as non-authoritative live metadata, preserve trial/entitlement behavior, and do not describe legacy cache contents as verified live state.

## Design conditions requiring explicit resolution

| ID | Severity / evidence | Required contract and decisive case |
| --- | --- | --- |
| B4-DESIGN-01 | Medium; design ambiguity, not an implemented defect | A tenant lock does not choose its current subscription. Comparing latest event time across different subscription IDs can let an old subscription's later cancellation replace a newer subscription's cache. Preserve a stated binding rule, or return 503 where ambiguous. Test subscription A, replacement B, then a later A update/cancellation. |
| B4-DESIGN-02 | Medium; source-confirmed timestamp meaning, proposed repair not yet tested | Existing `subscriptions.updated_at` is a server receipt/write timestamp, including its update trigger, not provider chronology. A frozen `legacy_floor` may serve as a conservative admission boundary with its clock assumption and reconciliation limitation stated. Never call it a recovered provider watermark. Keep it separate from timestamps on stale/no-op/repair receipts; retries and cache repair must not advance or lower it. |
| B4-DESIGN-03 | Medium; design ambiguity, not an implemented defect | Matching legacy subscription state is insufficient authority to overwrite a tenant cache bound to another subscription or a newer projection. Repair only after environment, immutable ownership/mapping, pointer and projection-order checks. Compare the complete state that would be written, not status alone. |
| B4-DESIGN-04 | Medium; design ambiguity, not an implemented defect | Separate event-input identity from resolved-state equivalence. Event deduplication excludes delivery-specific notification ID and JSON key order. Same event ID with different normalized semantic input is a conflict. Equal-time different events with equal written state are no-ops; equal-time different written state fails without an arbitrary lexical ID order. |
| B4-DESIGN-05 | Medium; platform precision boundary, no candidate yet | Preserve sub-millisecond event ordering. PostgreSQL timestamps have microsecond resolution; document validation or comparison behavior above that precision instead of silently rounding and claiming unlimited precision. Rejecting unsupported precision must be explicit. |
| B4-DESIGN-06 | Medium; design interaction, no candidate yet | A valid updated/canceled full snapshot can bootstrap only with verified identity and item mapping, or with a validated existing same-environment identity. Test updated-before-created for a new subscription while a different tenant pointer exists, followed by the earlier created event: per-subscription stale classification must neither regress stored state nor silently prevent a required binding repair. |

These are bounded design conditions, not six confirmed vulnerabilities or a new business-policy specification. The existing old handler rebinds on created and updates/cancels only the matching pointer. A replacement must state how legitimate out-of-order bootstrap composes with that distinction. Updating a non-current subscription with an explicit non-current receipt can be legitimate; choosing an active plan by an invented status priority, lexical ID, or newest event across unrelated subscriptions would change the contract.

For legacy rows, an older differing snapshot should fail closed rather than claim chronology. An exact match can be a safe subscription no-op, but cache repair is a separate decision. A later-than-floor event is an admission rule with the stated source-clock assumption, not a retrospective proof that every prior provider event is known. No automated production reconciliation is established by this design.

## Minimum decisive verification for the final candidate

1. Execute the actual final handler with synthetic signatures verified by the locked SDK against a disposable loopback stack. Preserve the original false-success/partial-write baseline on 47 migrations, then fresh 48 and populated 47→48 evidence. Identify this as handler execution unless an actual HTTP server is also exercised.
2. Inject failures at subscription, required tenant projection, and receipt writes. After each non-200, all three stores must be unchanged; after removing the fault, replay the identical event and demonstrate one committed effect. Include zero matched tenant/ownership rows and malformed RPC results.
3. Exercise sequential and concurrent duplicates, same-ID conflicting input, changed notification ID/key order, response loss after commit, timeout/late commit, newer/older reversed arrival and reversed commit, equal-time same/different state, and distinct sub-millisecond timestamps.
4. Exercise both environments and their secrets, invalid environment, cross-environment globally colliding ID, wrong/missing tenant mapping, customer/owner reassignment, two subscriptions for one tenant, legacy partial repair/floor ambiguity, and updated/canceled-before-created with valid and missing mapping. Unsupported verified event types need an explicit ignored outcome.
5. Observe effective function/table/schema privileges and RLS. New functions default to PUBLIC execution unless revoked. Client schema USAGE is not privacy. Check anonymous, owner A/B, two employees and disabled employee direct RPC/table denial with genuine service success. A payload/JWT role string cannot substitute for the actual trusted database execution role.
6. Keep the original 47 migrations, B2/B3 rights/functions, trial behavior, all unrelated source, package and lock exact. Capture populated public/catalog invariance, preserving unrelated private closure data. Keep raw advisor warnings and the current dependency/identity failures visible.
7. Reuse the evidence secret-sink guard with the actual new artifacts and safe upload gate. No full raw webhook, signature, secret, email/address or arbitrary exception contents should enter logs/evidence. Minimal necessary identifiers in a private receipt require explicit grants and retention documentation; no new erasure or retention policy is implied.

The route deadline should stay below Paddle's delivery deadline while treating timeout as an uncertain commit and relying on deduplication on retry. A retryable ambiguous legacy event may exhaust Paddle retries; document the remaining reconciliation/operational limit. No claim of automatic eventual repair is warranted without an implemented reconciliation path.

The supplied rollback revocation is a forward containment proposal only until its final function signature and effective service grant are checked. It must retain receipts/data and must not restore false-success handling.

## Sources and evidence limits

Primary technical references consulted read-only on 2026-10-21:

- [Paddle event model and delivery guarantees](https://developer.paddle.com/webhooks/about/how-webhooks-work/): events may be duplicated and delivered out of order; event ID differs from notification ID.
- [Paddle delivery handling](https://developer.paddle.com/webhooks/about/respond-to-webhooks/): five-second response deadline and finite retries.
- [Paddle subscription.updated](https://developer.paddle.com/webhooks/subscriptions/subscription-updated/): subscription snapshot contract and updates following lifecycle events.
- [PostgreSQL 17 date/time types](https://www.postgresql.org/docs/17/datatype-datetime.html): microsecond timestamp resolution.
- [Supabase database functions](https://supabase.com/docs/guides/database/functions): invoker behavior and explicit function execution grants.

These references inform the design review; they are not runtime evidence for this repository. Final B4 acceptance requires this reviewer's independent inspection of the exact executable SHA and its actual native receipts. No historical B2/B3 suite was rerun, and no provider call or production read was made.

