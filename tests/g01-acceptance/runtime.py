"""Local41 + unchanged Cloudflare entry/Auth UI; zero financial write flow."""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from guard_receipt import receipt as guard_receipt

root=Path(os.environ['RUNNER_TEMP']);out=root/'g01-evidence';out.mkdir(exist_ok=True)
record={'source_sha':os.environ['EXPECTED_SOURCE'],'verification_batch':'G1-ACCEPTANCE-REPAIR-01','checks':[],'integration_accepted':False}
private_secrets=[]
process=None

def check(name,passed,defer=False,**fields):
    record['checks'].append({'name':name,'passed':bool(passed),**fields})
    (out/'runtime-progress.json').write_text(json.dumps(record,indent=2)+'\n')
    if not passed and not defer:raise RuntimeError(name)

def query(sql):
    result=subprocess.run(['psql','-X','-h','127.0.0.1','-p','54322','-U','postgres','-d','postgres','-At','-v','ON_ERROR_STOP=1','-c',sql],capture_output=True,text=True,check=True)
    return result.stdout.strip()

def snapshot():
    names=json.loads(query("select json_agg(tablename order by tablename) from pg_tables where schemaname='public';"))
    assert all(re.fullmatch('[a-z_]+',x) for x in names)
    return {x:{'count':int(query('select count(*) from public.'+x+';')),'digest':query('select md5(coalesce(string_agg(to_jsonb(t)::text,\'\' order by to_jsonb(t)::text),\'\')) from public.'+x+' t;')} for x in names}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())

def http(path,method='GET',payload=None,token=None,admin=False):
    if path.startswith('/auth/v1/') or path.startswith('/rest/v1/'):
        base='http://127.0.0.1:54321';headers={'apikey':status['ANON_KEY']}
        if path.startswith('/rest/v1/'):headers['Prefer']='return=representation'
        if admin:token=status['SERVICE_ROLE_KEY']
    else:
        assert path in ['/','/app'];base='http://127.0.0.1:8080';headers={}
    if token:headers['Authorization']='Bearer '+token
    headers['Content-Type']='application/json'
    req=urllib.request.Request(base+path,method=method,headers=headers,data=json.dumps(payload).encode() if payload is not None else None)
    try:response=opener.open(req,timeout=15)
    except urllib.error.HTTPError as error:response=error
    with response:
        data=response.read();code=response.status
        if 300<=code<400:raise RuntimeError('local redirect rejected')
        if base.endswith('54321'):return code,json.loads(data)
        return code,data

def counters():
    v=subprocess.run(['sudo','iptables','-nvxL','G01_APP'],capture_output=True,text=True,check=True).stdout
    rows=[int(x.split()[0]) for x in v.splitlines() if 'REJECT' in x]
    assert len(rows)==1
    uid=subprocess.run(['id','-u','g01-app'],capture_output=True,text=True,check=True).stdout.strip()
    v6=subprocess.run(['sudo','ip6tables','-nvxL','OUTPUT'],capture_output=True,text=True,check=True).stdout
    ipv6=[int(x.split()[0]) for x in v6.splitlines() if 'REJECT' in x and ('owner UID match '+uid) in x]
    assert len(ipv6)==1
    return {'ipv4':rows[0],'ipv6':ipv6[0]}

def stop():
    global process
    subprocess.run(['sudo','pkill','-TERM','-u','g01-app'],capture_output=True)
    if process:process.wait(timeout=15)
    process=None

