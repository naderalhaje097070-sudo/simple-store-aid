import json,pathlib,shlex,urllib.request,urllib.error,uuid,secrets,os
from urllib.parse import urlparse
values={}
for line in pathlib.Path('/vercel/stack.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);values[k]=shlex.split(v)[0] if v else ''
base=values['API_URL'];parsed=urlparse(base);assert parsed.scheme=='http' and parsed.hostname=='127.0.0.1' and parsed.port==54321
assert not any(os.environ.get(k) for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'])
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs): return None
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
results=[]
def req(method,path,payload=None,token=None,admin=False,prefer=False):
 assert path.startswith('/') and not path.startswith('//')
 key=values['SERVICE_ROLE_KEY'] if admin else values['ANON_KEY']
 headers={'apikey':key,'Authorization':'Bearer '+(token or key),'Content-Type':'application/json'}
 if prefer:headers['Prefer']='return=representation'
 request=urllib.request.Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers=headers,method=method)
 try:
  with opener.open(request,timeout=40) as response: return response.status,json.loads(response.read() or b'null')
 except urllib.error.HTTPError as exc:
  data=exc.read()
  try:body=json.loads(data or b'null')
  except Exception:body={}
  return exc.code,body
def check(name,condition,**details):
 results.append({'name':name,'passed':bool(condition),**details})
users=[];tenants=[];password='Isolated-'+secrets.token_hex(16)+'!'
for label in ['A','B']:
 email='isolation-'+label.lower()+'-'+uuid.uuid4().hex[:8]+'@example.test'
 status,user=req('POST','/auth/v1/admin/users',{'email':email,'password':password,'email_confirm':True,'user_metadata':{'display_name':'Fixture '+label}},admin=True)
 check('auth_create_'+label,status==200 and bool(user.get('id')),status=status)
 if status!=200 or not user.get('id'): raise RuntimeError('Fixture account creation failed; no token output')
 uid=user['id'];tid=str(uuid.uuid4())
 status,body=req('POST','/rest/v1/tenants',{'id':tid,'name':'Tenant '+label,'owner_user_id':uid},admin=True,prefer=True)
 check('seed_tenant_'+label,status==201,status=status)
 status,body=req('PATCH','/rest/v1/profiles?id=eq.'+uid,{'tenant_id':tid},admin=True,prefer=True)
 check('seed_profile_'+label,status==200 and len(body or [])==1,status=status)
 status,body=req('POST','/rest/v1/user_roles',{'user_id':uid,'tenant_id':tid,'role':'owner'},admin=True,prefer=True)
 check('seed_role_'+label,status==201,status=status)
 status,auth=req('POST','/auth/v1/token?grant_type=password',{'email':email,'password':password})
 check('auth_login_'+label,status==200 and bool(auth.get('access_token')),status=status)
 if not auth.get('access_token'):raise RuntimeError('Login failed')
 users.append({'uid':uid,'email':email,'token':auth['access_token']});tenants.append(tid)
# Authenticated requests use actual user JWTs; no elevated token after fixture setup.
for idx,label in enumerate(['A','B']):
 own=tenants[idx];other=tenants[1-idx];token=users[idx]['token']
 status,rows=req('GET','/rest/v1/tenants?select=id',token=token)
 check(label+'_sees_only_own_tenant',status==200 and {r['id'] for r in rows or []}=={own},status=status,visible_rows=len(rows) if isinstance(rows,list) else None)
 status,rows=req('GET','/rest/v1/tenants?id=eq.'+other+'&select=id',token=token)
 check(label+'_cross_tenant_read_denied',status==200 and rows==[],status=status)
 status,rows=req('PATCH','/rest/v1/tenants?id=eq.'+other,{'name':'FORBIDDEN'},token=token,prefer=True)
 check(label+'_cross_tenant_update_no_effect',status==200 and rows==[],status=status)
 status,rows=req('POST','/rest/v1/tenants',{'name':'Forbidden tenant','owner_user_id':users[1-idx]['uid']},token=token,prefer=True)
 check(label+'_foreign_owner_insert_rejected',status in [401,403],status=status)
 status,rows=req('PATCH','/rest/v1/profiles?id=eq.'+users[idx]['uid'],{'tenant_id':other},token=token,prefer=True)
 check(label+'_tenant_reassignment_rejected',status in [401,403],status=status)
# Anonymous key must not read tenant records.
status,rows=req('GET','/rest/v1/tenants?select=id')
check('anonymous_tenant_read_denied',status in [401,403] or (status==200 and rows==[]),status=status)
status,rows=req('GET','/rest/v1/tenants?select=id,name',admin=True)
check('forbidden_updates_did_not_change_stored_names',status==200 and {r['name'] for r in rows}=={'Tenant A','Tenant B'},status=status)
# Test new login after ban; existing-token behavior is recorded as a separate limitation.
status,body=req('PUT','/auth/v1/admin/users/'+users[1]['uid'],{'ban_duration':'24h'},admin=True)
check('ban_fixture_account',status==200,status=status)
status,body=req('POST','/auth/v1/token?grant_type=password',{'email':users[1]['email'],'password':password})
check('banned_new_login_denied',status in [400,401,403],status=status)
status,rows=req('GET','/rest/v1/tenants?select=id',token=users[1]['token'])
existing_access=status==200 and isinstance(rows,list) and any(r['id']==tenants[1] for r in rows)
limitations={'pre_ban_token_still_reads_own_tenant':existing_access,'status':status,'disabled_user_strict_acceptance':False,'full_tenant_coverage':False}
pathlib.Path('/vercel/auth-fixture.json').write_text(json.dumps({'email':users[0]['email'],'password':password}))
os.chmod('/vercel/auth-fixture.json',0o600)
result={'source':'84c3444fcdf5fa2825809192cda5b15561c950cf','scope':'nonfinancial_auth_and_tenant_metadata_only','checks':results,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'limitations':limitations}
pathlib.Path('/vercel/evidence/auth-tenant-probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

