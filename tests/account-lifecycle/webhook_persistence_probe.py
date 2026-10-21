"""APP-02 actual signed route + real database on an isolated, guarded loopback stack."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import uuid

from scanner_auth_probe import ScannerProbe, explicit_denial
from live_probe import HarnessFailure, FINANCE_TABLES
from write_harness_guard import _psql_command, _psql_env

ROOT = Path(__file__).resolve().parents[2]
BASE = 'dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0'
PRIVATE = ('billing_tenant_bindings', 'billing_webhook_receipts')
RPC = '/rest/v1/rpc/apply_subscription_webhook'


def stamp(delta=0):
    return (datetime.now(timezone.utc)+timedelta(seconds=delta)).isoformat(timespec='microseconds').replace('+00:00','Z')


class WebhookProbe(ScannerProbe):
    sequence = 0

    def snapshot(self, billing=True):
        names = self.query("select jsonb_agg(tablename order by tablename) from pg_tables where schemaname='public';")
        terms = [(n, 'public.'+n) for n in names]
        terms.append(('private_closures','monjez_private.owner_account_closures'))
        if billing:
            for n in PRIVATE:
                if self.query("select to_jsonb(to_regclass('monjez_private."+n+"') is not null);"):
                    terms.append((n,'monjez_private.'+n))
        sql = 'select jsonb_build_object('+','.join("'"+name+"',(select jsonb_build_object('count',count(*),'digest',md5(coalesce(string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),''))) from "+table+' t)' for name,table in terms)+');'
        return self.query(sql)

    def catalog(self):
        return self.query("""select jsonb_build_object(
          'functions',(select md5(string_agg(pg_get_functiondef(p.oid),'' order by p.oid)) from pg_proc p
            join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('public','monjez_private') and p.prokind='f'
            and p.proname<>'apply_subscription_webhook'),
          'relations',(select md5(string_agg(jsonb_build_object('name',c.oid::regclass::text,'owner',c.relowner,
            'acl',c.relacl,'rls',c.relrowsecurity,'force',c.relforcerowsecurity)::text,'' order by c.oid))
            from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private')
            and c.relkind in ('r','p') and c.relname not in ('billing_tenant_bindings','billing_webhook_receipts')),
          'policies',(select md5(string_agg(row_to_json(p)::text,'' order by p.oid)) from pg_policy p
            where polrelid not in (select c.oid from pg_class c join pg_namespace n on n.oid=c.relnamespace
              where n.nspname='monjez_private' and c.relname in ('billing_tenant_bindings','billing_webhook_receipts'))),
          'triggers',(select md5(string_agg(pg_get_triggerdef(oid),'' order by oid)) from pg_trigger where not tgisinternal),
          'cron',(select jsonb_agg(jsonb_build_object('name',jobname,'schedule',schedule,'command',command,'username',username,'active',active) order by jobname) from cron.job)
        );""")

    def event(self, actor, **kwargs):
        self.sequence += 1
        return dict({'event':'evt_'+str(self.sequence).zfill(26),'sub':'sub_'+str(self.sequence).zfill(26),
            'tenant':actor['tenant'],'user':actor['uid'],'env':'live'},**kwargs)

    def next_event(self, event, **kwargs):
        self.sequence += 1
        return {**event,'event':'evt_'+str(self.sequence).zfill(26),**kwargs}

    def invoke(self, events, baseline=False):
        command=['node',str(ROOT/'tests/account-lifecycle/webhook_invoke.cjs')]
        run=subprocess.run(command,input=json.dumps({'statusFile':str(self.status_file),'events':events,'baseline':baseline}),
            text=True,capture_output=True,timeout=20,cwd=ROOT)
        if run.returncode or run.stderr:
            raise HarnessFailure('signed route invocation failed')
        try:
            result=json.loads(run.stdout)
        except json.JSONDecodeError as e:
            raise HarnessFailure('signed route response malformed') from e
        if not isinstance(result,list) or len(result)!=len(events):
            raise HarnessFailure('signed route result count')
        return result

    def send(self, name, event, status=200, unchanged=False, baseline=False):
        before=self.snapshot() if unchanged else None
        result=self.invoke([event],baseline)[0]
        self.control(name,result=={'status':status,'acknowledged':status==200},status=result['status'])
        if unchanged:
            self.control(name+'_data_unchanged',before==self.snapshot())
        return result

    def row(self, event):
        return self.query("select to_jsonb(t) from public.subscriptions t where paddle_subscription_id='"+event['sub']+"';") if self.sql("select count(*) from public.subscriptions where paddle_subscription_id='"+event['sub']+"';")=='1' else None

    def tenant(self, actor):
        return self.query("select to_jsonb(t) from public.tenants t where id='"+actor['tenant']+"';")

    def receipt(self, event):
        return self.query("select to_jsonb(t) from monjez_private.billing_webhook_receipts t where environment='"+event['env']+"' and event_id='"+event['event']+"';")

    def fault(self, table, kind):
        self.sql("CREATE FUNCTION monjez_private.app02_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN "+
            ("RETURN NULL;" if kind=='zero' else "RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_app02_fault';")+
            " END $$; CREATE TRIGGER app02_fault BEFORE INSERT OR UPDATE ON "+table+
            ' FOR EACH ROW EXECUTE FUNCTION monjez_private.app02_fault();')

    def unfault(self, table):
        self.sql('DROP TRIGGER app02_fault ON '+table+'; DROP FUNCTION monjez_private.app02_fault();')

    def seed(self, state):
        actors={}
        for label in ('a','b','legacy','legacy_order','banned','closed'):
            actors[label]=self.fixture('app02_'+label)
            state.write_text(json.dumps({'actors':actors}));state.chmod(0o600)
        for label,parent in (('staff_a','a'),('staff_b','b')):
            actors[label]=self.fixture('app02_'+label,actors[parent]['tenant'],True)
            state.write_text(json.dumps({'actors':actors}));state.chmod(0o600)
        return actors

    def baseline(self, actors):
        a=actors['a']
        e=self.event(a)
        self.fault('public.subscriptions','error')
        self.send('BASELINE_SUBSCRIPTION_ERROR_FALSE_200',e,baseline=True)
        self.control('baseline_tenant_partial_write_without_subscription',self.row(e) is None and self.tenant(a)['paddle_subscription_id']==e['sub'])
        self.unfault('public.subscriptions')
        e=self.event(a)
        self.fault('public.tenants','error')
        self.send('BASELINE_TENANT_ERROR_FALSE_200',e,baseline=True)
        self.control('baseline_subscription_partial_write_without_tenant',self.row(e) is not None and self.tenant(a)['paddle_subscription_id']!=e['sub'])
        self.unfault('public.tenants')
        self.send('BASELINE_UPDATED_MISSING_ROW_FALSE_200',self.event(a,type='subscription.updated'),baseline=True,unchanged=True)
        created_flag=self.event(a,cancel=True)
        self.send('BASELINE_CREATED_SCHEDULED_CANCEL_DEFAULT',created_flag,baseline=True)
        self.control('baseline_created_cancel_flag_false',self.row(created_flag)['cancel_at_period_end'] is False)
        self.sql("UPDATE public.tenants SET paddle_subscription_id=NULL,paddle_customer_id=NULL,subscription_plan=NULL,subscription_status='trialing' WHERE id='"+a['tenant']+"'; DELETE FROM public.subscriptions;")

    def make_legacy(self, actor, number, display=False):
        event=self.event(actor,sub='sub_'+str(number).zfill(26),at=stamp(-100),created=stamp(-1000))
        sql="INSERT INTO public.subscriptions(tenant_id,user_id,paddle_subscription_id,paddle_customer_id,product_id,price_id,status,current_period_start,current_period_end,environment,created_at,updated_at) VALUES ('"+actor['tenant']+"','"+actor['uid']+"','"+event['sub']+"','ctm_"+'c'*26+"','synthetic-plan','synthetic-price','active','2026-01-01T00:00:00Z','2026-03-01T00:00:00Z','live',now()-interval '10 seconds',now());"
        self.sql(sql+"UPDATE public.tenants SET paddle_subscription_id='"+event['sub']+"',paddle_customer_id='ctm_"+'c'*26+"',subscription_plan='synthetic-plan',subscription_status='active' WHERE id='"+actor['tenant']+"';")
        return event

    def run_cases(self, actors, legacy):
        a,b=actors['a'],actors['b']
        # The seeded legacy stream repairs a partial tenant projection without rewriting its watermark.
        e=legacy['event'];old=self.row(e);floor=old['updated_at']
        self.sql("UPDATE public.tenants SET subscription_status='paused' WHERE id='"+actors['legacy']['tenant']+"';")
        self.send('legacy_matching_snapshot_repairs_partial_cache',e)
        self.control('legacy_preserves_server_floor_and_subscription_timestamp',self.row(e)==old and self.receipt(e)['legacy_floor']==floor and self.receipt(e)['outcome']=='legacy_repaired')
        e2=self.next_event(e,at=stamp(-50))
        oldtenant=self.tenant(actors['legacy']);self.send('legacy_exact_later_noop',e2)
        self.control('legacy_noop_preserves_updated_at_and_floor',self.row(e)==old and self.tenant(actors['legacy'])==oldtenant and self.receipt(e2)['legacy_floor']==floor)
        self.send('legacy_ambiguous_different_state_retries',self.next_event(e,at=stamp(-20),type='subscription.updated',status='paused'),503,True)
        future=self.next_event(e,at=stamp(100),type='subscription.updated',status='past_due')
        self.send('legacy_event_past_floor_applies',future)
        self.send('legacy_older_after_known_watermark_stale',self.next_event(e,at=stamp(-1),status='active'))
        self.control('legacy_stale_does_not_rollback',self.row(e)['status']=='past_due')
        # Populated legacy display timestamps cannot silently disagree with a new binding.
        le=legacy['display'];self.send('legacy_binding_creation_learned',le)
        newer=self.event(actors['legacy_order'],created=stamp(-500),at=stamp(200))
        self.send('legacy_display_order_conflict_retries',newer,503,True)
        sandbox_old={**le,'sub':'sub_'+str(9002).zfill(26),'env':'sandbox'}
        self.sql("INSERT INTO public.subscriptions(tenant_id,user_id,paddle_subscription_id,paddle_customer_id,product_id,price_id,status,environment,created_at,updated_at) VALUES ('"+le['tenant']+"','"+le['user']+"','"+sandbox_old['sub']+"','ctm_"+'c'*26+"','synthetic-plan','synthetic-price','active','sandbox',now()-interval '10 seconds',now());")
        self.send('sandbox_legacy_display_order_conflict_retries',self.event(actors['legacy_order'],env='sandbox',created=stamp(-500),at=stamp(200)),503,True)
        # Every required SQL target must roll back on both real error and RETURN NULL.
        for table in ('public.subscriptions','public.tenants','monjez_private.billing_tenant_bindings','monjez_private.billing_webhook_receipts'):
            for kind in ('error','zero'):
                event=self.event(b,created=stamp(10+self.sequence),at=stamp(1000+self.sequence),cancel=True)
                name=table.replace('.','_')+'_'+kind
                self.fault(table,kind)
                self.send(name+'_retryable_atomic',event,503,True)
                self.unfault(table)
                self.send(name+'_same_event_recovery',event)
                self.control(name+'_one_receipt',self.receipt(event)['outcome']=='applied' and self.row(event)['cancel_at_period_end'] is False)
        # Duplicate delivery, alternate notification IDs, lost response and concurrent replay.
        bootstrap=self.event(a,type='subscription.updated',cancel=True,product='updated-plan',price='updated-price')
        self.send('updated_before_created_empty_cache_retries',bootstrap,503,True)
        e=self.next_event(bootstrap,type='subscription.created',at='2026-01-01T00:00:01Z',product='synthetic-plan',price='synthetic-price')
        self.send('created_original_fields_commit',e)
        self.control('created_cancel_default_false',self.row(e)['cancel_at_period_end'] is False)
        self.send('updated_replay_after_created_commits',bootstrap)
        self.control('updated_preserves_created_plan_price',self.row(e)['product_id']=='synthetic-plan' and self.row(e)['price_id']=='synthetic-price' and self.row(e)['cancel_at_period_end'] is True)
        self.control('created_required_state_visible',self.row(e)['status']=='active' and self.tenant(a)['paddle_subscription_id']==e['sub'])
        self.send('duplicate_exact_delivery',e,unchanged=True)
        equal_type=self.next_event(bootstrap,type='subscription.created',product='synthetic-plan',price='synthetic-price')
        before_row=self.row(e);before_tenant=self.tenant(a)
        self.send('equal_time_different_event_type_same_written_state',equal_type)
        self.control('equal_time_cross_type_no_timestamp_write',self.row(e)==before_row and self.tenant(a)==before_tenant and self.receipt(equal_type)['outcome']=='unchanged')
        self.send('duplicate_alternate_notification_id',{**e,'notification':'ntf_'+'x'*26},unchanged=True)
        self.send('event_id_reuse_conflict',{**e,'status':'paused'},503,True)
        before=self.snapshot();results=self.invoke([e]*8)
        self.control('concurrent_eight_duplicate_acks',all(x['status']==200 for x in results))
        self.control('concurrent_duplicate_stored_invariance',before==self.snapshot())
        fresh=self.next_event(e,type='subscription.updated',at='2026-04-01T00:00:00.123456Z',status='past_due',cancel=True)
        self.invoke([fresh])  # Deliberately discard an actually committed response.
        self.send('lost_response_replay',fresh,unchanged=True)
        self.control('lost_response_one_commit',self.row(e)['status']=='past_due' and self.row(e)['cancel_at_period_end'] is True)
        older=self.next_event(e,type='subscription.updated',at='2026-04-01T00:00:00.123455Z',status='active')
        self.send('microsecond_older_event_is_stale',older)
        self.control('microsecond_watermark_no_millisecond_rounding',self.row(e)['status']=='past_due' and self.receipt(older)['outcome']=='stale')
        same=self.next_event(fresh)
        self.send('equal_time_same_state_different_event',same)
        self.control('equal_time_unchanged_outcome',self.receipt(same)['outcome']=='unchanged')
        self.send('equal_time_conflicting_state_retry',self.next_event(fresh,status='paused'),503,True)
        self.send('unsupported_timestamp_precision',self.next_event(e,at='2026-04-01T00:00:00.1234567Z'),422,True)
        canceled=self.next_event(e,type='subscription.canceled',status='canceled',at='2026-05-01T00:00:00Z',noPeriod=True)
        prior=self.row(e);self.send('canceled_preserves_existing_period_and_flag',canceled)
        self.control('canceled_business_fields_unchanged',all(self.row(e)[k]==prior[k] for k in ('current_period_start','current_period_end','cancel_at_period_end')))
        # Out-of-order stream bootstrap with current pointer A: updated B is durable but non-current;
        # an older created B then binds its newest stored status, and late A never rebinds.
        newer=self.event(a,type='subscription.updated',created='2026-02-01T00:00:00Z',at='2026-07-01T00:00:00Z',status='past_due')
        self.send('updated_B_missing_stream_before_created_retries',newer,503,True)
        # A pre-existing public row from the old nontransactional handler can still receive
        # non-current updates before its created notification arrives. Do not invent bootstrap history.
        self.sql("INSERT INTO public.subscriptions(tenant_id,user_id,paddle_subscription_id,paddle_customer_id,product_id,price_id,status,current_period_start,current_period_end,environment,created_at,updated_at) VALUES ('"+a['tenant']+"','"+a['uid']+"','"+newer['sub']+"','ctm_"+'c'*26+"','synthetic-plan','synthetic-price','active','2026-01-01T00:00:00Z','2026-03-01T00:00:00Z','live','2026-02-01T00:00:00Z','2026-02-01T00:00:00Z');")
        self.send('updated_existing_B_before_created_notification_durable',newer)
        self.control('non_current_stream_does_not_rebind',self.receipt(newer)['outcome']=='non_current' and self.tenant(a)['paddle_subscription_id']==e['sub'])
        created=self.next_event(newer,type='subscription.created',at='2026-02-01T00:00:01Z',status='active')
        self.send('late_created_B_binds_latest_stored_state',created)
        self.control('binding_projects_latest_B_without_rollback',self.tenant(a)['paddle_subscription_id']==newer['sub'] and self.tenant(a)['subscription_status']=='past_due' and self.row(newer)['status']=='past_due')
        self.send('late_canceled_A_cannot_rebind',self.next_event(e,type='subscription.canceled',at='2026-08-01T00:00:00Z',status='canceled'))
        self.control('current_B_survives_late_A',self.tenant(a)['paddle_subscription_id']==newer['sub'])
        old=self.event(a,created='2025-01-01T00:00:00Z',at='2026-09-01T00:00:00Z')
        self.send('older_created_subscription_arriving_late',old)
        ui=self.query("select to_jsonb(paddle_subscription_id) from public.subscriptions where tenant_id='"+a['tenant']+"' and environment='live' order by created_at desc limit 1;")
        self.control('new_row_provider_creation_preserves_existing_UI_order',ui==newer['sub'])
        # Receipt identity survives a deleted public fixture. New delivery must not reassign it.
        self.sql("DELETE FROM public.subscriptions WHERE paddle_subscription_id='"+old['sub']+"';")
        self.send('missing_public_row_does_not_reassign_tenant_customer',self.next_event(old,tenant=b['tenant'],user=b['uid'],customer='ctm_'+'d'*26,at='2026-09-01T00:00:01Z'),503,True)
        self.send('missing_public_row_does_not_reassign_environment',{**self.next_event(old),'env':'sandbox'},503,True)
        for event_type in ('subscription.created','subscription.updated','subscription.canceled'):
            equal=self.event(a,type=event_type,created=newer['created'],at='2026-09-02T00:00:00Z',status='canceled' if event_type.endswith('canceled') else 'active')
            self.send('equal_subscription_creation_'+event_type+'_no_arbitrary_tiebreak',equal,503,True)
        self.send('immutable_customer_reassignment',self.next_event(newer,customer='ctm_'+'d'*26,at='2026-09-01T00:00:00Z'),503,True)
        self.send('immutable_creation_timestamp',self.next_event(newer,created='2026-01-31T00:00:00Z',at='2026-09-01T00:00:00Z'),503,True)
        self.send('cross_tenant_metadata_reassignment',self.next_event(newer,tenant=b['tenant'],user=b['uid'],at='2026-09-01T00:00:00Z'),503,True)
        self.send('unknown_owner_is_not_success',self.event(a,user=b['uid']),503,True)
        self.send('unknown_tenant_is_not_success',self.event(a,tenant=str(uuid.uuid4())),503,True)
        self.send('missing_metadata_is_not_success',self.event(a,noMetadata=True),422,True)
        self.send('missing_item_is_not_success',self.event(a,noItems=True),422,True)
        # Environment isolation uses the selected secret; no sandbox cache/binding mutations.
        missing_cancel=self.event(b,type='subscription.canceled',status='canceled',at='2026-05-01T00:00:00Z',noPeriod=True)
        self.send('canceled_before_created_empty_stream_retries',missing_cancel,503,True)
        self.send('canceled_full_period_still_requires_creation',{**missing_cancel,'noPeriod':False},503,True)
        cancel_created=self.next_event(missing_cancel,type='subscription.created',status='active',at='2026-02-01T00:00:00Z',noPeriod=False)
        self.send('canceled_stream_creation_recovery',cancel_created)
        cancel_update=self.next_event(cancel_created,type='subscription.updated',at='2026-03-01T00:00:00Z',cancel=True,product='changed-plan',price='changed-price')
        self.send('canceled_stream_prior_scheduled_change',cancel_update)
        self.send('canceled_missing_period_replay_preserves_history',missing_cancel)
        canceled_row=self.row(missing_cancel)
        self.control('reversed_canceled_arrival_preserves_original_contract',canceled_row['status']=='canceled' and canceled_row['cancel_at_period_end'] is True and canceled_row['current_period_end'].startswith('2026-03-01') and canceled_row['product_id']=='synthetic-plan')
        live=self.tenant(a);sandbox=self.event(a,env='sandbox',created='2026-09-01T00:00:00Z',at='2026-09-02T00:00:00Z')
        self.send('sandbox_own_subscription_commits',sandbox)
        self.control('sandbox_never_changes_live_cache',self.tenant(a)==live and self.row(sandbox)['environment']=='sandbox')
        self.send('same_provider_ID_cross_environment_rejected',{**self.next_event(newer), 'env':'sandbox'},503,True)
        self.send('wrong_secret_rejected_before_database',self.event(a,wrongSecret=True),400,True)
        self.send('invalid_environment_rejected_before_database',self.event(a,env='production'),400,True)
        # Concurrent independently signed ordered events must converge to provider order.
        c1=self.next_event(newer,at='2026-10-01T00:00:00.000001Z',status='paused')
        c2=self.next_event(newer,at='2026-10-01T00:00:00.000002Z',status='active')
        results=self.invoke([c2,c1,c2,c1])
        self.control('concurrent_ordered_events_acknowledged',all(r['status']==200 for r in results))
        self.control('concurrent_ordered_events_converge',self.row(newer)['status']=='active' and self.tenant(a)['subscription_status']=='active')
        # RPC and private storage remain inaccessible with actual ordinary/staff/inactive JWTs.
        payload={'p_environment':'live','p_event_id':e['event'],'p_event_type':'subscription.created','p_occurred_at':e.get('at','2026-02-01T00:00:00Z'),'p_subscription':{}}
        for label in ('banned','closed'):
            actor=actors[label]
            if label=='banned':code,_=self.request('PUT','/auth/v1/admin/users/'+actor['uid'],{'ban_duration':'24h'},admin=True)
            else:code,_=self.request('POST','/rest/v1/rpc/close_owner_account',{},token=actor['token'])
            self.control(label+'_actual_transition',code==200)
            self.send(label+'_trusted_billing_still_durable',self.event(actor))
        code,_=self.request('PUT','/auth/v1/admin/users/'+actors['staff_b']['uid'],{'ban_duration':'24h'},admin=True)
        self.control('actual_employee_B_disabled',code==200)
        code,rows=self.own_rows(actors['staff_a'],'tenants')
        self.control('active_employee_A_remains_visible',code==200 and len(rows)==1)
        for label in ('anonymous','a','b','staff_a','staff_b','banned','closed'):
            actor=actors.get(label);before=self.snapshot()
            code,body=self.request('POST',RPC,payload,token=actor['token'] if actor else None)
            self.control(label+'_service_RPC_denied',explicit_denial(code,body),status=code)
            self.control(label+'_denial_all_data_invariant',before==self.snapshot())
        self.control('B2_scanner_ordinary_denial_preserved',explicit_denial(*self.scan(a),'forbidden_platform_admin'))
        before=self.snapshot();code,body=self.request('PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],{'subscription_status':'forged'},token=a['token'])
        self.control('B3_client_billing_write_denied',explicit_denial(code,body) and before==self.snapshot())
        self.security_catalog()

    def security_catalog(self):
        data=self.query("""select jsonb_build_object(
          'body',(select prosrc from pg_proc where oid='public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'::regprocedure),
          'definer',(select prosecdef from pg_proc where oid='public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'::regprocedure),
          'settings',(select proconfig from pg_proc where oid='public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'::regprocedure),
          'execute',(select jsonb_object_agg(r,has_function_privilege(r,'public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)','EXECUTE')) from unnest(array['anon','authenticated','service_role']) r),
          'public_execute',(select exists(select 1 from pg_proc p,lateral aclexplode(p.proacl) a where p.oid='public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'::regprocedure and a.grantee=0 and a.privilege_type='EXECUTE')),
          'private',(select jsonb_agg(jsonb_build_object('name',c.relname,'rls',c.relrowsecurity,'auth',has_table_privilege('authenticated',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE'),'anon',has_table_privilege('anon',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE'),'service_truncate',has_table_privilege('service_role',c.oid,'TRUNCATE'),'service_delete',has_table_privilege('service_role',c.oid,'DELETE'))) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='monjez_private' and c.relname in ('billing_tenant_bindings','billing_webhook_receipts'))
        );""")
        expected=(ROOT/'changes/b4-app02/WEBHOOK_BOOTSTRAP.sql').read_text().split('$function$')[1]
        self.control('new_RPC_actual_body_matches_forward_correction',data['body']==expected)
        self.control('new_RPC_security_invoker_and_pinned_path',data['definer'] is False and 'search_path=pg_catalog, pg_temp' in data['settings'])
        self.control('new_RPC_explicit_service_only',data['execute']=={'anon':False,'authenticated':False,'service_role':True} and data['public_execute'] is False)
        self.control('new_private_tables_RLS_no_client_or_destructive_service_grants',len(data['private'])==2 and all(t['rls'] and not any(t[k] for k in ('auth','anon','service_truncate','service_delete')) for t in data['private']))
        for role in ('anon','authenticated'):
            for table in PRIVATE:
                sql='BEGIN; SET LOCAL ROLE '+role+'; SELECT count(*) FROM monjez_private.'+table+'; ROLLBACK;'
                run=subprocess.run(_psql_command(self.config,'-Atq','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose'),input=sql,text=True,capture_output=True,env=_psql_env(self.config),timeout=20)
                self.control(role+'_'+table+'_actual_private_denial',run.returncode!=0 and '42501' in run.stderr)
        (self.evidence_dir/'billing-security-catalog.json').write_text(json.dumps(data,indent=2)+'\n')

    def run(self, phase, state):
        files=sorted((ROOT/'supabase/migrations').glob('*.sql'))
        self.control('source_exact49_migrations',len(files)==49 and files[-2].name.endswith('_webhook_persistence_01.sql') and files[-1].name.endswith('_webhook_bootstrap_01.sql'))
        versions=self.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;')
        self.control('native_exact_chain_'+phase,versions==[p.name.split('_')[0] for p in (files[:-2] if phase=='before' else files)])
        self.control('financial_empty_at_start',all(self.counts()[t]==0 for t in FINANCE_TABLES))
        if phase=='before' or not state.exists():
            actors=self.seed(state)
            if phase=='before':self.baseline(actors)
            legacy={'event':self.make_legacy(actors['legacy'],9000),'display':self.make_legacy(actors['legacy_order'],9001)}
        else:
            saved=json.loads(state.read_text());actors=saved['actors'];legacy=saved['legacy']
            self.control('populated_upgrade_all_existing_data_preserved',self.snapshot(False)==saved['snapshot'])
            self.control('populated_upgrade_existing_catalog_preserved',self.catalog()==saved['catalog'])
            self.control('populated_upgrade_new_private_tables_empty',all(self.snapshot()[n]['count']==0 for n in PRIVATE))
        if phase=='before':
            state.write_text(json.dumps({'actors':actors,'legacy':legacy,'snapshot':self.snapshot(False),'catalog':self.catalog()}));state.chmod(0o600)
        else:
            self.sequence=20000
            self.run_cases(actors,legacy)
        self.control('financial_tables_remain_empty',all(self.counts()[t]==0 for t in FINANCE_TABLES))
        self.control('tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode==0)
        report={'source':self.source,'baseline_source':BASE if phase=='before' else None,'phase':phase,'passed':len(self.controls),'failed':0,'checks':self.controls,
            'postgres_version':self.query('select to_jsonb(version());'),'schema_versions':versions,'fingerprints':self.snapshot(),
            'scope':'synthetic signed callbacks through actual route/SDK with local real SQL only','provider_calls':False,
            'B4_runtime_accepted':phase=='after','package_B_accepted':False,'merge_approved':False}
        (self.evidence_dir/('webhook-'+phase+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        print('APP02_RECEIPT '+json.dumps({k:v for k,v in report.items() if k not in ('checks','fingerprints','schema_versions')}))


def main():
    p=argparse.ArgumentParser()
    for n in ('status-file','evidence-dir','private-state'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--expected-source',required=True);p.add_argument('--phase',choices=('before','after'),required=True)
    args=p.parse_args()
    try:
        probe=WebhookProbe(args.status_file,args.evidence_dir,args.expected_source)
        probe.status_file=args.status_file
        probe.run(args.phase,args.private_state)
    except (HarnessFailure,ValueError,OSError,subprocess.SubprocessError) as e:
        args.evidence_dir.mkdir(parents=True,exist_ok=True)
        reason=str(e) if isinstance(e,HarnessFailure) else type(e).__name__
        (args.evidence_dir/'failure.json').write_text(json.dumps({'source':args.expected_source,'phase':args.phase,'failure':reason}))
        print('APP02_HARNESS_FAILURE '+reason);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