def start(conflict=False):
    global process
    runtime=Path('/tmp/g01-runtime');runtime.mkdir(exist_ok=True)
    values={k:buildenv[k] for k in ['MONGEZZ_DEPLOY_TARGET','VITE_SUPABASE_URL','SUPABASE_URL','VITE_SUPABASE_PUBLISHABLE_KEY','SUPABASE_PUBLISHABLE_KEY','VITE_SUPABASE_PROJECT_ID','SUPABASE_PROJECT_ID']}
    if conflict:values['VITE_SUPABASE_PROJECT_ID']=values['SUPABASE_PROJECT_ID']='g01-conflict'
    envfile=runtime/'worker.env'
    staged=root/'g01-worker-private.env';staged.write_text('\n'.join(k+'='+v for k,v in values.items())+'\n');staged.chmod(0o600)
    try:
        subprocess.run(['sudo','install','-m','600','-o','g01-app','-g','g01-app',str(staged),str(envfile)],check=True)
    finally:
        staged.unlink(missing_ok=True)
    log=root/('g01-conflict-private.log' if conflict else 'g01-app-private.log')
    # Wrangler4.149.0's banner independently checks npm even with metrics disabled.
    # The official early-return flag suppresses that tooling request; firewall stays exact.
    command=['sudo','-u','g01-app','env','-i','PATH=/usr/bin:/bin','WRANGLER_SEND_METRICS=false','WRANGLER_HIDE_BANNER=true',
             shutil.which('node'),'/tmp/g01-tools/node_modules/wrangler/bin/wrangler.js','dev','--local',
             '--config','/tmp/g01-runtime/.output/server/wrangler.json','--env-file',str(envfile),
             '--compatibility-date','2026-08-08','--ip','127.0.0.1','--port','8080']
    with log.open('wb') as output:process=subprocess.Popen(command,stdout=output,stderr=output,cwd=runtime)
    for _ in range(100):
        if process.poll() is not None:raise RuntimeError('emulator exited')
        try:
            code,body=http('/')
            if (not conflict and code==200) or (conflict and code==500):return code,body,log
        except (urllib.error.URLError,TimeoutError):pass
        time.sleep(.5)
    raise RuntimeError('emulator readiness failed')

