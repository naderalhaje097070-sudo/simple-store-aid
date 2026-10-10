"""Focused live enforcement tests; baseline oracle remains immutable."""
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import urllib.error
import urllib.request

from live_probe import Probe, HarnessFailure, FINANCE_TABLES, denial
from write_harness_guard import _psql_command, _psql_env

MIGRATION = '20261010223557_enforce_live_account_state.sql'
COMPENSATION = '20261010225012_avoid_profile_policy_sublink_recursion.sql'
SUCCESS = 'ENV_NATIVE_01_FOCUSED_CORRECTION_GREEN'


def strict_guard_denial(status, body):
    return status == 403 and isinstance(body, dict) and body.get('code') == '42501' and body.get('message') == 'account_inactive'


def green_result(checks):
    names = [c.get('name') for c in checks]
    if not checks or any(c.get('passed') is not True for c in checks) or len(names) != len(set(names)):
        raise HarnessFailure('incomplete or duplicate correction checks')
    required = {f'banned_{actor}_{case}' for actor in ('owner','staff') for case in
                ('old_jwt_own_tenant','old_jwt_own_profiles','old_jwt_own_user_roles','summary','direct_rls')}
    required |= {'active_after_ban_owner_A','active_after_ban_staff_A','public_history_preserved'}
    if not required.issubset(names):
        raise HarnessFailure('named correction controls missing')
    return SUCCESS


def rpc_payloads(actor, other):
    uid, tid = other['uid'], actor['tenant']
    resource = '00000000-0000-4000-8000-000000000001'
    return {
        'current_tenant_id': {}, 'current_tenant_timezone': {}, 'is_platform_admin': {},
        'has_role': {'_user_id': uid, '_tenant_id': tid, '_role': 'owner'},
        'has_owner_role': {'_uid': uid, '_tid': tid},
        'has_staff_or_owner_role': {'_uid': uid, '_tid': tid},
        'tenant_today': {'_tid': tid},
        'tenant_has_active_subscription': {'_tenant_id': tid, '_check_env': 'live'},
        'get_tenant_today_estimate': {}, 'get_platform_admin_overview': {},
        'get_platform_admin_audit_log': {}, 'get_platform_courier_custody_health': {},
        'get_platform_day_close_health': {}, 'get_platform_financial_health': {},
        'get_platform_financial_health_rows': {'p_check_key': 'paid_gt_total'},
        'get_platform_system_health': {}, 'get_platform_tenants_health': {},
        'run_security_scan': {}, 'delete_email': {'queue_name': 'fixture', 'message_id': 1},
        'enqueue_email': {'queue_name': 'fixture', 'payload': {}},
        'read_email_batch': {'queue_name': 'fixture', 'batch_size': 1, 'vt': 30},
        'move_to_dlq': {'source_queue': 'fixture', 'dlq_name': 'fixture_dlq', 'message_id': 1, 'payload': {}},
        'close_day': {'p_note': 'forbidden'},
        'collect_order_debt': {'p_order_id': resource, 'p_amount': 1, 'p_method': 'cash'},
        'create_sale_with_items': {'p_customer_id': None, 'p_delivery': 'direct', 'p_courier_id': None,
                                  'p_paid': 0, 'p_method': 'cash', 'p_items': []},
        'delete_order_with_restore_stock': {'p_order_id': resource},
        'delete_product_safe': {'p_product_id': resource},
        'return_courier_order': {'p_order_id': resource},
        'settle_courier_orders': {'p_courier_id': resource, 'p_order_ids': []},
        'update_courier_order_state': {'p_order_id': resource, 'p_state': 'delivered', 'p_collected': 0},
    }


