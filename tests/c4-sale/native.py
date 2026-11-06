"""Current TS hook -> actual SDK -> real isolated Auth/RPC -> persisted money/stock."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/c3-composition'))
spec = importlib.util.spec_from_file_location('c3_probe', ROOT / 'tests/c3-composition/probe.py')
composition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composition)
CompositionProbe = composition.CompositionProbe
sys.path.insert(0, str(ROOT / 'tests/account-lifecycle'))
from scanner_evidence import verify_publication
sys.path.insert(0, str(ROOT / "tests/c5-collection"))
if os.environ.get('MONJEZ_RELEASE_TARGET') == '1':
    # Release workflow: migrations come from the release gate, not a stage pin.
    _rt = importlib.util.spec_from_file_location('monjez_release_target', ROOT / 'tests/release/target.py')
    _release = importlib.util.module_from_spec(_rt)
    _rt.loader.exec_module(_release)
    verify_source, verify_history = _release.verify_source, _release.verify_history
else:
    from collection_target import verify_source, verify_history


class ClientProbe(CompositionProbe):
    def hook(self, actor, draft, private, storage, mode='success', recover=False):
        config = {'url': self.base, 'anon': self.anon, 'actor': actor, 'input': draft,
                  'mode': mode, 'recover': recover, 'storage': str(storage),
                  'advanceMs': 31 * 60 * 1000 if recover else 0}
        file = private.parent / 'hook-private.json'
        self.save(file, config)
        result = subprocess.run(['node', 'tests/c4-sale/native-hook.cjs', str(file)],
                                text=True, capture_output=True, timeout=75)
        if result.returncode:
            raise RuntimeError('actual C4 hook setup failed')
        value = json.loads(result.stdout)
        self.control('hook_source_' + str(len(self.controls)), value['source'] == self.source and value['actualSDK'] and value['actualLoopbackRPC'])
        return value

    def draft(self, pid, paid=25, customer=None, courier=None):
        return {'operationId': str(uuid.uuid4()), 'items': [{'productId': pid, 'name': 'synthetic', 'qty': .25, 'price': 100, 'cost': 40}],
                'total': 25, 'paid': paid, 'delivery': 'courier' if courier else 'direct',
                'method': 'cash', **({'customerId': customer} if customer else {}), **({'courierId': courier} if courier else {})}

    def effects(self, key, pid):
        return self.query(f"select jsonb_build_object('reservations',(select count(*) from public.financial_idempotency where idempotency_key='{key}'), 'orders',(select count(*) from public.orders where id=(select (result->>'order_id')::uuid from public.financial_idempotency where idempotency_key='{key}')), 'payments',(select coalesce(sum(amount),0) from public.payments where order_id=(select (result->>'order_id')::uuid from public.financial_idempotency where idempotency_key='{key}')), 'stock',(select stock from public.products where id='{pid}'));" )

    def run_client(self, private):
        files = sorted((ROOT / 'supabase/migrations').glob('*.sql'))
        versions = self.query("select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;")
        expected, _ = verify_source(ROOT)
        verify_history(expected, versions)
        self.control('exact_approved55_chain_with_original54_preserved', True)
        state = self.actors_state(private)
        actors = state['actors']; a = actors['a']
        pid = self.seed_product(a, 10)
        if os.environ['CONTRACT_MODE'] == 'populated':
            code, _ = self.sale(a, pid, .25)
            self.control('nonempty_prior_quarter_sale', code == 200)
        seed_orders = self.query("select coalesce(jsonb_object_agg(id,md5(to_jsonb(o)::text)),'{}') from public.orders o;")
        initial_stock = self.stock(pid)
        storage = private.parent / 'browser-storage-private.json'
        for mode in ['lost', 'null']:
            draft = self.draft(pid); key = draft['operationId']
            failed = self.hook(a, draft, private, storage, mode)
            self.control(mode + '_real_commit_hidden_from_hook', failed['failure'] and failed['state'] == 'pending' and len(failed['responses']) >= 1 and all(code == 200 for code in failed['responses']) and failed['retainedKey'] == key)
            before = self.snapshot()
            blocked = self.hook(a, self.draft(pid), private, storage)
            self.control(mode + '_second_operation_blocked_without_rpc', blocked['failure'] and blocked['requests'] == [] and self.snapshot() == before)
            retry = self.hook(a, None, private, storage, recover=True)
            self.control(mode + '_reloaded_after31min_same_exact_request', not retry['failure'] and retry['state'] == 'completed' and all(request == failed['requests'][0] for request in retry['requests'] + failed['requests']))
            self.control(mode + '_no_second_stored_effect', self.snapshot() == before and self.effects(key, pid)['reservations'] == 1 and self.effects(key, pid)['payments'] == 25)
        parallel = self.draft(pid)
        done = self.hook(a, parallel, private, storage, 'parallel')
        self.control('parallel_actual_callbacks_same_UUID', not done['failure'] and len(done['requests']) == 2 and done['requests'][0] == done['requests'][1] and done['result'][0] == done['result'][1])
        self.control('parallel_one_financial_effect', self.effects(parallel['operationId'], pid)['orders'] == 1 and self.effects(parallel['operationId'], pid)['payments'] == 25)
        self.control('exact_fractional_stock_after_three_logical_sales', self.stock(pid) == initial_stock - .75)
        # Original idempotency conflict remains server-enforced, independent of UI guard.
        self.denied_atomic('server_samekey_changed_request', a, 'create_sale_with_items_idempotent', self.payload(pid, .5, key=parallel['operationId']), 'idempotency_conflict')
        for label in ['staff1', 'staff2']:
            value = self.hook(actors[label], self.draft(pid), private, private.parent / (label + '-storage-private.json'))
            self.control('actual_' + label + '_quarter_sale', not value['failure'])
        before = self.snapshot()
        foreign = self.hook(actors['b'], self.draft(pid), private, private.parent / 'foreign-storage-private.json')
        self.control('actual_foreign_product_rejected_atomically', foreign['failure'] and foreign['responses'] == [400] and self.snapshot() == before)
        self.control('fresh_known_SQL_rollback_clears_only_failed_slot', foreign['state'] is None)
        # Persisted courier behavior via current typed callback, not a hand-written RPC.
        customer, courier = str(uuid.uuid4()), str(uuid.uuid4())
        self.sql(f"insert into public.customers(id,tenant_id,name) values ('{customer}','{a['tenant']}','C4 synthetic'); insert into public.couriers(id,tenant_id,name,is_active) values ('{courier}','{a['tenant']}','C4 synthetic',true);")
        for paid, expected in [(0,'pending'),(10,'delivered_partial'),(25,'delivered_full')]:
            draft = self.draft(pid, paid, customer, courier)
            reply = self.hook(a, draft, private, storage)
            self.control('actual_courier_' + expected + '_success', not reply['failure'] and reply['requests'][0]['p_courier_state'] == expected)
            oid = str(uuid.UUID(reply['result']['orderId']))
            data = self.query(f"select jsonb_build_object('paid',paid,'collected',collected_by_courier,'state',courier_state,'payments',(select count(*) from public.payments where order_id=o.id)) from public.orders o where id='{oid}';")
            self.control('stored_courier_' + expected + '_no_early_receipt', data == {'paid':0,'collected':paid,'state':expected,'payments':0})
        self.control('all_seeded_nonempty_orders_preserved', all(self.query(f"select to_jsonb(md5(to_jsonb(o)::text)) from public.orders o where id='{oid}';") == value for oid,value in seed_orders.items()))
        verify_publication(self.evidence_dir, self.evidence_dir.parent / 'private-quarantine', [self.anon,self.admin] + [v for x in actors.values() for k,v in x.items() if k in ('token','refresh','password','email')])
        return {'source': self.source, 'mode': os.environ['CONTRACT_MODE'], 'checks': self.controls,
                'actual_hook_SDK_Auth_RPC_stored_effects': True, 'full_C5_acceptance': False}


def main():
    ap = argparse.ArgumentParser()
    for arg in ['status-file','evidence-dir','private-state']: ap.add_argument('--'+arg, type=Path, required=True)
    ap.add_argument('--expected-source', required=True)
    args = ap.parse_args()
    p = ClientProbe(args.status_file, args.evidence_dir, args.expected_source)
    result = p.run_client(args.private_state)
    (args.evidence_dir/'client.json').write_text(json.dumps(result,indent=2)+'\n')
    print('C4_STORED_CHECKS='+str(len(p.controls)))


if __name__ == '__main__': main()
