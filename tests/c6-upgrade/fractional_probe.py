#!/usr/bin/env python3
"""Local only. Fractional-quantity probe for an intermediate C6 state.

For each sale path (new idempotent RPC, v2 RPC opened by C1, legacy RPC) and each quantity, run the sale as owner A in a
transaction that is ROLLED BACK, and report: outcome, invoice qty, and the actual stock decrement.
A path whose EXECUTE privilege is missing is reported as DENIED without calling it (the local image
segfaults on calls without privilege, see C6_COMPAT_AND_RECOVERY.md section 7).

Correct behaviour (review 2026-11-19): before C3 a fractional sale must be REFUSED; after C3 the stock
decrement must equal the invoice quantity.

usage: fractional_probe.py CONTAINER LABEL
"""
import json
import subprocess
import sys
import uuid

sys.path.insert(0, __import__('os').path.dirname(__file__))
import harness  # noqa: E402  (reuses psql/as_user/items helpers; harness.C is set from argv[1])

C, LABEL = sys.argv[1], sys.argv[2]
s = json.load(open(harness.STATE_FILE))
A = harness.U['ownerA']
P = s['p1']


def run(fn, sql):
    if harness.q(f"select to_regprocedure('public.{fn}') is null") == 't':
        return {'outcome': 'ABSENT'}
    if harness.q(f"select has_function_privilege('authenticated', 'public.{fn}', 'EXECUTE')") != 't':
        return {'outcome': 'DENIED'}
    stock_type = harness.q("select format_type(atttypid, atttypmod) from pg_attribute "
                           "where attrelid = 'public.products'::regclass and attname = 'stock'")
    # Review fix 2026-11-19c: the invoice line is read from the order THIS sale returned (order_id), and that
    # order must belong to tenant A and hold exactly one line for the probed product.
    body = (f"select stock as s0 from public.products where id = '{P}' \\gset\n"
            f"select to_jsonb(({sql.rstrip(';')})) as r \\gset\n"
            f"select json_build_object('outcome', 'OK', 'stock_type', '{stock_type}', "
            f"'stock_before', :'s0'::numeric, 'stock_after', (select stock from public.products where id = '{P}'), "
            f"'order_id', o.id, 'order_tenant_ok', o.tenant_id = '{s['tenantA']}', "
            f"'lines_in_order', (select count(*) from public.order_items i where i.order_id = o.id), "
            f"'invoice_qty', (select i.qty from public.order_items i where i.order_id = o.id and i.product_id = '{P}')) "
            f"from public.orders o where o.id = coalesce((:'r'::jsonb)->>'order_id', (:'r'::jsonb)->'result'->>'order_id')::uuid;")
    r = harness.psql('begin;\n' + harness.as_user(A, body) + '\nrollback;', check=False)
    if r.returncode:
        return {'outcome': 'REFUSED', 'error': r.stderr.strip().splitlines()[0][:160] if r.stderr.strip() else '?'}
    lines = r.stdout.strip().splitlines()
    if not lines or not lines[-1].startswith('{'):
        return {'outcome': 'NO_ORDER', 'error': 'sale returned no order_id that matches an order'}
    out = json.loads(lines[-1])
    if out['invoice_qty'] is None:
        return {'outcome': 'NO_LINE', 'error': 'returned order has no line for the probed product', **out}
    out['stock_decrement'] = float(out['stock_before']) - float(out['stock_after'])
    out['decrement_equals_invoice'] = abs(out['stock_decrement'] - float(out['invoice_qty'])) < 1e-9
    return out


res = {'state': LABEL, 'ledger': int(harness.q('select count(*) from supabase_migrations.schema_migrations'))}
for qty in (0.5, 1.5, 0.25):
    it = harness.items((P, qty))
    paid = f"(select round(price * {qty}, 2) from public.products where id = '{P}')"
    res[f'new idempotent qty={qty}'] = run(
        'create_sale_with_items_idempotent(uuid,uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)',
        f"public.create_sale_with_items_idempotent(p_idempotency_key => '{uuid.uuid4()}', p_customer_id => null, "
        f"p_delivery => 'direct', p_courier_id => null, p_paid => {paid}, p_method => 'cash', p_items => {it}, p_courier_state => null);")
    res[f'v2 qty={qty}'] = run(
        'create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)',
        f"public.create_sale_with_items_v2(null, 'direct', null, {paid}, 'cash', {it}, null);")
    res[f'legacy qty={qty}'] = run(
        'create_sale_with_items(uuid,delivery_kind,uuid,numeric,payment_method,jsonb)',
        f"public.create_sale_with_items(null, 'direct', null, {paid}, 'cash', {it});")
for k, v in res.items():
    if isinstance(v, dict):
        v['qty_requested'] = float(k.split('qty=')[1])
print(json.dumps(res, ensure_ascii=False, default=str))
