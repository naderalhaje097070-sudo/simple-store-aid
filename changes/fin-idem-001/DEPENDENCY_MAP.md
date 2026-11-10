# FIN-IDEM-001 — Dependency Map

## Canonical write dependency

Initial implementation depends on FIN-COURIER PR-A producing the canonical `create_sale_with_items_v2` contract. Idempotency should wrap that canonical operation rather than duplicate the current legacy sale body.

## Database dependencies

- tenant identity and authorization helpers;
- orders and tenant numbering;
- products/stock mutation;
- order items;
- payments for direct sales;
- audit logging;
- forward-only migration policy.

## Client dependencies

- `src/lib/db.ts` sale mutation caller;
- sale screens that submit the logical request;
- retry/error behavior after ambiguous network outcomes.

## Testing dependencies

- FIN-COURIER Gate-4 E3 baseline;
- isolated Supabase financial test harness;
- multi-session PostgreSQL concurrency execution.

## Security dependencies

- server-resolved tenant identity;
- least privilege over idempotency storage;
- no cross-tenant replay/read path.

## Sequencing

1. FIN-IDEM Gates 0–4 may define storage/test contract.
2. FIN-COURIER Gate 4 approval remains independent and required before PR-A.
3. FIN-COURIER PR-A creates canonical sale v2.
4. FIN-IDEM implementation integrates with canonical v2.
5. Later governed slices may extend the primitive to settlement, debt collection, return, and day close.