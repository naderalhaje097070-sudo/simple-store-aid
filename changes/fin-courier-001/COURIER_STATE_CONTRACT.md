# FIN-COURIER-001 — Courier State Contract

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Defines the courier state machine, its accounting effects, the
creation-time RPC contract, the CHECK-constraint replacement, and the
post-creation atomic transition contract.

## States (`courier_state` enum — already exists, unchanged)

`pending | delivered_none | delivered_partial | delivered_full | returned`

No enum values are added or removed. `courier_state` is nullable (direct and
settled orders carry NULL); `total`, `paid`, `delivery` are `NOT NULL`
(`20260626143241_...8fe.sql:55-56`, `20260626143657_...8f.sql:26`).

## Accounting effect of each state

| courier_state       | order.status target | collected_by_courier | courier custody | customer debt              | customer required |
|---------------------|---------------------|----------------------|-----------------|----------------------------|-------------------|
| `pending`           | debt (operational)  | 0                    | 0               | 0 (not yet)                | No                |
| `delivered_full`    | debt→settle-ready   | total                | total           | 0                          | No                |
| `delivered_partial` | debt                | collected (0<c<total)| collected       | total − collected (> 0)    | **Yes**           |
| `delivered_none`    | debt                | 0                    | 0               | total                      | **Yes**           |
| `returned`          | debt (no debt calc) | 0                    | 0               | 0 (stock restored)         | No                |

Columns match `close_day` (`20260704105413_...908.sql`) and
`src/domain/finance/invoice-selectors.ts`; this contract does not change those
formulas.

## 1. Effective CHECK-constraint replacement (NULL-safe, forward-only)

Two `NOT VALID` CHECK constraints on `orders` (`20260626155319_...4e.sql`) block
customer-less courier orders on every new write (CURRENT_BEHAVIOR §1a):

- `orders_customer_required_when_unpaid` — `CHECK (paid >= total OR customer_id IS NOT NULL)`
- `orders_courier_requires_customer_id` — `CHECK (delivery <> 'courier' OR customer_id IS NOT NULL)`

Both must be replaced by a single outcome-based constraint. **Two corrections
from independent review (finding 1):**

1. **`returned` must be allowed without a customer independently of `delivery`.**
   `return_courier_order` flips the row to `courier_state='returned'`,
   `delivery='direct'`, `courier_id=NULL` (`20260626233231_...9c.sql:136-141`). A
   delivery-keyed permission would reject a customer-less returned order.
2. **The expression must be NULL-safe.** A courier row with `courier_state IS
   NULL` must **not** pass by PostgreSQL three-valued logic (a CHECK that
   evaluates to NULL is treated as satisfied). Every branch is written to yield a
   definite boolean, so a NULL `courier_state` on a courier row **fails closed**.

Proposed constraint:

```
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;

ALTER TABLE public.orders
  ADD CONSTRAINT orders_customer_required_when_debt
  CHECK (
    customer_id IS NOT NULL
    -- returned is debt-free regardless of delivery (return flips delivery→direct)
    OR (courier_state IS NOT NULL AND courier_state = 'returned')
    -- direct, no courier outcome, fully paid
    OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
    -- courier, debt-free outcomes; NOT NULL guard makes NULL courier_state fail closed
    OR (delivery = 'courier' AND courier_state IS NOT NULL
          AND courier_state IN ('pending','delivered_full'))
  ) NOT VALID;
```

Evaluation when `customer_id IS NULL` (all branches two-valued because
`courier_state` is guarded and `delivery/paid/total` are `NOT NULL`):

| Row | Result |
|---|---|
| courier pending | PASS (courier branch) |
| courier delivered_full | PASS (courier branch) |
| courier→returned (now delivery=direct) | PASS (returned branch) |
| courier, `courier_state IS NULL` | **FAIL** (all branches false — fail closed) |
| direct debt (paid<total) | **FAIL** |
| courier delivered_partial / delivered_none | **FAIL** |
| direct fully paid | PASS (direct branch) |

- `orders_courier_requires_courier_id` and `orders_collected_not_over_total` are
  **kept unchanged**.
