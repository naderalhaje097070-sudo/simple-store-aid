"""AC-02 real JWT/SQL privilege boundary on a disposable loopback stack only."""
import argparse
import json
from pathlib import Path
import secrets
import subprocess
import urllib.error
import urllib.request
import uuid

from scanner_auth_probe import ScannerProbe, explicit_denial
from live_probe import HarnessFailure, FINANCE_TABLES
from write_harness_guard import _psql_command, _psql_env

ROOT = Path(__file__).resolve().parents[2]
PROTECTED = ('trial_ends_at', 'subscription_status', 'subscription_plan', 'paddle_customer_id', 'paddle_subscription_id')
ALLOWED = ('id', 'name', 'owner_user_id', 'created_at', 'updated_at', 'timezone', 'business_type')
# C-TENANT-01 (20261110140000_tenants_narrow_client_grants_01): of the seven non-entitlement
# columns, a signed-in client may insert only these and update only these.
CLIENT_INSERT = ('name', 'owner_user_id', 'timezone', 'business_type')
CLIENT_UPDATE = ('name', 'timezone', 'business_type')
VALUES = dict(zip(PROTECTED, ('2299-01-01T00:00:00+00:00', 'active', 'forged-plan', 'fake-customer', 'fake-subscription')))


def safe_denial(status, body, rls=False):
    return explicit_denial(status, body) or (rls and status == 200 and body == [])


