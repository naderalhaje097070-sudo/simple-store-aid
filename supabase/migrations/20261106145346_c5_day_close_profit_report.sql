-- C5-PROFIT-BASIS-01: additive reporting only; legacy snapshots stay unchanged.
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
