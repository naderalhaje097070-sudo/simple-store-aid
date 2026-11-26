-- C7 final: read-only count of courier order states that F1 (20261120140000) treats differently.
-- Review-only candidate. Running it on any database other than a disposable lab needs the owner's approval.
-- Returns aggregate counts only: no identifiers, names, amounts or row contents.
--   pending_with_payment            pending courier orders with paid > 0. Their only delivery-dialog action
--                                   (delivered_full, collected = total) is refused after F1 when total - paid < total
--   none_with_payment               delivered_none courier orders with paid > 0 (no dialog action today)
--   custody_over_remaining          courier orders whose stored custody already exceeds total - paid; F1 does not
--                                   change stored balances, but later transitions on them are refused
--   courier_orders                  all courier orders, for scale
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'courier_orders', count(*),
  'pending_with_payment', count(*) filter (where courier_state = 'pending' and paid > 0),
  'none_with_payment', count(*) filter (where courier_state = 'delivered_none' and paid > 0),
  'custody_over_remaining', count(*) filter (where coalesce(collected_by_courier, 0) > greatest(total - paid, 0))
) as c7_courier_state_counts
from public.orders
where delivery = 'courier';
rollback;
