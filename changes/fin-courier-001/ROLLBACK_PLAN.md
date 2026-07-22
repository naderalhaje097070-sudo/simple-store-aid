# FIN-COURIER-001 — Rollback Plan

Status: Draft for review. Forward-only; no applied migration is edited or
reverted in place.

## Principle

Applied migrations are immutable (Architecture Rule, DEC, DATABASE_CHANGE_POLICY).
Rollback is achieved by an **additive corrective migration** that restores the
previous function definition, plus reverting the UI commits — never by deleting or
editing the migration that shipped the change.

## Database rollback

The change ships as `CREATE OR REPLACE FUNCTION` (and/or an added overload).
Because the pre-change definition is known verbatim
(`supabase/migrations/20260627201534_...c879.sql:358-444`), rollback is:

1. Author a new forward-only migration that `CREATE OR REPLACE`s
   `create_sale_with_items` back to the pre-change body (blanket courier guard
   restored), and, if an overload was added, `DROP FUNCTION` the new overload
   signature only.
2. This restores the exact prior behavior for all future calls.
3. No data migration is needed: because the relaxed guard only ever **allowed
   more** inserts, rows created while the change was live are all valid under the
   old formulas too, **except** courier orders created without a customer.

### Data created during the change window

- Courier orders created **without a customer** (newly permitted) are the only
  rows that could not have existed before.
  - `pending` / `delivered_full` without a customer: no customer debt, so
    `close_day` and selectors handle them with `customer_id IS NULL` fine
    (customer is not an input to custody math). Safe to keep after rollback.
  - There should be **no** `delivered_partial` / `delivered_none` rows without a
    customer, because the new rule still requires a customer for those. If the
    settlement-method item is deferred, none exist. A rollback verification query
    must confirm:
    ```
    SELECT count(*) FROM orders
    WHERE delivery='courier' AND customer_id IS NULL
      AND courier_state IN ('delivered_partial','delivered_none');
    ```
    Expected: 0. If non-zero, that is a data-integrity finding to resolve before
    rollback, not a silent revert.

## UI rollback

- The UI PR is a separate commit/PR (see PR_DECOMPOSITION). Reverting it restores
  quick-sale-default routing and the prior wording. Because the UI PR ships
  **after** and **depends on** the financial PR, roll back UI first, then DB.

## Rollback order

1. Revert the UI PR (default flow, wording, success screen, status display).
2. Apply the corrective DB migration (restore prior RPC).
3. Run the financial-rules suite (T1–T15) on an isolated environment to confirm
   the pre-change baseline is restored.
4. Run the isolated auth UI smoke to confirm the sale path still works.

## What rollback does NOT do

- It does not edit or remove the migration that introduced the change.
- It does not touch production data or secrets.
- It does not delete legitimately-created customer-less courier orders.

## Feature-flag option

Given High risk, a feature flag gating the default-advanced-sale routing and the
courier-outcome UI is recommended so the UI can be dark-launched and rolled back
without a code revert. The DB relaxation is low-blast-radius (strictly more
permissive) and may ship without a flag. Flag decision belongs to Gate 3/4.
