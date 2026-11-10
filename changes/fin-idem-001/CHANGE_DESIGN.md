# FIN-IDEM-001 — Change Design

## Root cause

The financial transaction boundary guarantees each RPC call is atomic, but there is no durable server-side identity for the **logical request**. After an ambiguous network outcome, a retry is a new valid transaction and can commit a second sale.

## Smallest correct architecture

Introduce one reusable database idempotency primitive and integrate it with the canonical financial RPC rather than implementing per-screen deduplication.

## Proposed storage contract

A forward-only table such as `financial_idempotency` with at least:

- `tenant_id uuid NOT NULL`;
- `operation text NOT NULL`;
- `idempotency_key text NOT NULL`;
- canonical request evidence (`request_hash` and/or normalized `request_json`);
- `result jsonb` containing the committed stable response;
- timestamps;
- unique constraint / primary key on `(tenant_id, operation, idempotency_key)`.

Exact hash primitive and whether canonical JSON is also retained are Gate-4 implementation details that must be verified against available PostgreSQL capabilities; do not rely on raw JSON text ordering.

## Transaction algorithm

Within the same authorized transaction as the financial write:

1. Resolve current tenant and actor; validate operation authorization.
2. Validate idempotency-key format/length.
3. Build the server-defined canonical financially material request.
4. Attempt to insert/reserve `(tenant, operation, key, request evidence)` under the unique constraint.
5. If this transaction owns the reservation:
   - execute canonical financial logic;
   - persist stable result in the idempotency row;
   - commit both together.
6. If a committed conflicting row already exists:
   - compare canonical request evidence;
   - same request → return stored result without financial mutation;
   - different request → `idempotency_conflict`.
7. If the owner transaction aborts, the reservation aborts with it; a retry may subsequently acquire the key.

The database unique constraint is the concurrency authority. Do not use client locks or timing windows as the correctness mechanism.

## Canonical request for sale creation

Must include every input that can change financial/business outcome, including as applicable:
- customer identity;
- delivery kind;
- courier identity;
- amount/collection input;
- payment method;
- normalized item IDs and quantities;
- courier outcome/state from FIN-COURIER v2.

Ordering of logically unordered representations must be normalized before equivalence comparison.

## Initial integration boundary

Implement only after FIN-COURIER PR-A provides `create_sale_with_items_v2`. Prefer either:

- a new idempotent v2 signature including `p_idempotency_key`; or
- a thin canonical wrapper that owns idempotency and invokes one internal sale implementation in the same transaction.

Do not copy the sale implementation into two RPC bodies.

## Client contract

One logical user submission receives one generated idempotency key. The client reuses that same key when retrying an ambiguous result. Starting a genuinely new sale creates a new key.

UI disabled/busy state remains useful but is not part of correctness proof.

## Retention

For the initial controlled pilot, prefer conservative retention over aggressive cleanup. Any TTL/cleanup design must prove that a late retry cannot become executable again merely because its key record expired.

## Acceptance criteria

- exact committed retry replays original result;
- conflicting retry rejects;
- concurrent duplicate creates one effect;
- failed transaction does not poison key;
- tenant/operation isolation;
- no duplicated order/stock/payment/custody/debt/audit mutation;
- T1–T15 and FIN-COURIER remain GREEN;
- independent financial/security review;
- explicit human merge only.