#!/usr/bin/env python3
"""C6 upgrade harness (local only). Never point at production.

Runs against a local Supabase database container that holds the production replica
(main replay + 20261107214500 + docs/reviews/c6-apply/replica_drift.sql + production ledger).

  seed       synthetic, operationally complex data through main's own RPCs and direct writes,
             under simulated JWT identities (owner A, staff A, owner B)
  snapshot   every row of every public/monjez_private base table -> JSON file
  battery    every frontend operation of the published frontend (legacy, main 1c5276f) and of
             the candidate frontend (new, 183dc50), each in its own transaction that is ROLLED BACK
  invariant  compare current rows to a snapshot on the snapshot's columns, by value
  facts      independent financial facts of the seeded data

usage: harness.py CONTAINER seed|snapshot FILE|battery|invariant FILE|facts
"""
import json
import subprocess
import sys
import uuid

C = sys.argv[1]
NS = uuid.UUID('6c2d9a52-0c6b-4a0e-9a1f-0c6000000000')
U = {k: str(uuid.uuid5(NS, k)) for k in ['ownerA', 'staffA', 'ownerB']}


def psql(sql, user='postgres', check=True):
    r = subprocess.run(['docker', 'exec', '-i', C, 'psql', '-U', user, '-v', 'ON_ERROR_STOP=1', '-At', '-q'],
                       input=sql, capture_output=True, text=True, timeout=120)
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip()[-800:])
    return r


def q(sql):
    return psql(sql).stdout.strip()


def as_user(uid, body):
    claims = json.dumps({'sub': uid, 'role': 'authenticated', 'aud': 'authenticated'})
    return (f"set local role authenticated; select set_config('request.jwt.claims', '{claims}', true);"
            f" select set_config('request.jwt.claim.sub', '{uid}', true);\n{body}")


def call(uid, body):
    """Run body as uid in a committed transaction; return the last output line."""
    out = psql('begin;\n' + as_user(uid, body) + '\ncommit;').stdout.strip().splitlines()
    return out[-1] if out else ''


def rpc(uid, fn, **args):
    named = ', '.join(f"{k} => {v}" for k, v in args.items())
    return json.loads(call(uid, f"select to_jsonb(public.{fn}({named}));") or 'null')


def lit(v):
    return "'" + str(v).replace("'", "''") + "'"


def items(*pairs):
    return lit(json.dumps([{'productId': p, 'qty': n} for p, n in pairs])) + '::jsonb'


STATE_FILE = '/tmp/c6_seed.json'


