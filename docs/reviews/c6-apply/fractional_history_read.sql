-- PROPOSED production read (NOT RUN on production; needs the owner's approval of this exact scope).
-- Purpose (review 2026-11-19b): find whether fractional sales already happened on integer stock, whose stock
-- decrement was rounded and is not corrected by C3. Counts and dates only: no names, ids, amounts or rows.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger', (select count(*) from supabase_migrations.schema_migrations),
  'order_items_total', (select count(*) from public.order_items),
  'fractional_items', (select count(*) from public.order_items where qty <> trunc(qty)),
  'fractional_tenants', (select count(distinct tenant_id) from public.order_items where qty <> trunc(qty)),
  'fractional_products', (select count(distinct product_id) from public.order_items where qty <> trunc(qty)),
  'first_fractional_at', (select min(created_at)::date from public.order_items where qty <> trunc(qty)),
  'last_fractional_at', (select max(created_at)::date from public.order_items where qty <> trunc(qty))
) as fractional_history;
rollback;
