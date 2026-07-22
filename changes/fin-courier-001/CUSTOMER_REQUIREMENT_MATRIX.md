# FIN-COURIER-001 — Customer Requirement Matrix

Status: Proposed contract for Gate 3 approval.

Rule: **A customer is mandatory if and only if the operation results in customer
debt.** The courier itself never makes a customer mandatory.

Enforcement is **two-layered**: the RPC (`create_sale_with_items_v2` /
`resolve_courier_order_v2`) raises a clear typed error, and a **CHECK constraint**
(`orders_customer_required_when_debt`, replacing
`orders_customer_required_when_unpaid` + `orders_courier_requires_customer_id`)
is the schema backstop. Both must change together — relaxing the RPC without
replacing the constraints leaves customer-less courier orders blocked at write
time (see COURIER_STATE_CONTRACT §1, CURRENT_BEHAVIOR §1a).

## Full matrix

| Operation | Delivery | Outcome | Customer debt result | Customer required | Enforced by |
|---|---|---|---|---|---|
| Direct sale, fully paid | direct | paid = total | 0 | **Optional** | RPC `:397-399` (already) |
| Direct sale, partial | direct | 0 < paid < total | total − paid | **Required** | RPC `:397-399` (already) |
| Direct sale, full debt | direct | paid = 0 | total | **Required** | RPC `:397-399` (already) |
| Courier order, pending | courier | outcome unknown | 0 (not yet) | **Optional** | RPC (to change) |
| Courier, delivered & collected full | courier | collected = total | 0 | **Optional** | RPC (to change) |
| Courier, delivered & collected partial | courier | collected < total | total − collected | **Required** | RPC (to change) |
| Courier, delivered without collection | courier | collected = 0, delivered | total | **Required** | RPC (to change) |
| Courier, returned / not delivered | courier | stock restored | 0 | **Optional** | `return_courier_order` (already) |

## Current vs target per row

| Row | Current UI (`needsCustomer = remaining>0`) | Current RPC | Target |
|---|---|---|---|
| Direct full | optional | optional | optional ✓ (no change) |
| Direct partial | required | required | required ✓ (no change) |
| Direct debt | required | required | required ✓ (no change) |
| Courier pending (paid 0) | **required** (remaining=total) | **required** (blanket guard) | **optional** — both must change |
| Courier collected full | **optional** (remaining 0) | **required** (blanket guard) | **optional** — RPC must change; UI already optional but currently fails at RPC |
| Courier collected partial | required | required (blanket) | required ✓ (rule reason changes: debt, not "courier") |
| Courier delivered_none | not expressible at creation | n/a at creation | **required** — needs creation-time outcome + rule |
| Courier returned | n/a at creation (post-hoc) | n/a | optional ✓ |

## UI change required

`PaymentSheet` (`app.tsx:929-1073`) currently computes
`needsCustomer = remaining > 0` (`:943`). For courier orders this must instead be
driven by the selected courier **outcome**, using the same debt definition as the
domain layer:

```
needsCustomer =
  (delivery === "direct"  && paid < subtotal) ||
  (delivery === "courier" && outcomeCreatesDebt(courierOutcome, collected, subtotal))
```

where `outcomeCreatesDebt` is:
- `delivered_partial` → true
- `delivered_none` → true
- `pending` → false
- `delivered_full` → false

This should reuse / align with `getCustomerDebtForInvoice(...) > 0` from
`src/domain/finance/invoice-selectors.ts` rather than re-deriving debt in the
component (Mongezz Architecture Rule 2).

## Error-name contract

- Keep `customer_required_for_debt` for all debt-creating operations (direct and
  courier).
- Retire `courier_requires_customer_and_courier` for new-signature calls; replace
  with `courier_requires_courier` for the missing-courier case only.
- Legacy old-signature calls continue to pass a customer and therefore never
  observe a behavior change (see BACKWARD_COMPATIBILITY).

## Post-creation transitions

The same rule governs transitions, not just creation: moving a customer-less
`pending` order to `delivered_partial`/`delivered_none` creates debt and so
requires a customer to be present or supplied in the same transaction. See the
atomic resolution contract in COURIER_STATE_CONTRACT §3.
