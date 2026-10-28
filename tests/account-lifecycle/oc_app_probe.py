"""Focused local45 actual TanStack price entry; only provider fetch is replaced."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from live_probe import HarnessFailure
from tanstack_route_probe import TanStackRouteProbe, METADATA, publish_result
from tanstack_route_build import app_environment


class PriceProbe(TanStackRouteProbe):
    def control(self, name, passed, **details):
        if any(x['name'] == name for x in self.controls):
            raise HarnessFailure('duplicate control')
        self.controls.append({'name': name, 'passed': bool(passed), **details})
        (self.evidence_dir/'price-progress.json').write_text(json.dumps(self.controls, indent=2)+'\n')
        if not passed:
            raise HarnessFailure('price control failed: '+name)

    def start(self, label='app', conflict=False):
        env = app_environment(self.anon)
        allowed = ('MONGEZZ_DEPLOY_TARGET', 'CI_ISOLATED_SUPABASE', 'SUPABASE_URL', 'VITE_SUPABASE_URL',
                   'SUPABASE_PUBLISHABLE_KEY', 'VITE_SUPABASE_PUBLISHABLE_KEY',
                   'SUPABASE_PROJECT_ID', 'VITE_SUPABASE_PROJECT_ID')
        server_env = {k: env[k] for k in allowed}
        server_env.update(LOVABLE_API_KEY="oc-app-dummy", PADDLE_SANDBOX_API_KEY="oc-app-dummy", PADDLE_LIVE_API_KEY="oc-app-dummy")
        if conflict:
            server_env['SUPABASE_PROJECT_ID'] = server_env['VITE_SUPABASE_PROJECT_ID'] = 'route-conflict'
        server_env.update(NITRO_HOST='127.0.0.1', NITRO_PORT='54325',
                          MCP_ROUTE_STATE=str(self.runtime / (label + '.json')),
                          MCP_ROUTE_RELEASE=str(self.runtime / ('release-' + label)))
        release = Path(server_env['MCP_ROUTE_RELEASE'])
        release.unlink(missing_ok=True)
        self.log = (Path(os.environ['RUNNER_TEMP']) / ('route-' + label + '-private.log')).open('w')
        command = ['sudo', '-u', 'mcp-route', 'env', '-i', 'PATH=/usr/bin:/bin']
        command += [k + '=' + v for k, v in server_env.items()]
        command += [shutil.which('node'), '--import', str(self.runtime / 'guard.mjs'),
                    str(self.runtime / '.output/server/index.mjs')]
        self.process = subprocess.Popen(command, stdout=self.log, stderr=self.log)
        for _ in range(80):
            if (self.runtime / (label + '.json')).exists() and self.state(label).get('guard_ready') is True:
                self.firewall_baseline = self.rejected_packets()
                subprocess.run(['sudo', '-u', 'mcp-route', 'touch', str(release)], check=True)
                break
            if self.process.poll() is not None:
                raise HarnessFailure('actual process containment failed')
            time.sleep(.1)
        else:
            raise HarnessFailure('actual preload not ready before bundle')
        for _ in range(80):
            if self.process.poll() is not None:
                raise HarnessFailure('built application process failed')
            try:
                status, _ = self.http('GET', METADATA)
                self.readiness.append({'process': label, 'status': status})
                if (conflict and status == 500) or (not conflict and status == 200):
                    return
                if not conflict and status >= 500:
                    self.failure_stage = 'built_metadata_http_500'
                    raise HarnessFailure('Actual built application metadata failed')
            except HarnessFailure:
                if self.failure_stage == 'built_metadata_http_500':
                    raise
                pass
            time.sleep(.25)
        raise HarnessFailure('built route did not become ready')

    def price(self, token=None, price='oc-app-price', environment='sandbox'):
        completed = subprocess.run(['node', 'tests/account-lifecycle/oc_app_client.mjs'], input=json.dumps(
            {'id': self.function_id, 'token': token, 'data': {'priceId': price, 'environment': environment}}),
            capture_output=True, text=True, timeout=15)
        if completed.returncode:
            raise HarnessFailure('locked price client failed')
        return json.loads(completed.stdout)

    def gateway_count(self):
        return len(self.state()['gateway_calls'])

    def check_price(self, label, token, expected, calls, **kwargs):
        before = self.gateway_count()
        activity_before=self.state()["activity_checks"]
        result = self.price(token, **kwargs)
        after = self.gateway_count()
        self.control(label, result.get('result') == expected if expected == 'pri_oc_app_dummy'
                     else result.get('error') == expected, response=result, gateway_before=before,
                     gateway_after=after, expected_gateway_delta=calls, activity_before=activity_before,
                     activity_after=self.state()["activity_checks"])
        self.control(label+'_gateway_delta', after-before == calls)
        expected_activity=0 if self.mode=='baseline' or expected.startswith('Unauthorized:') else 1
        self.control(label+'_activity_delta',self.state()['activity_checks']-activity_before==expected_activity)

    def state_snapshot(self):
        return {'public': self.snapshot(), 'auth': self.query("select jsonb_agg(jsonb_build_object("
            "'id',id,'deleted_at',deleted_at,'banned_until',banned_until) order by id) from auth.users;")}

    def run_price(self, mode):
        self.mode=mode
        self.control('empty_initial_stack', all(x == 0 for x in self.counts().values()))
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        manifest=json.loads(Path('changes/oc-app-01/SOURCE.json').read_text())
        self.control('all45_migration_blobs_immutable',len(manifest['migration_blobs'])==45 and all(
            hashlib.sha1(b'blob '+str(len(Path(x['path']).read_bytes())).encode()+b'\0'+Path(x['path']).read_bytes()).hexdigest()==x['git_blob_sha']
            for x in manifest['migration_blobs']))
        self.control('exact45_applied', len(files) == 45 and self.query(
            'select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;') ==
            [x.name.split('_')[0] for x in files])
        a,b = self.fixture('price_A'),self.fixture('price_B')
        c = self.fixture('price_staff', tenant=a['tenant'], staff=True)
        # This retains a real Auth identity/profile with no tenant; no new role requirement.
        self.sql("update public.profiles set tenant_id=null where id='%s';" % c['uid'])
        status, client = self.request('POST','/auth/v1/admin/oauth/clients', {
            'redirect_uris':['http://127.0.0.1:54325/test-oauth-callback'], 'client_type':'public',
            'token_endpoint_auth_method':'none', 'grant_types':['authorization_code','refresh_token'],
            'client_name':'oc-app-local'},admin=True)
        self.control('local_oauth_client', status == 201 and isinstance(client.get('client_id'),str))
        self.client_id=client['client_id']
        self.secrets=[self.anon,self.admin]+[x[k] for x in (a,b,c) for k in ('password','token','refresh')]
        for label, actor in [('A',a),('B',b),('no_tenant',c)]:
            self.oauth_token(actor,label,self.client_id);self.secrets.append(actor['token'])
        # Use the compiler's own manifest, not a hand-written test route or imported handler.
        manifests=list(Path('.tanstack').rglob('*')) if Path('.tanstack').exists() else []
        chunks=list(Path('.output/server').rglob('*.mjs'))
        candidates=[]
        for path in manifests+chunks:
            if not path.is_file():continue
            text=path.read_text(errors='replace')
            # Function manifest entries contain the original export name.
            candidates += re.findall(r'["\']([a-f0-9]{40,64})["\']\s*:\s*\{[^}]{0,1000}?(?:resolvePaddlePrice)',text)
            candidates += re.findall(r'createServerRpc\(["\']([^"\']+)["\'],\s*[^,]+,\s*["\']resolvePaddlePrice["\']',text)
        ids=sorted(set(candidates))
        self.control('one_compiled_price_function',len(ids)==1, count=len(ids))
        self.function_id=ids[0]
        before=self.state_snapshot()
        try:
            self.start()
            self.check_price('active_A',a['token'],'pri_oc_app_dummy',1)
            self.check_price('active_B',b['token'],'pri_oc_app_dummy',1)
            self.check_price('active_no_tenant_staff',c['token'],'pri_oc_app_dummy',1)
            self.check_price('live_environment_unchanged',a['token'],'pri_oc_app_dummy',1,environment='live')
            self.check_price('escaped_price_unchanged',a['token'],'pri_oc_app_dummy',1,price='oc-app-escaped &?')
            self.check_price('missing_price_unchanged',a['token'],'Price not found',1,price='oc-app-missing')
            self.check_price('missing_token',None,'Unauthorized: No authorization header provided',0)
            self.check_price('invalid_token','invalid','Unauthorized: Invalid token',0)
            parts=a['token'].split('.')
            # Same three-part shape with a corrupted signature, never a minted identity.
            parts[2]=('A' if parts[2][0]!='A' else 'B')+parts[2][1:]
            self.check_price('invalid_signature','.'.join(parts),'Unauthorized: Invalid token',0)
            old=b['token'];digest=hashlib.sha256(old.encode()).hexdigest()
            status,body=self.request('POST','/rest/v1/rpc/close_owner_account',{},token=old)
            self.control('self_owner_closed',status==200 and body=={'status':'closed'})
            fresh=copy.deepcopy(b);fresh['token']=b['session_token']
            self.oauth_token(fresh,'B_new',self.client_id);self.secrets.append(fresh['token'])
            self.control('genuine_new_token_differs',fresh['token']!=old)
            for label,token in [('old',old),('new',fresh['token'])]:
                claims=json.loads(__import__('base64').urlsafe_b64decode(token.split('.')[1]+'=='))
                status,user=self.request('GET','/auth/v1/user',token=token)
                self.control('provider_positive_'+label,status==200 and user.get('id')==b['uid'] and claims['exp']>time.time())
                expected='pri_oc_app_dummy' if mode=='baseline' else 'account_inactive'
                self.check_price('closed_B_'+label,token,expected,1 if mode=='baseline' else 0)
            self.control('old_token_exact',hashlib.sha256(old.encode()).hexdigest()==digest)
            if mode!='baseline':
                for field,value in [('banned_until',"now()+interval '1 hour'"),('deleted_at','now()')]:
                    self.sql("update auth.users set %s=%s where id='%s';" % (field,value,a['uid']))
                    try:self.check_price('auth_'+field,a['token'],'account_inactive',0)
                    finally:self.sql("update auth.users set %s=null where id='%s';" % (field,a['uid']))
                faultpath=self.runtime/'app.fault'
                for fault in ['database','transport','timeout']:
                    subprocess.run(['sudo','-u','mcp-route','tee',str(faultpath)],input=fault,text=True,capture_output=True,check=True)
                    t=time.monotonic()
                    try:self.check_price('state_failure_'+fault,a['token'],'account_state_unavailable',0)
                    finally:subprocess.run(['sudo','rm','-f',str(faultpath)],check=True)
                    if fault=='timeout':self.control('timeout_bounded',2<=time.monotonic()-t<10)
            if mode!='baseline':
                self.control('faults_reached_exact_boundaries',self.state()['injected_faults']==['database','transport','timeout'])
                expired=a['token']
                expiry=json.loads(__import__('base64').urlsafe_b64decode(expired.split('.')[1]+'=='))['exp']
                wait=expiry-time.time()+1
                self.control('local_token_lifetime_bounded',0<=wait<=65)
                # This wait is inside the disposable workflow, not an agent blocking sleep.
                if wait>0:time.sleep(wait)
                self.control('genuine_token_expired',time.time()>expiry,exp=expiry)
                self.check_price('expired_token',expired,'Unauthorized: Invalid token',0)
                self.control('expired_test_kept_token_bytes',a['token']==expired)
                status,session=self.request('POST','/auth/v1/token?grant_type=password',
                    {'email':a['email'],'password':a['password']})
                self.control('renew_active_session_after_expiry',status==200 and bool(session.get('access_token')))
                a['token']=session['access_token'];self.secrets.append(a['token'])
                self.oauth_token(a,'A_after_expiry',self.client_id);self.secrets.append(a['token'])
            self.check_price('A_unaffected_after',a['token'],'pri_oc_app_dummy',1)
            self.control('public_and_auth_unchanged',self.state_snapshot()==before)
            self.control('one_closure_only',self.sql('select count(*) from monjez_private.owner_account_closures;')=='1')
            self.control('no_financial_fixture_writes',all(self.sql('select count(*) from public.'+t+';')=='0'
                         for t in ('orders','order_items','payments','products','financial_audit_log')))
            self.firewall_after('app')
            self.control('no_unstubbed_external_fetch',self.state()['external_blocked']==0)
            self.control('tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode==0)
            result={'source_sha':self.source,'mode':mode,'outcome':'EXPECTED_RED_CLOSED_PRICE_ALLOWED' if mode=='baseline'
                    else 'PRICE_LIFECYCLE_TESTED_CANDIDATE','integration_accepted':False,'checks':self.controls,
                    'before':before,'after':self.state_snapshot(),'process_containment':self.state(),
                    'firewall':self.firewall_observations,'old_token_sha256':digest,
                    'migration_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in files}}
            result=publish_result(self.evidence_dir,result,self.secrets+self.oauth_refresh_tokens)
            (self.evidence_dir/'route-result.json').rename(self.evidence_dir/'price-result.json')
            if not result.get('evidence_no_credentials'):raise HarnessFailure('evidence quarantined')
            print(json.dumps({'mode':mode,'checks':len(self.controls),'outcome':result['outcome']}))
        finally:self.stop()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--status-file',type=Path,required=True)
    parser.add_argument('--evidence-dir',type=Path,required=True)
    parser.add_argument('--expected-source',required=True)
    parser.add_argument('--mode',choices=['baseline','fixed'],required=True)
    args=parser.parse_args()
    try:PriceProbe(args.status_file,args.evidence_dir,args.expected_source).run_price(args.mode)
    except (HarnessFailure,ValueError,KeyError,TypeError,subprocess.SubprocessError) as error:
        safe={'source_sha':args.expected_source,'failure_type':type(error).__name__,'integration_accepted':False}
        if isinstance(error,HarnessFailure):safe['reason']=str(error)
        (args.evidence_dir/'price-failure.json').write_text(json.dumps(safe,indent=2)+'\n')
        print(json.dumps(safe));raise SystemExit(2)