- Added **`NOT VALID`**; **not** validated in the same migration. Historical rows
  are not proven clean (the old constraints were themselves `NOT VALID` — see
  DATA_IMPACT / MIGRATION_IMPACT). Validation is a separate controlled step after
  a preflight shows zero violating rows (finding 2, decision 5B).

## 2. Creation-time state contract and the v2 RPC (decision 5A)

Today `create_sale_with_items` (`20260627201534_...c879.sql:401-408`) infers
state from `p_paid`, so `pending` and `delivered_none` are indistinguishable at
creation. Resolved by an explicit outcome parameter.

**`create_sale_with_items_v2`** — canonical, single source of truth. Signature:

```
create_sale_with_items_v2(
  p_customer_id  uuid,
  p_delivery     public.delivery_kind,
  p_courier_id   uuid,
  p_paid         numeric,
  p_method       public.payment_method,
  p_items        jsonb,
  p_courier_state public.courier_state   -- explicit, typed, NO DEFAULT
)
```

Rules enforced in `_v2`:

- **Direct** (`p_delivery='direct'`):
  - `p_courier_state` **must be NULL** → else `courier_state_must_be_null_for_direct`.
  - `p_courier_id` **must be NULL** → else `courier_id_must_be_null_for_direct`.
  - Customer required iff `p_paid < total` (`customer_required_for_debt`).
- **Courier** (`p_delivery='courier'`):
  - `p_courier_id` **required** → else `courier_requires_courier`.
  - `p_courier_state` **required** and ∈ `{pending, delivered_none,
    delivered_partial, delivered_full}`.
  - **`returned` is rejected at creation** → `returned_not_allowed_at_creation`
    (a return is only ever produced by `return_courier_order`).
  - `collected_by_courier`: pending→0 (`p_paid=0`), delivered_none→0 (`p_paid=0`),
    delivered_partial→`p_paid` (0<p_paid<total), delivered_full→total
    (`p_paid=total`).
  - `orders.paid` stays 0 for all courier creations.
  - Customer required iff outcome creates debt: `delivered_partial` or
    `delivered_none` → `customer_required_for_debt`; `pending`/`delivered_full` →
    optional.

**Adapter:** the existing six-parameter `create_sale_with_items` is kept as a thin
adapter that derives `p_courier_state` from `p_paid` (0→pending, full→
delivered_full, else delivered_partial) and delegates to `_v2`. It holds **no
independent financial logic**. Rejected: a defaulted-parameter overload
(ambiguous under PostgREST; unproven).

## 3. Normal outcome transition — `update_courier_outcome_v2` (decision 5C, finding 3)

The normal outcome-update RPC is a **named** `update_courier_outcome_v2`
(canonical). The old `update_courier_order_state` is preserved **only** as a
compatibility adapter if a caller still needs it; canonical state/financial logic
lives in exactly one place. **The adapter delegates to the v2 safety rules and
must not reproduce the old unsafe behavior** — the old RPC today permits custody
reduction and backward transitions (e.g. `delivered_full → pending`,
`delivered_partial → delivered_none`); those become rejected. Backward
compatibility covers only previously valid **and safe** flows
(BACKWARD_COMPATIBILITY §1). The canonical RPC updates, in **one server-side
transaction** under the existing `SELECT ... FOR UPDATE` row lock:

- `courier_state` (the new outcome),
- `collected_by_courier`,
- `customer_id` when the target outcome creates debt.

### Approved transition matrix

| From | Allowed → |
|---|---|
| `pending` | `delivered_none`, `delivered_partial`, `delivered_full`, `returned` |
| `delivered_none` | `delivered_partial`, `delivered_full`, `returned` |
| `delivered_partial` | `delivered_full` |
| `delivered_full` | *(settlement only — no outcome transition)* |
| `returned` | *terminal* |
| *settled* (delivery flipped to direct, courier_state NULL) | *terminal* |

### Invariants

- **`collected_by_courier` is monotonic non-decreasing** before settlement.
  `pending(0) → delivered_none(0) → delivered_partial(c) → delivered_full(total)`
  never decreases.
