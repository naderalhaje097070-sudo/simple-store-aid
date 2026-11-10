# FIN-IDEM-001 — Impact Analysis

## UI

Client must generate/reuse one idempotency key for one logical submission and preserve it across ambiguous retry. UI disabling remains a UX control only, not the financial authority.

## API / RPC

The canonical financial RPC gains an idempotency input or delegates through a canonical idempotent wrapper. Legacy adapters must not create a parallel deduplication implementation.

## Database schema / data

A tenant-scoped idempotency record is required with a unique operation/key contract and stored canonical request/result evidence. New schema is forward-only.

## Authentication / authorization

Replay requires normal authentication/tenant authorization. Cross-tenant key reuse must neither expose nor replay another tenant's result.

## Tenant isolation

Tenant ID is part of the unique scope and is derived server-side. RLS/privileges for the idempotency table must deny direct unsafe client manipulation; writes should be owned by authorized server-side functions.

## Business rules / state transitions

Idempotency must wrap existing canonical financial logic rather than alter sale/custody/debt rules. A replay skips a second state transition because the first committed result is authoritative.

## Financial operations / reports

Duplicate retries must not double:
- order rows/numbers;
- stock decrement;
- payment rows/amounts;
- customer debt;
- courier custody;
- day-close effects or audit events attributable to the original write.

## Background / integrations

No external payment-provider integration in initial slice.

## Performance

One indexed idempotency lookup/insert plus result persistence per protected operation. Index/storage growth requires a retention policy, but correctness takes priority over premature cleanup.

## Tests / CI

Requires SQL concurrency, exact duplicate, conflicting duplicate, failure/rollback, tenant isolation, and compatibility tests.

## Deployment / rollback

Forward-only table/constraint/function changes. Corrective rollback must preserve already-committed financial operations and avoid making old keys replay as new writes accidentally.

## Backward compatibility

Legacy callers without keys require an explicit transition strategy. For the initial FIN-COURIER integration, the preferred contract is that the modern client uses the canonical idempotent v2 path while any compatibility adapter has a clearly documented non-idempotent or delegated behavior until safely migrated.