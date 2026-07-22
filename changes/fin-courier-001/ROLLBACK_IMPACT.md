# FIN-COURIER-001 — Rollback Impact (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Reversal for every layer. Full procedure in ROLLBACK_PLAN.

## Layers to reverse

| Layer | Forward change | Rollback action |
|---|---|---|
| Sale RPC | `create_sale_with_items_v2` + adapter | `CREATE OR REPLACE` adapter back to pre-change body; `DROP FUNCTION create_sale_with_items_v2(...)` |
| Transition RPC | `resolve_courier_order_v2` / added `p_customer_id` | `CREATE OR REPLACE update_courier_order_state` to pre-change body; `DROP` new function if added |
| CHECK constraints | `orders_customer_required_when_debt` | `DROP` it; re-add `orders_customer_required_when_unpaid` + `orders_courier_requires_customer_id` **`NOT VALID`** (do not validate until data reconciled) |
| Health/report | outcome-aware `get_platform_financial_health` (+`_rows`) | `CREATE OR REPLACE` back to pre-change bodies |
| UI (PR-C) | default flow, wording, success, status | Revert the PR-C commits |

## Rollback ordering

Reverse of rollout: **UI (PR-C) → reporting (PR-B) → schema/RPC (PR-A)**. Reverting
schema/RPC last ensures the console is already back to its old predicates before
constraints tighten again.

## Data created during the change window

- Customer-less `pending` / `delivered_full` courier orders become **invalid**
  under the re-added `orders_courier_requires_customer_id`. Re-add it `NOT VALID`
  so these rows persist legally; do **not** `VALIDATE` until each is either
  assigned a customer or otherwise reconciled.
- Verify no debt-state customer-less rows exist (should be impossible under the
  new rule while live):
  ```
  SELECT id FROM orders
  WHERE delivery='courier' AND customer_id IS NULL
    AND courier_state IN ('delivered_partial','delivered_none');   -- expect none
  ```
- Any non-zero result is a data-integrity finding, resolved before validation —
  never a silent revert.

## Reversibility properties

- All DB rollback is forward-only (`CREATE OR REPLACE`, `ADD/DROP CONSTRAINT`);
  no applied migration edited or deleted.
- UI rollback is a git revert of PR-C (Lovable-linked history preserved — additive
  revert commit, no force-push).
- No production data or secrets touched at any point.

## Feature flag (risk reducer)

- A flag on the PR-C default-flow + courier-outcome UI lets the frontend roll back
  without a code revert; the DB layer (strictly more permissive) can remain.
- PR-B reporting must stay applied while any customer-less courier order exists,
  or those valid rows re-appear as Critical.

## Verification after rollback

- T1–T15 baseline green (isolated).
- TEST_PLAN H cases pass.
- `get_platform_financial_health` shows pre-change predicates.
- Isolated auth UI smoke passes.
