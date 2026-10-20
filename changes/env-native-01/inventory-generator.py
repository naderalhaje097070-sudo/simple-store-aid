import argparse
import hashlib
import json
import pathlib
import re

parser = argparse.ArgumentParser(description='Pinned source discovery; not a SQL catalog replay')
parser.add_argument('--source-root', type=pathlib.Path, required=True)
parser.add_argument('--tree', type=pathlib.Path, required=True)
parser.add_argument('--output', type=pathlib.Path, required=True)
args = parser.parse_args()
source = args.source_root
tree = {x['path']: x for x in json.loads(args.tree.read_text())['tree'] if x['type'] == 'blob'}
expected = {p for p in tree if p.startswith('supabase/migrations/') and p.endswith('.sql')}
actual = {str(p.relative_to(source)) for p in (source / 'supabase/migrations').glob('*.sql')}
if actual != expected:
    raise ValueError('Incomplete or extra migration snapshot')
records = []
events = []
calls = []
for p in sorted((source / 'supabase/migrations').glob('*.sql')):
    text = p.read_text()
    path = str(p.relative_to(source))
    raw = p.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != tree[path]['sha']:
        raise ValueError('Migration source hash mismatch: ' + path)
    records.append({'path': path, 'git_blob': blob})
    # Lexical discovery only: includes historical/dynamic declarations, not a catalog replay.
    for m in re.finditer(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+public\.([a-z_][a-z_0-9]*)\s*\(', text, re.I):
        tail = text[m.start():]
        body = re.search(r'\bAS\s+(\$[a-z_0-9]*\$)(.*?)\1', tail, re.I | re.S)
        if not body:
            raise ValueError('Unrecognized function body: ' + path)
        declaration = tail[:body.end()]
        events.append({'kind': 'function_definition', 'name': m[1], 'path': path,
                       'line': text[:m.start()].count('\n') + 1,
                       'security_definer': bool(re.search(r'SECURITY\s+DEFINER', declaration, re.I)),
                       'calls': sorted(set(re.findall(r'public\.([a-z_][a-z_0-9]*)\s*\(', body[2], re.I))),
                       'auth_uid': 'auth.uid()' in body[2],
                       'lifecycle_state_reference': any(s in body[2].lower() for s in ['banned_until', 'auth.sessions', 'disabled'])})
    for m in re.finditer(r'(CREATE|DROP)\s+POLICY\s+(?:IF\s+EXISTS\s+)?"([^"]+)"\s+ON\s+public\.([a-z_0-9]+)', text, re.I):
        snippet = text[m.start():].split(';', 1)[0]
        events.append({'kind': 'policy_' + m[1].lower(), 'name': m[2], 'table': m[3],
                       'path': path, 'line': text[:m.start()].count('\n') + 1,
                       'calls': sorted(set(re.findall(r'public\.([a-z_][a-z_0-9]*)\s*\(', snippet, re.I))),
                       'auth_uid': 'auth.uid()' in snippet, 'statement': snippet})
    for m in re.finditer(r'(GRANT|REVOKE)\s+[^;]+;', text, re.I):
        events.append({'kind': 'privilege_statement', 'path': path,
                       'line': text[:m.start()].count('\n') + 1, 'statement': m[0]})
    for m in re.finditer(r'DROP\s+FUNCTION\s+(?:IF\s+EXISTS\s+)?public\.([a-z_0-9]+)\s*\([^;]+;', text, re.I):
        events.append({'kind': 'function_drop', 'name': m[1], 'path': path,
                       'line': text[:m.start()].count('\n') + 1, 'statement': m[0]})
expected_app = {p for p in tree if p.startswith('src/') and pathlib.Path(p).suffix in ('.ts', '.tsx')}
actual_app = {str(p.relative_to(source)) for p in (source / 'src').rglob('*') if p.is_file() and p.suffix in ('.ts', '.tsx')}
if expected_app != actual_app:
    raise ValueError('Incomplete or extra application snapshot')
for p in sorted((source / 'src').rglob('*')):
    if not p.is_file() or p.suffix not in ('.ts', '.tsx'): continue
    raw = p.read_bytes()
    path = str(p.relative_to(source))
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != tree[path]['sha']:
        raise ValueError('Application source hash mismatch: ' + path)
    for n, line in enumerate(p.read_text().splitlines(), 1):
        if re.search(r'\.rpc\(|requireSupabaseAuth|getClaims|getUser|\.from\(', line):
            calls.append({'path': str(p.relative_to(source)), 'line': n, 'text': line.strip()})
out = args.output
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'source_sha': 'b9aa56bc3bb30948d95961c06fd493dfb866f476',
    'method': 'source lexical discovery; historical and dynamic events retained; not effective pg_catalog state',
    'limitations': ['Not a SQL parser', 'No function overload resolution', 'Dynamic SQL strings require catalog reconciliation', 'No runtime authorization proof'],
    'migration_files': records, 'events': events, 'application_callsites': calls}, indent=2) + '\n')
print(json.dumps({'migrations': len(records), 'events': len(events), 'callsites': len(calls),
                  'functions': sorted(set(e['name'] for e in events if e['kind'] == 'function_definition'))}))
