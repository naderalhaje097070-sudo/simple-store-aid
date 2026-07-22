# FIN-COURIER-001 — Test Plan (mandatory safety net)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Tests are authored **before** the corresponding implementation
(Gate 4). No existing test may be weakened to pass a change.

Suites referenced:
- Financial rules (SQL): `tests/financial-rules/rules.sql` (T1–T15), run via
  `tests/financial-rules/run.sh` against an isolated Supabase.
- Unit: `tests/unit/invoice-selectors.test.ts` (`bun test tests/unit`).
- E2E: `tests/e2e/sale-dashboard-close.py`, `tests/e2e/isolated-auth-smoke.py`.
- Visual/mobile RTL: `tests/visual/mobile-rtl-smoke.py`.

## A. Regression (existing behavior must not break)

- **A1** T1 direct full paid → `paid=total`, payment row, status=paid.
- **A2** T2 direct partial with customer → status=partial, debt correct.
- **A3** T3 direct debt **without** customer → still **rejected**
  `customer_required_for_debt`.
- **A4** T4 overpay → still rejected.
- **A5** T5 courier pending **with** customer → custody 0, no payment row.
- **A6** T6 courier partial money **with** customer → custody = collected, no
  payment row.
- **A7** T7 collect_order_debt while custody held → rejected `settle_courier_first`.
- **A8** T8 settlement → money enters `payments`, order flips to direct.
- **A9** T9/T10 returned → stock restored, debt 0, custody 0.
- **A10** *(corrected)* `close_day` customer-debt and unsettled-custody totals are
  unchanged for all five states (aggregate regression).
  **Correction:** `get_tenant_today_estimate` does **not** return debt or custody
  today (`20260627201534:240-276` returns only sales/collected/expenses/profit),
  so it is asserted only on sales/collected/expenses, not on debt/custody. The
  earlier A10 wording claiming it returns debt/custody was wrong.

## B. New behavior (the change)

- **B1** Courier **pending without customer** (paid=0) → **succeeds**;
  `courier_state='pending'`, custody 0, no payment row, no debt.
- **B2** Courier **delivered_full without customer** (collected=total) →
  **succeeds**; custody=total, settlement-ready, debt 0.
- **B3** Courier **delivered_partial without customer** → **rejected**
  `customer_required_for_debt`.
- **B4** Courier **delivered_none without customer** → **rejected**
  `customer_required_for_debt`.
- **B5** Courier **delivered_none with customer** at creation → **succeeds**;
  custody 0, customer debt = total (verifies create-time `delivered_none`).
- **B6** Courier **delivered_partial with customer** → custody = collected,
  customer debt = total − collected.
- **B7** Missing courier id on courier order → rejected `courier_requires_courier`.
- **B8** `close_day` after B1/B2/B5: unsettled custody and customer debt match the
  COURIER_STATE_CONTRACT table (B5 adds `total` to debt, 0 to custody; B2 adds
  `total` to custody, 0 to debt; B1 adds 0/0).
- **B9** Settlement of a customer-less `delivered_full` order (from B2) →
  succeeds; payment row created; no null-customer failure.

## C. Effective CHECK constraints (new — finding 1/6)

- **C-CK1** Old constraints replaced: after migration, `orders` has
  `orders_customer_required_when_debt` and **not**
  `orders_customer_required_when_unpaid` / `orders_courier_requires_customer_id`;
  `orders_courier_requires_courier_id` and `orders_collected_not_over_total`
  still present. (query `pg_constraint`)
- **C-CK2** Direct debt insert without customer is still rejected by the
  constraint (independently of the RPC) — attempt a `service_role` insert.
- **C-CK3** Courier `delivered_partial`/`delivered_none` row without customer is
  rejected by the constraint at write time.
- **C-CK4** Courier `pending`/`delivered_full` row without customer is **accepted**
  by the constraint.
- **C-CK5** Constraint validates against all pre-seeded historical rows without
  error (proves the `NOT VALID`→`VALIDATE` step is safe).

## D. Post-creation atomic transition (new — finding 2/6)

- **D-T1** Customer-less pending → `delivered_full` (no customer supplied) →
  **succeeds**; custody=total, debt 0.
- **D-T2** Customer-less pending → `delivered_partial` with **no** customer and
  none supplied → **rejected** `customer_required_for_debt`; row unchanged
  (still pending, no debt persisted).
- **D-T3** Customer-less pending → `delivered_none` with **no** customer →
  **rejected**; row unchanged.
- **D-T4** Customer-less pending → `delivered_partial` **with a same-tenant
  `p_customer_id` supplied** → **succeeds atomically**; `customer_id` and
  `courier_state` both set in one transaction; debt = total − collected.
- **D-T5** Transition supplying a **cross-tenant** customer → **rejected**
  `customer_not_found` / `forbidden_tenant`; no partial write.
- **D-T6** Transition supplying a **nonexistent** customer → **rejected**; no
  partial write.
- **D-T7** `returned` transition still delegates to `return_courier_order` and
  obeys its `paid=0 AND collected=0` guard.
- **D-T8** Atomicity: a forced failure after the `courier_state` write (fault
  injection or constraint) rolls back the whole transaction — no order is left in
  a debt state without a customer.

## E. Concurrency & idempotency (sensitive financial path)

- **E1** Two concurrent `create_sale_with_items_v2` for the same product with
  stock = 1 → exactly one succeeds, the other fails `insufficient_stock`
  (`SELECT ... FOR UPDATE` product lock at `:389`).
