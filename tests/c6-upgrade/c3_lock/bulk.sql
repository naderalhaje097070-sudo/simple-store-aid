-- local replica only: adds synthetic rows to tenant A. vars: np, ni, b (batch tag)
set session_replication_role = replica;
\set t '''db5488ad-34a9-4221-848a-0937a258f791'''
insert into public.products(id,tenant_id,name,price,cost,stock)
 select md5(:'b'||'p'||g)::uuid,:t::uuid,'BULK p'||g,10,5,(g%500) from generate_series(1,:np) g;
insert into public.orders(id,tenant_id,total,paid,status)
 select md5(:'b'||'o'||g)::uuid,:t::uuid,30,30,'paid' from generate_series(1,(:ni/3)+1) g;
insert into public.order_items(tenant_id,order_id,product_id,name,qty,unit_price,unit_cost)
 select :t::uuid,md5(:'b'||'o'||(g/3+1))::uuid,md5(:'b'||'p'||(1+g%:np))::uuid,'BULK i'||g,1+(g%4),10,5 from generate_series(1,:ni) g;
