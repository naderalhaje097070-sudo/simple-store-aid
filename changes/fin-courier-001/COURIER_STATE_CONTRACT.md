# FIN-COURIER-001 — Courier State Contract

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Defines the courier state machine, its accounting effects, the
creation-time RPC contract, the CHECK-constraint replacement, and the
post-creation atomic transition contract.

## States (`courier_state` enum — already exists, unchanged)

`pending | delivered_none | delivered_partial | delivered_full | returned`

No enum values are added or removed.

## Accounting effect of each state

| courier_state       | order.status target | collected_by_courier | courier custody | customer debt              | customer required |
|---------------------|---------------------|----------------------|-----------------|----------------------------|-------------------|
| `pending`           | debt (operational)  | 0                    | 0               | 0 (not yet)                | No                |
| `delivered_full`    | debt→settle-ready   | total                | total           | 0                          | No                |
| `delivered_partial` | debt                | collected (0<c<total)| collected       | total − collected (> 0)    | **Yes**           |
| `delivered_none`    | debt                | 0                    | 0               | total                      | **Yes**           |
| `returned`          | debt (no debt calc) | 0                    | 0               | 0 (stock restored)         | No                |

Columns match `close_day` (`20260704105413_...908.sql`) and
`src/domain/finance/invoice-selectors.ts` exactly; this contract does not change
those formulas.

## 1. Effective CHECK-constraint replacement (forward-only)

The RPC guard is not the only enforcement. Two `NOT VALID` CHECK constraints on
`orders` (`20260626155319_...4e.sql`) block customer-less courier orders on every
new write (see CURRENT_BEHAVIOR §1a):

- `orders_customer_required_when_unpaid` — `CHECK (paid >= total OR customer_id IS NOT NULL)`
- `orders_courier_requires_customer_id` — `CHECK (delivery <> 'courier' OR customer_id IS NOT NULL)`

Because courier orders always store `paid = 0`, the first constraint requires a
customer on **every** courier order, including `delivered_full`. Both must be
replaced by a single outcome-based constraint in a **new forward-only** migration
(no edit to the applied file):

```
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;

ALTER TABLE public.orders
  ADD CONSTRAINT orders_customer_required_when_debt
  CHECK (
    customer_id IS NOT NULL
    OR (delivery = 'direct'  AND paid >= total)
    OR (delivery = 'courier' AND courier_state IN ('pending','delivered_full','returned'))
  ) NOT VALID;
```

- `orders_courier_requires_courier_id` (courier id) is **kept unchanged**.
- `orders_collected_not_over_total` is **kept unchanged**.
- `NOT VALID` is safe: every historical row satisfied the stricter old
  constraints, so it also satisfies this looser one. A separate `VALIDATE
  CONSTRAINT` step may run in the same migration since no legacy row can violate
  it; decision recorded in MIGRATION_IMPACT.
- This constraint is the **schema-level backstop** that keeps the state-transition
  hole (§3) from ever persisting debt without a customer, independent of RPC
  correctness.

## 2. Creation-time state contract and the v2 RPC

Today `create_sale_with_items` (`20260627201534_...c879.sql:401-408`) infers
state from `p_paid` alone, so `pending` and `delivered_none` are
indistinguishable at creation (both collected = 0). The target requires both to
be expressible at creation, because `pending` needs no customer while
`delivered_none` does.

### RPC design decision (independent-review correction to finding 5)

A `DEFAULT`-parameter overload of `create_sale_with_items` is **not** adopted as
the preferred path. Under Supabase/PostgREST, overload resolution with defaulted
parameters can be ambiguous, and that ambiguity is not proven safe here. Adopting
it would require an isolated proof test first, which is out of scope for
documentation.

**Preferred design:**

- Introduce a clearly named **`create_sale_with_items_v2`** (canonical, single
  source of truth) with an explicit courier outcome parameter:
  `p_courier_state text` accepting
  `pending | delivered_none | delivered_partial | delivered_full`
  (`returned` is never a creation outcome).