- **E2** Concurrent transition + `settle_courier_orders` on the same order → no
  double-count of `collected_by_courier` into `payments` (row lock `:471`).
  Targets the known P1 "repeated RPC may rewrite custody".
- **E3** *(relabeled — finding 6)* **Known non-idempotent baseline, NOT
  idempotency protection.** A retried/duplicate `create_sale_with_items_v2` (same
  client retry) creates a **second** order; there is no idempotency key today.
  The test documents this baseline (each call increments `tenant_number` once and
  decrements stock once per order). True idempotency is tracked separately as
  **FIN-IDEM-001** and is out of scope here.
- **E4** *(corrected — finding 6)* `settle_courier_orders` called **twice** on the
  same order id → the **second call is rejected** with
  `order_not_in_courier_custody` (the first settle flipped the row to
  `delivery='direct'`, `courier_id=NULL`), and **no duplicate payment** row is
  created. The earlier C4 wording ("sees collected=0 and does nothing") was wrong:
  the row is no longer in the courier's custody, so the guard at
  `20260627201534_...c879.sql:473-474` raises.

## F. Backward compatibility

- **F1** Legacy six-param `create_sale_with_items` adapter with a customer →
  identical result to today for all courier paths (delegates to `_v2`).
- **F2** Existing courier rows (all five states) read by `invoice-selectors` and
  `close_day` → identical debt/custody before and after the migration (snapshot
  compare on an isolated DB seeded with pre-change rows).
- **F3** Rollback verification query (ROLLBACK_PLAN §Data) returns 0
  customer-less `delivered_partial`/`delivered_none` rows.

## G. Platform health & reporting (new — finding 3/6)

- **G1** `get_platform_financial_health` after seeding a **customer-less
  `pending`** and a **customer-less `delivered_full`** order → **no Critical**
  from `courier_missing_refs` and **no Warning** from `debt_without_customer`
  (both must be outcome-aware post-change).
- **G2** `get_platform_financial_health` still flags a genuinely corrupt row
  (courier order with debt-creating state but null customer, if one could be
  forced via `service_role`) — the check detects real corruption, not just the
  old blanket predicate.
- **G3** `get_platform_financial_health_rows` detail queries for
  `courier_missing_refs` / `debt_without_customer` return the corrected row sets.
- **G4** `get_platform_admin_overview.open_customer_debts` is **unchanged** by
  customer-less courier orders (they have `courier_id IS NOT NULL`, so already
  excluded) and `critical_alerts` stays 0 for the valid new orders.
- **G5** `get_platform_tenants_health` per-tenant health stays `Healthy` for a
  tenant whose only "anomaly" is valid customer-less courier orders.
- **G6** `get_platform_day_close_health` reconciliation still `Matches` for a day
  containing customer-less courier orders.

## H. Rollback (new — finding 6/7)

- **H1** Corrective migration restores the two original constraints and the prior
  RPC/transition definitions; T1–T15 baseline passes again.
- **H2** Post-rollback verification query confirms no customer-less
  `delivered_partial`/`delivered_none` rows remain (ROLLBACK_IMPACT).
- **H3** Legacy client path works after rollback.

## I. Mobile (RTL) UI

- **I1** Default "+ بيع جديد" opens **advanced** sale on mobile; quick sale
  reachable as a labelled secondary shortcut.
- **I2** PaymentSheet courier outcomes render in Arabic RTL; `delivered_none`/
  `delivered_partial` mark customer required; `pending`/`delivered_full` allow
  "بدون عميل".
- **I3** CourierCustodyScreen shows "تم التسليم دون تحصيل" (not "لم تُسلَّم (دين)");
  a separate "لم يتم التسليم / مرتجع" path leads to returned.
- **I4** Success screen wording is type-aware (custody vs collected vs pending).

## J. Desktop UI

- **J1** Desktop CTA and sidebar open advanced sale by default; quick sale is a
  secondary action.
- **J2** Courier invoice list shows operational status (قيد التوصيل / عهدة كاملة
  / عهدة جزئية ودين / دين كامل / تمت التسوية / مرتجع), not a bare "دين".
- **J3** Payment sheet layout and customer-required affordance correct at desktop
  width.

## Coverage → contract traceability

| Contract clause | Tests |
|---|---|
| Effective CHECK constraint replacement | C-CK1..5, H1 |
| Customer optional when no debt (pending/full) | B1, B2, C-CK4, D-T1, I2 |
| Customer required when debt (partial/none) | B3, B4, B6, C-CK3, D-T2/3, I2 |
| Create-time delivered_none | B5, B8 |
| Atomic post-creation transition | D-T1..8 |
| Cross-tenant/nonexistent customer rejection | D-T5, D-T6 |
| Custody ≠ pending order value | B1, B8, A10 |
| Delivered ≠ settled | A8, B9, E4 |
| Returned ≠ debt/custody | A9, D-T7 |
| Outcome-aware platform health/reporting | G1..G6 |
| Backward compat (v2 + adapter) | F1, F2, F3 |
| Concurrency / non-idempotent baseline | E1, E2, E3, E4 |
| Advanced sale default | I1, J1 |
| Wording corrections | I3, I4, J2 |
| Rollback | H1, H2, H3 |

## Exit criteria

- All of T1–T15 plus B/C/D/E/F/G/H SQL cases pass on isolated Supabase.
- Unit and UI (mobile + desktop) smokes pass on the branch head.
- GitHub checks (Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke)
  green on the head commit — the authoritative source.
- No existing test modified except to **add** the no-customer courier path
  alongside the existing with-customer cases.
