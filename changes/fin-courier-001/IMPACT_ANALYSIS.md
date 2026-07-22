# FIN-COURIER-001 — Impact Analysis (NAADF-CMF Change Gate 2)

Status: Draft for review. Search-based caller/consumer map with impact per area.

## Caller / consumer map

### `create_sale_with_items`
- Client wrapper: `src/lib/db.ts:440-463` (`useCreateSale`), called with
  `p_customer_id, p_delivery, p_courier_id, p_paid, p_method, p_items`.
- UI caller: `PaymentSheet.onSave` → `createSaleAsync` in
  `src/routes/_authenticated/app.tsx:909-921` (advanced `SaleScreen`) and the
  quick-sale path in `SaleQuickScreen` (`app.tsx:1132+`, `setScreen("sale_success")`
  at `:1228`).
- Tests: `tests/financial-rules/rules.sql` T1–T8 exercise this RPC directly.

### `update_courier_order_state`
- Client wrapper: `src/lib/db.ts:530` (`updateCourierStateAsync`, exposed via
  `ctx` at `app.tsx:267`).
- UI caller: `CourierCustodyScreen` mark controls (`app.tsx:445-597`).

### `settle_courier_orders`
- Client wrapper: `src/lib/db.ts:507` (`useSettleCourier`).
- UI caller: `SettlementsScreen` (`app.tsx:599-694`).

### Debt/custody read model consumers
- `src/domain/finance/invoice-selectors.ts` (single source of truth).
- `HomeScreen` totals/alerts (`app.tsx:220-230`, `src/features/home/HomeScreen.tsx`).
- `close_day` / `get_tenant_today_estimate` / `get_platform_admin_overview`
  (server aggregates).

## Impact by area

### UI
- **Default flow:** change 4 entry points from `sale_quick` to `sale`
  (`app.tsx:291,302,329,1124`); add a labelled secondary quick-sale shortcut.
- **PaymentSheet:** replace generic status buttons with courier outcomes when
  delivery=courier; change `needsCustomer` to outcome-based
  (`app.tsx:943,945,964,973`).
- **CourierCustodyScreen:** rename "لم تُسلَّم (دين)" → "تم التسليم دون تحصيل";
  ensure "not delivered" routes to returned (`app.tsx:484,566,579`).
- **SaleSuccessScreen:** type-aware wording (`app.tsx:1112`).
- **Courier invoice status display:** derive operational status via selectors,
  not `order.status` alone.
- Risk: medium. Screens are large and share one route file; no logic should be
  duplicated — reuse `invoice-selectors`.

### API / RPC contracts
- `create_sale_with_items`: **contract change** (customer rule + optional
  creation-time courier outcome). New forward-only overload; old signature
  preserved. This is the highest-risk item.
- `settle_courier_orders`: possible method-semantics change (open item).
- `update_courier_order_state`, `return_courier_order`: **no change** required;
  they already support the target states.

### Database schema & data
- No column adds/drops required for the core rule change (enum already complete,
  `collected_by_courier` already exists).
- If settlement-method separation is approved, it may add a nullable column or a
  new payment `kind`; that is a separate, additive, forward-only change.
- Existing rows: unaffected by the RPC guard change (guard only runs on new
  inserts). See DATA impact below.

### Auth / authorization
- No change. All affected RPCs are `SECURITY DEFINER` with `_assert_staff` /
  `_assert_owner`. Direct table writes remain revoked
  (`20260627201534_...c879.sql:511-513`). No RLS change.

### Tenant isolation
- No change. Tenant is derived from `current_tenant_id()` inside the RPCs.

### Business rules & state transitions
- Core of the change (see COURIER_STATE_CONTRACT, CUSTOMER_REQUIREMENT_MATRIX).
- Invariants preserved: returned ≠ debt/custody; delivered ≠ settled; custody
  never enters `payments` before settlement.

### Financial operations & reports
- `close_day`, `get_tenant_today_estimate`, `get_platform_admin_overview`,
  `get_platform_day_close_health`: formulas **unchanged**; they already handle all
  five courier states. Must be re-verified as regression, not modified.
- New capability (create-time `delivered_none`, no-customer pending/full) must be
  proven not to distort day-close debt/custody.

### Background jobs / integrations
- None affected. No cron or external integration reads courier state.

### Performance
- Out of scope by explicit instruction. No pagination/loading changes here.

### Tests & CI
- Financial-rules SQL suite (T1–T15) must be extended: no-customer courier
  create paths, create-time `delivered_none`, and negative cases (partial/none
  without customer must fail). Existing T5/T6 pass a customer today and must be
  kept plus complemented, never weakened.
- Unit selectors: add cases if UI debt derivation is centralized.
- E2E/visual: cover default-advanced-flow and courier wording on mobile+desktop.
- CI Quality lints only changed JS/TS; SQL correctness is proven by the isolated
  financial-rules workflow — both must pass on the branch head.

### Deployment & rollback
- Forward-only migration; no edits to applied migrations. Rollback is an
  additive corrective migration, not a revert of an applied file. See
  ROLLBACK_PLAN.

### Backward compatibility
- Old RPC signature preserved; historical rows unaffected. See
  BACKWARD_COMPATIBILITY.

## Cross-change conflicts to avoid
- Do **not** merge with BUGFIX-APP-001 (home slice, midnight dependency),
  PERF-APP-001, or EMP-*. Those touch the same route file (`app.tsx`) and the
  same home screen; keep commits scoped so reviews stay independent (DEC-009,
  Architecture Rule 6).
