import pathlib,json,hashlib,shlex,re,tarfile,io,base64,os,datetime
root=pathlib.Path('/vercel'); ev=root/'evidence';out=root/'safe-evidence';out.mkdir(exist_ok=True)
m=json.loads((root/'remote-manifest.json').read_text());bad=[]
for e in m['files']:
 p=root/'candidate'/e['path'];data=p.read_bytes()
 h=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if h!=e['sha']:bad.append(e['path'])
(out/'source-match.json').write_text(json.dumps({'source_sha':m['source_sha'],'tree_sha':m['tree_sha'],'files':len(m['files']),'mismatches':bad},indent=2)+'\n')
values={}
for line in (root/'stack.env').read_text().splitlines():
 if '=' in line:
  k,v=line.split('=',1);values[k]=shlex.split(v)[0] if v else ''
fixture=json.loads((root/'auth-fixture.json').read_text())
redactions=[v for k,v in values.items() if (('KEY' in k or k=='DB_URL') and v)]+list(fixture.values())
files=['native-start.log','fresh-inventory.log','owner-trigger-check.log','auth-tenant-probe.json','frozen-install.log','gate4.log','auth-preflight.log','unit.log','typecheck.log','build.log','build-checks.json','browser-install.log','emulator-initial-bunx-failure.log','emulator.log','auth-ui.log','auth-ui-result.json','final-inventory.json']
for name in files:
 p=ev/name
 if not p.exists():continue
 s=p.read_text()
 for value in sorted(redactions,key=len,reverse=True):s=s.replace(value,'[REDACTED]')
 s=re.sub(r'(?i)(postgres(?:ql)?://[^:\s]+:)[^@\s]+(@)',r'\1[REDACTED]\2',s)
 s=re.sub(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+','[REDACTED_JWT]',s)
 s=re.sub(r'isolation-[ab]-[a-f0-9]+@example\.test','[REDACTED_FIXTURE_EMAIL]',s)
 assert all(value not in s for value in redactions)
 (out/name).write_text(s)
for p in pathlib.Path('/tmp/mongezz-auth-smoke').glob('*.png'):(out/p.name).write_bytes(p.read_bytes())
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir()}
(out/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w:gz') as archive:
 for p in sorted(out.iterdir()):archive.add(p,arcname=p.name)
data=buffer.getvalue();(root/'safe-evidence.tar.gz').write_bytes(data)
chunks=root/'evidence-chunks';chunks.mkdir(exist_ok=True)
for i,start in enumerate(range(0,len(data),1350)):(chunks/(str(i)+'.part')).write_bytes(data[start:start+1350])
print(json.dumps({'archive_bytes':len(data),'archive_sha256':hashlib.sha256(data).hexdigest(),'chunks':(len(data)+1349)//1350,'source_mismatches':bad,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}))

