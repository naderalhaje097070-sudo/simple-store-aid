"""C3 catalog, ACL and stored behavior on a disposable full-chain stack only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/c2-quantity'))
from probe import QuantityProbe
from source_order import functions

MIGRATION = 'supabase/migrations/20261029044024_c3_reconcile_financial_adapters.sql'
SIGNATURES = {
    '_create_sale_with_items_core': 'uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state,boolean',
    'create_sale_with_items_v2': 'uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state',
    'create_sale_with_items': 'uuid,delivery_kind,uuid,numeric,payment_method,jsonb',
    'create_sale_with_items_idempotent': 'uuid,uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state',
    'update_courier_outcome_v2': 'uuid,courier_state,numeric,uuid',
    'update_courier_order_state': 'uuid,text,numeric',
}


class CompositionProbe(QuantityProbe):
    def save(self, private, state):
        private.write_text(json.dumps(state))
        private.chmod(0o600)

    def sale(self, actor, pid, qty, paid=None, customer=None, courier=None, state=None, key=None):
        payload = self.payload(pid, qty, paid, customer, courier, state, key)
        return self.request('POST', '/rest/v1/rpc/create_sale_with_items_idempotent', payload, token=actor['token'])

    def payload(self, pid, qty, paid=None, customer=None, courier=None, state=None, key=None):
        return {'p_idempotency_key': key or str(uuid.uuid4()), 'p_customer_id': customer,
                'p_delivery': 'courier' if courier else 'direct', 'p_courier_id': courier,
                'p_paid': float(qty) * 100 if paid is None else paid, 'p_method': 'cash',
                'p_items': [{'productId': pid, 'qty': qty}], 'p_courier_state': state}

    def actors_state(self, private):
        if private.exists():
            return json.loads(private.read_text())
        actors = {'a': self.fixture('C3_owner_A'), 'b': self.fixture('C3_owner_B')}
        self.save(private, {'actors': actors})
        for label in ('staff1', 'staff2'):
            actors[label] = self.fixture('C3_' + label, actors['a']['tenant'], True)
            self.save(private, {'actors': actors})
        return {'actors': actors}

    def seed(self, private):
        state = self.actors_state(private)
        a = state['actors']['a']
        pid = self.seed_product(a)
        # Accepted C2 RPC, before the backdated August idempotency migration.
        code, body = QuantityProbe.sale(self, a, pid, .25)
        self.control('accepted51_quarter_sale_persisted', code == 200 and body.get('success') is True and self.stock(pid) == 9.75)
        state['seed_snapshot'] = self.snapshot()
        self.save(private, state)
        return {'source': self.source, 'phase': 'seed51', 'checks': self.controls}

    def before(self, private):
        state = self.actors_state(private)
        current = self.snapshot()
        if 'seed_snapshot' in state:
            self.control('August_import_preserves_all51_nonempty_relations', all(current.get(k) == v for k, v in state['seed_snapshot'].items()))
        self.control('53_pre_correction_migrations', self.query('select count(*) from supabase_migrations.schema_migrations;') == 53)
        legacy = self.query("select to_jsonb(prosrc) from pg_proc where oid='public.create_sale_with_items(uuid,delivery_kind,uuid,numeric,payment_method,jsonb)'::regprocedure;")
        adapter = self.query("select to_jsonb(prosrc) from pg_proc where oid='public.update_courier_order_state(uuid,text,numeric)'::regprocedure;")
        is_upgrade = os.environ['CONTRACT_MODE'] == 'upgrade'
        self.control('pre_correction_legacy_order_difference_reproduced', ('public._create_sale_with_items_core(' in legacy) == is_upgrade)
        self.control('pre_correction_courier_order_difference_reproduced', ('public.update_courier_outcome_v2(' in adapter) == is_upgrade)
        pid = self.seed_product(state['actors']['a'])
        code, body = self.sale(state['actors']['a'], pid, .999, paid=100)
        self.control('pre_correction_raw_fraction_is_silently_coerced', code == 200 and body.get('success') is True)
        self.control('pre_correction_stored_one_instead_of_point999', self.query(f"select to_jsonb(qty) from public.order_items where product_id='{pid}';") == 1 and self.stock(pid) == 9)
        state['snapshot'] = self.snapshot()
        self.save(private, state)
        return {'source': self.source, 'expected_red': 'C3_ORDER_DEPENDENCE_AND_RAW_CORE_ROUNDING', 'mode': os.environ['CONTRACT_MODE'], 'checks': self.controls}

    def denied_atomic(self, name, actor, rpc, payload, message=None, permission=False):
        before = self.snapshot()
        code, body = self.request('POST', '/rest/v1/rpc/' + rpc, payload, token=actor['token'] if actor else None)
        expected = (code in (401, 403) and body.get('code') == '42501') if permission else (code == 400 and body.get('code') == 'P0001' and body.get('message') == message)
        self.control(name, expected, status=code)
        self.control(name + '_all_relations_unchanged', self.snapshot() == before)

    def outcome(self, actor, order, target, collected=None, customer=None, legacy=False):
        rpc = 'update_courier_order_state' if legacy else 'update_courier_outcome_v2'
        payload = {'p_order_id': order, 'p_state': target, 'p_collected': collected}
        if not legacy:
            payload['p_customer_id'] = customer
        return self.request('POST', '/rest/v1/rpc/' + rpc, payload, token=actor['token'])

    def after(self, private):
        state = json.loads(private.read_text())
        actors = state['actors']
        a, b = actors['a'], actors['b']
        self.control('forward_migration_preserves_all_populated_relations', self.snapshot() == state['snapshot'])
        self.control('54_migrations_applied', self.query('select count(*) from supabase_migrations.schema_migrations;') == 54)
        expected = dict(functions(ROOT / MIGRATION))
        catalog = {}
        for name, signature in SIGNATURES.items():
            reg = 'public.' + name + '(' + signature + ')'
            record = self.query(f"select jsonb_build_object('body_md5',md5(prosrc),'definer',prosecdef,'settings',proconfig,'owner',pg_get_userbyid(proowner),'auth',has_function_privilege('authenticated',oid,'EXECUTE'),'anon',has_function_privilege('anon',oid,'EXECUTE')) from pg_proc where oid='{reg}'::regprocedure;")
            catalog[name] = record
            allowed = name in ('create_sale_with_items_idempotent', 'update_courier_outcome_v2', 'update_courier_order_state')
            self.control('catalog_body_and_acl_' + name, record == {'body_md5': hashlib.md5(expected[name].encode()).hexdigest(), 'definer': True, 'settings': ['search_path=public'], 'owner': 'postgres', 'auth': allowed, 'anon': False})
        self.control('idempotency_table_RLS_deny_by_default', self.query("select jsonb_build_object('rls',relrowsecurity,'auth_select',has_table_privilege('authenticated',oid,'SELECT'),'auth_insert',has_table_privilege('authenticated',oid,'INSERT'),'anon_select',has_table_privilege('anon',oid,'SELECT'),'policies',(select count(*) from pg_policy where polrelid=c.oid)) from pg_class c where oid='public.financial_idempotency'::regclass;") == {'rls': True, 'auth_select': False, 'auth_insert': False, 'anon_select': False, 'policies': 0})
        for actor_label in ('a', 'staff1', 'staff2'):
            actor = actors[actor_label]
            code, body = self.request('GET', '/rest/v1/financial_idempotency?select=*', token=actor['token'])
            self.control('direct_idempotency_table_denied_' + actor_label, code == 403 and body.get('code') == '42501')
        pid = self.seed_product(a)
        key = str(uuid.uuid4())
        payload = self.payload(pid, .25, key=key)
        code, result = self.sale(a, pid, .25, key=key)
        self.control('owner_idempotent_fractional_sale', code == 200 and result.get('success') is True and self.stock(pid) == 9.75)
        before = self.snapshot()
        code, replay = self.sale(a, pid, .25, key=key)
        self.control('same_key_replay_returns_original_without_writes', code == 200 and replay == result and self.snapshot() == before)
        self.denied_atomic('same_key_different_request_conflict', a, 'create_sale_with_items_idempotent', self.payload(pid, .5, key=key), 'idempotency_conflict')
        for label in ('staff1', 'staff2'):
            code, body = self.sale(actors[label], pid, .25)
            self.control('authorized_' + label + '_fractional_sale', code == 200 and body.get('success') is True)
        for qty in (.001, .999, 1.001, 0, -.25, 'NaN', 'Infinity', None):
            self.denied_atomic('raw_quantity_' + str(qty), a, 'create_sale_with_items_idempotent', self.payload(pid, qty, paid=0), 'invalid_item')
        # The entire reservation is rolled back, so the exact same key can be corrected.
        aborted_key = str(uuid.uuid4())
        self.denied_atomic('invalid_reservation_rolls_back', a, 'create_sale_with_items_idempotent', self.payload(pid, .001, paid=0, key=aborted_key), 'invalid_item')
        code, body = self.sale(a, pid, .25, key=aborted_key)
        self.control('failed_owner_key_can_succeed_after_rollback', code == 200 and body.get('success') is True)
        for rpc in ('create_sale_with_items', 'create_sale_with_items_v2', '_create_sale_with_items_core'):
            bypass = dict(payload)
            del bypass['p_idempotency_key']
            if rpc == 'create_sale_with_items':
                del bypass['p_courier_state']
            if rpc == '_create_sale_with_items_core':
                bypass['p_infer_courier_state'] = False
            self.denied_atomic('no_authenticated_bypass_' + rpc, a, rpc, bypass, permission=True)
        self.denied_atomic('anonymous_idempotency_denied', None, 'create_sale_with_items_idempotent', payload, permission=True)
        self.denied_atomic('foreign_product_rejected', b, 'create_sale_with_items_idempotent', self.payload(pid, .25), 'product_not_found')
        customer, courier = str(uuid.uuid4()), str(uuid.uuid4())
        self.sql(f"insert into public.customers(id,tenant_id,name) values ('{customer}','{a['tenant']}','C3 synthetic customer'); insert into public.couriers(id,tenant_id,name,is_active) values ('{courier}','{a['tenant']}','C3 synthetic courier',true);")
        code, order = self.sale(a, pid, 1, paid=0, courier=courier, state='pending')
        self.control('customerless_pending_created', code == 200 and order.get('success') is True)
        oid = order['order_id']
        transition = {'p_order_id': oid, 'p_state': 'delivered_partial', 'p_collected': 40, 'p_customer_id': None}
        self.denied_atomic('debt_transition_requires_customer', a, 'update_courier_outcome_v2', transition, 'customer_required_for_debt')
        code, body = self.outcome(actors['staff1'], oid, 'delivered_partial', 40, customer)
        self.control('staff_atomic_customer_attachment', code == 200 and body.get('success') is True)
        values = self.query(f"select jsonb_build_object('state',courier_state,'collected',collected_by_courier,'paid',paid,'customer',customer_id,'payments',(select count(*) from public.payments where order_id=o.id)) from public.orders o where id='{oid}';")
        self.control('delivered_partial_is_custody_not_receipt', values == {'state': 'delivered_partial', 'collected': 40, 'paid': 0, 'customer': customer, 'payments': 0})
        legacy = {'p_order_id': oid, 'p_state': 'delivered_none', 'p_collected': 0}
        self.denied_atomic('legacy_adapter_rejects_backward_custody_move', a, 'update_courier_order_state', legacy, 'invalid_transition')
        before = self.snapshot()
        code, body = self.outcome(a, oid, 'delivered_partial', 40, customer)
        self.control('same_state_retry_is_noop', code == 200 and body.get('idempotent') is True and self.snapshot() == before)
        self.denied_atomic('foreign_order_transition_denied', b, 'update_courier_outcome_v2', transition, 'forbidden_tenant')
        code, body = self.outcome(actors['staff2'], oid, 'delivered_full', legacy=True)
        self.control('legacy_adapter_safe_full_transition', code == 200 and body.get('success') is True)
        self.control('delivered_full_still_not_settled', self.query(f"select jsonb_build_object('paid',paid,'collected',collected_by_courier,'delivery',delivery,'payments',(select count(*) from public.payments where order_id=o.id)) from public.orders o where id='{oid}';") == {'paid': 0, 'collected': 100, 'delivery': 'courier', 'payments': 0})
        # Lost response / simultaneous requests must share one persisted result.
        concurrent_pid = self.seed_product(a, 1)
        concurrent_key = str(uuid.uuid4())
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.sale(a, concurrent_pid, .75, key=concurrent_key), range(2)))
        self.control('same_key_concurrent_single_result', all(c == 200 and r.get('success') is True for c, r in replies) and replies[0][1] == replies[1][1] and self.stock(concurrent_pid) == .25)
        self.control('same_key_single_persisted_sale', self.query(f"select to_jsonb(count(*)) from public.order_items where product_id='{concurrent_pid}';") == 1)
        priced = self.seed_product(a, 1)
        self.sql(f"update public.products set price=12.50,cost=4.25 where id='{priced}';")
        code, body = self.sale(a, priced, .25, paid=3.13)
        self.control('unchanged_cent_policy_full_paid_without_customer', code == 200 and self.stock(priced) == .75 and self.query(f"select to_jsonb(total) from public.orders where id='{body['order_id']}';") == 3.13)
        # Reachable positive before ban; old session is reused, never refreshed.
        code, _ = self.request('PUT', '/auth/v1/admin/users/' + a['uid'], {'ban_duration': '24h'}, admin=True)
        self.control('synthetic_owner_banned', code == 200)
        self.denied_atomic('banned_old_token_cannot_replay_committed_sale', a, 'create_sale_with_items_idempotent', payload, permission=True)
        for rpc, p in (('update_courier_order_state', legacy), ('update_courier_outcome_v2', transition)):
            self.denied_atomic('banned_old_token_' + rpc, a, rpc, p, permission=True)
        code, body = self.sale(actors['staff2'], pid, .25)
        self.control('unaffected_active_staff_after_owner_ban', code == 200 and body.get('success') is True)
        return {'source': self.source, 'mode': os.environ['CONTRACT_MODE'], 'catalog': catalog, 'checks': self.controls, 'bounded_C3_pass': True, 'full_C_acceptance': False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--status-file', type=Path, required=True)
    ap.add_argument('--evidence-dir', type=Path, required=True)
    ap.add_argument('--private-state', type=Path, required=True)
    ap.add_argument('--expected-source', required=True)
    ap.add_argument('--phase', choices=['seed', 'before', 'after'], required=True)
    args = ap.parse_args()
    probe = CompositionProbe(args.status_file, args.evidence_dir, args.expected_source)
    result = getattr(probe, args.phase)(args.private_state)
    (args.evidence_dir / ('composition-' + args.phase + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print('C3_' + args.phase.upper() + '_CHECKS=' + str(len(probe.controls)))


if __name__ == '__main__':
    main()
