# FIN-IDEM-001 — Change Intake

## Change goal

Make sensitive financial writes retry-safe and concurrency-safe through server-enforced idempotency.

## Change type

P0 financial correctness / transactional integrity change under NAADF-CMF.

## In scope

- idempotency key contract;
- canonical request hashing;
- tenant/operation scoping;
- concurrent duplicate serialization;
- deterministic replay/conflict result;
- auditability and retention of idempotency records;
- tests for duplicate, conflicting, concurrent, and pre-commit failure cases.

## Initial operation

Sale creation through the future canonical `create_sale_with_items_v2` after FIN-COURIER PR-A.

## Out of scope

- UI double-click prevention as the financial control;
- FIN-COURIER business-state implementation;
- employee accounts;
- payment-provider/webhook idempotency unrelated to store financial RPCs;
- automatic migration/deploy.

## Urgency

P0 pilot blocker. Network retry after a lost successful response can otherwise duplicate a sale, stock decrement, numbering, and payment effects.

## Risk level

High. This change modifies the transactional write boundary and requires concurrency testing.

## Owner

Nader — product and repository owner.

## Expected outcome

A canonical idempotency primitive and sale-write integration where retries return one result and cannot duplicate financial effects.

## Missing blocking information

The exact final signature/body of `create_sale_with_items_v2` is produced by FIN-COURIER PR-A and does not exist on current `main`. Implementation therefore waits for PR-A, while the storage/transaction/test contract can be approved beforehand.

## Explicit assumptions

- Server/database is the authority for idempotency.
- Client-generated keys are identifiers, not trust decisions.
- Tenant identity is resolved server-side.
- Applied migrations remain immutable; any schema is added forward-only.
- No automatic merge or production access.