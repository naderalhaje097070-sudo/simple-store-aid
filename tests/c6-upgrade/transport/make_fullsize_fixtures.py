#!/usr/bin/env python3
"""C6 full-size write/rollback fixtures for the ISOLATED lab only (Issue #97, Codex handoff 2026-11-19).

Writes, into OUT_DIR:
  fullsize_fail.sql     exactly 82,065 bytes, ending in COMMIT; every non-SQL byte is inside a checked padding. ONE transaction, ten DO blocks; every block does real writes
                        (CREATE TABLE, CREATE FUNCTION, ALTER COLUMN ... TYPE numeric, INSERT into a ledger-style
                        table) and checks its own padding md5. Block 10 raises C6_FX_FINAL_BLOCK_FAILURE AFTER its
                        own writes, so the error comes after all preceding writes. Expected: zero residue.
  fullsize_ok.sql       exactly 82,065 bytes, the same without the raise. Expected: all ten effects committed.
  check_baseline.sql    read only: the lab's c6_fx footprint (must be all zero before and after).
  check_after_ok.sql    read only: per block, table present, one row id 1, qty = block + 0.5 (numeric), function
                        returns the block number, one ledger row with the block's padding md5; ok = all ten.
  cleanup.sql           drops everything fullsize_ok.sql created (one transaction), then the baseline check.
  MANIFEST.txt          byte length and sha256 of every file.

Every object is named c6_fx_*; nothing else is touched. Never run against production: block 0 refuses any
database that has a supabase_migrations ledger (production has 52 rows; the lab has no ledger).

usage: make_fullsize_fixtures.py OUT_DIR
"""
import hashlib
import os
import sys

TARGET = 82065
out = sys.argv[1]
os.makedirs(out, exist_ok=True)

base = "-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 "
line = base + "x" * (99 - len(base)) + "\n"
assert len(line) == 100
LINES = 73
pad = line * LINES
pmd5 = hashlib.md5(pad.encode()).hexdigest()

GUARD = ("DO $g$ BEGIN IF to_regclass('supabase_migrations.schema_migrations') IS NOT NULL THEN "
         "RAISE EXCEPTION 'C6_FX_REFUSED: a migration ledger exists, this is not the isolated lab'; END IF; END $g$;")


def block(i, fail, bpad=None):
    bpad = pad if bpad is None else bpad
    bmd5 = hashlib.md5(bpad.encode()).hexdigest()
    raise_tail = " RAISE EXCEPTION 'C6_FX_FINAL_BLOCK_FAILURE after block % writes', 10;" if fail and i == 10 else ""
    return (f"DO $b{i}$ DECLARE p text := $p${bpad}$p$; BEGIN\n"
            f"  IF length(p) <> {len(bpad)} OR md5(p) <> '{bmd5}' THEN RAISE EXCEPTION 'C6_FX_ALTERED block {i}: len % md5 %', length(p), md5(p); END IF;\n"
            f"  CREATE TABLE public.c6_fx_t{i}(id int primary key, qty integer not null);\n"
            f"  INSERT INTO public.c6_fx_t{i} VALUES (1, {i});\n"
            f"  ALTER TABLE public.c6_fx_t{i} ALTER COLUMN qty TYPE numeric USING qty::numeric;\n"
            f"  UPDATE public.c6_fx_t{i} SET qty = qty + 0.5;\n"
            f"  CREATE FUNCTION public.c6_fx_f{i}() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT {i}';\n"
            f"  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES ({i}, md5(p));{raise_tail}\n"
            f"END $b{i}$;")


def build(fail):
    # Review fix (#97, Codex 2026-11-19): no unchecked bytes. Block 10's padding absorbs the size filler, so every
    # byte except the fixed SQL text is inside a database-verified checksum, and COMMIT is the last statement.
    def assemble(extra):
        b10 = pad + "-- c6 fixture block 10 filler " + "f" * extra + "\n" if extra >= 0 else pad
        parts = ["BEGIN;", GUARD,
                 "CREATE TABLE public.c6_fx_ledger(block int primary key, pad_md5 text not null, at timestamptz not null default now());"]
        parts += [block(i, fail, b10 if i == 10 else None) for i in range(1, 11)]
        parts.append("COMMIT;")
        return "\n".join(parts) + "\n", b10
    extra = 0
    for _ in range(10):   # the length literal's digit count can shift the size; iterate to the exact target
        body, b10 = assemble(extra)
        diff = TARGET - len(body.encode())
        if diff == 0:
            break
        extra += diff
    assert len(body.encode()) == TARGET and body.endswith("COMMIT;\n"), len(body.encode())
    return body, hashlib.md5(b10.encode()).hexdigest()


