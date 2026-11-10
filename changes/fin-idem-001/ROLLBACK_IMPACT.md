# FIN-IDEM-001 — Rollback Impact

## Principle

Rollback must never turn a previously used committed key into permission to execute the same financial request again silently.

## Corrective rollback scope

If the idempotent RPC integration must be disabled:

- restore the previous callable financial path through a forward-only corrective migration;
- preserve committed financial business rows;
- preserve idempotency records unless an explicit migration proves deletion is safe;
- document that callers returning to a non-idempotent legacy path lose retry protection.

## Schema rollback

Dropping the idempotency table is not the default rollback because it destroys replay evidence and can make old retries dangerous. Prefer leaving inert control data in place while routing new calls through the prior contract.

## Client rollback

A client revert may stop sending keys only if the server compatibility contract explicitly supports it. This is a degradation of safety and requires human approval.

## Verification

Corrective rollback must run on isolated database state containing:
- committed idempotent sale;
- replayed sale;
- conflicting key attempt;
- unrelated tenant key;
and prove no duplicate business effects are introduced.