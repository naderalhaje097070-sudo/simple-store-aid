# FIN-COURIER-001 — Courier State Contract

Status: Proposed contract for Gate 3 approval. Defines the courier state machine,
its accounting effects, and the creation-time RPC contract.

## States (`courier_state` enum — already exists, unchanged)

`pending | delivered_none | delivered_partial | delivered_full | returned`

No enum values are added or removed. This change adds no new enum labels.

## Accounting effect of each state

| courier_state       | order.status target | collected_by_courier | courier custody | customer debt              | customer required |
|---------------------|---------------------|----------------------|-----------------|----------------------------|-------------------|
| `pending`           | debt (operational)  | 0                    | 0               | 0 (not yet)                | No                |
| `delivered_full`    | debt→settle-ready   | total                | total           | 0                          | No                |
| `delivered_partial` | debt                | collected (0<c<total)| collected       | total − collected (> 0)    | **Yes**           |
| `delivered_none`    | debt                | 0                    | 0               | total                      | **Yes**           |
| `returned`          | debt (no debt calc) | 0                    | 0               | 0 (stock restored)         | No                |

"customer custody" and "customer debt" columns match `close_day`
(`20260704105413_...908.sql`) and `src/domain/finance/invoice-selectors.ts`
exactly; this contract does not change those formulas.

## Creation-time derivation — the core gap

Today (`create_sale_with_items`, `20260627201534_...c879.sql:401-408`) the state
is derived from `p_paid` alone:

- `p_paid = 0` → `pending`
- `p_paid >= total` → `delivered_full`
- else → `delivered_partial`

This makes `pending` and `delivered_none` **indistinguishable at creation** (both
have collected = 0). The target requires both to be expressible at creation
(§12 of EXPECTED_BEHAVIOR), because `pending` needs no customer while
`delivered_none` needs one.

### Proposed resolution — explicit outcome parameter

Introduce an explicit courier outcome at creation instead of inferring it:

- Add a **new forward-only overload** of `create_sale_with_items` that accepts an
  explicit `p_courier_state` (or `p_courier_outcome`) argument:
  `pending | delivered_none | delivered_partial | delivered_full`.
  `returned` is never a creation outcome.
- Keep the **existing signature working** (backward compatibility): when called
  without the outcome argument, preserve today's paid-derived mapping
  (0→pending, full→delivered_full, else delivered_partial). See
  BACKWARD_COMPATIBILITY.
- `collected_by_courier` at creation:
  - `pending` → 0 (and `p_paid` must be 0)
  - `delivered_none` → 0 (and `p_paid` must be 0)
  - `delivered_partial` → `p_paid` (0 < p_paid < total)
  - `delivered_full` → total (p_paid == total)
- `orders.paid` stays 0 for all courier creations (unchanged); collected money
  lives in `collected_by_courier` until settlement (unchanged).

Exact parameter name, ordering, and whether to overload vs add a companion RPC
are an **open decision for Gate 3** (recorded in CHANGE_INTAKE §Missing info).

## Customer-requirement rule inside the RPC

Replace the blanket courier guard
(`20260627201534_...c879.sql:381-383`) with an outcome-based rule, mirroring the
existing direct-sale rule (`:397-399`):

```
-- courier still requires a courier id
IF p_delivery = 'courier' AND p_courier_id IS NULL THEN
  RAISE EXCEPTION 'courier_requires_courier';
END IF;

-- customer required only when the outcome creates customer debt
IF p_customer_id IS NULL AND <outcome creates debt> THEN
  RAISE EXCEPTION 'customer_required_for_debt';
END IF;
```

where `<outcome creates debt>` is:

- direct: `p_paid < total`
- courier `delivered_partial`: `collected < total` (always true for partial)
- courier `delivered_none`: always
- courier `pending` / `delivered_full`: never

The error name `customer_required_for_debt` already exists and is reused, keeping
one debt-guard vocabulary. `courier_requires_customer_and_courier` is retired for
new calls but its behavior is preserved for legacy callers of the old signature
(they still pass a customer, so they never hit a changed path).

## State transitions after creation (unchanged RPCs, re-stated for the contract)

- `update_courier_order_state(pending → delivered_full | delivered_partial |
  delivered_none | returned)` sets `collected_by_courier` per the table above.
  `returned` delegates to `return_courier_order`.
- `settle_courier_orders` consumes `collected_by_courier`, moves it into
  `payments`, and flips the order to `direct` (settled). Delivered → settled is
  the only place money enters `payments` for courier orders.
- `return_courier_order` requires `paid = 0` and `collected_by_courier = 0`,
  restores stock, sets `returned`.

## Settlement method (open contract item)

`settle_courier_orders` hard-codes `method='cash'`
(`20260627201534_...c879.sql:496`). The target separates:

- **Customer transferred directly to the shop** → should enter `payments`
  directly, not courier custody.
- **Customer paid the courier** → `collected_by_courier` (custody).
- **Courier's handover method to the shop** (cash/transfer) → recorded at
  settlement.

The first version should stop overloading one `method` field for three events.
Whether this ships in the financial PR or a follow-up is a Gate 3 decision; it is
listed as blocking information in CHANGE_INTAKE and must be resolved before the
financial PR is considered complete.
