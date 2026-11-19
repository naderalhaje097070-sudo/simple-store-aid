BEGIN;
DO $g$ BEGIN IF to_regclass('supabase_migrations.schema_migrations') IS NOT NULL THEN RAISE EXCEPTION 'C6_FX_REFUSED: a migration ledger exists, this is not the isolated lab'; END IF; END $g$;
CREATE TABLE public.c6_fx_ledger(block int primary key, pad_md5 text not null, at timestamptz not null default now());
DO $b1$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 1: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t1(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t1 VALUES (1, 1);
  ALTER TABLE public.c6_fx_t1 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t1 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f1() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 1';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (1, md5(p));
END $b1$;
DO $b2$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 2: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t2(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t2 VALUES (1, 2);
  ALTER TABLE public.c6_fx_t2 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t2 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f2() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 2';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (2, md5(p));
END $b2$;
DO $b3$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 3: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t3(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t3 VALUES (1, 3);
  ALTER TABLE public.c6_fx_t3 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t3 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f3() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 3';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (3, md5(p));
END $b3$;
DO $b4$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 4: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t4(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t4 VALUES (1, 4);
  ALTER TABLE public.c6_fx_t4 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t4 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f4() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 4';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (4, md5(p));
END $b4$;
DO $b5$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 5: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t5(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t5 VALUES (1, 5);
  ALTER TABLE public.c6_fx_t5 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t5 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f5() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 5';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (5, md5(p));
END $b5$;
DO $b6$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 6: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t6(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t6 VALUES (1, 6);
  ALTER TABLE public.c6_fx_t6 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t6 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f6() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 6';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (6, md5(p));
END $b6$;
DO $b7$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 7: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t7(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t7 VALUES (1, 7);
  ALTER TABLE public.c6_fx_t7 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t7 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f7() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 7';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (7, md5(p));
END $b7$;
DO $b8$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 8: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t8(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t8 VALUES (1, 8);
  ALTER TABLE public.c6_fx_t8 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t8 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f8() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 8';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (8, md5(p));
END $b8$;
DO $b9$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 7300 OR md5(p) <> '5249767b6f691d5632bafe479d95001c' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 9: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t9(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t9 VALUES (1, 9);
  ALTER TABLE public.c6_fx_t9 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t9 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f9() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 9';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (9, md5(p));
END $b9$;
DO $b10$ DECLARE p text := $p$-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxx
-- c6 fixture block 10 filler ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
$p$; BEGIN
  IF length(p) <> 9877 OR md5(p) <> '2a7963eae3f17b4375ad37e2df5164fa' THEN RAISE EXCEPTION 'C6_FX_ALTERED block 10: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_fx_t10(id int primary key, qty integer not null);
  INSERT INTO public.c6_fx_t10 VALUES (1, 10);
  ALTER TABLE public.c6_fx_t10 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_fx_t10 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_fx_f10() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 10';
  INSERT INTO public.c6_fx_ledger(block, pad_md5) VALUES (10, md5(p)); RAISE EXCEPTION 'C6_FX_FINAL_BLOCK_FAILURE after block % writes', 10;
END $b10$;
COMMIT;