class EntitlementProbe(ScannerProbe):
    def catalog(self):
        return self.query("""select jsonb_build_object(
          'role_memberships',(select coalesce(jsonb_agg(jsonb_build_object('role',pg_get_userbyid(roleid),'member',pg_get_userbyid(member),'grantor',pg_get_userbyid(grantor)) order by roleid,member),'[]'::jsonb) from pg_auth_members),
          'tenant_acl_expanded',(select jsonb_agg(jsonb_build_object('grantee',a.grantee,'grantor',a.grantor,'privilege',a.privilege_type,'grantable',a.is_grantable) order by a.grantee,a.privilege_type) from pg_class c,lateral aclexplode(c.relacl) a where c.oid='public.tenants'::regclass),
          'tenant_acl',(select relacl from pg_class where oid='public.tenants'::regclass),
          'column_acl',(select jsonb_object_agg(attname,attacl) from pg_attribute
            where attrelid='public.tenants'::regclass and attnum>0 and not attisdropped),
          'effective',(select jsonb_object_agg(r,rights) from (select r,jsonb_object_agg(attname,
            jsonb_build_object('insert',has_column_privilege(r,'public.tenants',attname,'INSERT'),
                              'update',has_column_privilege(r,'public.tenants',attname,'UPDATE'),
                              'select',has_column_privilege(r,'public.tenants',attname,'SELECT'))) rights
            from unnest(array['anon','authenticated','service_role']) r cross join pg_attribute
            where attrelid='public.tenants'::regclass and attnum>0 and not attisdropped group by r) x),
          'other_relations',(select md5(string_agg(jsonb_build_object('name',c.oid::regclass::text,
            'owner',c.relowner,'acl',c.relacl,'rls',c.relrowsecurity,'force',c.relforcerowsecurity)::text,'' order by c.oid))
            from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private')
            and c.relkind in ('r','p') and c.oid<>'public.tenants'::regclass),
          'tenant_structure',(select jsonb_build_object('oid',oid,'owner',relowner,'rls',relrowsecurity,'force',relforcerowsecurity)
            from pg_class where oid='public.tenants'::regclass),
          'functions',(select md5(string_agg(pg_get_functiondef(p.oid),'' order by p.oid)) from pg_proc p
            join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('public','monjez_private') and p.prokind='f'),
          'policies',(select md5(string_agg(row_to_json(p)::text,'' order by p.oid)) from pg_policy p),
          'triggers',(select md5(string_agg(pg_get_triggerdef(oid),'' order by oid)) from pg_trigger where not tgisinternal),
          'constraints',(select md5(string_agg(pg_get_constraintdef(oid),'' order by oid)) from pg_constraint),
          'defaults',(select md5(string_agg(pg_get_expr(adbin,adrelid),'' order by oid)) from pg_attrdef)
        );""")

    def stored(self, tenant):
        return self.query("select to_jsonb(t) from public.tenants t where id='" + str(uuid.UUID(tenant)) + "';")

    def patch(self, actor, payload, target=None, admin=False):
        return self.request('PATCH', '/rest/v1/tenants?id=eq.' + (target or actor['tenant']), payload,
                            token=actor['token'] if actor else None, admin=admin)

    def denied(self, name, method, path, payload, actor=None, rls=False):
        before = self.snapshot()
        status, body = self.request(method, path, payload, token=actor['token'] if actor else None)
        self.control(name, safe_denial(status, body, rls), status=status,
                     sqlstate=body.get('code') if isinstance(body, dict) else None)
        self.control(name + '_stored_invariance', before == self.snapshot())

    def upsert(self, actor, payload):
        # Fixed loopback path, same credential-free proxy/redirect policy as base Probe.
        req = urllib.request.Request(self.base + '/rest/v1/tenants?on_conflict=id',
            data=json.dumps(payload).encode(), method='POST', headers={'apikey': self.anon,
            'Authorization': 'Bearer ' + actor['token'], 'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates,return=representation'})
        try:
            with self.opener.open(req, timeout=15) as r: status, raw = r.status, r.read()
        except urllib.error.HTTPError as e: status, raw = e.code, e.read()
        except (urllib.error.URLError, TimeoutError) as e: raise HarnessFailure('upsert transport failure') from e
        if status >= 500 or 300 <= status < 400: raise HarnessFailure('upsert server or redirect failure')
        try: return status, json.loads(raw) if raw else None
        except json.JSONDecodeError as e: raise HarnessFailure('upsert response shape') from e

    def unlinked(self, name):
        email = 'ac02-' + uuid.uuid4().hex + '@example.test'
        password = secrets.token_urlsafe(32) + '!aA1'
        code, body = self.request('POST','/auth/v1/admin/users',
            {'email':email,'password':password,'email_confirm':True},admin=True)
        self.control(name + '_auth_user_created', code == 200 and isinstance(body,dict) and bool(body.get('id')),status=code)
        uid = str(uuid.UUID(body['id']))
        code, session = self.request('POST','/auth/v1/token?grant_type=password',{'email':email,'password':password})
        self.control(name + '_real_login', code == 200 and bool(session.get('access_token')),status=code)
        return {'uid':uid,'email':email,'password':password,'token':session['access_token'],'refresh':session['refresh_token']}

    def settings(self, name, actor):
        old = self.stored(actor['tenant'])
        for col,value in (('name','Allowed '+name),('business_type','retail'),('timezone','Africa/Tripoli')):
            code, rows = self.patch(actor,{col:value})
            self.control(name + '_' + col, code == 200 and isinstance(rows,list) and len(rows)==1
                and rows[0][col]==value,status=code)
        new = self.stored(actor['tenant'])
        self.control(name + '_protected_values_preserved', {c:old[c] for c in PROTECTED} == {c:new[c] for c in PROTECTED})

    def trusted(self, name, actor):
        code, rows = self.patch(actor, VALUES, admin=True)
        self.control(name, code==200 and isinstance(rows,list) and len(rows)==1
            and all(rows[0][k]==v for k,v in VALUES.items()),status=code)

    def entitlement(self, actor):
        code, result = self.request('POST','/rest/v1/rpc/tenant_has_active_subscription',
            {'_tenant_id':actor['tenant'],'_check_env':'live'},token=actor['token'])
        self.control('helper_response_' + str(len(self.controls)), code==200 and type(result) is bool,status=code)
        return result

    def seed(self):
        self.control('financial_tables_empty',all(self.counts()[t]==0 for t in FINANCE_TABLES))
        a,b=self.fixture('owner_A'),self.fixture('owner_B')
        return {'a':a,'b':b,'staff_a':self.fixture('staff_A',a['tenant'],True),
            'staff_b':self.fixture('staff_B',b['tenant'],True),'banned':self.fixture('banned_owner'),
            'closed':self.fixture('closed_owner'),'onboard':self.unlinked('onboarding')}

    def run(self, phase, state_file):
        files=sorted((ROOT/'supabase/migrations').glob('*.sql'))
        self.control('exact47_source_migrations',len(files)==47 and files[-1].name.endswith('_tenant_entitlement_01.sql'))
        versions=self.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;')
        self.control('exact_chain_'+phase,versions==[p.name.split('_')[0] for p in (files[:-1] if phase=='before' else files)])
        if phase=='before' or not state_file.exists():
            actors=self.seed()
            state_file.write_text(json.dumps({'actors':actors}));state_file.chmod(0o600)
        else:
            saved=json.loads(state_file.read_text());actors=saved['actors']
            self.control('populated_upgrade_all_data_preserved',self.snapshot()==saved['snapshot'])
            old,new=saved['catalog'],self.catalog()
            self.control('only_tenant_write_acl_changed',
                {k:v for k,v in old.items() if k not in ('tenant_acl','tenant_acl_expanded','column_acl','effective')} ==
                {k:v for k,v in new.items() if k not in ('tenant_acl','tenant_acl_expanded','column_acl','effective')})
            self.control('anon_service_effective_privileges_preserved',all(old['effective'][r]==new['effective'][r] for r in ('anon','service_role')))
            self.control('all_authenticated_select_preserved',all(old['effective']['authenticated'][c]['select']==new['effective']['authenticated'][c]['select'] for c in ALLOWED+PROTECTED))
        a,b=actors['a'],actors['b']
        self.settings(phase+'_settings_before',a)
        self.trusted(phase+'_service_before',b)
        if phase=='before':
            for col,value in VALUES.items():
                code,rows=self.patch(a,{col:value})
                self.control('BASELINE_CLIENT_UPDATE_'+col,code==200 and len(rows)==1 and rows[0][col]==value,status=code,expected_denial_assertion=False)
            code,rows=self.request('POST','/rest/v1/tenants',{'name':'Baseline forged','owner_user_id':a['uid'],**VALUES},token=a['token'])
            self.control('BASELINE_CLIENT_INSERT_ALL_FIVE',code==201 and len(rows)==1 and all(rows[0][k]==v for k,v in VALUES.items()),status=code,expected_denial_assertion=False)
            code,_=self.patch(a,{'trial_ends_at':'2000-01-01T00:00:00+00:00'},admin=True)
            self.control('baseline_expired_trial_helper_false',code==200 and self.entitlement(a) is False)
            code,_=self.patch(a,{'trial_ends_at':VALUES['trial_ends_at']})
            self.control('BASELINE_CLIENT_EXTENDS_STORED_ENTITLEMENT',code==200 and self.entitlement(a) is True,expected_denial_assertion=False)
            state_file.write_text(json.dumps({'actors':actors,'snapshot':self.snapshot(),'catalog':self.catalog()}));state_file.chmod(0o600)
        else:
            catalog=self.catalog()
            self.control('effective_protected_write_rights_absent',all(catalog['effective']['authenticated'][c][p] is False for c in PROTECTED for p in ('insert','update')))
            eff=catalog['effective']['authenticated']
            self.control('effective_client_insert_rights_exact',all(eff[c]['insert'] is (c in CLIENT_INSERT) for c in ALLOWED))
            self.control('effective_client_update_rights_exact',all(eff[c]['update'] is (c in CLIENT_UPDATE) for c in ALLOWED))
            self.control('service_all_column_rights_retained',all(catalog['effective']['service_role'][c][p] is True for c in ALLOWED+PROTECTED for p in ('insert','update','select')))
            onboard=actors['onboard']
            code,rows=self.request('POST','/rest/v1/tenants?select=id',{'name':'Real client onboarding','owner_user_id':onboard['uid']},token=onboard['token'])
            self.control('actual_client_onboarding_minimal_payload',code==201 and len(rows)==1,status=code)
            onboard['tenant']=str(uuid.UUID(rows[0]['id']))
            state_file.write_text(json.dumps({'actors':actors}));state_file.chmod(0o600)
            defaults=self.query("select jsonb_build_object('days',extract(epoch from (trial_ends_at-created_at))/86400,'status',subscription_status,'plan',subscription_plan,'customer',paddle_customer_id,'subscription',paddle_subscription_id) from public.tenants where id='"+onboard['tenant']+"';")
            self.control('original_trial_defaults_preserved',defaults=={'days':14,'status':'trialing','plan':None,'customer':None,'subscription':None})
            linked=self.query("select jsonb_build_object('profile',(select tenant_id from public.profiles where id='"+onboard['uid']+"'),'roles',(select count(*) from public.user_roles where user_id='"+onboard['uid']+"' and tenant_id='"+onboard['tenant']+"' and role='owner'));")
            self.control('existing_trigger_owner_and_profile_link',linked=={'profile':onboard['tenant'],'roles':1})
            self.settings('new_client_settings',onboard)
            self.trusted('nonempty_protected_seed',a)
            for col,value in VALUES.items():
                for label,v in (('explicit',value),('null',None),('same_value',self.stored(a['tenant'])[col])):
                    self.denied('owner_patch_'+col+'_'+label,'PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],{col:v},a)
                    self.denied('owner_insert_'+col+'_'+label,'POST','/rest/v1/tenants',{'name':'Forbidden','owner_user_id':a['uid'],col:v},a)
                self.denied('mixed_setting_'+col,'PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],{'name':'MUST_NOT_PERSIST',col:value},a)
                before=self.snapshot()
                code,body=self.upsert(a,{'id':a['tenant'],'owner_user_id':a['uid'],'name':'Forbidden upsert',col:value})
                self.control('upsert_'+col+'_denied',explicit_denial(code,body),status=code)
                self.control('upsert_'+col+'_unchanged',before==self.snapshot())
                code,body=self.upsert(a,{'id':str(uuid.uuid4()),'owner_user_id':a['uid'],'name':'Forbidden new upsert',col:value})
                self.control('upsert_new_'+col+'_denied',explicit_denial(code,body),status=code)
                self.control('upsert_new_'+col+'_unchanged',before==self.snapshot())
                for operation in ('INSERT','UPDATE'):
                    stmt=("INSERT INTO public.tenants(name,owner_user_id,"+col+") VALUES ('Forbidden default','"+a['uid']+"',DEFAULT)" if operation=='INSERT' else "UPDATE public.tenants SET "+col+"=DEFAULT WHERE id='"+a['tenant']+"'")
                    before=self.snapshot()
                    sql="BEGIN; SET LOCAL ROLE authenticated; SELECT set_config('request.jwt.claim.sub','"+a['uid']+"',true); "+stmt+"; ROLLBACK;"
                    r=subprocess.run(_psql_command(self.config,'-Atq','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose'),input=sql,capture_output=True,text=True,env=_psql_env(self.config),timeout=30)
                    self.control(operation+'_explicit_DEFAULT_'+col,r.returncode!=0 and '42501' in r.stderr)
                    self.control(operation+'_DEFAULT_'+col+'_unchanged',before==self.snapshot())
            # A client upsert names id, which a client may no longer write: denied, nothing changes.
            old=self.stored(a['tenant']);before=self.snapshot()
            code,body=self.upsert(a,{'id':a['tenant'],'name':'Metadata upsert','owner_user_id':a['uid']})
            self.control('metadata_upsert_on_id_denied',explicit_denial(code,body),status=code)
            self.control('metadata_upsert_on_id_unchanged',before==self.snapshot())
            self.control('denied_upsert_does_not_reset_entitlement_defaults',all(old[c]==self.stored(a['tenant'])[c] for c in PROTECTED))
            for col,value in (('id',str(uuid.uuid4())),('created_at','2000-01-01T00:00:00+00:00'),('updated_at','2000-01-01T00:00:00+00:00')):
                self.denied('owner_insert_fixed_'+col,'POST','/rest/v1/tenants',{'name':'Forbidden fixed','owner_user_id':a['uid'],col:value},a)
            for col,value in (('id',str(uuid.uuid4())),('owner_user_id',a['uid']),('created_at','2000-01-01T00:00:00+00:00'),('updated_at','2000-01-01T00:00:00+00:00')):
                self.denied('owner_patch_fixed_'+col,'PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],{col:value},a)
            self.denied('multirow_protected_update_atomic','PATCH','/rest/v1/tenants?id=in.('+a['tenant']+','+b['tenant']+')',VALUES,a)
            self.denied('homogeneous_bulk_insert_atomic','POST','/rest/v1/tenants',[
                {'name':'Bulk1','owner_user_id':a['uid'],'trial_ends_at':None},
                {'name':'Bulk2','owner_user_id':a['uid'],'trial_ends_at':VALUES['trial_ends_at']}],a)
            self.denied('cross_tenant_protected_patch','PATCH','/rest/v1/tenants?id=eq.'+b['tenant'],VALUES,a)
            self.denied('cross_tenant_settings_rls','PATCH','/rest/v1/tenants?id=eq.'+b['tenant'],{'name':'Forbidden cross'},a,rls=True)
            self.denied('forged_owner_insert_rls','POST','/rest/v1/tenants',{'name':'Wrong owner','owner_user_id':b['uid']},a)
            for label in ('staff_a','staff_b'):
                actor=actors[label]
                code,rows=self.own_rows(actor,'tenants')
                self.control(label+'_known_own_tenant_visible',code==200 and len(rows)==1,status=code)
                self.denied(label+'_settings_rls','PATCH','/rest/v1/tenants?id=eq.'+actor['tenant'],{'name':'Forbidden staff'},actor,rls=True)
                self.denied(label+'_protected_patch','PATCH','/rest/v1/tenants?id=eq.'+actor['tenant'],VALUES,actor)
                self.denied(label+'_protected_own_insert','POST','/rest/v1/tenants',{'name':'Forbidden staff insert','owner_user_id':actor['uid'],**VALUES},actor)
            self.denied('anonymous_patch','PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],VALUES)
            self.denied('anonymous_insert','POST','/rest/v1/tenants',{'name':'Anon','owner_user_id':a['uid'],**VALUES})
            for label in ('banned','closed'):
                actor=actors[label];self.settings(label+'_before_transition',actor)
                if label=='banned':
                    code,_=self.request('PUT','/auth/v1/admin/users/'+actor['uid'],{'ban_duration':'24h'},admin=True)
                    self.control('actual_ban_confirmed',code==200,status=code)
                else:
                    code,body=self.request('POST','/rest/v1/rpc/close_owner_account',{},token=actor['token'])
                    self.control('actual_closure_confirmed',code==200 and body=={'status':'closed'},status=code)
                self.denied(label+'_old_jwt_minimal_insert','POST','/rest/v1/tenants',{'name':'Forbidden inactive onboarding','owner_user_id':actor['uid']},actor)
                self.denied(label+'_old_jwt_protected_patch','PATCH','/rest/v1/tenants?id=eq.'+actor['tenant'],VALUES,actor)
                self.denied(label+'_old_jwt_settings','PATCH','/rest/v1/tenants?id=eq.'+actor['tenant'],{'name':'Forbidden inactive'},actor,rls=True)
            code,_=self.patch(a,{'trial_ends_at':'2000-01-01T00:00:00+00:00'},admin=True)
            self.control('expired_trial_helper_false',code==200 and self.entitlement(a) is False)
            self.denied('client_cannot_extend_entitlement','PATCH','/rest/v1/tenants?id=eq.'+a['tenant'],{'trial_ends_at':VALUES['trial_ends_at']},a)
            self.control('helper_stays_false_after_attack',self.entitlement(a) is False)
            self.trusted('service_after_denials',a)
            self.control('trusted_trial_helper_true',self.entitlement(a) is True)
            code,rows=self.request('POST','/rest/v1/tenants',{'name':'Trusted billing insert','owner_user_id':b['uid'],**VALUES},admin=True)
            self.control('trusted_insert_all_five_persisted',code==201 and len(rows)==1 and all(rows[0][k]==v for k,v in VALUES.items()),status=code)
            staff=actors['staff_b']
            code,rows=self.own_rows(staff,'tenants')
            self.control('staff_before_ban_known_row_positive',code==200 and len(rows)==1,status=code)
            code,_=self.request('PUT','/auth/v1/admin/users/'+staff['uid'],{'ban_duration':'24h'},admin=True)
            self.control('actual_employee_ban_confirmed',code==200,status=code)
            self.denied('disabled_employee_old_jwt_minimal_insert','POST','/rest/v1/tenants',{'name':'Forbidden disabled employee onboarding','owner_user_id':staff['uid']},staff)
            self.denied('disabled_employee_old_jwt_protected_patch','PATCH','/rest/v1/tenants?id=eq.'+staff['tenant'],VALUES,staff)
            self.denied('disabled_employee_old_jwt_settings','PATCH','/rest/v1/tenants?id=eq.'+staff['tenant'],{'timezone':'UTC'},staff,rls=True)
            code,rows=self.own_rows(staff,'tenants')
            self.control('disabled_employee_old_jwt_known_row_hidden',safe_denial(code,rows,rls=True),status=code)
            code,rows=self.own_rows(actors['staff_a'],'tenants')
            self.control('active_employee_A_unaffected_after_employee_B_ban',code==200 and len(rows)==1,status=code)
            self.settings('owner_B_unaffected_after_denials',b)
            self.control('B2_ordinary_scanner_still_denied',explicit_denial(*self.scan(a),'forbidden_platform_admin'))
        self.control('no_financial_rows_written',all(self.counts()[t]==0 for t in FINANCE_TABLES))
        self.control('tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode==0)
        report={'source':self.source,'phase':phase,'checks':self.controls,'passed':len(self.controls),'failed':0,
            'schema_versions':versions,'postgres_version':self.query('select to_jsonb(version());'),'fingerprints':self.snapshot(),'b3_runtime_accepted':phase=='after',
            'independent_review':'pending','package_B_accepted':False,
            'limits':['synthetic loopback only','financial tables empty','no provider calls','no paywall enforcement claim','B4/B5 deferred']}
        (self.evidence_dir/('entitlement-'+phase+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        (self.evidence_dir/('catalog-'+phase+'.json')).write_text(json.dumps(self.catalog(),indent=2)+'\n')
        print('AC02_RECEIPT '+json.dumps({k:v for k,v in report.items() if k not in ('checks','fingerprints')}))


def main():
    p=argparse.ArgumentParser()
    for name in ('status-file','evidence-dir','private-state'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--expected-source',required=True);p.add_argument('--phase',choices=('before','after'),required=True)
    a=p.parse_args()
    try: EntitlementProbe(a.status_file,a.evidence_dir,a.expected_source).run(a.phase,a.private_state)
    except (HarnessFailure,ValueError,OSError,subprocess.SubprocessError) as e:
        a.evidence_dir.mkdir(parents=True,exist_ok=True)
        safe=str(e) if isinstance(e,HarnessFailure) else type(e).__name__
        (a.evidence_dir/'failure.json').write_text(json.dumps({'source':a.expected_source,'phase':a.phase,'failure':safe}))
        print('AC02_HARNESS_FAILURE: '+safe);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
