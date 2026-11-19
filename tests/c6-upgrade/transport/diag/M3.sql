BEGIN;
DO $g$ BEGIN IF to_regclass('supabase_migrations.schema_migrations') IS NOT NULL THEN RAISE EXCEPTION 'C6_DX_REFUSED: a migration ledger exists, this is not the isolated lab'; END IF; END $g$;
CREATE TABLE public.c6_dx_ledger(block int primary key, pad_md5 text not null);
DO $b1$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 1: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t1(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t1 VALUES (1, 1);
  ALTER TABLE public.c6_dx_t1 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t1 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f1() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 1';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (1, md5(p));
END $b1$;
DO $b2$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 2: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t2(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t2 VALUES (1, 2);
  ALTER TABLE public.c6_dx_t2 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t2 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f2() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 2';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (2, md5(p));
END $b2$;
DO $b3$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 3: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t3(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t3 VALUES (1, 3);
  ALTER TABLE public.c6_dx_t3 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t3 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f3() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 3';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (3, md5(p));
END $b3$;
DO $b4$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 4: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t4(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t4 VALUES (1, 4);
  ALTER TABLE public.c6_dx_t4 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t4 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f4() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 4';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (4, md5(p));
END $b4$;
DO $b5$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 5: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t5(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t5 VALUES (1, 5);
  ALTER TABLE public.c6_dx_t5 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t5 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f5() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 5';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (5, md5(p));
END $b5$;
DO $b6$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 6: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t6(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t6 VALUES (1, 6);
  ALTER TABLE public.c6_dx_t6 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t6 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f6() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 6';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (6, md5(p));
END $b6$;
DO $b7$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 7: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t7(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t7 VALUES (1, 7);
  ALTER TABLE public.c6_dx_t7 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t7 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f7() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 7';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (7, md5(p));
END $b7$;
DO $b8$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 8: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t8(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t8 VALUES (1, 8);
  ALTER TABLE public.c6_dx_t8 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t8 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f8() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 8';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (8, md5(p));
END $b8$;
DO $b9$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 9: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t9(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t9 VALUES (1, 9);
  ALTER TABLE public.c6_dx_t9 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t9 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f9() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 9';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (9, md5(p));
END $b9$;
DO $b10$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 500 OR md5(p) <> '0f1ca21ac319b5140ca5540d87a02669' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 10: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t10(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t10 VALUES (1, 10);
  ALTER TABLE public.c6_dx_t10 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t10 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f10() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 10';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (10, md5(p));
END $b10$;
DO $x$ BEGIN RAISE EXCEPTION 'C6_DX_INJECTED M3'; END $x$;
COMMIT;
