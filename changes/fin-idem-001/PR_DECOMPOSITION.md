# FIN-IDEM-001 — PR Decomposition

## PR-1 — Gates 0–3 documentation

Documentation only:
- baseline and current retry behavior;
- expected idempotency contract;
- impact/security/data/API/migration/rollback analysis;
- transaction design;
- test plan and sequencing dependency on FIN-COURIER PR-A.

## PR-2 — Gate 4 safety net

Test-only:
- exact committed retry;
- conflicting same-key request;
- concurrent duplicates;
- injected transaction failure and retry;
- tenant/operation isolation;
- canonical request normalization;
- replay audit behavior.

No production idempotency implementation.

## PR-3 — Idempotency primitive + canonical sale integration

After FIN-COURIER PR-A:
- forward-only idempotency storage migration;
- server-side transactional primitive;
- integrate canonical `create_sale_with_items_v2` path;
- client key generation/reuse contract;
- no extension to unrelated operations in the same PR.

## PR-4 — Independent review and release verification

Verify:
- financial effects exactly once;
- concurrency serialization;
- authorization/tenant isolation;
- failure rollback;
- compatibility with FIN-COURIER and T1–T15;
- rollback/retention risks.

## Later governed slices

Extend the approved primitive in risk order to:
1. courier settlement;
2. customer debt collection;
3. courier return where retry ambiguity remains relevant;
4. day close;
5. other financial writes based on pilot evidence.

Each extension requires its own focused tests and must not become a broad rewrite.

## Merge boundary

No automatic merge/deploy. PR-3 cannot begin until both FIN-IDEM Gate 4 and the required FIN-COURIER canonical sale dependency are approved/available.