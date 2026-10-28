# Current, inherited and expected boundaries

Accepted main220fc2066b4d6254b1803b5e32919c47d60a9c7e:50 migrations; legacy six-argument create_sale_with_items; current UI CreateSaleInput has no courierState or idempotency key; PaymentSheet requires customer whenever remaining>0. No financial_idempotency/core/v2 candidate migration has reached main.

Original49 adds one August migration: canonical core/v2, compatibility adapters, customer-required-only-for-debt constraint and monotonic courier transition. Original50 adds one August idempotency migration, changes src/lib/db.ts and adds two SQL/concurrency tests.35 is the original14-document design;39 is its5-file safety net.27 contributes25 incremental paths, including two historical state files. Their old CI/billing/gate statuses remain historical, not current blockers or passes without fresh observation.

Expected composed outcome remains the existing approved contracts: canonical server sale, customer only when customer debt arises, courier collection distinct from settled cash, exact-key replay/conflict/atomic rollback, stable unresolved operation identity and tenant/actor isolation. Main UI and current typed RPC bridge must be extended semantically; do not overwrite db.ts with50's old file or duplicate domain formulas.

Current source evidence re-confirms FIN-01 quantity mismatch, FIN-02 order-dependent legacy adapters, and FIN-03 key continuity. New callback coverage expands FIN-03 to the single-pending replacement and null-result clear boundaries; these are not newly claimed stored-money incidents. Definitions/ACL/RLS/persisted fresh and populated upgrade acceptance are still required.