def seed():
    for k, uid in U.items():
        psql(f"insert into auth.users(instance_id,id,aud,role,email,encrypted_password,email_confirmed_at,raw_app_meta_data,raw_user_meta_data,created_at,updated_at)"
             f" values ('00000000-0000-0000-0000-000000000000','{uid}','authenticated','authenticated','{k.lower()}@c6.invalid','',now(),'{{}}','{{}}',now(),now());")
    s = {}
    for owner, name in [('ownerA', 'C6 Shop A'), ('ownerB', 'C6 Shop B')]:
        s['tenant' + owner[-1]] = call(U[owner], f"insert into public.tenants(name, owner_user_id) values ({lit(name)}, '{U[owner]}') returning id;")
    psql(f"update public.profiles set tenant_id='{s['tenantA']}' where id='{U['staffA']}';"
         f" insert into public.user_roles(user_id, tenant_id, role) values ('{U['staffA']}','{s['tenantA']}','staff');")
    A, B = U['ownerA'], U['ownerB']

    def ins(uid, table, cols):
        keys = ','.join(cols); vals = ','.join(lit(v) if v is not None else 'null' for v in cols.values())
        return call(uid, f"insert into public.{table}({keys}) values ({vals}) returning id;")
    s['p1'] = ins(A, 'products', {'tenant_id': s['tenantA'], 'name': 'C6 tea', 'price': 100, 'cost': 40, 'stock': 20, 'is_discount': False})
    s['p2'] = ins(A, 'products', {'tenant_id': s['tenantA'], 'name': 'C6 cake', 'price': 30, 'cost': 10, 'stock': 5, 'is_discount': False})
    s['p3'] = ins(A, 'products', {'tenant_id': s['tenantA'], 'name': 'C6 old', 'price': 10, 'cost': 5, 'stock': 3, 'is_discount': False})
    call(A, f"update public.products set is_active=false where id='{s['p3']}';")
    s['pB'] = ins(B, 'products', {'tenant_id': s['tenantB'], 'name': 'C6 B item', 'price': 50, 'cost': 20, 'stock': 10, 'is_discount': False})
    s['c1'] = ins(A, 'customers', {'tenant_id': s['tenantA'], 'name': 'C6 customer 1', 'phone': None})
    s['c2'] = ins(A, 'customers', {'tenant_id': s['tenantA'], 'name': 'C6 customer 2', 'phone': '0910000000'})
    s['cB'] = ins(B, 'customers', {'tenant_id': s['tenantB'], 'name': 'C6 B customer', 'phone': None})
    s['k1'] = ins(A, 'couriers', {'tenant_id': s['tenantA'], 'name': 'C6 courier', 'phone': None})

    def sale(uid, cust, delivery, courier, paid, its):
        r = rpc(uid, 'create_sale_with_items', p_customer_id=lit(cust) if cust else 'null::uuid',
                p_delivery=lit(delivery) + '::delivery_kind', p_courier_id=lit(courier) if courier else 'null::uuid',
                p_paid=paid, p_method="'cash'::payment_method", p_items=its)
        return r['order_id'] if isinstance(r, dict) and 'order_id' in r else r
    s['paid'] = sale(A, None, 'direct', None, 100, items((s['p1'], 1)))
    s['partial'] = sale(U['staffA'], s['c1'], 'direct', None, 100, items((s['p1'], 2)))
    s['debt'] = sale(A, s['c2'], 'direct', None, 0, items((s['p2'], 2)))
    s['cour_pending'] = sale(A, s['c1'], 'courier', s['k1'], 0, items((s['p2'], 1)))
    s['cour_partial'] = sale(A, s['c1'], 'courier', s['k1'], 0, items((s['p1'], 1)))
    s['cour_full'] = sale(A, s['c2'], 'courier', s['k1'], 0, items((s['p2'], 1)))
    s['cour_return'] = sale(A, s['c2'], 'courier', s['k1'], 0, items((s['p1'], 1)))
    s['to_delete'] = sale(A, s['c1'], 'direct', None, 0, items((s['p2'], 1)))
    s['debtB'] = sale(B, s['cB'], 'direct', None, 10, items((s['pB'], 1)))
    rpc(A, 'update_courier_order_state', p_order_id=lit(s['cour_partial']), p_state="'delivered_partial'", p_collected=40)
    rpc(A, 'update_courier_order_state', p_order_id=lit(s['cour_full']), p_state="'delivered_full'", p_collected=30)
    rpc(A, 'update_courier_order_state', p_order_id=lit(s['cour_return']), p_state="'returned'")
    rpc(A, 'settle_courier_orders', p_courier_id=lit(s['k1']), p_order_ids=f"array['{s['cour_partial']}','{s['cour_full']}']::uuid[]")
    rpc(U['staffA'], 'collect_order_debt', p_order_id=lit(s['partial']), p_amount=40, p_method="'transfer'::payment_method")
    rpc(A, 'delete_order_with_restore_stock', p_order_id=lit(s['to_delete']))
    ins(A, 'expenses', {'tenant_id': s['tenantA'], 'type': 'C6 transport', 'amount': 5, 'method': 'cash', 'note': None, 'created_by': A})
    s['close'] = rpc(A, 'close_day', p_note="'C6 seed close'")
    json.dump(s, open(STATE_FILE, 'w'))
    psql(f"select 1;")  # keep
    print(json.dumps({'seeded': {k: v for k, v in s.items() if k != 'close'}, 'close': s['close']}, default=str))


def load():
    return json.load(open(STATE_FILE))


TABLES = "select n.nspname||'.'||c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private') and c.relkind='r' order by 1"


def snapshot(path):
    snap = {}
    for t in q(TABLES).splitlines():
        snap[t] = json.loads(q(f"select coalesce(jsonb_agg(to_jsonb(x) order by to_jsonb(x)::text),'[]') from {t} x;"))
    json.dump(snap, open(path, 'w'))
    print(json.dumps({'tables': len(snap), 'rows': sum(len(v) for v in snap.values())}))


