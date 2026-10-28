# FIN-IDEM-001 — Data Impact

## New data class

Idempotency metadata is operational financial-control data. Initial proposed record fields:

- `tenant_id`;
- `operation`;
- `idempotency_key`;
- canonical request representation and/or deterministic hash;
- committed result JSON/reference;
- created/completed timestamps as applicable;
- optional actor/audit reference if required by final design.

## Uniqueness

The database must enforce one logical key per:

`tenant_id + operation + idempotency_key`

Client-side uniqueness is insufficient.

## Transaction ownership

The idempotency record is created/finalized inside the same transaction as the protected financial operation. A failed transaction removes its uncommitted reservation automatically.

## Existing business data

No backfill is required for historical orders. Idempotency applies prospectively to requests using the new contract.

## Retention

Do not delete records while a legitimate retry could still occur. Initial pilot may retain records indefinitely or use a conservative reviewed retention window; cleanup must never make an old retried key execute again unexpectedly.

## Privacy/security

Do not store unnecessary raw client payload or personal data. Canonical request representation must include only fields needed to prove request equivalence and replay correctness.