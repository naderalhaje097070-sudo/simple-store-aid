# FIN-COURIER-001 — Backward Compatibility

Status: Draft for review.

## 1. RPC signature compatibility

Current signature:

```
create_sale_with_items(
  p_customer_id uuid, p_delivery delivery_kind, p_courier_id uuid,
  p_paid numeric, p_method payment_method, p_items jsonb)
```

Constraints:

- Applied migrations are immutable; the existing function is not edited in place
  — a new forward-only migration `CREATE OR REPLACE`s it and/or adds an overload.
- **The existing parameter list must keep working** because the client sends
  exactly those six parameters (`src/lib/db.ts:445-452`). During and after
  rollout, a call with no courier-outcome argument must behave safely.

Compatibility strategy (one of, decided at Gate 3):

- **Preferred — additive overload.** Add
  `create_sale_with_items(..., p_courier_state text DEFAULT NULL)` as a new
  overload. When `p_courier_state IS NULL`, reproduce today's paid-derived
  mapping AND today's customer rule for legacy safety; when provided, apply the
  outcome-based rule. The client is updated to pass the new argument; older
  clients keep working.
- **Alternative — same signature, relaxed guard only.** If create-time
  `delivered_none` is deferred to a follow-up, the first migration only relaxes
  the customer guard (courier no longer forces a customer when no debt). This is
  strictly more permissive than today, so every previously-valid call remains
  valid.

Either way: **no previously-successful call becomes an error.** The only
behavioral change is that some previously-rejected calls (courier without
customer, no debt) now succeed.

## 2. Historical data compatibility

- The customer guard runs only on new inserts. Existing `orders` rows are never
  re-validated, so relaxing it cannot invalidate stored data.
- No `orders` rows are back-filled or mutated by this change.
- `collected_by_courier`, `courier_state`, `paid`, `status` semantics for
  existing rows are unchanged; `close_day` and selectors read them identically.

## 3. Enum compatibility

- `courier_state` already contains all five values used here; no enum migration.
  (Adding enum values would be forward-only and non-breaking, but is not needed.)
- `order_status` is unchanged. Note there is deliberately **no** `returned`
  value in `order_status`; returned orders keep `status='debt'` and are excluded
  from debt by `courier_state='returned'` priority in `close_day`
  (`20260701090000_returned_order_not_debt.sql`). This change does not alter that.

## 4. Client/read-model compatibility

- `src/domain/finance/invoice-selectors.ts` already handles all five states and
  the no-customer case (customer is not an input to its debt/custody math), so no
  read-model breakage.
- Screens that display `order.status` for courier orders will show more accurate
  operational status after the UI PR, but the underlying stored `status` is
  unchanged, so any report keyed on `status` is unaffected.

## 5. Settlement-method compatibility (if that item ships)

- Existing `payments` rows with `kind='courier_settlement', method='cash'` remain
  valid. Any new method field/kind must be additive and default to today's
  behavior for historical rows.

## 6. Migration immutability guarantee

- No file under `supabase/migrations/` is edited.
- The change is one or more **new** timestamped migrations appended after
  `20260717180906_...` (current latest).
- Lovable-linked published history is not rewritten (DEC-010, AGENTS.md).
