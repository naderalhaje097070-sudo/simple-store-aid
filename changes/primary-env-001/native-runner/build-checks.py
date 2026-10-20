import os,pathlib,json,shlex,subprocess
values={}
for line in pathlib.Path('/vercel/stack.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);values[k]=shlex.split(v)[0] if v else ''
env=os.environ.copy();env['PATH']='/vercel/tools/bun-linux-x64:/vercel/tools/node-v22.16.0-linux-x64/bin:'+env.get('PATH','/usr/bin:/bin')
for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:env.pop(k,None)
env.update(MONGEZZ_DEPLOY_TARGET='ci',CI_ISOLATED_SUPABASE='1',APP_BASE_URL='http://127.0.0.1:8080',VITE_SUPABASE_URL=values['API_URL'],SUPABASE_URL=values['API_URL'],VITE_SUPABASE_PUBLISHABLE_KEY=values['ANON_KEY'],SUPABASE_PUBLISHABLE_KEY=values['ANON_KEY'],VITE_SUPABASE_PROJECT_ID='local',SUPABASE_PROJECT_ID='local')
root='/vercel/candidate';evidence=pathlib.Path('/vercel/evidence');results=[]
commands=[('gate4',['bun','tests/gate4/sec-env/probe.ts']),('auth-preflight',['python3','tests/e2e/isolated-auth-smoke.py','--preflight-only']),('unit',['bun','test','tests/unit']),('typecheck',['bun','run','typecheck']),('build',['bun','run','build'])]
for name,cmd in commands:
 with (evidence/(name+'.log')).open('w') as out:
  res=subprocess.run(cmd,cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=180)
 results.append({'check':name,'exit_code':res.returncode});pathlib.Path('/vercel/evidence/build-checks.json').write_text(json.dumps(results,indent=2))
 if res.returncode:print(json.dumps(results));raise SystemExit(res.returncode)
worker={k:env[k] for k in ['MONGEZZ_DEPLOY_TARGET','VITE_SUPABASE_URL','SUPABASE_URL','VITE_SUPABASE_PUBLISHABLE_KEY','SUPABASE_PUBLISHABLE_KEY','VITE_SUPABASE_PROJECT_ID','SUPABASE_PROJECT_ID']}
worker['SUPABASE_SERVICE_ROLE_KEY']=values['SERVICE_ROLE_KEY'];w=pathlib.Path('/vercel/worker.env');w.write_text('\n'.join(k+'='+v for k,v in worker.items())+'\n');os.chmod(w,0o600)
print(json.dumps(results))

