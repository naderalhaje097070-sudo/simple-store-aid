# FIN-COURIER-001 — Rollback Plan

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Forward-only; no applied migration is edited or reverted in place.
See ROLLBACK_IMPACT for the Gate-2 artifact form.

## Principle

Applied migrations are immutable (Architecture Rule, DATABASE_CHANGE_POLICY).
Rollback is an **additive corrective migration** that restores the previous
definitions, plus reverting the UI commits — never editing or deleting a shipped
migration. Lovable-linked history is not rewritten.

## Scope of rollback (all layers introduced by this change)

1. **Sale RPC** — `create_sale_with_items_v2` and the six-param adapter.
2. **Transition RPC** — `update_courier_outcome_v2` (or the `p_customer_id`
   transition) and `update_courier_order_state`.
3. **CHECK constraints** — the replaced `orders_customer_required_when_debt`.
4. **Platform health / report functions** — the outcome-aware
   `get_platform_financial_health` (+ `_rows`) and any other reporting function
   changed in PR-B.
5. **UI** — PR-C commits (default flow, wording, success screen, status display).
6. **Data verification** — customer-less rows created during the change window.

## Database rollback steps (forward-only corrective migration)

1. **Constraints:** drop `orders_customer_required_when_debt`; re-add the two
   original constraints verbatim from `20260626155319_...4e.sql`
   (`orders_customer_required_when_unpaid`, `orders_courier_requires_customer_id`)
   as `NOT VALID`. **Do not `VALIDATE`** immediately — customer-less courier rows
   created during the change window would fail validation (see §Data). Validate
   only after those rows are reconciled.
2. **Sale RPC:** `CREATE OR REPLACE` `create_sale_with_items` back to the
   pre-change body (`20260627201534_...c879.sql:358-444`, blanket courier guard);
   `DROP FUNCTION` `create_sale_with_items_v2` (its specific signature only).
3. **Transition RPC:** `CREATE OR REPLACE` `update_courier_order_state` back to
   its pre-change body; `DROP FUNCTION` `update_courier_outcome_v2` if added.
4. **Health/report:** `CREATE OR REPLACE` `get_platform_financial_health` and
   `get_platform_financial_health_rows` (and any other PR-B function) back to
   their pre-change bodies (`20260626191523_...b1.sql`).

## UI rollback

- Revert PR-C. Because PR-C ships **after** and depends on PR-A/PR-B, roll back in
  reverse order: **PR-C UI → PR-B reporting → PR-A schema/RPC**.

## Data created during the change window

The only rows that could not have existed before are courier orders **without a
customer**:

- `pending` / `delivered_full` without a customer: zero debt; `close_day` and
  selectors handle them (`customer_id` is not an input to custody math). Safe to
  keep after rollback, **but** they violate the re-added
  `orders_courier_requires_customer_id` constraint. Therefore the corrective
  migration re-adds that constraint `NOT VALID` and leaves these rows in place;
  they are legal historical data under `NOT VALID`.
- `delivered_partial` / `delivered_none` without a customer should **not** exist,
  because the new rule (RPC + constraint) still requires a customer for those.
  Verify with:
  ```
  SELECT count(*) FROM orders
  WHERE delivery='courier' AND customer_id IS NULL
    AND courier_state IN ('delivered_partial','delivered_none');
  ```
  Expected 0. A non-zero result is a data-integrity finding to resolve before any
  constraint `VALIDATE`, not a silent revert.

## Rollback verification

1. Revert UI, then apply the corrective DB migration.
2. Run the financial-rules suite (T1–T15) on an isolated environment — the
   pre-change baseline must pass.
3. Run TEST_PLAN H (rollback cases) and the customer-less-row verification query.
4. Run `get_platform_financial_health` — it returns to its pre-change predicates.
5. Run the isolated auth UI smoke to confirm the sale path still works.

## What rollback does NOT do

- It does not edit or remove the migration that introduced the change.
- It does not touch production data or secrets.
- It does not delete legitimately-created customer-less courier orders; it leaves
  them under a `NOT VALID` constraint.

## Feature-flag option

Given High risk, a feature flag gating the PR-C default-advanced-sale routing and
courier-outcome UI is recommended so the UI can be dark-launched and rolled back
without a code revert. The DB relaxation (PR-A) is strictly more permissive and
may ship without a flag; the reporting change (PR-B) must ship **with or before**
PR-C so valid orders are never reported Critical. Flag decision belongs to
Gate 3/4.
