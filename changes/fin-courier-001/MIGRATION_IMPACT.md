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

1. **Replace CHECK constraints** on `public.orders` — **`NOT VALID`, not
   validated in this migration** (decision 5B, finding 2):
   ```
   ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_customer_required_when_unpaid;
   ALTER TABLE public.orders DROP CONSTRAINT IF EXISTS orders_courier_requires_customer_id;
   ALTER TABLE public.orders
     ADD CONSTRAINT orders_customer_required_when_debt
     CHECK (
       customer_id IS NOT NULL
       OR (courier_state IS NOT NULL AND courier_state = 'returned')
       OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
       OR (delivery = 'courier' AND courier_state IS NOT NULL
             AND courier_state IN ('pending','delivered_full'))
     ) NOT VALID;
   -- NO "VALIDATE CONSTRAINT" here.
   ```
   - **Do NOT `VALIDATE` in the same migration.** The old constraints
     (`orders_customer_required_when_unpaid`, `orders_courier_requires_customer_id`)
     were themselves added `NOT VALID` (`20260626155319_...4e.sql:16,28`), so they
     do **not** prove historical rows satisfy them. There is no evidence yet that
     every older row is clean.
   - The constraint is NULL-safe and `returned`-safe (COURIER_STATE_CONTRACT §1).
   - Keep `orders_courier_requires_courier_id` and
     `orders_collected_not_over_total` untouched.
2. **Historical-data preflight (separate, before any VALIDATE):**
   ```
   SELECT id, delivery, courier_state, paid, total
   FROM public.orders
   WHERE customer_id IS NULL
     AND NOT (
          (courier_state IS NOT NULL AND courier_state = 'returned')
       OR (delivery = 'direct'  AND courier_state IS NULL AND paid >= total)
       OR (delivery = 'courier' AND courier_state IS NOT NULL
             AND courier_state IN ('pending','delivered_full'))
     );
   ```
   Must return **zero rows** on the target data before validation is authorized.
   Any hit is a data-integrity finding to resolve first, not to override.
3. **Separate validation step** (a later, controlled migration/operation, only
   after step 2 shows zero violations):
   ```
   ALTER TABLE public.orders VALIDATE CONSTRAINT orders_customer_required_when_debt;
   ```
4. **`create_sale_with_items_v2`** — new canonical function with explicit
   `p_courier_state public.courier_state` (no DEFAULT; decision 5A), outcome-based
   rule, direct/courier argument rules (COURIER_STATE_CONTRACT §2), with
   `REVOKE ... FROM PUBLIC, anon; GRANT EXECUTE TO authenticated`.
5. **`create_sale_with_items`** — `CREATE OR REPLACE` as an adapter delegating to
   `_v2` (grants unchanged).
6. **`update_courier_outcome_v2`** — new canonical transition RPC (decision 5C):
   approved transition matrix, monotonic custody, forbidden backward/reduction,
   atomic same-tenant customer attachment, `returned` delegated to
   `return_courier_order`; grants as above. Old `update_courier_order_state` kept
   only as a compatibility adapter if required.
7. Regenerate `src/integrations/supabase/types.ts` (implementation step, not this
   doc).

## PR-B migration

8. `CREATE OR REPLACE FUNCTION get_platform_financial_health()` and
   `get_platform_financial_health_rows(text, integer)` with outcome-aware
   `courier_missing_refs` / `debt_without_customer` predicates.
9. `CREATE OR REPLACE FUNCTION get_platform_admin_overview()` and
   `get_platform_tenants_health()` so `open_customer_debts` / `open_debts` are
   **outcome-aware** and include courier `delivered_partial` / `delivered_none`
   customer debt (finding 4), using the same per-order debt contract as
   `close_day`. Signatures unchanged; grants unchanged.
- Single-source strategy: define the per-order customer-debt expression once
  (see DATA_IMPACT / PR_DECOMPOSITION) and reuse it; do not re-inline the CASE in
  each function casually.

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
  long lock. The **deferred** `VALIDATE CONSTRAINT` (separate step 3) takes a
  `SHARE UPDATE EXCLUSIVE` lock and scans, but runs only after the preflight
  proves zero violations — never blindly in the same migration.
- `CREATE OR REPLACE FUNCTION` is non-blocking.
- No data backfill, no table rewrite.

## Verification

- `list_migrations` shows the new migration(s) appended, none edited.
- `pg_constraint` shows `orders_customer_required_when_debt` present and
  `convalidated = false` after PR-A (test C-CK1); `true` only after the separate
  validation step.
- Historical-data preflight query returns zero rows before validation
  (test C-CK5).
- Isolated financial-rules suite (T1–T15 + new cases) green on the migrated DB.
