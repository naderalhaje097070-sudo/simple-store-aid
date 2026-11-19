-- stage C6
DO $stage$
DECLARE src text; body text;
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  PERFORM set_config('lock_timeout','5s', true);
  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations) <> '51cfbefdfef5431f6b838a3f41014ef3' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before 20261106145346: expected exactly 57 known versions'; END IF;
  src := $src5636a42b$-- C5-PROFIT-BASIS-01: additive reporting only; legacy snapshots stay unchanged.
BEGIN;
SET LOCAL lock_timeout = '5s';

CREATE VIEW public.day_close_profit_report
WITH (security_invoker = true)
AS
SELECT
  dc.id, dc.tenant_id, dc.closed_for,
  dc.sales, dc.collected, dc.expenses,
  dc.realized_profit,
  dc.realized_profit AS realized_margin_before_expenses,
  dc.realized_profit - dc.expenses AS realized_net_profit,
  dc.customer_debts, dc.unsettled_custody,
  dc.note, dc.created_at
FROM public.day_closes AS dc;

-- Simple views can be updatable. Expose only SELECT, using the caller's RLS.
REVOKE ALL ON TABLE public.day_close_profit_report FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.day_close_profit_report TO authenticated;

COMMENT ON VIEW public.day_close_profit_report IS
  'Recorded collection-based closing margin and net after recorded expenses; legacy values and history unchanged.';
COMMENT ON COLUMN public.day_close_profit_report.realized_profit IS
  'Legacy before-expense payment-weighted margin; retained for compatibility.';
COMMENT ON COLUMN public.day_close_profit_report.realized_net_profit IS
  'Saved before-expense margin minus saved expenses once; not a reconstruction or audit of historical inputs.';

COMMIT;
$src5636a42b$;
  IF md5(src) <> '1d313800b3bbaa1b1ef0c7b3e9517269' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH 20261106145346_c5_day_close_profit_report'; END IF;
  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '20261106145346') THEN RAISE EXCEPTION 'ALREADY_APPLIED 20261106145346'; END IF;
  body := regexp_replace(regexp_replace(src, E'(^|\n)BEGIN;\n', E'\\1'), E'\nCOMMIT;\n*$', E'\n');
  EXECUTE body;
  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('20261106145346', 'c5_day_close_profit_report', ARRAY[src], 'claude-c6');
END
$stage$;