- **Reducing `collected_by_courier` is forbidden** through this RPC
  (`custody_cannot_decrease`). This is a real change from today's
  `update_courier_order_state`, which would zero custody on a
  `delivered_full → delivered_none` move.
- **Backward transitions are forbidden** (`invalid_transition`): e.g.
  `delivered_full → delivered_partial`, `delivered_partial → delivered_none`,
  anything `→ pending`, `delivered_partial → returned`.
- **Same-state retry** with an identical financial value **may be idempotent**
  (no-op success), to tolerate client retries; a same-state call with a different
  value is rejected (`custody_cannot_decrease` / `invalid_transition`).
- **Customer attachment is atomic** for debt-creating targets
  (`delivered_partial`, `delivered_none`): the order must already have a customer
  or a same-tenant `p_customer_id` is supplied and written in the same
  transaction; cross-tenant/nonexistent → `customer_not_found` /
  `forbidden_tenant`; never persist a debt state before the customer is attached.
- **`returned` continues through `return_courier_order`** (delegated), which keeps
  its `paid=0 AND collected_by_courier=0` guard and stock restore — this is why
  `delivered_partial → returned` is not allowed (custody > 0).
- **Financial corrections/reversals** (reducing custody, un-settling, reversing a
  delivered outcome) are **out of scope for this RPC** and must go through a
  separate audited correction workflow (future governed change). Documented so the
  normal path stays append-only in custody terms.

### `delivered_none → returned` — explicit business condition (finding: clarification)

`delivered_none` means *the goods were delivered but nothing was collected* (full
customer debt); `returned` means *the goods physically came back and re-enter
stock* (no debt). The transition is therefore permitted **only when the goods are
physically returned after delivery** — never as a mere change of mind or a way to
clear a debt without the goods coming back. It is executed through
`return_courier_order` and must satisfy, atomically in one transaction:

- **Physical return is the trigger** — the caller asserts the goods came back;
  the state flip records that event, it does not invent it.
- **No settled payment** and **`collected_by_courier = 0`** — enforced by
  `return_courier_order`'s existing `paid = 0 AND collected_by_courier = 0` guard
  (`20260626233231_...9c.sql`). `delivered_none` already has collected = 0, so it
  qualifies; `delivered_partial` does not.
- **Atomic cancellation of the debt effect** — customer debt for `delivered_none`
  is *derived* (`close_day` CASE / `getCustomerDebtForInvoice`), not a stored
  payable; the same `UPDATE` that sets `courier_state='returned'` makes the
  derived debt 0 in the same transaction (returned has priority → 0). No separate
  debt row to reverse; `collect_order_debt` is already blocked on returned
  (`cannot_collect_returned_order`).
- **Stock restored exactly once** — `return_courier_order` restores each
  `order_items` line once per successful return.
- **Idempotent / terminal protection** — after the first return the row is
  `delivery='direct'`, `courier_state='returned'`; a second return (or any further
  outcome transition) is **rejected** because `return_courier_order` requires
  `delivery='courier'` (`not_a_courier_order`), so stock is never restored twice
  and a returned/settled order cannot transition again.
- **Audit evidence** — the return is recorded in the financial/audit log
  (`_fin_audit_trigger` on `orders` UPDATE already captures before/after;
  the contract requires the return to be attributable in the audit trail).

These conditions are contract + test requirements to be proven before Gate 4;
they do not require a new change.

The replaced CHECK constraint (§1) is the schema backstop; `update_courier_
outcome_v2` provides the typed errors, the monotonic/forbidden-transition
enforcement, and the atomic customer attachment so callers never hit a raw
constraint violation.

## 4. Settlement / handover (unchanged here)

`settle_courier_orders` consumes `collected_by_courier`, moves it into `payments`,
and flips the order to `direct` (settled). Delivered → settled is the only place
money enters `payments` for courier orders. **The settlement payment-method
redesign is deferred to `FIN-SETTLEMENT-METHOD-001`** (the hard-coded
`method='cash'` at `20260627201534_...c879.sql:496` is documented there, not fixed
here).
