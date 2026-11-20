BEGIN;
CREATE TABLE public.c6_dx_ledger(block int primary key, pad_md5 text not null);
DO $b1$ DECLARE p text := $p$-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
-- c6 diag padding: the quick brown fox jumps over the lazy dog 0123456789 xxxxxxxxxxxxxxxxxxxxxxxx
$p$; BEGIN
  IF length(p) <> 2000 OR md5(p) <> '89cb61b13bee7171b00403cd46c08aba' THEN RAISE EXCEPTION 'C6_DX_ALTERED block 1: len % md5 %', length(p), md5(p); END IF;
  CREATE TABLE public.c6_dx_t1(id int primary key, qty integer not null);
  INSERT INTO public.c6_dx_t1 VALUES (1, 1);
  ALTER TABLE public.c6_dx_t1 ALTER COLUMN qty TYPE numeric USING qty::numeric;
  UPDATE public.c6_dx_t1 SET qty = qty + 0.5;
  CREATE FUNCTION public.c6_dx_f1() RETURNS int LANGUAGE sql IMMUTABLE AS 'SELECT 1';
  INSERT INTO public.c6_dx_ledger(block, pad_md5) VALUES (1, md5(p));
END $b1$;
DO $x$ BEGIN RAISE EXCEPTION 'C6_DX_INJECTED D3'; END $x$;
COMMIT;
