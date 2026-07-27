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
- **Correction (finding 2):** it is **not** proven that all existing courier
  orders have a customer. The old constraints
  (`orders_customer_required_when_unpaid`, `orders_courier_requires_customer_id`)
  were themselves added `NOT VALID` (`20260626155319_...4e.sql:16,28`), so they
  never validated pre-existing rows. The replacement is therefore added
  `NOT VALID` and **not** validated in the same migration.
- Before any `VALIDATE`, a **historical-data preflight** (MIGRATION_IMPACT step 2)
  must return zero rows that would violate the new constraint. Validation is a
  separate controlled step gated on that evidence.
- No re-validation of stored rows is triggered by relaxing the RPC guard alone.

## Single-source debt strategy

The per-order customer-debt definition exists in `close_day`
(`20260704105413_...908.sql`, CASE on `courier_state`) and mirrored in
`src/domain/finance/invoice-selectors.ts::getCustomerDebtForInvoice`:

- direct → `GREATEST(total - paid, 0)`
- `delivered_none` → `total`
- `delivered_partial` → `GREATEST(total - collected_by_courier, 0)`
- `pending` / `delivered_full` / `returned` → 0

PR-B must reuse **this exact contract** for platform totals (below) rather than
re-inlining a divergent CASE. Preferred: extract one canonical SQL expression /
immutable helper consumed by `close_day`, `get_platform_admin_overview`, and
`get_platform_tenants_health` (Architecture Rule 2 — do not duplicate the debt
formula). Whether to refactor `close_day` onto the helper is a Gate-4 detail; the
**definition must be identical** across all consumers.

## Integrity-monitor & reporting impact (must ship with the change)

- `get_platform_financial_health.courier_missing_refs` (**Critical**) currently
  counts every `delivery='courier' AND customer_id IS NULL` → false Critical on
  valid new rows unless made outcome-aware (PR-B).
- `get_platform_financial_health.debt_without_customer` (**Warning**) counts
  `status IN ('partial','debt') AND customer_id IS NULL`; courier orders are
  always `status='debt'`, so valid customer-less courier orders trip it → false
  Warning unless outcome-aware (PR-B).
- **`get_platform_admin_overview.open_customer_debts`** and
  **`get_platform_tenants_health.open_debts`** currently **exclude** courier
  orders (`delivery='direct' OR courier_id IS NULL`,
  `20260627201534_...c879.sql:299-300`). This is a **debt-under-reporting bug**
  (finding 4): `delivered_partial` (remainder) and `delivered_none` (full) carry
  real customer debt that is hidden. PR-B must make both totals **outcome-aware**
  using the single-source contract above, and prove equality with the financial
  source of truth for all courier states (tests G4/G7).

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
