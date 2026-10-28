# FIN-IDEM-001 — Expected Behavior

## Canonical key scope

Every protected financial operation is identified by:

`tenant_id + operation + idempotency_key`

The client supplies the opaque idempotency key; tenant identity and authorization are resolved server-side.

## Same key, same request

If a committed record already exists with the same operation/key and equivalent canonical request:

- no financial write is executed again;
- the original committed result is returned;
- stock, numbering, payments, custody, debt, audit effects, and timestamps that represent the original operation are not duplicated.

## Same key, different request

If the same tenant/operation/key is reused for a materially different canonical request:

- reject deterministically with an idempotency conflict;
- do not execute any financial effect;
- do not overwrite the original record/result.

## Concurrent duplicate calls

When two sessions submit the same logical operation/key concurrently:

- the unique key contract serializes ownership;
- one transaction executes the financial operation;
- the other returns the committed canonical result after the winner commits;
- exactly one financial effect exists.

## Failure semantics

The idempotency reservation and financial write live in the same database transaction.

If the winning transaction fails before commit:

- its idempotency reservation rolls back with the financial changes;
- a later retry may acquire the same key and execute normally;
- no permanently `in_progress`/poisoned success record remains.

## Request equivalence

Request equality is based on a canonical server-defined representation of the financially material input, not raw client JSON text ordering. The persisted contract may store canonical request JSON and/or a deterministic request hash; implementation must prove collision/normalization behavior appropriate to the chosen mechanism.

## Result contract

The stored replay result must contain the stable identifiers/data required for the client to continue as though it received the original response, beginning with the canonical sale result (`order_id`, tenant order number, and other contractually returned fields).

## Authorization

A replay still requires an authenticated actor authorized for the tenant/operation. Possession of an idempotency key alone never grants access to another tenant's result.