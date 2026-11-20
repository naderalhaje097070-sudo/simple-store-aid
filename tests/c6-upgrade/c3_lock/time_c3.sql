begin;
select pg_relation_filenode('public.products') p0, pg_relation_filenode('public.order_items') o0, (select count(*) from public.products) np, (select count(*) from public.order_items) ni \gset
select clock_timestamp() t0 \gset
\i /tmp/C3.sql
select format('products=%s order_items=%s held_s=%s products_rewritten=%s order_items_rewritten=%s', :np, :ni, round(extract(epoch from clock_timestamp()-:'t0')::numeric,3), pg_relation_filenode('public.products')<>:p0, pg_relation_filenode('public.order_items')<>:o0);
rollback;
