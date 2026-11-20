#!/usr/bin/env python3
"""Self-test for the platform-owned COPY filter in rehearse.sh (#99, Graphify P2). Synthetic input only: no database.
Runs the filter text extracted from rehearse.sh itself on a dump that mixes quoted and unquoted COPY headers.
Pass: only the COPY blocks of the schemas storage and supabase_functions are removed, in either form; every other
block, including look-alike schema names and an application table called "storage", is kept byte for byte.
usage: python3 -I selftest_copy_filter.py
"""
import subprocess, sys, tempfile
from pathlib import Path
here = Path(__file__).resolve().parent
src = (here / 'rehearse.sh').read_text()
code = src.split("<<'EOF'\n", 1)[1].split('\nEOF\n', 1)[0]
def block(header, rows):
    return [f'{header} FROM stdin;'] + rows + ['\\.', '']
dropped = [('COPY "storage"."buckets" ("id")', ['b1']), ('COPY storage.objects ("id")', ['o1']),
           ('COPY "supabase_functions"."hooks" ("id")', ['h1']), ('COPY supabase_functions.migrations ("v")', ['m1'])]
kept = [('COPY "public"."orders" ("id")', ['1']), ('COPY public.order_items (id)', ['2']),
        ('COPY "storage_archive"."files" ("id")', ['3']), ('COPY storagex.t (id)', ['4']),
        ('COPY "supabase_functions2"."x" ("id")', ['5']), ('COPY public."storage" ("id")', ['6']),
        ('COPY "auth"."users" ("id")', ['7'])]
lines = ['-- synthetic dump']
for h, r in dropped[:2] + kept[:3] + dropped[2:] + kept[3:]:
    lines += block(h, r)
with tempfile.TemporaryDirectory() as t:
    i, o = Path(t) / 'data.sql', Path(t) / 'data_app.sql'
    i.write_text('\n'.join(lines))
    subprocess.run([sys.executable, '-I', '-c', code, str(i), str(o)], check=True)
    out = o.read_text().split('\n')
ok = True
for h, r in dropped:
    good = h + ' FROM stdin;' not in out and r[0] not in out
    print(f"removed {h.split(' (')[0]}: {'PASS' if good else 'FAIL'}"); ok &= good
for h, r in kept:
    i0 = out.index(h + ' FROM stdin;') if h + ' FROM stdin;' in out else -1
    good = i0 >= 0 and out[i0 + 1:i0 + 3] == [r[0], '\\.']
    print(f"kept    {h.split(' (')[0]}: {'PASS' if good else 'FAIL'}"); ok &= good
sys.exit(0 if ok else 1)
