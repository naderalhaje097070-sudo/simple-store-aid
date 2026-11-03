"""Real Auth/RPC/stored finance; preserve a failed retry target as a failed acceptance."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
import subprocess
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/c3-composition'))
spec = importlib.util.spec_from_file_location('c5_composition', ROOT / 'tests/c3-composition/probe.py')
composition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composition)
sys.path.insert(0, str(ROOT / 'tests/c5-acceptance'))
sys.path.insert(0, str(ROOT / 'tests/c5-collection'))
from collection_target import verify_source, verify_history
sys.path.insert(0, str(ROOT / 'tests/c5-finance'))
from scanner_evidence import verify_publication
from verdict import single_effect


class FinanceProbe(composition.CompositionProbe):
    def seed_upgrade(self, private):
        state=self.actors_state(private)
        a=state['actors']['b']
        customer,_=self.customer_courier(a)
        oid=self.order(a,self.seed_product(a),1,0,customer)
        code,_=self.rpc(a,'collect_order_debt',{'p_order_id':oid,'p_amount':20,'p_method':'cash'})
        self.control('prior54_real_collection_seed',code==200 and self.effect(oid)['paid']==20)
        state['upgrade_snapshot']=self.snapshot()
        state['upgrade_checks']=self.controls
        self.save(private,state)
        return {'source_sha':self.source,'phase':'seed54','controls':self.controls}

    def actual_hook(self,a,oid,private):
        storage=private.parent/'collection-storage-private.json'
        config_file=private.parent/'collection-hook-private.json'
        draft={'operationId':str(uuid.uuid4()),'expectedActorId':a['uid'],'orderId':oid,'amount':20,'method':'cash'}
        replies=[]
        for mode,recover in [('lost',False),('success',True)]:
            self.save(config_file,{'url':self.base,'anon':self.anon,'actor':a,'input':draft,'mode':mode,'recover':recover,'storage':str(storage),'advanceMs':10**12 if recover else 0})
            r=subprocess.run(['node','tests/c5-collection/native-hook.cjs',str(config_file)],capture_output=True,text=True,timeout=75)
            self.control('native_hook_process_'+mode,r.returncode==0)
            replies.append(json.loads(r.stdout))
        lost,retry=replies
        self.control('real_hook_hidden_success_and_reload',lost['failure'] and not retry['failure'] and lost['requests']==retry['requests'] and lost['retainedKey']==draft['operationId'] and retry['retainedKey']==draft['operationId'])
        self.control('real_hook_single_stored_collection',self.effect(oid)['paid']==20 and self.effect(oid)['payment_count']==1)

    def keyed_controls(self, a, b, staff, order, customer, request, first):
        rpc = 'collect_order_debt_idempotent'
        for field, value in [('p_amount',21),('p_method','transfer'),('p_order_id',self.order(a,self.seed_product(a),1,0,customer))]:
            self.denied_atomic('same_key_changed_'+field,a,rpc,{**request,field:value},'idempotency_conflict')
        self.denied_atomic('same_tenant_different_actor_replay',staff,rpc,request,'idempotency_conflict')
        self.denied_atomic('foreign_completed_replay',b,rpc,request,'forbidden_tenant')
        self.denied_atomic('anon_completed_replay',None,rpc,request,permission=True)
        self.denied_atomic('unkeyed_authenticated_bypass',a,'collect_order_debt',{k:v for k,v in request.items() if k!='p_idempotency_key'},permission=True)
        self.denied_atomic('null_operation_key',a,rpc,{**request,'p_idempotency_key':None},'idempotency_key_required')
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies=list(pool.map(lambda _:self.rpc(a,rpc,request),range(2)))
        self.control('parallel_same_completed_key_no_effect',all(c==200 for c,_ in replies) and replies[0][1]==replies[1][1] and self.effect(order)==first)
        newkey=str(uuid.uuid4())
        fresh={**request,'p_idempotency_key':newkey}
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies=list(pool.map(lambda _:self.rpc(a,rpc,fresh),range(2)))
        self.control('parallel_fresh_key_exactly_one_effect',all(c==200 for c,_ in replies) and replies[0][1]==replies[1][1] and self.effect(order)['paid']==40 and self.effect(order)['payment_count']==2)
        code, result=self.rpc(a,rpc,request)
        self.control('old_result_does_not_revert_later_payment',code==200 and result['new_paid']==20 and self.effect(order)['paid']==40)
        self.control('two_genuine_equal_payments_distinct_keys',self.query(f"select count(*) from public.financial_idempotency where operation='order.debt.collect.v1' and request_payload->>'order_id'='{order}';")==2)
        failing={**request,'p_idempotency_key':str(uuid.uuid4()),'p_amount':1000}
        self.denied_atomic('reservation_rollback_overbalance',a,rpc,failing,'amount_exceeds_remaining')
        self.control('failed_reservation_absent',self.query(f"select count(*) from public.financial_idempotency where idempotency_key='{failing['p_idempotency_key']}';")==0)
        code,_=self.rpc(a,rpc,{**failing,'p_amount':10})
        self.control('failed_first_attempt_can_retry_same_key',code==200 and self.effect(order)['paid']==50)
        acl=self.query("select jsonb_build_object('raw_authenticated',has_function_privilege('authenticated','public.collect_order_debt(uuid,numeric,public.payment_method)','EXECUTE'),'raw_anon',has_function_privilege('anon','public.collect_order_debt(uuid,numeric,public.payment_method)','EXECUTE'),'keyed_authenticated',has_function_privilege('authenticated','public.collect_order_debt_idempotent(uuid,uuid,numeric,public.payment_method)','EXECUTE'),'keyed_anon',has_function_privilege('anon','public.collect_order_debt_idempotent(uuid,uuid,numeric,public.payment_method)','EXECUTE'),'direct_ledger',has_table_privilege('authenticated','public.financial_idempotency','INSERT,UPDATE,DELETE'),'ledger_rls',(select relrowsecurity from pg_class where oid='public.financial_idempotency'::regclass));")
        self.control('keyed_only_acl_and_existing_ledger_rls',acl=={'raw_authenticated':False,'raw_anon':False,'keyed_authenticated':True,'keyed_anon':False,'direct_ledger':False,'ledger_rls':True})
        code,_=self.request('PUT','/auth/v1/admin/users/'+a['uid'],{'ban_duration':'24h'},admin=True)
        self.control('owner_banned_for_completed_replay',code==200)
        self.denied_atomic('banned_owner_old_token_completed_replay',a,rpc,request,permission=True)
        code,_=self.request('PUT','/auth/v1/admin/users/'+a['uid'],{'ban_duration':'none'},admin=True)
        self.control('owner_unbanned_after_control',code==200)

    def rpc(self, actor, name, payload):
        return self.request('POST', '/rest/v1/rpc/' + name, payload, token=actor['token'])

    def order(self, actor, product, qty=1, paid=0, customer=None, courier=None, state=None):
        code, result = self.sale(actor, product, qty, paid, customer, courier, state)
        self.control('create_order_' + str(len(self.controls)), code == 200 and result.get('success') is True)
        return str(uuid.UUID(result['order_id']))

    def customer_courier(self, actor):
        customer, courier = str(uuid.uuid4()), str(uuid.uuid4())
        self.sql(f"insert into public.customers(id,tenant_id,name) values ('{customer}','{actor['tenant']}','C5 synthetic'); insert into public.couriers(id,tenant_id,name,is_active) values ('{courier}','{actor['tenant']}','C5 synthetic',true);")
        return customer, courier

    def effect(self, order):
        return self.query(f"select jsonb_build_object('total',total,'paid',paid,'payment_count',(select count(*) from public.payments where order_id=o.id),'payment_sum',(select coalesce(sum(amount),0) from public.payments where order_id=o.id),'debt_payment_count',(select count(*) from public.payments where order_id=o.id and kind='debt_collection'),'debt_payment_sum',(select coalesce(sum(amount),0) from public.payments where order_id=o.id and kind='debt_collection')) from public.orders o where id='{order}';")

    def courier_effect(self, order):
        return self.query(f"select jsonb_build_object('total',total,'paid',paid,'status',status,'delivery',delivery,'state',courier_state,'custody',collected_by_courier,'unassigned',courier_id is null,'payments',(select count(*) from public.payments where order_id=o.id),'cash',(select coalesce(sum(amount),0) from public.payments where order_id=o.id)) from public.orders o where id='{order}';")

    def collect(self, actor, order, amount):
        return self.rpc(actor, 'collect_order_debt_idempotent', {'p_idempotency_key':str(uuid.uuid4()), 'p_order_id': order, 'p_amount': amount, 'p_method': 'cash'})

    def denied_atomic(self, name, actor, rpc, payload, message=None, permission=False):
        if rpc == 'collect_order_debt_idempotent' and 'p_idempotency_key' not in payload:
            payload = {'p_idempotency_key':str(uuid.uuid4()), **payload}
        return super().denied_atomic(name, actor, rpc, payload, message, permission)

    def settle(self, actor, courier, orders):
        return self.rpc(actor, 'settle_courier_orders', {'p_courier_id': courier, 'p_order_ids': orders})

    def report(self, actor, expected):
        code, value = self.rpc(actor, 'close_day', {'p_note': 'C5 synthetic control'})
        observed = {k: value.get(k) for k in expected}
        self.control('stored_close_day_' + str(len(self.controls)), code == 200 and observed == expected,
                     observed=observed, expected=expected)

    def run_finance(self, private):
        versions, target = verify_source(ROOT)
        verify_history(versions, self.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;'))
        self.control('exact_pinned55_history', True)
        state = self.actors_state(private)
        a, b, staff1, staff2 = [state['actors'][n] for n in ['a','b','staff1','staff2']]
        if 'upgrade_snapshot' in state:
            self.control('populated54_to55_all_relations_preserved',self.snapshot()==state['upgrade_snapshot'])
            self.controls=state['upgrade_checks']+self.controls
        if os.environ['CONTRACT_MODE'] == 'populated':
            prior_pid = self.seed_product(b)
            prior = self.order(b, prior_pid, .25, 25)
            state['prior_order'] = prior
            state['prior_effect'] = self.effect(prior)
            state['prior_stock'] = self.stock(prior_pid)
            state['prior_pid'] = prior_pid
            self.save(private, state)
            self.control('nonempty_prior_tenant_seed', state['prior_effect']['paid'] == 25 and state['prior_stock'] == 9.75)
        customer, courier = self.customer_courier(a)
        pid = self.seed_product(a)
        direct = self.order(a, pid, .25, 25)
        self.control('stored_quarter_sale_cash_stock', self.effect(direct) == {'total':25,'paid':25,'payment_count':1,'payment_sum':25,'debt_payment_count':0,'debt_payment_sum':0} and self.stock(pid) == 9.75)
        self.report(a, {'sales':25,'collected':25,'expenses':0,'realized_profit':15,'customer_debts':0,'unsettled_custody':0})
        carried = self.order(a, pid, 1, 40, customer, courier, 'delivered_partial')
        self.control('delivery_is_custody_not_cash', self.courier_effect(carried) == {'total':100,'paid':0,'status':'debt','delivery':'courier','state':'delivered_partial','custody':40,'unassigned':False,'payments':0,'cash':0})
        self.report(a, {'sales':125,'collected':25,'expenses':0,'realized_profit':15,'customer_debts':60,'unsettled_custody':40})
        self.denied_atomic('collect_before_settlement', a, 'collect_order_debt_idempotent', {'p_order_id':carried,'p_amount':10,'p_method':'cash'}, 'settle_courier_first')
        self.denied_atomic('foreign_settlement', b, 'settle_courier_orders', {'p_courier_id':courier,'p_order_ids':[carried]}, 'courier_not_found')
        code, value = self.settle(staff1, courier, [carried])
        self.control('authorized_staff_settlement', code == 200 and value.get('total_collected') == 40)
        self.control('settlement_single_stored_cash', self.courier_effect(carried) == {'total':100,'paid':40,'status':'partial','delivery':'direct','state':None,'custody':0,'unassigned':True,'payments':1,'cash':40})
        before = self.effect(carried)
        code, value = self.settle(staff2, courier, [carried])
        self.control('settlement_retry_no_second_cash', code == 200 and value.get('total_collected') == 0 and self.effect(carried) == before)
        code, _ = self.collect(staff2, carried, 60)
        self.control('authorized_remaining_customer_debt_collection', code == 200 and self.effect(carried) == {'total':100,'paid':100,'payment_count':2,'payment_sum':100,'debt_payment_count':1,'debt_payment_sum':60})
        self.report(a, {'sales':125,'collected':125,'expenses':0,'realized_profit':75,'customer_debts':0,'unsettled_custody':0})
        self.denied_atomic('collect_over_remaining', a, 'collect_order_debt_idempotent', {'p_order_id':carried,'p_amount':1,'p_method':'cash'}, 'amount_exceeds_remaining')
        pending = self.order(a, pid, .5, 0, customer, courier, 'pending')
        self.control('pending_fractional_stock_reserved', self.stock(pid) == 8.25)
        code, _ = self.rpc(staff1, 'return_courier_order', {'p_order_id':pending})
        self.control('return_restores_exact_half_and_no_cash', code == 200 and self.stock(pid) == 8.75 and self.courier_effect(pending) == {'total':50,'paid':0,'status':'debt','delivery':'direct','state':'returned','custody':0,'unassigned':True,'payments':0,'cash':0})
        self.denied_atomic('returned_cannot_create_customer_collection', a, 'collect_order_debt_idempotent', {'p_order_id':pending,'p_amount':10,'p_method':'cash'}, 'cannot_collect_returned_order')
        self.denied_atomic('return_retry_cannot_add_stock', a, 'return_courier_order', {'p_order_id':pending}, 'not_a_courier_order')
        debt = self.order(a, pid, 1, 0, customer)
        payload = {'p_order_id':debt,'p_amount':10,'p_method':'cash'}
        self.denied_atomic('foreign_order_collection', b, 'collect_order_debt_idempotent', payload, 'forbidden_tenant')
        self.denied_atomic('anonymous_collection', None, 'collect_order_debt_idempotent', payload, permission=True)
        self.denied_atomic('invalid_zero_collection', a, 'collect_order_debt_idempotent', {**payload,'p_amount':0}, 'invalid_amount')
        code, _ = self.collect(staff1, debt, 5)
        self.control('staff_positive_before_ban', code == 200 and self.effect(debt)['paid'] == 5)
        code, _ = self.request('PUT', '/auth/v1/admin/users/' + staff1['uid'], {'ban_duration':'24h'}, admin=True)
        self.control('previously_authorized_staff_banned', code == 200)
        self.denied_atomic('banned_old_token_collection', staff1, 'collect_order_debt_idempotent', payload, permission=True)
        code, _ = self.collect(staff2, debt, 5)
        self.control('unaffected_active_staff_positive_after_ban', code == 200 and self.effect(debt)['paid'] == 10)
        limited = self.seed_product(a, 1)
        with ThreadPoolExecutor(max_workers=2) as pool:
            sales = list(pool.map(lambda _: self.sale(a, limited, .75, 75), range(2)))
        self.control('concurrent_distinct_sales_one_winner', sorted(c for c,_ in sales) == [200,400] and self.stock(limited) == .25)
        same_pid, key = self.seed_product(a, 1), str(uuid.uuid4())
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.sale(a, same_pid, .75, 75, key=key), range(2)))
        self.control('concurrent_same_sale_key_exactly_one_effect', all(c == 200 for c,_ in replies) and replies[0][1] == replies[1][1] and self.stock(same_pid) == .25)
        cap = self.order(a, self.seed_product(a), .25, 0, customer)
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: self.collect(a, cap, 20), range(2)))
        self.control('concurrent_collection_cannot_exceed_total', sorted(c for c,_ in replies) == [200,400] and self.effect(cap)['paid'] == 20 and self.effect(cap)['payment_count'] == 1)
        # Simulate response loss AFTER the real RPC commit; discard the first reply.
        retry_order = self.order(a, self.seed_product(a), 1, 0, customer)
        request = {'p_idempotency_key':str(uuid.uuid4()),'p_order_id':retry_order,'p_amount':20,'p_method':'cash'}
        first_status, _ = self.rpc(a, 'collect_order_debt_idempotent', request)
        first = self.effect(retry_order)
        self.control('lost_reply_first_commit_persisted_once', first_status == 200 and first == {'total':100,'paid':20,'payment_count':1,'payment_sum':20,'debt_payment_count':1,'debt_payment_sum':20})
        replay_status, _ = self.rpc(a, 'collect_order_debt_idempotent', request)
        replay = self.effect(retry_order)
        self.target('partial_collection_lost_reply_retry_single_effect', single_effect(first,replay), replay_status,
                    intended_logical_collections=1, request_fields=['p_idempotency_key','p_order_id','p_amount','p_method'],
                    same_exact_payload_and_actor=True, first=first, replay=replay,
                    actual_UI_retry_observed=False)
        self.keyed_controls(a, b, staff2, retry_order, customer, request, first)
        hook_order=self.order(a,self.seed_product(a),1,0,customer)
        self.actual_hook(a,hook_order,private)
        from browser import run as run_browser
        browser_receipts=run_browser(self,a,customer)
        if 'prior_order' in state:
            self.control('populated_prior_tenant_unchanged', self.effect(state['prior_order']) == state['prior_effect'] and self.stock(state['prior_pid']) == state['prior_stock'])
        return {'source_sha':self.source,'mode':os.environ['CONTRACT_MODE'],'target_contract':target,
                'controls':self.controls,'targets':self.targets,'financial_acceptance':all(t['passed'] for t in self.targets),
                'full_C5_acceptance':False,'browser_financial_flow_executed':True,'browser':browser_receipts,'restore_executed':False}


def main():
    parser = argparse.ArgumentParser()
    for name in ['status-file','evidence-dir','private-state']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    p = FinanceProbe(args.status_file, args.evidence_dir, args.expected_source)
    try:
        if os.environ.get('COLLECTION_PHASE')=='seed54':
            result=p.seed_upgrade(args.private_state)
            (args.evidence_dir/'upgrade-seed.json').write_text(json.dumps(result,indent=2)+'\n')
            return 0
        result = p.run_finance(args.private_state)
        (args.evidence_dir/'financial-result.json').write_text(json.dumps(result,indent=2)+'\n')
        forbidden = [p.anon,p.admin]
        state = json.loads(args.private_state.read_text())
        forbidden += [v for a in state['actors'].values() for k,v in a.items() if k in ('token','refresh','password','email')]
        verify_publication(args.evidence_dir, args.evidence_dir.parent/'private-quarantine', forbidden)
        print(json.dumps({'source_sha':p.source,'controls':len(p.controls),'controls_passed':True,
                          'targets':p.targets,'financial_acceptance':result['financial_acceptance']}))
        return 0 if result['financial_acceptance'] else 2
    except Exception as error:
        (args.evidence_dir/'financial-failure.json').write_text(json.dumps({'source_sha':p.source,'failure_type':type(error).__name__,'controls_completed':len(p.controls)},indent=2)+'\n')
        raise


if __name__ == '__main__':
    raise SystemExit(main())

