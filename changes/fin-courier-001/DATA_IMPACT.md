# FIN-COURIER-001 — Data Impact (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval.

## Tables touched (schema/behavior, not bulk data)

- `public.orders` — CHECK constraints replaced; no column add/drop; no backfill.
- No other table schema changes. `payments`, `order_items`, `products`,
  `customers`, `couriers`, `day_closes` unchanged.

## New data shapes now permitted

- Courier orders with `customer_id IS NULL` and
  `courier_state IN ('pending','delivered_full')`. These are **new** (previously
  blocked by RPC guard + CHECK). They carry:
  - `paid = 0`, `collected_by_courier` = 0 (pending) or total (delivered_full),
  - zero customer debt, so `close_day` and selectors treat them correctly.

## Data shapes still forbidden

- Courier `delivered_partial` / `delivered_none` with `customer_id IS NULL`
  (debt without a customer) — rejected by the new RPC **and** the new CHECK
  `orders_customer_required_when_debt`.
- Direct partial/debt with `customer_id IS NULL` — unchanged rejection.
- `collected_by_courier > total` — unchanged rejection.

## Historical rows

- No historical row is mutated or backfilled.
- All existing courier orders have a customer (old constraint), so they satisfy
  the new, looser constraint — the replacement can be `VALIDATE`d without a legacy
  violation (MIGRATION_IMPACT).
- No re-validation of stored rows is triggered by relaxing the RPC guard.

## Integrity-monitor impact (must ship with the change)

- `get_platform_financial_health.courier_missing_refs` (**Critical**) currently
  counts every `delivery='courier' AND customer_id IS NULL`. After this change
  those include **valid** rows → false Critical unless the predicate is made
  outcome-aware (PR-B).
- `get_platform_financial_health.debt_without_customer` (**Warning**) counts
  `status IN ('partial','debt') AND customer_id IS NULL`; courier orders are
  always `status='debt'`, so valid customer-less courier orders trip it → false
  Warning unless outcome-aware (PR-B).
- `get_platform_admin_overview.open_customer_debts` excludes courier orders
  (`delivery='direct' OR courier_id IS NULL`) → **not** distorted by the new rows;
  verified, no change (test G4).

## Data-loss / corruption risk

- None from the schema change (more permissive, additive constraint).
- The transition hole (COURIER_STATE_CONTRACT §3), if left unfixed, would allow
  **debt without a customer** — a data-integrity regression. It is closed by both
  the atomic RPC and the new CHECK, and covered by tests D-T* and C-CK3.

## Verification queries

- Pre/post snapshot of `close_day` debt & custody per state on a seeded isolated
  DB (test F2).
- Customer-less debt-state guard:
  ```
  SELECT count(*) FROM orders
  WHERE delivery='courier' AND customer_id IS NULL
    AND courier_state IN ('delivered_partial','delivered_none');   -- expect 0
  ```
- No production data is accessed; all queries run on isolated environments.
