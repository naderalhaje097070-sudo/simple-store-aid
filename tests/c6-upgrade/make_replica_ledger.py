#!/usr/bin/env python3
"""Local only. Give the replica ledger statement text, so the content guard can be tested.

- 47 production entries have a repository file with the same content (version_map.tsv): their statements
  are set to that file's text, and the md5 MUST equal production's recorded md5 (checked here).
- 5 production entries have no repository text: they get a local placeholder, so their md5 differs from
  production. Consequence: the PRODUCTION apply files must refuse the replica (negative control), and a
  TEST expected-ledger file (same as production except these 5 md5) is written for the acceptance tests.

usage: make_replica_ledger.py REPO_ROOT OUT_SQL OUT_EXPECTED_TEST
"""
import hashlib
import subprocess
import sys

root, out_sql, out_exp = sys.argv[1:4]
prod = [l.split() for l in open(f'{root}/docs/reviews/c6-ledger/prod_ledger_2026-11-16.txt') if l.strip()]
vmap = {}
for line in open(f'{root}/docs/reviews/c6-ledger/version_map.tsv').read().splitlines()[1:]:
    v, m, files, status = line.split('\t')
    vmap[v] = (m, files.split(',')[0] if files else '', status)

sql, exp, matched, placeholder = ['begin;'], [], 0, []
for v, m in prod:
    rm, f, status = vmap[v]
    assert rm == m, v
    if status == 'no_repo_file':
        text = f'-- local replica placeholder for production ledger entry {v} (text not in the repository)'
        placeholder.append(v)
    else:
        text = subprocess.run(['git', '-C', root, 'show', f'183dc50:supabase/migrations/{f}'],
                              capture_output=True, check=True).stdout.decode()
        assert hashlib.md5(text.encode()).hexdigest() == m, f'content md5 differs from production for {v}'
        matched += 1
    tag = '$t' + hashlib.sha1(text.encode()).hexdigest()[:8] + '$'
    sql.append(f"update supabase_migrations.schema_migrations set statements = ARRAY[{tag}{text}{tag}] where version = '{v}';")
    exp.append(f'{v} {hashlib.md5(text.encode()).hexdigest()}')
sql.append('commit;')
open(out_sql, 'w').write('\n'.join(sql) + '\n')
open(out_exp, 'w').write('\n'.join(exp) + '\n')
print(f'matched_production_md5={matched} placeholders={len(placeholder)} {",".join(placeholder)}')
