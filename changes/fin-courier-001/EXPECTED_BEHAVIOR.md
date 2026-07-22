# FIN-COURIER-001 — Expected Behavior

Status: **Proposed target based on product-owner direction; pending formal Gate
approval.** Gates 0–3 are **not** approved. This is the contract the
implementation must satisfy and the tests must prove **once approved**; no
implementation is authorized until then.

## Sale flow

1. **Advanced sale is the primary flow.** The main "+ بيع جديد" action opens the
   advanced sale (`SaleScreen`).
2. **Quick sale is a secondary shortcut**, clearly labelled, for direct, cash,
   fully-paid, customer-free sales only. It is not removed; it is not the default.

## Customer requirement (outcome-based, not delivery-based)

3. A courier order **may be created without a customer** when the outcome creates
   **no customer debt**.
4. A customer is **mandatory only when the outcome creates customer debt.**

See CUSTOMER_REQUIREMENT_MATRIX for the full table.

## Courier order vs financial custody vs debt (three separate things)

5. **Pending courier orders appear immediately** under courier orders, showing
   order value, but are **not** financial custody and **not** money held by the
   courier.
6. Money explicitly recorded as **collected by the courier becomes
   `collected_by_courier` immediately** (custody), and never enters `payments`
   until settlement.
7. A **fully-collected** courier order becomes **`delivered_full`** and appears
   **immediately in settlement**.
8. A **partially-collected** courier order becomes **`delivered_partial`**: the
   collected part is **custody**, and the remainder is **customer debt** (so a
   customer is required).
9. **"Delivered without collection"** (`delivered_none`) creates **customer debt
   for the full total** and **requires a customer**.
10. **"Not delivered / returned"** (`returned`) creates **no customer debt** and
    **restores stock**.
11. **Delivered and settled remain separate states.** Recording a courier
    outcome is not settlement; settlement is the later handover of custody to the
    shop.

## Known-at-creation vs updated-later

12. If the courier outcome is **known when the invoice is created**, it is
    recorded directly (pending, delivered_full, delivered_partial, or
    delivered_none) **without a mandatory second update step**.
13. If the outcome is **unknown** at creation, the order is `pending` and the
    owner updates the result later from the courier orders screen.

## Wording corrections

14. In the payment flow, when delivery = courier, the generic
    "مدفوع / جزئي / دين" choices are replaced by explicit courier outcomes:
    - قيد التوصيل (pending)
    - تم التسليم واستلم المندوب كامل المبلغ (delivered_full)
    - تم التسليم واستلم المندوب جزءًا من المبلغ (delivered_partial)
    - تم التسليم دون تحصيل (delivered_none)
15. The control currently labelled **"لم تُسلَّم (دين)"** and the message
    **"لم تُسلَّم — دين كامل على العميل"** are renamed to **"تم التسليم دون
    تحصيل"**. "Not delivered" must lead to **returned** (no debt, stock
    restored), never to a customer debt.

## Display corrections (within this change)

16. Courier invoices display an **operational status** (قيد التوصيل / تم
    التسليم — عهدة كاملة / عهدة جزئية ودين / دين كامل / تمت التسوية / مرتجع), not
    `order.status='debt'` alone.
17. The sale success screen reflects the sale type:
    - Direct: "تم تحصيل {amount}".
    - Courier collected: "عهدة لدى المندوب {amount}".
    - Courier pending: "لا يوجد تحصيل بعد".

## Reporting correctness (finding 4)

18. Platform and tenant customer-debt totals
    (`get_platform_admin_overview.open_customer_debts`,
    `get_platform_tenants_health.open_debts`) reflect **real** customer debt for
    all courier states — `delivered_none` → total, `delivered_partial` → total −
    collected — using the **same** per-order debt contract as `close_day` and the
    domain selectors. No under-reporting from excluding courier orders, and no
    divergent inline formula.
19. Platform integrity checks do not flag valid customer-less courier orders
    (`pending` / `delivered_full`) as corrupt.

## Courier custody state machine (finding 3)

20. `collected_by_courier` is **monotonic non-decreasing** before settlement. The
    normal outcome-update path follows the approved transition matrix, never
    reduces recorded custody, and never moves backward. Financial
    corrections/reversals use a separate audited workflow, not the normal update.

## Invariants that must NOT change

- Financial writes go only through approved RPCs.
- Debt, custody, remaining, and margin formulas are not duplicated in screens;
  screens reuse `src/domain/finance/`.
- Returned orders are never customer debt and never courier custody.
- Delivered is not settled.
- `close_day` / dashboard debt and custody formulas stay as they are today
  (they already match this target).
- Tenant isolation and RLS unchanged.
