#!/usr/bin/env python3
"""INVALID_ARGUMENT diagnosis fixtures for the ISOLATED lab only (Issue #97, 2026-11-19). Local generation only.

Every file is synthetic (objects named c6_dx_*), refuses any database that has a migration ledger (production has
one), and ends in a deliberate raise C6_DX_INJECTED <name>, so a working call returns that PostgreSQL error and
leaves zero residue. Expected after every file: check_baseline.sql all zero (it also covers c6_dx_* objects).

Single-factor set (each differs from D1 in exactly one factor, small size, one write block):
  D1  guard + one block with the full write content (table, insert, ALTER TYPE, UPDATE, CREATE FUNCTION, ledger)
  D2  D1 without the CREATE FUNCTION line
  D3  D1 without the guard block
Controlled comparison (proposed, NOT for the cloud without owner approval; generated so the factors are pinned):
  M2  82,065 bytes, ONE write block (all padding in it), multi-statement BEGIN..COMMIT   -> size + writes, 1 block
  M3  small (~8 KB), TEN write blocks, multi-statement                                 -> block count, small size
  M4  82,065 bytes, TEN blocks with NO writes (checksum only), multi-statement          -> size + 10 blocks, no writes
  M5  82,065 bytes, TEN write blocks inside ONE outer DO statement (no BEGIN/COMMIT)    -> statement count / shape
  (M1 = tests/c6-upgrade/transport/fullsize/fullsize_fail.sql: 82,065 B, ten write blocks, multi-statement.)

usage: make_diag_fixtures.py OUT_DIR
"""
import hashlib
import os
import sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
FULL = 82065
base = "-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 "
LINE = base + "x" * (99 - len(base)) + "\n"
assert len(LINE) == 100
GUARD = ("DO $g$ BEGIN IF to_regclass('supabase_migrations.schema_migrations') IS NOT NULL THEN "
         "RAISE EXCEPTION 'C6_DX_REFUSED: a migration ledger exists, this is not the isolated lab'; END IF; END $g$;")
LEDGER = "CREATE TABLE public.c6_dx_ledger(block int primary key, pad_md5 text not null);"


def body_stmts(i, writes, func):
    if not writes:
        return ""
    s = (f"  CREATE TABLE public.c6_dx_t{i}(id int primary key, qty integer not null);\n"
         f"  INSERT INTO public.c6_dx_t{i} VALUES (1, {i});\n"
         f"  ALTER TABLE public.c6_dx_t{i} ALTER COLUMN qty TYPE numeric USING qty::numeric;\n"
         f"  UPDATE public.c6_dx_t{i} SET qty = qty + 0.5;\n")
    if func:
        s += f"  CREATE FUNCTION public.c6_dx_f{i}() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT {i}';\n"
    s += f"  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES ({i}, md5(p));\n"
    return s


def check(i, pad):
    return (f"  IF length(p) <> {len(pad)} OR md5(p) <> '{hashlib.md5(pad.encode()).hexdigest()}' THEN "
            f"RAISE EXCEPTION 'C6_DX_ALTERED block {i}: len % md5 %', length(p), md5(p); END IF;\n")


def do_block(i, pad, writes, func):
    return (f"DO $b{i}$ DECLARE p text := $p${pad}$p$; BEGIN\n" + check(i, pad) + body_stmts(i, writes, func)
            + f"END $b{i}$;")


def inner_block(i, pad, writes, func):   # for M5: a nested PL/pgSQL block inside one outer DO
    return (f"  DECLARE p text := $p{i}${pad}$p{i}$; BEGIN\n" + check(i, pad).replace("\n  ", "\n    ")
            + body_stmts(i, writes, func) + f"  END;\n")


def multi(name, nblocks, lines, writes=True, func=True, guard=True, target=None):
    def assemble(extra):
        parts = ["BEGIN;"] + ([GUARD] if guard else []) + ([LEDGER] if writes else [])
        for i in range(1, nblocks + 1):
            pad = LINE * lines + (("-- c6 diag filler " + "f" * extra + "\n") if (target and i == nblocks) else "")
            parts.append(do_block(i, pad, writes, func))
        parts.append(f"DO $x$ BEGIN RAISE EXCEPTION 'C6_DX_INJECTED {name}'; END $x$;")
        parts.append("COMMIT;")
        return "\n".join(parts) + "\n"
    return fit(assemble, target)


def single_do(name, nblocks, lines, target):
    def assemble(extra):
        s = "DO $outer$ BEGIN\n"
        s += ("  IF to_regclass('supabase_migrations.schema_migrations') IS NOT NULL THEN "
              "RAISE EXCEPTION 'C6_DX_REFUSED: a migration ledger exists, this is not the isolated lab'; END IF;\n")
        s += "  " + LEDGER.replace(";", "") + ";\n"
        for i in range(1, nblocks + 1):
            pad = LINE * lines + (("-- c6 diag filler " + "f" * extra + "\n") if i == nblocks else "")
            s += inner_block(i, pad, True, True)
        s += f"  RAISE EXCEPTION 'C6_DX_INJECTED {name}';\nEND $outer$;\n"
        return s
    return fit(assemble, target)


def fit(assemble, target):
    if not target:
        return assemble(0)
    extra = 0
    for _ in range(10):
        t = assemble(extra)
        d = target - len(t.encode())
        if d == 0:
            return t
        extra += d
    raise SystemExit("could not fit size")


files = {
    "D1.sql": multi("D1", 1, 20),
    "D2.sql": multi("D2", 1, 20, func=False),
    "D3.sql": multi("D3", 1, 20, guard=False),
    "M2.sql": multi("M2", 1, 790, target=FULL),
    "M3.sql": multi("M3", 10, 5),
    "M4.sql": multi("M4", 10, 79, writes=False, target=FULL),
    "M5.sql": single_do("M5", 10, 73, FULL),
    "check_baseline_dx.sql": """-- read only: c6_dx_* and c6_fx_* footprint in the isolated lab. Expected: all zero.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_exists', to_regclass('supabase_migrations.schema_migrations') is not null,
  'c6_dx_tables', (select count(*) from pg_tables where schemaname = 'public' and tablename like 'c6\\_dx\\_%'),
  'c6_dx_functions', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname like 'c6\\_dx\\_%'),
  'public_tables_total', (select count(*) from pg_tables where schemaname = 'public'),
  'public_functions_total', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace)
) as c6_dx_baseline;
rollback;
""",
}
for n, t in files.items():
    open(os.path.join(out, n), "w").write(t)
with open(os.path.join(out, "MANIFEST.txt"), "w") as m:
    for n in sorted(files):
        b = files[n].encode()
        m.write(f"{len(b)} {hashlib.sha256(b).hexdigest()} {n}\n")
print(open(os.path.join(out, "MANIFEST.txt")).read(), end="")