try:
    # No credentials read before the exact legacy guard and credential-free firewall canary.
    for name in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy','PGSERVICE','PGSERVICEFILE','PGHOSTADDR','PGOPTIONS','CLOUDFLARE_API_TOKEN','LOVABLE_API_KEY']:
        check('clean_'+name,not os.environ.get(name))
    check('native_canary_rejected',counters()['ipv4']>0)
    firewall_before=counters()
    record['native_phase_counters']={'before':firewall_before}
    status=json.loads((root/'g01-status.json').read_text())
    check('exact_local_API',status['API_URL']=='http://127.0.0.1:54321')
    private_secrets=[status['ANON_KEY'],status['SERVICE_ROLE_KEY']]
    files=sorted(Path('supabase/migrations').glob('*.sql'))
    versions=json.loads(query('select json_agg(version order by version) from supabase_migrations.schema_migrations;'))
    check('exact41_migrations',len(files)==41 and versions==[p.name.split('_')[0] for p in files])
    check('initial_empty_finance_auth',all(int(query('select count(*) from public.'+t+';'))==0 for t in ['orders','products','payments','customers']) and query('select count(*) from auth.users;')=='0')
    actors=[]
    for label in ['A','B']:
        email='g01-'+uuid.uuid4().hex+'@example.test';password=secrets.token_urlsafe(30)+'!aA1';private_secrets.append(password)
        code,user=http('/auth/v1/admin/users','POST',{'email':email,'password':password,'email_confirm':True},admin=True)
        check(label+'_auth_created',code==200 and bool(user.get('id')))
        uid=str(uuid.UUID(user['id']));tid=str(uuid.uuid4())
        code,rows=http('/rest/v1/tenants','POST',{'id':tid,'owner_user_id':uid,'name':'G01 '+label},admin=True)
        check(label+'_tenant_created',code==201 and len(rows)==1)
        code,rows=http('/rest/v1/profiles?id=eq.'+uid,'PATCH',{'tenant_id':tid,'display_name':'G01 QA '+label},admin=True)
        check(label+'_profile_assigned',code==200 and len(rows)==1)
        check(label+'_trigger_owner_role_one',query("select count(*) from public.user_roles where user_id='%s' and tenant_id='%s' and role='owner';"%(uid,tid))=='1')
        code,session=http('/auth/v1/token?grant_type=password','POST',{'email':email,'password':password})
        check(label+'_real_login',code==200 and bool(session.get('access_token')))
        private_secrets += [session['access_token'],session.get('refresh_token','')]
        actors.append({'id':uid,'tenant':tid,'email':email,'password':password,'token':session['access_token']})
    for i,actor in enumerate(actors):
        code,rows=http('/rest/v1/tenants?id=eq.'+actor['tenant'],token=actor['token'])
        check(str(i)+'_own_tenant_positive',code==200 and len(rows)==1 and rows[0]['id']==actor['tenant'])
        code,rows=http('/rest/v1/tenants?id=eq.'+actors[1-i]['tenant'],token=actor['token'])
        check(str(i)+'_foreign_metadata_empty_with_own_positive',code==200 and rows==[])
    before=snapshot();record['before']=before
    buildenv=dict(os.environ)
    for name in ['SUPABASE_SERVICE_ROLE_KEY','LOVABLE_API_KEY','NODE_OPTIONS']:buildenv.pop(name,None)
    buildenv.update(MONGEZZ_DEPLOY_TARGET='ci',CI_ISOLATED_SUPABASE='1',APP_BASE_URL='http://127.0.0.1:8080',
                    VITE_SUPABASE_URL=status['API_URL'],SUPABASE_URL=status['API_URL'],
                    VITE_SUPABASE_PUBLISHABLE_KEY=status['ANON_KEY'],SUPABASE_PUBLISHABLE_KEY=status['ANON_KEY'],
                    VITE_SUPABASE_PROJECT_ID='g01-local',SUPABASE_PROJECT_ID='g01-local')
    with (root/'g01-build-private.log').open('wb') as log:
        result=subprocess.run(['bun','run','build'],env=buildenv,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    check('actual_default_Cloudflare_build',result.returncode==0 and Path('.output/server/wrangler.json').is_file())
    record['build_warnings']={'precache_zero':bool(re.search(r'precache\s+.*0 entries',(root/'g01-build-private.log').read_text()))}
    subprocess.run(['sudo','mkdir','-p','/tmp/g01-runtime'],check=True)
    subprocess.run(['sudo','cp','-a','.output','/tmp/g01-runtime/'],check=True)
    subprocess.run(['sudo','chown','-R','g01-app:g01-app','/tmp/g01-runtime'],check=True)
    record['build_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('.output').rglob('*') if p.is_file()}
    code,body,log=start()
    record['native_phase_counters']['matching_ready']=counters()
    check('real_SSR_matching_target',code==200 and b'<!DOCTYPE html' in body or code==200 and b'<!doctype html' in body)
    smokeenv=dict(buildenv);smokeenv.update(PILOT_QA_EMAIL=actors[0]['email'],PILOT_QA_PASSWORD=actors[0]['password'])
    with (root/'g01-auth-private.log').open('wb') as log:
        smoke=subprocess.run(['python','tests/e2e/isolated-auth-smoke.py'],env=smokeenv,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('existing_actual_Auth_UI_desktop_mobile',smoke.returncode==0 and 'PASS: isolated authenticated UI smoke' in (root/'g01-auth-private.log').read_text())
    record['native_phase_counters']['after_auth_ui']=counters()
    stop();code,body,log=start(True)
    # Drain the native process log before inspecting it; publish only static codes/hashes.
    stop()
    denial=guard_receipt(code,body,log.read_text())
    record['native_phase_counters']['after_conflict_stopped']=counters()
    record['conflict_guard_receipt']=denial
    check('real_SSR_conflict_named_denial',denial['passed'],defer=True,
          status=code,log_drained_before_classification=True)
    check('public_fixture_unchanged',snapshot()==before);record['after']=snapshot()
    check('finance_zero_at_end',all(query('select count(*) from public.'+x+';')=='0' for x in ['orders','order_items','products','payments','expenses','financial_audit_log']))
    check('native_unexpected_outbound_zero',counters()==firewall_before,defer=True,native_before=firewall_before,native_after=counters())
    check('tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode==0)
    record['runtime']={'supabase_cli':'2.101.0','wrangler':'4.149.0','playwright':'1.62.0','node':subprocess.run(['node','--version'],capture_output=True,text=True).stdout.strip()}
    record['g2_known_unfixed']='preissued banned JWT still has old access on source54; original native evidence retained, not retested/imported'
    record['financial_flow_executed']=False
    check('credential_free_receipt',not any(x and x in json.dumps(record) for x in private_secrets))
    # A deferred mismatch failure still fails the job after collecting end-state evidence.
    if any(not item['passed'] for item in record['checks']):
        raise RuntimeError('deferred_acceptance_checks_failed')
    (out/'runtime-result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'checks':len(record['checks']),'passed':all(x['passed'] for x in record['checks']),'source_sha':record['source_sha']}))
except Exception as error:
    record['failure_type']=type(error).__name__
    record['failed_phase']='after_'+(record['checks'][-1]['name'] if record['checks'] else 'start')
    if isinstance(error,RuntimeError):record['reason']=str(error)
    (out/'runtime-failure.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'failure_type':type(error).__name__,'reason':record.get('reason')}));raise SystemExit(2)
finally:
    stop()
    (root/'g01-status.json').unlink(missing_ok=True)
    subprocess.run(['sudo','rm','-f','/tmp/g01-runtime/worker.env'],check=False)