FAIL_BODY, _ = build(True)
OK_BODY, B10MD5 = build(False)
files = {
    "fullsize_fail.sql": FAIL_BODY,
    "fullsize_ok.sql": OK_BODY,
    "check_baseline.sql": """-- read only: the c6_fx footprint in the isolated lab. Baseline = all zero.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_exists', to_regclass('supabase_migrations.schema_migrations') is not null,
  'c6_fx_tables', (select count(*) from pg_tables where schemaname = 'public' and tablename like 'c6\\_fx\\_%'),
  'c6_fx_functions', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname like 'c6\\_fx\\_%'),
  'public_tables_total', (select count(*) from pg_tables where schemaname = 'public'),
  'public_functions_total', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace)
) as c6_fx_baseline;
rollback;
""",
    "check_after_ok.sql": f"""-- read only: the ten expected effects of fullsize_ok.sql, by VALUE. Expected: ok = true.
begin transaction read only;
with t as (select i, to_regclass('public.c6_fx_t' || i) rel, to_regprocedure('public.c6_fx_f' || i || '()') fn
           from generate_series(1, 10) i),
v as (select i, rel is not null as table_ok, fn is not null as fn_ok,
             (select data_type = 'numeric' from information_schema.columns where table_schema = 'public'
               and table_name = 'c6_fx_t' || i and column_name = 'qty') as numeric_ok,
             (select count(*) from public.c6_fx_ledger l where l.block = i
               and l.pad_md5 = case when i = 10 then '{B10MD5}' else '{pmd5}' end) = 1 as ledger_ok
      from t),
d as (select i, xpath('/row/n/text()', query_to_xml(format('select count(*) as n from public.c6_fx_t%s', i), false, true, ''))::text[] as n,
             xpath('/row/q/text()', query_to_xml(format('select max(qty) filter (where id = 1) as q from public.c6_fx_t%s', i), false, true, ''))::text[] as q,
             xpath('/row/r/text()', query_to_xml(format('select public.c6_fx_f%s() as r', i), false, true, ''))::text[] as r
      from t where rel is not null and fn is not null),
p as (select v.i, (v.table_ok and v.fn_ok and v.numeric_ok and v.ledger_ok
                  and d.n[1] = '1' and d.q[1]::numeric = v.i + 0.5 and d.r[1]::int = v.i) is true as pass,
             v.table_ok, v.numeric_ok, v.ledger_ok, d.n[1] as n, d.q[1] as q, d.r[1] as r
      from v left join d using (i))
-- Review fix (#97, Codex): each block's predicate is wrapped in IS TRUE, so NULL (a missing row or a NULL
-- function result) fails closed; ok requires ten passing blocks, and per_block.pass is the same boolean.
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from public.c6_fx_ledger),
  'per_block', (select json_agg(json_build_object('block', i, 'pass', pass, 'table', table_ok, 'numeric', numeric_ok,
                 'ledger', ledger_ok, 'rows', n, 'qty', q, 'fn', r) order by i) from p),
  'ok', (select count(*) from public.c6_fx_ledger) = 10 and (select count(*) filter (where pass) from p) = 10
) as c6_fx_after_ok;
rollback;
""",
    "cleanup.sql": "BEGIN;\n" + "".join(f"DROP TABLE public.c6_fx_t{i};\nDROP FUNCTION public.c6_fx_f{i}();\n" for i in range(1, 11))
                   + "DROP TABLE public.c6_fx_ledger;\nCOMMIT;\n",
}
for name, text in files.items():
    open(os.path.join(out, name), "w").write(text)
with open(os.path.join(out, "MANIFEST.txt"), "w") as m:
    for name in sorted(files):
        b = files[name].encode()
        m.write(f"{len(b)} {hashlib.sha256(b).hexdigest()} {name}\n")
print(open(os.path.join(out, "MANIFEST.txt")).read(), end="")
