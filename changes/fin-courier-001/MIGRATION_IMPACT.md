# FIN-COURIER-001 — Migration Impact (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. Forward-only. No applied migration file is edited. New migrations are
appended after the current latest (`20260717180906_...`).

## Immutability

- Existing migrations under `supabase/migrations/` are immutable
  (DATABASE_CHANGE_POLICY, DEC). Every change here is a **new** timestamped
  migration using `CREATE OR REPLACE FUNCTION`, `ALTER TABLE ... ADD/DROP
  CONSTRAINT`. No Lovable-linked history rewrite.

## PR-A migration(s)

Order within the migration matters (constraints before/with RPC is fine since
both ship together):

1. **Replace CHECK constraints** on `public.orders`:
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
   ALTER TABLE public.orders VALIDATE CONSTRAINT orders_customer_required_when_debt;
   ```
   - `VALIDATE` is safe: all historical rows had a customer, so none can violate a
     looser rule. If any environment cannot afford the validate scan, ship
     `NOT VALID` only and validate in a follow-up; decision at Gate 4.
   - Keep `orders_courier_requires_courier_id` and
     `orders_collected_not_over_total` untouched.
2. **`create_sale_with_items_v2`** — new canonical function (outcome-based rule,
   explicit `p_courier_state`), with `REVOKE ... FROM PUBLIC, anon; GRANT EXECUTE
   TO authenticated`.
3. **`create_sale_with_items`** — `CREATE OR REPLACE` as an adapter delegating to
   `_v2` (grants unchanged).
4. **Atomic transition RPC** — `resolve_courier_order_v2` (or `CREATE OR REPLACE`
   `update_courier_order_state` with an added optional `p_customer_id`), same-tenant
   customer validation, grants as above.
5. Regenerate `src/integrations/supabase/types.ts` (implementation step, not this
   doc).

## PR-B migration

6. `CREATE OR REPLACE FUNCTION get_platform_financial_health()` and
   `get_platform_financial_health_rows(text, integer)` with outcome-aware
   `courier_missing_refs` / `debt_without_customer` predicates. Signatures
   unchanged; grants unchanged.

## PR-C

- No migration (UI only).

## Ordering constraints

- The constraint replacement and `_v2` must be in the **same** migration/PR so
  there is never a window where the RPC allows a row the constraint rejects, or
  vice versa.
- PR-B health migration must be applied **before or with** the PR-C UI rollout so
  valid customer-less courier orders are not reported Critical.

## Migration safety

- All statements are online-safe: `ADD CONSTRAINT ... NOT VALID` does not take a
  long lock; `VALIDATE CONSTRAINT` takes a `SHARE UPDATE EXCLUSIVE` lock and scans
  but does not block reads/writes materially at pilot scale.
- `CREATE OR REPLACE FUNCTION` is non-blocking.
- No data backfill, no table rewrite.

## Verification

- `list_migrations` shows the new migration(s) appended, none edited.
- `pg_constraint` reflects the replacement (test C-CK1).
- Isolated financial-rules suite (T1–T15 + new cases) green on the migrated DB.