class CorrectionProbe(Probe):
    def sql(self, sql):
        result=subprocess.run(_psql_command(self.config,'-Atq','-v','ON_ERROR_STOP=1','-v','VERBOSITY=sqlstate'),
                              input=sql,capture_output=True,text=True,env=_psql_env(self.config))
        if result.returncode:
            match=re.search(r'ERROR:\s*([0-9A-Z]{5})\b',result.stderr)
            raise HarnessFailure('isolated SQL failure: '+(match.group(1) if match else 'unknown'))
        return result.stdout.strip()

    def request(self, method, path, payload=None, token=None, admin=False):
        if not path.startswith(('/auth/v1/','/rest/v1/')) or '\n' in path:
            raise HarnessFailure('unsupported local API path')
        key=self.admin if admin else self.anon
        headers={'apikey':key,'Authorization':'Bearer '+(key if admin else token or self.anon),
                 'Content-Type':'application/json','Prefer':'return=representation'}
        request=urllib.request.Request(self.base+path,data=None if payload is None else json.dumps(payload).encode(),method=method,headers=headers)
        try:
            with self.opener.open(request,timeout=15) as response:status,raw=response.status,response.read()
        except urllib.error.HTTPError as error:status,raw=error.code,error.read()
        except (urllib.error.URLError,TimeoutError) as error:raise HarnessFailure('local transport failure') from error
        try:body=json.loads(raw) if raw else None
        except json.JSONDecodeError as error:raise HarnessFailure('non-JSON local API result') from error
        if status>=500 or 300<=status<400:
            code=body.get('code','unknown') if isinstance(body,dict) else 'unknown'
            code=code if re.fullmatch(r'[A-Z0-9]{5,10}',code) else 'unknown'
            raise HarnessFailure(f'server/redirect failure: status={status}, code={code}')
        return status,body

    def history_all(self, tables):
        return {t: self.query(f"select to_jsonb(md5(coalesce(jsonb_agg(to_jsonb(t) order by to_jsonb(t)::text)::text,'[]'))) from public.{t} t;") for t in tables}

    def sql_rls_denied(self, actor):
        # Catch only the named guard error or prove zero rows; all other SQL errors fail.
        sql = f"""begin; set local role authenticated;
        select set_config('request.jwt.claim.sub','{actor['uid']}',true) is not null;
        do $test$ declare n bigint; begin
          begin
            select count(*) into n from public.tenants where id='{actor['tenant']}'::uuid;
            if n <> 0 then raise exception 'old token RLS rows still visible'; end if;
          exception when insufficient_privilege then
            if SQLERRM <> 'account_inactive' then raise; end if;
          end;
        end $test$;
        select 'denied'; rollback;"""
        return self.sql(sql).splitlines()[-1] == 'denied'

    def migrate_upgrade(self, stack, before, tables):
        stack = stack.resolve()
        if stack != (Path(os.environ['RUNNER_TEMP']) / 'monjez-lifecycle-correction').resolve():
            raise HarnessFailure('upgrade stack path mismatch')
        help_result = subprocess.run(['supabase', 'migration', 'up', '--help'], capture_output=True, text=True)
        if help_result.returncode or '--local' not in help_result.stdout:
            raise HarnessFailure('pinned CLI local migration capability missing')
        for name in (MIGRATION,COMPENSATION):
            shutil.copy2(Path('supabase/migrations') / name, stack / 'supabase/migrations' / name)
        start = time.monotonic()
        result = subprocess.run(['supabase', '--workdir', str(stack), 'migration', 'up', '--local'], capture_output=True, text=True)
        self.control('prior_state_upgrade_applied', result.returncode == 0, duration_ms=round((time.monotonic()-start)*1000, 2))
        self.control('upgrade_public_history_preserved', self.history_all(tables) == before)

    def run_correction(self, mode, stack):
        baseline = json.loads(Path('changes/env-native-01/evidence/clean-baseline/catalog.json').read_text())
        tables = sorted({p['tablename'] for p in baseline['policies']})
        initial = self.counts()
        self.control('fresh_empty_stack', all(v == 0 for v in initial.values()))
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        expected = files if mode == 'fresh' else [f for f in files if f.name not in (MIGRATION,COMPENSATION)]
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        self.control('initial_exact_migration_chain', len(files) == 43 and versions == [p.name.split('_')[0] for p in expected])
        a, b = self.fixture('owner_A'), self.fixture('owner_B')
        s1, s2 = self.fixture('staff_A', a['tenant'], True), self.fixture('staff_B', b['tenant'], True)
        if mode=='fresh':
            # Regression proves the precise42P17 root cause in a rolled-back DDL
            # transaction; do not turn a server error into permission success.
            self.sql(f'''begin;
            alter policy monjez_live_actor on public.profiles
              using ((select monjez_private.actor_is_active()))
              with check ((select monjez_private.actor_is_active()));
            set local role authenticated;
            select set_config('request.jwt.claim.sub','{a['uid']}',true) is not null;
            do $test$ begin
              begin
                update public.profiles set display_name=display_name where id='{a['uid']}'::uuid;
                raise exception 'expected42P17 not reproduced';
              exception when sqlstate '42P17' then
                if SQLERRM <> 'infinite recursion detected in policy for relation "profiles"' then raise; end if;
              end;
            end $test$; rollback;''')
            self.control('prior_42p17_profile_recursion_reproduced',True)
        # Existing-schema membership only; no product/admin contract added.
        self.sql(f"insert into public.platform_admins(user_id) values ('{a['uid']}'),('{b['uid']}');")
        for n, actor in enumerate([a,b,s1,s2]):
            status, rows = self.own_rows(actor, 'tenants')
            self.control(f'active_{n}_own_tenant', status == 200 and isinstance(rows,list) and len(rows)==1, status=status)
            foreign = b['tenant'] if actor['tenant']==a['tenant'] else a['tenant']
            for method, payload in [('GET',None),('PATCH',{'name':'FORBIDDEN'})]:
                status, body = self.request(method, '/rest/v1/tenants?id=eq.'+foreign, payload, token=actor['token'])
                self.control(f'active_{n}_foreign_{method}', denial(status,body),status=status)
            status, body = self.request('PATCH','/rest/v1/profiles?id=eq.'+actor['uid'],{'tenant_id':foreign},token=actor['token'])
            self.control(f'active_{n}_tenant_reassignment',denial(status,body),status=status)
        for name, actor in [('A',a),('B',b)]:
            status, body=self.request('POST','/rest/v1/rpc/get_tenant_today_estimate',{},token=actor['token'])
            self.control('active_summary_'+name,status==200 and isinstance(body,dict) and 'sales' in body,status=status)
        status, body=self.request('POST','/rest/v1/rpc/get_platform_admin_audit_log',{},token=a['token'])
        self.control('active_admin_read',status==200 and isinstance(body,list),status=status)
        status,rows=self.request('PATCH','/rest/v1/profiles?id=eq.'+a['uid'],{'display_name':'ACTIVE FIXTURE'},token=a['token'])
        self.control('active_profile_edit_preserved',status==200 and isinstance(rows,list) and len(rows)==1,status=status)
        status,body=self.request('GET','/rest/v1/tenants?select=id')
        self.control('anonymous_denied',denial(status,body),status=status)
        for name,actor in [('owner',b),('staff',s2)]:
            status,_=self.request('PUT','/auth/v1/admin/users/'+actor['uid'],{'ban_duration':'24h'},admin=True)
            self.control('ban_'+name,status==200,status=status)
            self.control('stored_ban_'+name,self.sql(f"select (banned_until>now())::text from auth.users where id='{actor['uid']}';")=='true')
        before=self.history_all(tables)
        if mode=='upgrade':
            status,rows=self.own_rows(b,'tenants')
            self.control('prior_schema_named_regression',status==200 and isinstance(rows,list) and len(rows)==1,status=status)
            self.migrate_upgrade(stack,before,tables)
        versions=self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        self.control('final_exact_43_chain',versions==[p.name.split('_')[0] for p in files])
        self.export_catalog(files)
        current=json.loads((self.evidence_dir/'catalog.json').read_text())
        old=[p for p in current['policies'] if p['policyname']!='monjez_live_actor']
        added=[p for p in current['policies'] if p['policyname']=='monjez_live_actor']
        self.control('original_58_policies_preserved',old==baseline['policies'])
        self.control('restrictive_22_policy_surface',len(added)==22 and {p['tablename'] for p in added}==set(tables) and all(p['permissive']=='RESTRICTIVE' and p['cmd']=='ALL' and p['roles']==['authenticated'] and p['qual'] and p['with_check'] for p in added))
        self.control('public_table_grants_preserved',current['table_grants']==baseline['table_grants'])
        old_f={f['name']:f for f in baseline['functions']}
        self.control('all_public_function_acls_preserved',all(f['acl']==old_f[f['name']]['acl'] for f in current['functions']) and len(current['functions'])==40)
        guarded=[f for f in current['functions'] if 'PERFORM monjez_private.assert_active_actor();' in f['definition']]
        self.control('all_33_definer_entries_guarded',len(guarded)==33)
        private=self.query("select jsonb_build_object('functions',(select jsonb_agg(jsonb_build_object('name',p.proname,'acl',p.proacl::text,'config',p.proconfig,'definition',pg_get_functiondef(p.oid))) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='monjez_private'),'anon_usage',has_schema_privilege('anon','monjez_private','USAGE'),'auth_create',has_schema_privilege('authenticated','monjez_private','CREATE'),'auth_auth_table',has_table_privilege('authenticated','auth.users','SELECT'));")
        self.control('private_lookup_not_public_auth_table',not private['anon_usage'] and not private['auth_create'] and not private['auth_auth_table'] and len(private['functions'])==2 and all(f['config']==['search_path=""'] for f in private['functions']))
        (self.evidence_dir/'private-catalog.json').write_text(json.dumps(private,indent=2)+'\n')
        plan=self.query(f"explain (analyze,buffers,format json) select exists(select 1 from auth.users where id='{b['uid']}'::uuid and deleted_at is null and (banned_until is null or banned_until<=statement_timestamp()));")
        (self.evidence_dir/'lookup-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        self.control('fixture_lookup_plan_recorded',isinstance(plan,list) and bool(plan))
        expected_rpc={f['name'] for f in baseline['functions'] if f['definer'] and 'authenticated=X/' in f['acl']}
        for name, actor in [('owner',b),('staff',s2)]:
            from live_probe import auth_ban_denial
            for op, grant, payload in [('login','password',{'email':actor['email'],'password':actor['password']}),('refresh','refresh_token',{'refresh_token':actor['refresh']})]:
                status,body=self.request('POST','/auth/v1/token?grant_type='+grant,payload)
                self.control('banned_'+name+'_'+op,auth_ban_denial(status,body),status=status)
            for table in ('tenants','profiles','user_roles'):
                status,rows=self.own_rows(actor,table)
                suffix='tenant' if table=='tenants' else table
                self.control('banned_'+name+'_old_jwt_own_'+suffix,denial(status,rows),status=status,visible_rows=len(rows) if isinstance(rows,list) else 0)
            for table in tables:
                status,body=self.request('GET','/rest/v1/'+table+'?select=*&limit=1',token=actor['token'])
                self.control('banned_'+name+'_table_'+table,denial(status,body),status=status)
            payloads=rpc_payloads(actor,a)
            self.control(name+'_exact_30_rpc_surface',set(payloads)==expected_rpc)
            for rpc,payload in payloads.items():
                status,body=self.request('POST','/rest/v1/rpc/'+rpc,payload,token=actor['token'])
                check='banned_'+name+'_summary' if rpc=='get_tenant_today_estimate' else 'banned_'+name+'_rpc_'+rpc
                self.control(check,strict_guard_denial(status,body),status=status)
            self.control('banned_'+name+'_direct_rls',self.sql_rls_denied(actor))
            for table,where,payload in [('tenants',actor['tenant'],{'name':'FORBIDDEN'}),('profiles',actor['uid'],{'display_name':'FORBIDDEN'})]:
                status,body=self.request('PATCH','/rest/v1/'+table+'?id=eq.'+where,payload,token=actor['token'])
                self.control('banned_'+name+'_update_'+table,denial(status,body),status=status)
            status,body=self.request('POST','/rest/v1/tenants',{'name':'FORBIDDEN','owner_user_id':actor['uid']},token=actor['token'])
            self.control('banned_'+name+'_insert_tenant',denial(status,body),status=status)
        self.control('public_history_preserved',self.history_all(tables)==before)
        for name,actor in [('owner_A',a),('staff_A',s1)]:
            status,rows=self.own_rows(actor,'tenants')
            self.control('active_after_ban_'+name,status==200 and isinstance(rows,list) and len(rows)==1,status=status)
        # Live clock/expiry, unban and absence are tested without deleting identities/history.
        self.sql(f"update auth.users set banned_until=now()-interval '1 second' where id='{b['uid']}';")
        status,rows=self.own_rows(b,'tenants')
        self.control('expired_ban_active',status==200 and isinstance(rows,list) and len(rows)==1,status=status)
        status,_=self.request('PUT','/auth/v1/admin/users/'+b['uid'],{'ban_duration':'24h'},admin=True)
        self.control('reban_stored',status==200)
        status,rows=self.own_rows(b,'tenants')
        self.control('committed_reban_denied',denial(status,rows),status=status)
        status,_=self.request('PUT','/auth/v1/admin/users/'+b['uid'],{'ban_duration':'none'},admin=True)
        self.control('unban_saved',status==200)
        status,session=self.request('POST','/auth/v1/token?grant_type=password',{'email':b['email'],'password':b['password']})
        self.control('unban_new_login',status==200 and isinstance(session,dict) and bool(session.get('access_token')),status=status)
        status,rows=self.request('GET','/rest/v1/tenants?id=eq.'+b['tenant'],token=session['access_token'])
        self.control('unban_new_token_own_tenant',status==200 and isinstance(rows,list) and len(rows)==1,status=status)
        missing=str(uuid.uuid4())
        text=self.sql(f"begin; set local role authenticated; select set_config('request.jwt.claim.sub','{missing}',true) is not null; select monjez_private.actor_is_active()::text; rollback;").splitlines()[-1]
        self.control('missing_identity_denied',text=='false')
        self.sql(f"""begin; set local role authenticated;
        select set_config('request.jwt.claim.sub','{s2['uid']}',true) is not null;
        select set_config('request.jwt.claims','{{"sub":"{s2['uid']}","role":"service_role"}}',true) is not null;
        do $test$ begin
          begin
            perform public.has_owner_role('{a['uid']}'::uuid,'{a['tenant']}'::uuid);
            raise exception 'caller spoof allowed';
          exception when insufficient_privilege then
            if SQLERRM <> 'account_inactive' then raise; end if;
          end;
        end $test$; rollback;""")
        self.control('jwt_role_and_helper_uid_cannot_bypass',True)
        self.sql("begin; set local role service_role; select monjez_private.assert_active_actor(); rollback;")
        self.control('trusted_service_role_entry',True)
        # Reversible schema roundtrip on dummy data only; finance assertions never executed active.
        unchanged=self.history_all(tables)
        self.sql(Path('changes/env-native-01/rollback-compensation.sql').read_text())
        self.control('rollback_prior_schema_restored',self.sql("select count(*) from pg_namespace where nspname='monjez_private';")=='0' and self.history_all(tables)==unchanged)
        restored=self.query("select jsonb_object_agg(p.proname,pg_get_functiondef(p.oid)) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.prokind='f';")
        self.control('rollback_all_40_definitions_exact',restored=={f['name']:f['definition'] for f in baseline['functions']})
        self.sql((Path('supabase/migrations')/MIGRATION).read_text())
        self.sql((Path('supabase/migrations')/COMPENSATION).read_text())
        self.control('compensation_reapply_no_data_change',self.history_all(tables)==unchanged)
        status,rows=self.own_rows(s2,'tenants')
        self.control('reapply_banned_staff_denied',denial(status,rows),status=status)
        status,body=self.request('PATCH','/rest/v1/profiles?id=eq.'+s2['uid'],{'display_name':'FORBIDDEN'},token=s2['token'])
        self.control('reapply_banned_staff_profile_denied',denial(status,body),status=status)
        final=self.counts()
        self.control('zero_financial_rows',all(final[t]==0 for t in FINANCE_TABLES))
        self.control('exact_fixture_counts',{k:final[k] for k in ('users','tenants','profiles','roles')}=={'users':4,'tenants':2,'profiles':4,'roles':4})
        self.control('tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode==0)
        result={'outcome':green_result(self.controls),'source_sha':self.source,'mode':mode,'checks':self.controls,
                'initial_counts':initial,'final_counts':final,'history_before':before,'history_after':self.history_all(tables),
                'integration_accepted':False,'independent_review':False,
                'missing_coverage':['MCP transport','actual deleted identity/history','expired signed JWT','nonempty financial history',
                                    'concurrent/in-flight transactions','active financial writes','independent review','production-scale performance']}
        (self.evidence_dir/'correction-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'outcome':result['outcome'],'mode':mode,'checks_passed':len(self.controls),'integration_accepted':False}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--status-file',type=Path,required=True);p.add_argument('--evidence-dir',type=Path,required=True)
    p.add_argument('--expected-source',required=True);p.add_argument('--mode',choices=['fresh','upgrade'],required=True)
    p.add_argument('--stack-dir',type=Path,required=True)
    a=p.parse_args()
    try:
        CorrectionProbe(a.status_file,a.evidence_dir,a.expected_source).run_correction(a.mode,a.stack_dir)
    except (HarnessFailure,OSError,ValueError,subprocess.SubprocessError) as e:
        a.evidence_dir.mkdir(parents=True,exist_ok=True)
        reason=str(e) if isinstance(e,HarnessFailure) else 'local harness execution failure'
        (a.evidence_dir/'harness-failure.json').write_text(json.dumps({'outcome':'ENV_NATIVE_01_CORRECTION_HARNESS_FAILURE','reason':reason,'integration_accepted':False})+'\n')
        print('ENV_NATIVE_01_CORRECTION_HARNESS_FAILURE: '+reason)
        raise SystemExit(2)
