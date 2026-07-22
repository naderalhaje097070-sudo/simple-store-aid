# FIN-COURIER-001 — Test Plan (mandatory safety net)

Status: Draft for review. Tests are authored **before** the corresponding
implementation (Gate 4). No existing test may be weakened to pass a change.

Suites referenced:
- Financial rules (SQL): `tests/financial-rules/rules.sql` (T1–T15), run via
  `tests/financial-rules/run.sh` against an isolated Supabase.
- Unit: `tests/unit/invoice-selectors.test.ts` (`bun test tests/unit`).
- E2E: `tests/e2e/sale-dashboard-close.py`, `tests/e2e/isolated-auth-smoke.py`.
- Visual/mobile RTL: `tests/visual/mobile-rtl-smoke.py`.

## A. Regression (existing behavior must not break)

- **A1** T1 direct full paid → `paid=total`, payment row, status=paid. (existing)
- **A2** T2 direct partial with customer → status=partial, debt correct. (existing)
- **A3** T3 direct debt **without** customer → still **rejected**
  `customer_required_for_debt`. (existing — must stay red-on-violation)
- **A4** T4 overpay → still rejected. (existing)
- **A5** T5 courier pending **with** customer → custody 0, no payment row.
  (existing — keep)
- **A6** T6 courier partial money **with** customer → custody = collected, no
  payment row. (existing — keep)
- **A7** T7 collect_order_debt while custody held → rejected `settle_courier_first`.
- **A8** T8 settlement → money enters `payments`, order flips to direct.
- **A9** T9/T10 returned → stock restored, debt 0, custody 0.
- **A10** `close_day` / `get_tenant_today_estimate` debt & custody totals
  unchanged for all five states (aggregate regression).

## B. New behavior (the change)

- **B1** Courier **pending without customer** (`p_customer_id=NULL`, paid=0) →
  **succeeds**; `courier_state='pending'`, custody 0, no payment row, no debt.
- **B2** Courier **delivered_full without customer** (collected=total) →
  **succeeds**; custody=total, settlement-ready, debt 0.
- **B3** Courier **delivered_partial without customer** → **rejected**
  `customer_required_for_debt`.
- **B4** Courier **delivered_none without customer** → **rejected**
  `customer_required_for_debt`.
- **B5** Courier **delivered_none with customer** at creation → **succeeds**;
  custody 0, customer debt = total (verifies create-time `delivered_none`, the
  new capability).
- **B6** Courier **delivered_partial with customer** → custody = collected,
  customer debt = total − collected.
- **B7** Missing courier id on courier order → rejected `courier_requires_courier`.
- **B8** `close_day` after B1/B2/B5: unsettled custody and customer debt match the
  COURIER_STATE_CONTRACT table (e.g. B5 adds `total` to customer debt, 0 to
  custody; B2 adds `total` to custody, 0 to debt).
- **B9** Settlement of a customer-less `delivered_full` order (from B2) →
  succeeds; payment row created; no null-customer crash.

## C. Concurrency & idempotency (sensitive financial path)

- **C1** Two concurrent `create_sale_with_items` for the same product with stock
  = 1 → exactly one succeeds, the other fails `insufficient_stock` (verifies the
  `SELECT ... FOR UPDATE` product lock at `:389` still holds under the new path).
- **C2** Concurrent `update_courier_order_state` + `settle_courier_orders` on the
  same order → no double-count of `collected_by_courier` into `payments`
  (row lock `:471`). This targets the known P1 "repeated RPC may rewrite custody".
- **C3** Retried/duplicate `create_sale_with_items` (same client retry) → each
  call is a distinct order (no idempotency key today); assert `tenant_number`
  increments once per successful call and stock decrements once per order.
- **C4** `settle_courier_orders` twice on the same order id → second call sees
  `collected_by_courier=0` (already flipped to direct) and does not create a
  second payment.

## D. Backward compatibility

- **D1** Legacy call shape (six params, no courier-outcome arg) with a customer →
  identical result to today for all courier paths.
- **D2** Existing courier rows (all five states) read by
  `invoice-selectors` and `close_day` → identical debt/custody before and after
  the migration (snapshot compare on an isolated DB seeded with pre-change rows).
- **D3** Rollback verification query (ROLLBACK_PLAN §Data) returns 0
  customer-less `delivered_partial`/`delivered_none` rows.

## E. Mobile (RTL) UI

- **E1** Default "+ بيع جديد" opens **advanced** sale on mobile; quick sale
  reachable as a labelled secondary shortcut. (extend `mobile-rtl-smoke.py`)
- **E2** PaymentSheet courier outcomes render in Arabic RTL; selecting
  `delivered_none`/`delivered_partial` marks customer as required; `pending`/
  `delivered_full` allow "بدون عميل".
- **E3** CourierCustodyScreen shows "تم التسليم دون تحصيل" (not "لم تُسلَّم (دين)");
  a separate "لم يتم التسليم / مرتجع" path leads to returned.
- **E4** Success screen wording is type-aware (custody vs collected vs pending).

## F. Desktop UI

- **F1** Desktop CTA and sidebar open advanced sale by default; quick sale is a
  secondary action (extend an E2E or add a desktop smoke).
- **F2** Courier invoice list shows operational status (قيد التوصيل / عهدة كاملة
  / عهدة جزئية ودين / دين كامل / تمت التسوية / مرتجع), not a bare "دين".
- **F3** Payment sheet layout and customer-required affordance correct at desktop
  width.

## Coverage → contract traceability

| Contract clause | Tests |
|---|---|
| Customer optional when no debt (pending/full) | B1, B2, E2 |
| Customer required when debt (partial/none) | B3, B4, B6, E2 |
| Create-time delivered_none | B5, B8 |
| Custody ≠ pending order value | B1, B8, A10 |
| Delivered ≠ settled | A8, B9, C4 |
| Returned ≠ debt/custody | A9 |
| Backward compat | D1, D2, D3 |
| Concurrency/idempotency | C1–C4 |
| Advanced sale default | E1, F1 |
| Wording corrections | E3, E4, F2 |

## Exit criteria

- All of T1–T15 plus B/C/D SQL cases pass on isolated Supabase.
- Unit and UI (mobile + desktop) smokes pass on the branch head.
- GitHub checks (Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke)
  green on the head commit — the authoritative source.
- No existing test modified except to **add** the no-customer courier path
  alongside the existing with-customer cases.
