# Plan: Prevent cost > price except for discount products

## Problem
Currently a user can add a product where cost > selling price with no warning or block. Business rule: this should only be allowed for products that are explicitly on discount/sale.

## Solution
1. Database schema change
   - Add `is_discount` boolean column to `public.products` (default false).
   - Add a CHECK constraint: `cost <= price OR is_discount = true`.
   - Keep existing RLS/policies; no new table needed.

2. Frontend - Add Product form
   - Add a checkbox labelled "✅ منتج على تخفيض" to the Add Product sheet.
   - Client-side validation: if `cost > price` and checkbox is unchecked, block save with inline error under the cost field.
   - Include `is_discount` in the insert payload sent to Supabase.

3. Frontend - Product listing
   - Show a "تخفيض" badge next to product name when `is_discount = true`.

4. Type + API layer
   - Update `DBProduct` type and `useProducts`/`useAddProduct` in `src/lib/db.ts` to include `is_discount`.

## Files to change
- `supabase/migrations/` (new migration for schema)
- `src/lib/db.ts` (types + hooks)
- `src/routes/_authenticated/app.tsx` (AddProductSheet UI + validation + badge)

## Acceptance criteria
- Adding a product with cost > price without checking "تخفيض" is blocked both by UI validation and database constraint.
- Adding a product with cost > price **with** "تخفيض" checked succeeds.
- Products marked as discount show a visible badge in the inventory grid.
- Existing products remain valid (default `is_discount = false`).