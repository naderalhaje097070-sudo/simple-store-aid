# FIN-COURIER-001 — Current Behavior (NAADF-CMF Change Gate 1)

Status: Baseline documentation. Read from the working tree at `main = 906df4b`.
Every claim below cites a file and line. No defect is asserted without evidence.

## 1. Sale RPC: `create_sale_with_items`

Latest definition: `supabase/migrations/20260627201534_...c879.sql:358-444`.

### 1.1 Customer is required for **every** courier order

```
supabase/migrations/20260627201534_...c879.sql:381-383
IF p_delivery = 'courier' AND (p_courier_id IS NULL OR p_customer_id IS NULL) THEN
  RAISE EXCEPTION 'courier_requires_customer_and_courier';
END IF;
```

A courier order with no customer is rejected **regardless of paid amount or
outcome**, including a fully-collected order that produces no customer debt.

### 1.2 Direct sale requires a customer only when a balance remains

```
:397-399
IF p_delivery = 'direct' AND p_paid < v_total AND p_customer_id IS NULL THEN
  RAISE EXCEPTION 'customer_required_for_debt';
END IF;
```

So the customer rule is already outcome-based for direct sales, but not for
courier sales.

### 1.3 Courier state is derived purely from `p_paid` at creation

```
:401-408
IF p_delivery = 'courier' THEN
  v_order_paid := 0;
  v_order_collected := p_paid;
  v_order_courier_state := CASE
    WHEN p_paid = 0        THEN 'pending'
    WHEN p_paid >= v_total THEN 'delivered_full'
    ELSE                       'delivered_partial' END;
  v_status := 'debt';
```

Consequences:

- `orders.paid` is always `0` for courier orders at creation; the collected
  amount goes to `collected_by_courier` (`v_order_collected`).
- `order.status` is always `'debt'` for a new courier order, even one collected
  in full. There is no operational courier status stored separately.
- `p_paid = 0` **always** maps to `pending`. A "delivered but not collected"
  outcome (`delivered_none`) **cannot be expressed at sale-creation time**; it is
  reachable only later via `update_courier_order_state`.

### 1.4 No payment row for courier custody at creation

```
:438-441
IF p_delivery = 'direct' AND p_paid > 0 THEN
  INSERT INTO public.payments(... kind='sale' ...);
END IF;
```

Courier collection never enters `payments` at creation — correct per
"Delivered is not settled". Money only enters `payments` at settlement.

## 1a. Effective database CHECK constraints (independent-review correction)

The RPC guard is **not** the only enforcement. `orders` carries CHECK
constraints added in
`supabase/migrations/20260626155319_...4e.sql:12-34`, all `NOT VALID`:

```
:12-16  orders_customer_required_when_unpaid
          CHECK (paid >= total OR customer_id IS NOT NULL) NOT VALID
:18-22  orders_courier_requires_courier_id
          CHECK (delivery <> 'courier' OR courier_id IS NOT NULL) NOT VALID
:24-28  orders_courier_requires_customer_id
          CHECK (delivery <> 'courier' OR customer_id IS NOT NULL) NOT VALID
:30-34  orders_collected_not_over_total
          CHECK (collected_by_courier <= total) NOT VALID
```

Critical facts, verified in code:

- **`NOT VALID` skips *existing* rows only; it is still enforced on every new
  INSERT/UPDATE.** So these constraints actively block new customer-less courier
  orders **even if the RPC guard is relaxed**. Relaxing the RPC alone is
  insufficient — the earlier draft missed this.
- `orders_customer_required_when_unpaid` keys off **`paid`**, but courier orders
  always store `paid = 0` at creation (§1.3) — courier custody lives in
  `collected_by_courier`, not `paid`. Therefore `paid >= total` is false for
  every non-zero-total courier order, so this constraint **requires a customer on
  every courier order, including `delivered_full`** (collected in full, zero
  debt).
- `orders_courier_requires_customer_id` independently requires a customer on
  every courier order regardless of outcome.
- Net effect: **two** constraints must be replaced with the outcome-based rule
  (see COURIER_STATE_CONTRACT / MIGRATION_IMPACT). `orders_courier_requires_courier_id`
  (courier id) and `orders_collected_not_over_total` are kept.

## 2. Courier state-update RPC: `update_courier_order_state`

Latest definition: `supabase/migrations/20260626233231_...c9.sql`.

- Accepts `pending | delivered_none | delivered_partial | delivered_full`;
  `returned` is delegated to `return_courier_order`.
- `delivered_full` → `collected_by_courier = total`.
- `delivered_partial` → `collected_by_courier = clamp(0, total, p_collected)`.
- `pending` / `delivered_none` → `collected_by_courier = 0`.

So `delivered_none` is a valid stored state with zero custody and full customer
debt — but only settable **after** creation.

