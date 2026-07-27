# FIN-COURIER-001 — Dependency Map (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Callers, consumers, and readers of every affected contract.

## Write-path RPCs

### `create_sale_with_items` (→ becomes adapter over `_v2`)
- Latest def: `supabase/migrations/20260627201534_...c879.sql:358-444`.
- Client wrapper: `src/lib/db.ts:440-463` (`useCreateSale`).
- UI callers: advanced `SaleScreen` payment sheet
  `src/routes/_authenticated/app.tsx:909-921`; quick sale `SaleQuickScreen`
  (`app.tsx:1132+`, success at `:1228`).
- SQL tests: `tests/financial-rules/rules.sql` T1–T8.
- Change: add `_v2` (canonical); this becomes a delegating adapter.

### `update_courier_order_state` (→ canonical `update_courier_outcome_v2`)
- Latest def: `supabase/migrations/20260626233231_...9c.sql`.
- Client wrapper: `src/lib/db.ts:530` (`updateCourierStateAsync`, exposed at
  `app.tsx:267`).
- UI caller: `CourierCustodyScreen` mark controls (`app.tsx:445-597`).
- Delegates `returned` → `return_courier_order`.
- Change (decision 5C): canonical `update_courier_outcome_v2` enforces the
  transition matrix, monotonic non-decreasing custody, forbidden backward/
  reduction transitions, idempotent same-state retry, and atomic same-tenant
  `customer_id` attachment for debt-creating targets. Old RPC kept only as a
  compatibility adapter.

### `settle_courier_orders` (unchanged in this change)
- Latest def: `20260627201534_...c879.sql:448-503`.
- Client wrapper: `src/lib/db.ts:507` (`useSettleCourier`).
- UI caller: `SettlementsScreen` (`app.tsx:599-694`).
- Note: hard-coded `method='cash'` (`:496`) is deferred to
  FIN-SETTLEMENT-METHOD-001.

### `return_courier_order` (unchanged)
- Latest def: `20260626233231_...9c.sql`. Guard
  `cannot_return_partially_paid_order`. Stays the single place returns are
  handled.

### `collect_order_debt` (unchanged; re-verify)
- Latest def: `20260704105413_...908.sql`. Guards returned + settle_courier_first.

## Schema constraints (`orders`)
- Def: `20260626155319_...4e.sql:12-34`.
- `orders_customer_required_when_unpaid`, `orders_courier_requires_customer_id`
  → **replaced** by `orders_customer_required_when_debt`.
- `orders_courier_requires_courier_id`, `orders_collected_not_over_total` → kept.

## Read models / aggregates / reporting

| Consumer | Location | Reads | Impact |
|---|---|---|---|
| `getCustomerDebtForInvoice` etc. | `src/domain/finance/invoice-selectors.ts` | courier_state, collected, paid, total | None (already outcome-correct); customer not an input |
| `close_day` | `20260704105413_...908.sql` | courier_state (CASE) | None — re-verify |
| `get_tenant_today_estimate` | `20260627201534:240-276` | sales/collected/expenses/profit | None (no debt/custody output) |
| `get_platform_admin_overview` | `20260627201534:282-324` | `open_customer_debts` **excludes** courier debt (`:299-300`) | **Changes (PR-B)** — outcome-aware; include delivered_partial/none debt (finding 4) |
| `get_platform_financial_health` (+`_rows`) | `20260626191523_...b1.sql` | `courier_missing_refs`, `debt_without_customer` | **Changes (PR-B)** — make outcome-aware |
| `get_platform_tenants_health` | `20260626191523_...b1.sql` | `open_debts` **excludes** courier debt; health flag | **Changes (PR-B)** — outcome-aware debt total (finding 4); health flag reviewed |
| `get_platform_day_close_health` | `20260627201534:326-355` | recompute vs stored | Re-verify only |
| `get_platform_courier_custody_health` | `20260626191523_...b1.sql` | courier rows with `collected_by_courier > 0` | None (custody filter, not customer) |
| `HomeScreen` totals/alerts | `app.tsx:220-230`, `src/features/home/HomeScreen.tsx` | selectors | Display only (PR-C) |

## UI screens (PR-C)
- Entry points → advanced sale: `app.tsx:291,302,329,1124`.
- `PaymentSheet`: `app.tsx:929-1073` (`needsCustomer` `:943`).
- `CourierCustodyScreen`: `app.tsx:445-597` (wording `:484,566,579`).
- `SaleSuccessScreen`: `app.tsx:1074-1129` (`:1112`).
- Advanced entry from quick: `app.tsx:1335`.

## Type / client contract
- `CreateSaleInput` and RPC arg mapping: `src/lib/db.ts:431-455`.
- Generated types: `src/integrations/supabase/types.ts` (regenerate after the
  migration; that regeneration is part of PR-A implementation, not this doc).
