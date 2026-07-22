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

Compatibility strategy (independent-review correction, finding 5):

- **Preferred — named v2 + adapter.** Introduce a clearly named
  `create_sale_with_items_v2` with an explicit final
  `p_courier_state public.courier_state` argument (**no DEFAULT**; decision 5A)
  as the single source of truth. Keep the existing six-parameter
  `create_sale_with_items` as a thin **adapter** that maps its `p_paid` to the
  legacy outcome and delegates to `_v2` — the adapter holds no independent
  financial logic. The client is repointed to `_v2`; older/cached clients calling
  the six-param adapter keep working with identical behavior.
- **Rejected — DEFAULT-parameter overload.** Adding
  `create_sale_with_items(..., p_courier_state public.courier_state DEFAULT NULL)` as an overload
  is **not** adopted: Supabase/PostgREST overload resolution with defaulted
  parameters can be ambiguous, and that ambiguity is unproven here. It may only be
  reconsidered if an isolated test proves resolution is unambiguous — out of scope
  for documentation.

Scope of the compatibility guarantee (clarified):

- **All previously valid and financially *safe* business flows remain
  supported.** Creating direct/courier sales, recording collection, settling,
  returning an uncollected order, and collecting debt all keep working.
- **This is not an absolute "every previously-successful call still succeeds"
  guarantee, and that claim is withdrawn.** The old
  `update_courier_order_state` technically permits **unsafe** operations —
  reducing `collected_by_courier`, reversing a delivered outcome, and backward
  transitions such as `delivered_full → pending` or
  `delivered_partial → delivered_none`. Under the canonical v2 rules these are
  **intentionally rejected** as unsafe (`custody_cannot_decrease` /
  `invalid_transition`). This is deliberate and financially correct, not a
  regression.
- **The legacy adapter must delegate to the canonical v2 safety rules.** It must
  **not** reproduce the old unsafe behavior merely to preserve technical
  compatibility. Its only job is argument translation; all state/financial
  guards live in `_v2`.

For the create path specifically: no previously-valid `create_sale_with_items`
call becomes an error (the adapter maps to `_v2`); the only new outcome is that
some previously-rejected calls (courier without customer, no debt) now succeed —
which also requires the CHECK-constraint replacement (§3a), not just the RPC.

## 2. Historical data compatibility

- The customer guard runs only on new inserts. Existing `orders` rows are never
  re-validated, so relaxing it cannot invalidate stored data.
- No `orders` rows are back-filled or mutated by this change.
- `collected_by_courier`, `courier_state`, `paid`, `status` semantics for
  existing rows are unchanged; `close_day` and selectors read them identically.

## 3a. CHECK-constraint compatibility

- Replacing `orders_customer_required_when_unpaid` +
  `orders_courier_requires_customer_id` with the NULL-safe, `returned`-aware
  `orders_customer_required_when_debt` (COURIER_STATE_CONTRACT §1) is **more
  permissive** for the customer-less debt-free courier shapes.
- **Correction (finding 2):** it is **not** proven that all historical rows would
  satisfy the new constraint. The old constraints were added `NOT VALID`
  (`20260626155319_...4e.sql:16,28`) and never validated existing data. Therefore
  the replacement is added `NOT VALID` and is **not** validated in the same
  migration; a separate historical-data preflight must show zero violations before
  a controlled `VALIDATE` step (MIGRATION_IMPACT steps 1–3).
- `orders_courier_requires_courier_id` and `orders_collected_not_over_total` are
  unchanged.
- Rollback restores the two original constraint definitions verbatim (known from
  `20260626155319_...4e.sql`), forward-only, and re-adds them `NOT VALID`. See
  ROLLBACK_IMPACT.

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

## 5. Settlement-method compatibility (deferred — FIN-SETTLEMENT-METHOD-001)

- The settlement payment-method redesign is **not** part of FIN-COURIER-001; it is
  the separate governed change FIN-SETTLEMENT-METHOD-001.
- For reference: existing `payments` rows with
  `kind='courier_settlement', method='cash'` remain valid, and any future method
  field/kind introduced by that change must be additive and default to today's
  behavior for historical rows.

## 6. Migration immutability guarantee

- No file under `supabase/migrations/` is edited.
- The change is one or more **new** timestamped migrations appended after
  `20260717180906_...` (current latest).
- Lovable-linked published history is not rewritten (DEC-010, AGENTS.md).