**State-transition hole (independent-review correction).**
`update_courier_order_state(p_order_id, p_state, p_collected)` does **not** accept
or validate `customer_id`. Once customer-less courier orders are permitted at
creation (pending / delivered_full), this RPC can transition a **customer-less**
`pending` order to `delivered_partial` or `delivered_none`, which creates customer
debt — with **no customer attached**. The only backstop today is the
`orders_courier_requires_customer_id` CHECK, which this change removes; the
replacement outcome-based CHECK would reject such an UPDATE, but the RPC would
surface a raw constraint violation rather than attach a customer atomically. The
earlier draft's statement that this RPC "needs no change" is **withdrawn**. The
required atomic resolution contract is defined in COURIER_STATE_CONTRACT §
"Post-creation transition".

## 3. Settlement RPC: `settle_courier_orders`

Definition: `supabase/migrations/20260627201534_...c879.sql:448-503`.

- Source of truth for collected money is the stored `collected_by_courier`
  (`:478`).
- Guards `collected > total - paid` → `collected_exceeds_remaining` (`:479-481`).
- On settle: `paid += collected`, recomputes `status`, flips the row to
  `delivery='direct'`, `courier_id=NULL`, `courier_state=NULL`,
  `collected_by_courier=0` (`:489-492`).
- Inserts a `payments` row with **`method` hard-coded to `'cash'`** (`:496`):

```
INSERT INTO public.payments(... kind='courier_settlement', method='cash', ...);
```

There is no way to record whether the customer transferred to the shop, paid the
courier in cash, or the courier later handed over by transfer — one field is
overloaded for three distinct events.

## 4. Return RPC: `return_courier_order`

Definition: `supabase/migrations/20260626233231_...c9.sql`.

- Rejects return when `paid > 0` OR `collected_by_courier > 0`
  (`cannot_return_partially_paid_order`).
- Restores stock, sets `courier_state='returned'`, `collected_by_courier=0`,
  `courier_id=NULL`, `delivery='direct'`.

## 5. Debt / custody accounting (server)

`close_day` (latest: `supabase/migrations/20260704105413_...908.sql`) computes
customer debt as:

```
CASE
  WHEN courier_state = 'returned'                         THEN 0
  WHEN delivery='direct' OR courier_id IS NULL            THEN GREATEST(total-paid,0)
  WHEN delivery='courier' AND courier_state='delivered_none'    THEN total
  WHEN delivery='courier' AND courier_state='delivered_partial' THEN GREATEST(total-collected_by_courier,0)
  ELSE 0
END
```

and unsettled custody as `SUM(collected_by_courier)` over courier orders.

`close_day` **is** outcome-aware: its CASE keys on `courier_state` and never
references `customer_id`, so a customer-less pending/`delivered_full` order
contributes 0 debt correctly. This function does **not** need to change.

**But the blanket earlier claim that "all existing server aggregates already
handle all five courier states" is WRONG and is withdrawn.** Per-function
reality (independent-review correction), verified in code:

| Function | Debt/custody by state? | Effect of customer-less courier orders |
|---|---|---|
| `close_day` (`20260704105413`) | Yes, correct | None — keyed on `courier_state`, not `customer_id`. No change needed. |
| `get_tenant_today_estimate` (`20260627201534:240-276`) | **Does not compute debt or custody at all** | Returns only sales/collected/expenses/profit. My earlier A10 claim that it returns debt/custody was false. |
| `get_platform_admin_overview` (`20260627201534:282-324`) | Partial | `open_customer_debts` counts only `delivery='direct' OR courier_id IS NULL` — courier debt is **excluded entirely**; `critical_alerts` does not check `customer_id`. |
| `get_platform_financial_health` (`20260626191523`) | Integrity checks | **False-positives** — see §5a. |
| `get_platform_tenants_health` (`20260626191523`) | Per-tenant health flag | Debt/custody aggregation excludes courier debt (`delivery='direct' OR courier_id IS NULL`); health flag keyed on sign/overflow, not `customer_id`. Low but must be reviewed. |
| `get_platform_day_close_health` (`20260627201534:326-355`) | Recompute vs stored | Reconciliation only; unaffected by customer nulls, but exercised by new rows. |

## 5a. Platform financial-health checks false-positive on valid new orders

`get_platform_financial_health` (`20260626191523_...b1.sql`) runs a fixed check
array. Two checks flag now-valid orders as corrupt:

```
key='courier_missing_refs'  sev='Critical'
  SELECT COUNT(*) FROM orders WHERE delivery='courier' AND (customer_id IS NULL OR courier_id IS NULL)
key='debt_without_customer'  sev='Warning'
  SELECT COUNT(*) FROM orders WHERE status IN ('partial','debt') AND customer_id IS NULL
```

- `courier_missing_refs` (**Critical**) fires on **every** customer-less courier
  order — exactly the orders this change makes valid.
- `debt_without_customer` (**Warning**) also fires, because courier orders are
  created with `status='debt'` (§1.3), regardless of outcome.
- The paired detail RPC `get_platform_financial_health_rows` repeats the same two
  predicates for the `courier_missing_refs` and `debt_without_customer` keys and
  must be corrected in lock-step.