def norm(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return round(float(v), 6)
    if isinstance(v, str):
        try:
            return round(float(v), 6) if v.replace('.', '', 1).lstrip('-').isdigit() else v
        except ValueError:
            return v
    return v


def invariant(path):
    snap = json.load(open(path)); bad = []
    for t, rows in snap.items():
        if not rows:
            continue
        cur = json.loads(q(f"select coalesce(jsonb_agg(to_jsonb(x)),'[]') from {t} x;"))
        key = 'id' if 'id' in rows[0] else sorted(rows[0])[0]
        byk = {r.get(key): r for r in cur}
        for r in rows:
            c = byk.get(r.get(key))
            if c is None:
                bad.append(f"{t}: row {r.get(key)} missing"); continue
            for col, val in r.items():
                if col not in c:
                    bad.append(f"{t}.{col}: column dropped"); continue
                if col == 'updated_at':
                    continue
                if norm(c[col]) != norm(val):
                    bad.append(f"{t}.{col} row {r.get(key)}: {val!r} -> {c[col]!r}")
    print(json.dumps({'invariant_ok': not bad, 'problems': bad[:30], 'n_problems': len(bad)}))


def facts():
    s = load()
    f = {o: json.loads(q(f"select jsonb_build_object('total',total,'paid',paid,'status',status,'delivery',delivery,'state',courier_state,'custody',collected_by_courier) from public.orders where id='{s[o]}';") or 'null')
         for o in ['paid', 'partial', 'debt', 'cour_pending', 'cour_partial', 'cour_full', 'cour_return', 'debtB']}
    f['deleted_gone'] = q(f"select count(*) from public.orders where id='{s['to_delete']}';") == '0'
    f['stock'] = json.loads(q(f"select jsonb_object_agg(name, stock) from public.products where tenant_id in ('{s['tenantA']}','{s['tenantB']}');"))
    f['payments'] = json.loads(q(f"select jsonb_build_object('n',count(*),'sum',coalesce(sum(amount),0)) from public.payments where tenant_id='{s['tenantA']}';"))
    f['close'] = json.loads(q(f"select to_jsonb(d) - 'id' - 'created_at' - 'created_by' - 'tenant_id' from public.day_closes d where tenant_id='{s['tenantA']}';") or 'null')
    print(json.dumps(f, sort_keys=True))


def battery():
    s = load(); A, S, B = U['ownerA'], U['staffA'], U['ownerB']
    key = lambda: str(uuid.uuid4())
    ops = {
        'legacy': [
            ('create_sale paid', A, f"select public.create_sale_with_items(null, 'direct', null, 100, 'cash', {items((s['p1'], 1))});"),
            ('create_sale debt', S, f"select public.create_sale_with_items('{s['c1']}', 'direct', null, 0, 'cash', {items((s['p2'], 1))});"),
            ('create_sale courier', A, f"select public.create_sale_with_items('{s['c2']}', 'courier', '{s['k1']}', 0, 'cash', {items((s['p1'], 1))});"),
            ('collect_order_debt legacy debt', A, f"select public.collect_order_debt('{s['debt']}', 10, 'cash');"),
            ('update_courier_order_state', A, f"select public.update_courier_order_state('{s['cour_pending']}', 'delivered_partial', 5);"),
            ('settle_courier_orders', A, f"select public.update_courier_order_state('{s['cour_pending']}', 'delivered_full', 30); select public.settle_courier_orders('{s['k1']}', array['{s['cour_pending']}']::uuid[]);"),
            ('return courier', A, f"select public.update_courier_order_state('{s['cour_pending']}', 'returned');"),
            ('close_day other tenant', B, "select public.close_day('battery');"),
            ('delete_order_with_restore_stock', A, f"select public.delete_order_with_restore_stock('{s['debt']}');"),
            ('delete_product_safe', A, f"select public.delete_product_safe('{s['p3']}');"),
            ('tenants update name', A, f"update public.tenants set name='C6 renamed' where id='{s['tenantA']}' returning id;"),
            ('tenants update business_type', A, f"update public.tenants set business_type='grocery' where id='{s['tenantA']}' returning id;"),
            ('tenants update timezone', A, f"update public.tenants set timezone='Africa/Tripoli' where id='{s['tenantA']}' returning id;"),
            ('products insert', A, f"insert into public.products(tenant_id,name,price,cost,stock,is_discount) values ('{s['tenantA']}','C6 new',5,2,7,false) returning id;"),
            ('products update', A, f"update public.products set name='C6 tea2', price=101, cost=41, stock=19, is_discount=false where id='{s['p1']}' returning id;"),
            ('products toggle active', A, f"update public.products set is_active=true where id='{s['p3']}' returning id;"),
            ('customers insert', S, f"insert into public.customers(tenant_id,name,phone) values ('{s['tenantA']}','C6 c3',null) returning id;"),
            ('couriers insert', A, f"insert into public.couriers(tenant_id,name,phone) values ('{s['tenantA']}','C6 k2',null) returning id;"),
            ('expenses insert', A, f"insert into public.expenses(tenant_id,type,amount,method,note,created_by) values ('{s['tenantA']}','C6 e',3,'cash',null,'{A}') returning id;"),
            ('profiles update tenant_id', S, f"update public.profiles set tenant_id='{s['tenantA']}' where id='{S}' returning id;"),
            ('read orders/payments/day_closes/items', A, "select (select count(*) from public.orders)+(select count(*) from public.payments)+(select count(*) from public.day_closes)+(select count(*) from public.order_items)+(select count(*) from public.expenses)+(select count(*) from public.customers)+(select count(*) from public.couriers)+(select count(*) from public.products);"),
            ('read tenants/profiles/user_roles/subscriptions', A, "select (select count(*) from public.tenants)+(select count(*) from public.profiles)+(select count(*) from public.user_roles)+(select count(*) from public.subscriptions)+(select count(*) from public.financial_audit_log);"),
            ('get_tenant_today_estimate', A, "select public.get_tenant_today_estimate();"),
            ('current_tenant_id', A, "select public.current_tenant_id();"),
        ],
        'new': [
            ('create_sale_idempotent paid', A, f"select public.create_sale_with_items_idempotent(p_idempotency_key => '{key()}', p_customer_id => null, p_delivery => 'direct', p_courier_id => null, p_paid => 100, p_method => 'cash', p_items => {items((s['p1'], 1))}, p_courier_state => null);"),
            ('create_sale_idempotent fractional', A, f"select public.create_sale_with_items_idempotent(p_idempotency_key => '{key()}', p_customer_id => '{s['c1']}', p_delivery => 'direct', p_courier_id => null, p_paid => 0, p_method => 'cash', p_items => {items((s['p1'], 0.5))}, p_courier_state => null);"),
            ('create_sale_idempotent courier pending', A, f"select public.create_sale_with_items_idempotent(p_idempotency_key => '{key()}', p_customer_id => '{s['c2']}', p_delivery => 'courier', p_courier_id => '{s['k1']}', p_paid => 0, p_method => 'cash', p_items => {items((s['p2'], 1))}, p_courier_state => 'pending');"),
            ('collect_idempotent legacy debt', A, f"select public.collect_order_debt_idempotent(p_idempotency_key => '{key()}', p_order_id => '{s['debt']}', p_amount => 10, p_method => 'cash');"),
            ('collect_idempotent legacy partial', S, f"select public.collect_order_debt_idempotent(p_idempotency_key => '{key()}', p_order_id => '{s['partial']}', p_amount => 60, p_method => 'cash');"),
            ('EXPECT-REFUSE collect_idempotent on returned order', A, f"select public.collect_order_debt_idempotent(p_idempotency_key => '{key()}', p_order_id => '{s['cour_return']}', p_amount => 1, p_method => 'cash');"),
            ('day_close_profit_report on legacy close', A, f"select count(*) from public.day_close_profit_report where tenant_id='{s['tenantA']}';"),
            ('settle_courier_orders', A, f"select public.update_courier_order_state('{s['cour_pending']}', 'delivered_full', 30); select public.settle_courier_orders('{s['k1']}', array['{s['cour_pending']}']::uuid[]);"),
            ('close_day other tenant', B, "select public.close_day('battery');"),
            ('tenants update name', A, f"update public.tenants set name='C6 renamed' where id='{s['tenantA']}' returning id;"),
            ('couriers insert', A, f"insert into public.couriers(tenant_id,name,phone) values ('{s['tenantA']}','C6 k2',null) returning id;"),
        ],
    }
    res = {}
    # The local image (supabase/postgres 17.6.1.106) segfaults when a role calls a function it may not
    # execute. Production returns a clean permission error (RECOVERY-02 check B6). So the privilege is
    # checked first, and the call is made only when the role may execute some overload of each function.
    import re
    for group, lst in ops.items():
        for name, uid, body in lst:
            fns = sorted(set(re.findall(r"public\.([a-z_0-9]+)\(", body)))
            denied = [f for f in fns if q(f"select exists(select 1 from pg_proc p where p.pronamespace='public'::regnamespace and p.proname='{f}');") == 't'
                      and q(f"select bool_or(has_function_privilege('authenticated', p.oid, 'execute')) from pg_proc p where p.pronamespace='public'::regnamespace and p.proname='{f}';") != 't']
            missing = [f for f in fns if q(f"select exists(select 1 from pg_proc p where p.pronamespace='public'::regnamespace and p.proname='{f}');") != 't'
                       and q(f"select to_regclass('public.{f}') is null;") == 't']
            expect_refuse = name.startswith('EXPECT-REFUSE')
            if denied or missing:
                verdict = ('MISSING ' + ','.join(missing)) if missing else ('DENIED ' + ','.join(denied))
                res[f"{group}: {name}"] = verdict
                continue
            r = psql('begin;\n' + as_user(uid, body) + '\nrollback;', check=False)
            out = (r.stdout.strip().splitlines() or [''])[-1]
            ok = r.returncode == 0 and '"ok": false' not in out and '"error"' not in out
            err = r.stderr.strip().splitlines()[-1][:160] if r.returncode else (out[:160] if not ok else '')
            if expect_refuse:
                res[f"{group}: {name}"] = ('OK refused: ' + err) if not ok else 'FAIL accepted'
            else:
                res[f"{group}: {name}"] = 'OK' if ok else 'FAIL ' + err
    print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    cmd = sys.argv[2]
    {'seed': seed, 'battery': battery, 'facts': facts}.get(cmd, lambda: None)()
    if cmd == 'snapshot':
        snapshot(sys.argv[3])
    if cmd == 'invariant':
        invariant(sys.argv[3])
