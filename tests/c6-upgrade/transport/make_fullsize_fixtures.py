#!/usr/bin/env python3
"""C6 full-size write/rollback fixtures for the ISOLATED lab only (Issue #97, Codex handoff 2026-11-19).

Writes, into OUT_DIR:
  fullsize_fail.sql     exactly 82,065 bytes. ONE transaction, ten DO blocks; every block does real writes
                        (CREATE TABLE, CREATE FUNCTION, ALTER COLUMN ... TYPE numeric, INSERT into a ledger-style
                        table) and checks its own padding md5. Block 10 raises C6_FX_FINAL_BLOCK_FAILURE AFTER its
                        own writes, so the error comes after all preceding writes. Expected: zero residue.
  fullsize_ok.sql       exactly 82,065 bytes, the same without the raise. Expected: all ten effects committed.
  check_baseline.sql    read only: the lab's c6_fx footprint (must be all zero before and after).
  check_after_ok.sql    read only: the ten expected effects, exactly.
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


def block(i, fail):
    raise_tail = " RAISE EXCEPTION 'C6_FX_FINAL_BLOCK_FAILURE after block % writes', 10;" if fail and i == 10 else ""
    return (f"DO $b{i}$ DECLARE p text := $p${pad}$p$; BEGIN\n"
            f"  IF length(p) <> {len(pad)} OR md5(p) <> '{pmd5}' THEN RAISE EXCEPTION 'C6_FX_ALTERED block {i}: len % md5 %', length(p), md5(p); END IF;\n"
            f"  CREATE TABLE public.c6_fx_t{i}(id int primary key, qty integer not null);\n"
            f"  INSERT INTO public.c6_fx_t{i} VALUES (1, {i});\n"
            f"  ALTER TABLE public.c6_fx_t{i} ALTER COLUMN qty TYPE numeric USING qty::numeric;\n"
            f"  UPDATE public.c6_fx_t{i} SET qty = qty + 0.5;\n"
            f"  CREATE FUNCTION public.c6_fx_f{i}() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT {i}';\n"
            f"  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES ({i}, md5(p));{raise_tail}\n"
            f"END $b{i}$;")


def build(fail):
    parts = ["BEGIN;", GUARD,
             "CREATE TABLE public.c6_fx_ledger(block int primary key, pad_md5 text not null, at timestamptz not null default now());"]
    parts += [block(i, fail) for i in range(1, 11)]
    parts.append("COMMIT;")
    body = "\n".join(parts) + "\n"
    filler = TARGET - len(body.encode())
    assert filler > 4, filler
    # exact size: a trailing comment of the remaining bytes (after COMMIT, executed as nothing)
    body += "--" + "f" * (filler - 3) + "\n"
    assert len(body.encode()) == TARGET
    return body


files = {
    "fullsize_fail.sql": build(True),
    "fullsize_ok.sql": build(False),
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
    "check_after_ok.sql": f"""-- read only: the ten expected effects of fullsize_ok.sql. Expected: ok = true.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'ledger_rows', (select count(*) from public.c6_fx_ledger),
  'ledger_md5_ok', (select count(*) from public.c6_fx_ledger where pad_md5 = '{pmd5}'),
  'tables', (select count(*) from pg_tables where schemaname = 'public' and tablename ~ '^c6_fx_t([1-9]|10)$'),
  'numeric_columns', (select count(*) from information_schema.columns where table_schema = 'public'
                      and table_name ~ '^c6_fx_t([1-9]|10)$' and column_name = 'qty' and data_type = 'numeric'),
  'functions', (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname ~ '^c6_fx_f([1-9]|10)$'),
  'ok', (select count(*) from public.c6_fx_ledger) = 10
        and (select count(*) from public.c6_fx_ledger where pad_md5 = '{pmd5}') = 10
        and (select count(*) from pg_tables where schemaname = 'public' and tablename ~ '^c6_fx_t([1-9]|10)$') = 10
        and (select count(*) from information_schema.columns where table_schema = 'public'
             and table_name ~ '^c6_fx_t([1-9]|10)$' and column_name = 'qty' and data_type = 'numeric') = 10
        and (select count(*) from pg_proc where pronamespace = 'public'::regnamespace and proname ~ '^c6_fx_f([1-9]|10)$') = 10
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