Both checks must become **outcome-aware** (flag only rows that genuinely carry
customer debt with no customer) or valid pilot orders will be reported as
Critical corruption. Tracked in PR-B.

## 6. Domain selectors (client) already model the target

`src/domain/finance/invoice-selectors.ts`:

- `getCustomerDebtForInvoice` — returned→0, direct→remaining, courier
  delivered_none→total, delivered_partial→total−collected, else 0.
- `getCourierCustodyForInvoice` — courier delivered_partial/full→collected.
- `getPendingCourierValueForInvoice` — courier pending→total (order value, not
  custody).
- `canCollectCustomerDebtForInvoice` — false while custody is held.

The selectors are correct against the target. The gaps are in the **RPC guard**,
the **creation-time state contract**, and the **screens**, not the math library.

## 7. UI: default sale flow routes to quick sale

`src/routes/_authenticated/app.tsx`:

- Desktop CTA → `go("sale_quick")` (`:291`).
- Header button "+ بيع سريع" → `go("sale_quick")` (`:302`).
- Bottom nav sale button → `go("sale_quick")` (`:329`).
- Success screen "بيع جديد" → `setScreen("sale_quick")` (`:1124`).
- The advanced `SaleScreen` is reachable only from inside `SaleQuickScreen`
  via `setScreen("sale")` (`:1335`).

The advanced flow exists but is hidden behind quick sale.

## 8. UI: payment sheet customer rule conflicts with the RPC

`PaymentSheet` in `app.tsx:929-1073`:

- `needsCustomer = remaining > 0` (`:943`).
- `canSave = subtotal>0 && !overpaid && (!needsCustomer || customerId) && (!needsCourier || courierId)` (`:945`).

Reproducible conflicts against the RPC (§1.1):

| UI action (courier) | UI `needsCustomer` | UI allows save w/o customer? | RPC result |
|---|---|---|---|
| status=paid (collected in full, remaining 0) | false | **yes** | **rejects** `courier_requires_customer_and_courier` |
| status=debt (paid 0 → pending) | true (remaining=total) | no | would reject too, and forces an unnecessary customer for a pending order |
| status=partial | true | no | consistent |

So a fully-collected courier order is offered as saveable without a customer,
then fails at the RPC; and a pending courier order is forced to have a customer
even though it creates no debt yet.

## 9. UI: courier result wording is generic and one label is wrong

- Payment status buttons are generic "مدفوع / جزئياً / دين" (`:964`), not
  courier outcomes.
- For courier, the paid field is relabelled "قبضه المندوب الآن" (`:973`) — good,
  but the outcome semantics are still the generic three.
- In `CourierCustodyScreen`, the control reads **"لم تُسلَّم (دين)"** (`:566`)
  and the confirmation reads **"لم تُسلَّم — دين كامل على العميل"** (`:484`,
  `:579`). This maps to `delivered_none`, whose real meaning is *delivered but
  not collected*. The wording tells the owner "not delivered" while creating a
  full customer debt — commercially contradictory.

## 10. UI: success screen always says "مدفوع"

`SaleSuccessScreen` (`app.tsx:1074-1129`):

```
:1112  الإجمالي {fmt(s.total)} · مدفوع {fmt(s.paid)}
```

`s.paid` is the amount the user entered. For a courier order that is
`collected_by_courier` (custody), not cash in the till — yet the screen labels it
"مدفوع".

## 11. Adjacent, explicitly OUT OF SCOPE (do not fix here)

- `src/features/home/HomeScreen.tsx:18` — `invoices.slice(-3).reverse()` shows the
  oldest three, not the latest. Tracked as BUGFIX-APP-001.
- Courier invoices displaying as `debt` on the home list stems from
  `order.status='debt'` (§1.3). The *display* correction is in FIN-COURIER-001's
  UI PR; the underlying midnight/timezone `useMemo` dependency and generic list
  ordering are BUGFIX-APP-001.

## 12. Existing verification baseline

- Financial-rules SQL suite `tests/financial-rules/rules.sql` covers T1–T15,
  including courier cases: **T5** (courier pending, paid=0, custody=0, no payment
  row), **T6** (courier partial money → custody, no payment row), **T7** (collect
  blocked while courier holds custody), **T8** (settlement → cash payment),
  **T9/T10** (returned restores stock, no debt).
- **T5 and T6 currently pass a customer id** to `create_sale_with_items` for
  courier orders, because both the RPC guard **and the CHECK constraints** (§1a)
  require it today. These tests must be extended (not weakened) to cover the
  no-customer courier path, which requires replacing the constraints as well as
  the RPC.
- Note: `get_tenant_today_estimate` returns only sales/collected/expenses/
  realized_profit — it does **not** expose debt or custody (§5), so it is not a
  debt/custody regression surface.
- Unit selectors: `tests/unit/invoice-selectors.test.ts`.
- E2E: `tests/e2e/sale-dashboard-close.py`, `tests/e2e/isolated-auth-smoke.py`.
- Visual: `tests/visual/mobile-rtl-smoke.py`.
