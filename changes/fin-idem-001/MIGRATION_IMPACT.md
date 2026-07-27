# FIN-IDEM-001 — Migration Impact

## Schema direction

A new forward-only idempotency table/constraint is expected. Exact name and columns are finalized in Gate 3/4 before implementation.

Minimum database properties:

- tenant-scoped operation/key uniqueness;
- canonical request evidence;
- committed result evidence;
- timestamps;
- indexes supporting exact key lookup;
- privileges/RLS or function-only ownership preventing unsafe direct client mutation.

## Historical data

No backfill for existing financial rows. Historical orders remain valid without idempotency records.

## Transaction migration

The canonical financial RPC must acquire/create the idempotency record and finalize the result inside the same transaction as the financial write.

## Forward-only rule

Do not edit existing migrations. Add a new migration after the canonical FIN-COURIER PR-A baseline.

## Corrective rollback

A corrective migration may disable the new idempotent entry point and restore the prior callable contract if required, but it must not delete committed business transactions or cause previously used keys to become executable as fresh writes without an explicit compensation strategy.

## Deployment order

1. Gate-4 tests approved.
2. FIN-COURIER canonical v2 available.
3. Add idempotency schema/function contract.
4. Update client caller.
5. Run isolated migration/concurrency/regression suite.
6. Independent financial review.
7. Human merge only.