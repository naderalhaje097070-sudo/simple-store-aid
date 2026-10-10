import os,json,pathlib,shlex,subprocess
env=os.environ.copy()
for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']: env.pop(k,None)
values={}
for line in pathlib.Path('/vercel/stack.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);values[k]=shlex.split(v)[0] if v else ''
fixture=json.loads(pathlib.Path('/vercel/auth-fixture.json').read_text())
env.update(CI_ISOLATED_SUPABASE='1',MONGEZZ_DEPLOY_TARGET='ci',APP_BASE_URL='http://127.0.0.1:8080',VITE_SUPABASE_URL=values['API_URL'],VITE_SUPABASE_PUBLISHABLE_KEY=values['ANON_KEY'],PILOT_QA_EMAIL=fixture['email'],PILOT_QA_PASSWORD=fixture['password'])
with pathlib.Path('/vercel/evidence/auth-ui.log').open('w') as out:
 result=subprocess.run(['/vercel/browser/bin/python','tests/e2e/isolated-auth-smoke.py'],cwd='/vercel/candidate',env=env,stdout=out,stderr=subprocess.STDOUT,timeout=120)
pathlib.Path('/vercel/evidence/auth-ui-result.json').write_text(json.dumps({'source':'84c3444fcdf5fa2825809192cda5b15561c950cf','command':'python tests/e2e/isolated-auth-smoke.py','exit_code':result.returncode},indent=2)+'\n')
print('auth_ui_exit',result.returncode)

