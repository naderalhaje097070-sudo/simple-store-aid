# Finding C5-COLLECTION-RETRY-01

Severity: **High — blocks financial acceptance**.
Status: Runtime-tested, reproduced twice; no fix applied.

Source: executablee0a75541b981eed0bf1715315f7e418e466330c6; existing collect_order_debt(uuid,numeric,payment_method), body in the live-account migration; actual useCollectDebt caller in src/lib/db.ts sends only order/amount/method. C3 forward composition does not add collection idempotency. Tests: tests/c5-finance/native.py and verdict.py; raw artifacts13200182471/13200716463, jobs125697199766/125697199654.

Authenticated, authorized own-tenant operator → real local PostgREST RPC → locked order update and new payments row. First20on100posts paid20/payment1. The same payload/actor resent after hiding that success posts paid40/payment2. Expected for one logical collection is paid20/payment1. All63/66 preceding controls pass; unauthorized/foreign/anonymous/banned paths and over-total concurrent requests remain denied. This is not an authorization bypass or a claim of all concurrency being broken.

The current RPC is an increment-per-call contract with no operation identity. Two genuine equal payments are valid; simply deduplicating equal amount/order/time would lose legitimate money records. Required fix: one durable logical UUID across request/reload/retry, transactional server dedupe with exact request/actor/tenant validation, and no authenticated raw bypass. Reuse current financial_idempotency and canonical collection logic; do not alter amount/rounding/remaining/courier/return rules.

Reachability limits: response loss is simulated after a real server commit; actual automatic UI retry is not observed. No public unauthenticated exploit, external transfer, production access, real-customer duplicate, or historical reconciliation requirement is proven. Invoice totals still cap collection; the problem can occur within that cap, e.g20+20under100. Product/operator UX and restore still need verification after remediation. Owner approval of the core RPC/privilege/client compatibility transition is required; see PROPOSAL.md. Independent review not performed.
