# FIN-COURIER-001 — API Compatibility (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval.

## RPC surface changes

### `create_sale_with_items` → adapter over `create_sale_with_items_v2`

- **Canonical:** `create_sale_with_items_v2(p_customer_id, p_delivery,
  p_courier_id, p_paid, p_method, p_items, p_courier_state text)` — single source
  of truth for state, custody, debt, stock, and the outcome-based customer rule.
- **Adapter (kept):** the existing six-parameter
  `create_sale_with_items(p_customer_id, p_delivery, p_courier_id, p_paid,
  p_method, p_items)` is preserved and **delegates** to `_v2`, deriving
  `p_courier_state` from `p_paid` exactly as today (0→pending, full→delivered_full,
  else delivered_partial). It carries **no independent financial logic**.
- **Rejected design:** a defaulted overload
  `create_sale_with_items(..., p_courier_state DEFAULT NULL)`. Supabase/PostgREST
  overload resolution with defaults can be ambiguous; not adopted without an
  isolated proof test (finding 5).

Compatibility guarantee: any call that succeeds today still succeeds with
identical effect (via the adapter). The only new outcomes are previously-rejected
customer-less courier creations that now succeed.

### Courier outcome transition

- Today: `update_courier_order_state(p_order_id, p_state, p_collected)` — no
  customer.
- Target: an atomic transition (preferred: `resolve_courier_order_v2(p_order_id,
  p_state, p_collected, p_customer_id)`), or an added optional `p_customer_id` on
  the existing RPC preserving the old 3-arg call. Backward compatibility: the
  3-arg form keeps working for `pending → delivered_full` and for orders that
  already have a customer; it must **reject** debt-creating transitions on
  customer-less orders rather than silently violate the constraint.
- `returned` continues to route to `return_courier_order` (unchanged signature).

### Unchanged signatures

- `settle_courier_orders(p_courier_id, p_order_ids uuid[])` — unchanged
  (method redesign is FIN-SETTLEMENT-METHOD-001).
- `return_courier_order(p_order_id)` — unchanged.
- `collect_order_debt(p_order_id, p_amount, p_method)` — unchanged.

### Reporting RPCs (PR-B)

- `get_platform_financial_health()` and `get_platform_financial_health_rows(
  p_check_key, p_limit)` — **signatures unchanged**; only the internal predicates
  for `courier_missing_refs` and `debt_without_customer` change (outcome-aware).
  No client contract change.

## Client (`src/lib/db.ts`) contract

- `CreateSaleInput` gains a courier-outcome field; `useCreateSale` calls `_v2`.
- `updateCourierStateAsync` gains an optional `customerId` and calls the atomic
  transition.
- Both changes are additive to the TypeScript types; older compiled clients that
  call the six-param adapter or 3-arg transition keep functioning.

## PostgREST exposure

- New functions must be exposed to `authenticated` only (SECURITY_IMPACT). The
  generated `src/integrations/supabase/types.ts` is regenerated in PR-A so the
  typed client sees `_v2`; the six-param adapter remains in the types for
  compatibility.

## Versioning note

- `_v2` is a **named** version, not a semantic-version overload. If a future
  change supersedes it, prefer another named RPC over mutating `_v2`'s contract,
  keeping each version's financial logic in exactly one function.