- Keep the existing six-parameter `create_sale_with_items` as a thin
  **backward-compatible adapter** that calls `_v2`, mapping its `p_paid` to the
  legacy paid-derived outcome (0→pending, full→delivered_full, else
  delivered_partial) and passing the customer through. The adapter contains **no
  independent financial logic** — it only translates arguments and delegates, so
  there is exactly one place where state, custody, debt, and stock are decided.
- The client (`src/lib/db.ts`) is repointed to `_v2`; older/cached clients
  calling the six-param adapter keep working unchanged.

`_v2` behavior by outcome:

- `pending` → `collected_by_courier = 0`, requires `p_paid = 0`.
- `delivered_none` → `collected_by_courier = 0`, requires `p_paid = 0`.
- `delivered_partial` → `collected_by_courier = p_paid` (0 < p_paid < total).
- `delivered_full` → `collected_by_courier = total` (p_paid = total).
- `orders.paid` stays 0 for all courier creations (unchanged).

### Customer-requirement rule inside `_v2`

Replace the blanket courier guard
(`20260627201534_...c879.sql:381-383`) with an outcome-based rule, mirroring the
existing direct-sale rule (`:397-399`):

```
IF p_delivery = 'courier' AND p_courier_id IS NULL THEN
  RAISE EXCEPTION 'courier_requires_courier';
END IF;

IF p_customer_id IS NULL AND <outcome creates debt> THEN
  RAISE EXCEPTION 'customer_required_for_debt';
END IF;
```

`<outcome creates debt>`:

- direct: `p_paid < total`
- courier `delivered_partial`: always (collected < total)
- courier `delivered_none`: always
- courier `pending` / `delivered_full`: never

`customer_required_for_debt` is reused (one debt vocabulary).
`courier_requires_customer_and_courier` is retired for `_v2`; the legacy adapter
still passes a customer so it never observes a changed path.

## 3. Post-creation transition — atomic resolution contract (finding 2)

`update_courier_order_state` today takes no `customer_id` and can move a
customer-less `pending` order to `delivered_partial`/`delivered_none`, creating
debt with no customer. This must be closed with an **atomic** contract. Preferred
shape: a named **`resolve_courier_order_v2`** (or an added `p_customer_id` on the
transition RPC) that, in **one server-side transaction**, updates:

- the courier outcome (`courier_state`),
- `collected_by_courier`,
- `customer_id` when the outcome requires it.

Contract requirements:

- **Allow** `pending → delivered_full` with no customer (zero debt).
- **Reject** `pending → delivered_partial` / `delivered_none` when the order has
  no customer **and** none is supplied → `customer_required_for_debt`.
- **Allow** the transition when the order already has a customer, or a
  `p_customer_id` is supplied that belongs to the **same tenant**.
- **Reject** a supplied customer that is cross-tenant or nonexistent →
  `customer_not_found` / `forbidden_tenant` (validate via
  `SELECT ... WHERE id = p_customer_id AND tenant_id = current_tenant_id()`).
- **Never** persist a debt-creating state before the customer is attached — the
  `customer_id` write and the `courier_state` write happen in the same
  transaction and under the existing `SELECT ... FOR UPDATE` row lock.
- **`returned` stays delegated** to `return_courier_order` (which keeps its
  `paid = 0 AND collected_by_courier = 0` guard and stock restore).

The replaced CHECK constraint (§1) is the schema backstop; the RPC provides the
clear error and the atomic customer attachment so callers never hit a raw
constraint violation.

## 4. Settlement / handover (unchanged here)

`settle_courier_orders` consumes `collected_by_courier`, moves it into
`payments`, and flips the order to `direct` (settled). Delivered → settled is the
only place money enters `payments` for courier orders. **The settlement
payment-method redesign is out of scope for FIN-COURIER-001 and is deferred to a
separate governed change, `FIN-SETTLEMENT-METHOD-001`** (the hard-coded
`method='cash'` at `20260627201534_...c879.sql:496` is documented there, not
fixed here).
