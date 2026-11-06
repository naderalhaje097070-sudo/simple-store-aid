"""C2 stored fractional quantities on disposable full-chain Supabase only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from live_probe import Probe, HarnessFailure
from scanner_evidence import verify_publication


class QuantityProbe(Probe):
    def snapshot(self):
        names = self.query("select jsonb_agg(schemaname||'.'||tablename order by schemaname,tablename) from pg_tables where schemaname in ('public','monjez_private');")
        if not names or any(not __import__('re').fullmatch(r'(public|monjez_private)\.[a-z_]+', n) for n in names):
            raise HarnessFailure('relation inventory')
        terms = ["'" + n + "',(select md5(coalesce(string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),'')) from " + n + " t)" for n in names]
        return self.query('select jsonb_build_object(' + ','.join(terms) + ');')

    def seed_product(self, actor, stock=10):
        pid = str(uuid.uuid4())
        self.sql(f"insert into public.products(id,tenant_id,name,price,cost,stock,is_active) values ('{pid}','{actor['tenant']}','C2 dummy',100,40,{stock},true);")
        return pid

    def stock(self, pid):
        return self.query(f"select to_jsonb(stock) from public.products where id='{pid}';")

    def sale(self, actor, pid, qty, paid=None, customer=None, courier=None):
        if paid is None:
            paid = float(qty) * 100
        return self.request('POST', '/rest/v1/rpc/create_sale_with_items', {
            'p_customer_id': customer, 'p_delivery': 'courier' if courier else 'direct',
            'p_courier_id': courier, 'p_paid': paid, 'p_method': 'cash',
            'p_items': [{'productId': pid, 'qty': qty}],
        }, token=actor['token'])

    def actors(self):
        return {'a': self.fixture('C2_owner_A'), 'b': self.fixture('C2_owner_B')}

    def before(self, private):
        actors = self.actors()
        private.write_text(json.dumps({'actors': actors}))
        private.chmod(0o600)
        pid = self.seed_product(actors['a'])
        code, body = self.sale(actors['a'], pid, .25)
        self.control('old_fractional_sale_reaches_actual_RPC', code == 200 and body.get('success') is True)
        self.control('old_integer_stock_rounding_reproduced', self.stock(pid) == 10)
        self.control('old_order_item_retains_quarter', self.query(f"select to_jsonb(qty) from public.order_items where product_id='{pid}';") == .25)
        state = {'actors': actors, 'snapshot': self.snapshot()}
        private.write_text(json.dumps(state))
        private.chmod(0o600)
        return {'expected_red': 'C2_INTEGER_STOCK_FRACTION_MISMATCH', 'checks': self.controls}

    def after(self, private):
        if private.exists():
            state = json.loads(private.read_text())
            actors = state['actors']
            self.control('populated_upgrade_preserves_every_relation', self.snapshot() == state['snapshot'])
        else:
            actors = self.actors()
            private.write_text(json.dumps({'actors': actors}))
            private.chmod(0o600)
        a, b = actors['a'], actors['b']
        if os.environ.get('MONJEZ_RELEASE_TARGET') == '1':
            # Release workflow: history must equal the gate-verified candidate set.
            sys.path.insert(0, str(ROOT / 'tests/release'))
            import target
            versions, _ = target.verify_source(ROOT)
            observed = self.query('select coalesce(jsonb_agg(version order by version),\'[]\'::jsonb) from supabase_migrations.schema_migrations;')
            self.control('release_history_matches_gate', observed == versions, observed={'applied': len(observed), 'candidate': len(versions)})
        else:
            self.control('51_migrations_applied', self.query('select count(*) from supabase_migrations.schema_migrations;') == 51)
        types = self.query("select jsonb_object_agg(table_name||'.'||column_name,format_type(a.atttypid,a.atttypmod)) from information_schema.columns c join pg_namespace n on n.nspname=c.table_schema join pg_class t on t.relnamespace=n.oid and t.relname=c.table_name join pg_attribute a on a.attrelid=t.oid and a.attname=c.column_name where table_schema='public' and (table_name,column_name) in (('products','stock'),('order_items','qty'));")
        self.control('uncoerced_decimal_quantity_columns', types == {'products.stock': 'numeric', 'order_items.qty': 'numeric'})
        pid = self.seed_product(a)
        code, _ = self.request('PATCH', '/rest/v1/products?id=eq.' + pid, {'stock': 10.25}, token=a['token'])
        self.control('authenticated_fractional_stock_update', code == 200 and self.stock(pid) == 10.25)
        code, _ = self.request('PATCH', '/rest/v1/products?id=eq.' + pid, {'stock': 10}, token=a['token'])
        self.control('stock_reset_exact', code == 200 and self.stock(pid) == 10)
        for n in range(4):
            code, body = self.sale(a, pid, .25)
            self.control('quarter_sale_' + str(n), code == 200 and body.get('success') is True)
            self.control('quarter_stock_' + str(n), self.stock(pid) == 10 - (n + 1) / 4)
        totals = self.query(f"select jsonb_build_object('qty',(select sum(qty) from public.order_items where product_id='{pid}'),'orders',count(*),'total',sum(total),'paid',sum(paid),'payments',(select sum(amount) from public.payments where order_id in (select order_id from public.order_items where product_id='{pid}'))) from public.orders where id in (select order_id from public.order_items where product_id='{pid}');")
        self.control('stored_four_quarters_equal_one_unit_and_100_cash', totals == {'qty': 1, 'orders': 4, 'total': 100, 'paid': 100, 'payments': 100})
        for qty in [.001, .999, 1.001, 0, -1, 'NaN', 'Infinity', None, 99]:
            before = self.snapshot()
            code, body = self.sale(a, pid, qty, paid=0)
            self.control('reject_invalid_quantity_' + str(qty), code == 400 and isinstance(body, dict) and body.get('code') == 'P0001' and (body.get('message') == 'invalid_item' or body.get('message', '').startswith('insufficient_stock')))
            self.control('rejection_atomic_' + str(qty), self.snapshot() == before)
        for stock in [.001, -.25, 'NaN', 'Infinity']:
            before = self.snapshot()
            code, body = self.request('PATCH', '/rest/v1/products?id=eq.' + pid, {'stock': stock}, token=a['token'])
            self.control('reject_invalid_stock_' + str(stock), code == 400 and isinstance(body, dict) and body.get('code') == '23514')
            self.control('stock_rejection_atomic_' + str(stock), self.snapshot() == before)
        before = self.snapshot()
        code, body = self.sale(b, pid, .25)
        self.control('foreign_product_denied', code == 400 and body.get('message') == 'product_not_found')
        self.control('foreign_denial_atomic', self.snapshot() == before)
        staff = self.fixture('C2_staff_A', a['tenant'], True)
        actors['staff'] = staff
        private.write_text(json.dumps({'actors': actors}))
        code, body = self.sale(staff, pid, .25)
        self.control('active_staff_fractional_sale', code == 200 and body.get('success') is True and self.stock(pid) == 8.75)
        customer, courier = str(uuid.uuid4()), str(uuid.uuid4())
        self.sql(f"insert into public.customers(id,tenant_id,name) values ('{customer}','{a['tenant']}','C2 customer'); insert into public.couriers(id,tenant_id,name,is_active) values ('{courier}','{a['tenant']}','C2 courier',true);")
        code, body = self.sale(a, pid, .25, paid=0, customer=customer, courier=courier)
        self.control('fractional_courier_created', code == 200 and body.get('success') is True and self.stock(pid) == 8.5)
        code, _ = self.request('POST', '/rest/v1/rpc/return_courier_order', {'p_order_id': body['order_id']}, token=a['token'])
        self.control('return_restores_exact_quarter', code == 200 and self.stock(pid) == 8.75)
        code, body = self.sale(a, pid, .25, paid=0, customer=customer)
        self.control('unpaid_fractional_direct_sale', code == 200 and self.stock(pid) == 8.5)
        code, _ = self.request('POST', '/rest/v1/rpc/delete_order_with_restore_stock', {'p_order_id': body['order_id']}, token=a['token'])
        self.control('delete_restores_exact_quarter', code == 200 and self.stock(pid) == 8.75)
        concurrent = self.seed_product(a, 1)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.sale(a, concurrent, .75), range(2)))
        self.control('concurrent_fractional_sale_one_winner', sorted(x[0] for x in results) == [200, 400])
        self.control('concurrent_fractional_stock_exact', self.stock(concurrent) == .25)
        self.control('concurrent_one_persisted_line', self.query(f"select jsonb_build_object('n',count(*),'qty',sum(qty)) from public.order_items where product_id='{concurrent}';") == {'n': 1, 'qty': .75})
        priced = self.seed_product(a, 1)
        self.sql(f"update public.products set price=12.50,cost=4.25 where id='{priced}';")
        code, half = self.sale(a, priced, .25, paid=3.13)
        self.control('existing_half_cent_policy_accepts_full_payment_without_customer', code == 200 and half.get('success') is True)
        values = self.query(f"select jsonb_build_object('total',total,'paid',paid,'status',status,'customer',customer_id) from public.orders where id='{half['order_id']}';")
        self.control('stored_half_cent_total_paid_and_stock', values == {'total': 3.13, 'paid': 3.13, 'status': 'paid', 'customer': None} and self.stock(priced) == .75)
        code, _ = self.request('PUT', '/auth/v1/admin/users/' + a['uid'], {'ban_duration': '24h'}, admin=True)
        self.control('dummy_owner_banned', code == 200)
        before = self.snapshot()
        code, body = self.sale(a, pid, .25)
        self.control('old_banned_token_rejected', code in (401, 403) and body.get('code') == '42501')
        self.control('banned_denial_atomic', self.snapshot() == before)
        return {'source': self.source, 'checks': self.controls, 'bounded_C2_pass': True, 'full_C_acceptance': False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--status-file', type=Path, required=True)
    ap.add_argument('--evidence-dir', type=Path, required=True)
    ap.add_argument('--private-state', type=Path, required=True)
    ap.add_argument('--expected-source', required=True)
    ap.add_argument('--phase', choices=['before', 'after'], required=True)
    args = ap.parse_args()
    probe = QuantityProbe(args.status_file, args.evidence_dir, args.expected_source)
    result = getattr(probe, args.phase)(args.private_state)
    (args.evidence_dir / ('quantity-' + args.phase + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print('C2Q_' + args.phase.upper() + '_CHECKS=' + str(len(probe.controls)))


if __name__ == '__main__':
    main()
