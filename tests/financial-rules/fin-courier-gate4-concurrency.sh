#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:?PGHOST required}"
: "${PGPORT:?PGPORT required}"
: "${PGUSER:?PGUSER required}"
: "${PGDATABASE:?PGDATABASE required}"
: "${GATE4_UID:?GATE4_UID required}"
: "${GATE4_TID:?GATE4_TID required}"

PSQL=(psql -v ON_ERROR_STOP=1 -Atq)
CLAIMS="{\"sub\":\"${GATE4_UID}\",\"role\":\"authenticated\"}"

has_v2="$(${PSQL[@]} -c "select (to_regprocedure('public.create_sale_with_items_v2(uuid,public.delivery_kind,uuid,numeric,public.payment_method,jsonb,public.courier_state)') is not null and to_regprocedure('public.update_courier_outcome_v2(uuid,public.courier_state,numeric,uuid)') is not null)::text")"
if [[ "$has_v2" != "true" && "$has_v2" != "t" ]]; then
  echo "GATE4_CONCURRENCY_EXPECTED_RED: PR-A v2 RPCs are missing" >&2
  exit 3
fi

sql_auth_prefix="select set_config('request.jwt.claims', '${CLAIMS}'::text, false);"

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
${PSQL[@]} <<SQL
${sql_auth_prefix}
insert into public.products(id, tenant_id, name, price, cost, stock, is_active)
values
 ('dd990001-6000-4000-8000-000000000001', '${GATE4_TID}', 'G4-CONC-STOCK1', 100, 60, 1, true),
 ('dd990002-6000-4000-8000-000000000002', '${GATE4_TID}', 'G4-CONC-TRANSITION', 100, 60, 5, true),
 ('dd990003-6000-4000-8000-000000000003', '${GATE4_TID}', 'G4-CONC-SETTLE', 100, 60, 5, true)
on conflict (id) do nothing;
insert into public.customers(id, tenant_id, name)
values ('ee990001-6000-4000-8000-000000000001', '${GATE4_TID}', 'G4-CONC-CUSTOMER')
on conflict (id) do nothing;
insert into public.couriers(id, tenant_id, name, is_active)
values ('ff990001-6000-4000-8000-000000000001', '${GATE4_TID}', 'G4-CONC-COURIER', true)
on conflict (id) do nothing;
SQL

# ----------------------------------------------------------------------
# E1: two concurrent creates compete for stock=1. Exactly one succeeds.
# ----------------------------------------------------------------------
rm -f /tmp/g4-e1-a.log /tmp/g4-e1-b.log
set +e
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.create_sale_with_items_v2(null,'direct'::delivery_kind,null,100,'cash'::payment_method,'[{\"productId\":\"dd990001-6000-4000-8000-000000000001\",\"qty\":1}]'::jsonb,null::courier_state);" \
    > /tmp/g4-e1-a.log 2>&1
) & p1=$!
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.create_sale_with_items_v2(null,'direct'::delivery_kind,null,100,'cash'::payment_method,'[{\"productId\":\"dd990001-6000-4000-8000-000000000001\",\"qty\":1}]'::jsonb,null::courier_state);" \
    > /tmp/g4-e1-b.log 2>&1
) & p2=$!
wait "$p1"; r1=$?
wait "$p2"; r2=$?
set -e

successes=0
[[ $r1 -eq 0 ]] && successes=$((successes+1))
[[ $r2 -eq 0 ]] && successes=$((successes+1))
if [[ $successes -ne 1 ]]; then
  echo "E1 FAIL: expected one success, got r1=$r1 r2=$r2" >&2
  cat /tmp/g4-e1-a.log /tmp/g4-e1-b.log >&2
  exit 1
fi
if [[ $r1 -ne 0 ]] && ! grep -q 'insufficient_stock' /tmp/g4-e1-a.log; then
  echo "E1 FAIL: losing request did not fail insufficient_stock" >&2; cat /tmp/g4-e1-a.log >&2; exit 1
fi
if [[ $r2 -ne 0 ]] && ! grep -q 'insufficient_stock' /tmp/g4-e1-b.log; then
  echo "E1 FAIL: losing request did not fail insufficient_stock" >&2; cat /tmp/g4-e1-b.log >&2; exit 1
fi
read -r e1_stock e1_orders < <(${PSQL[@]} -F' ' -c "select p.stock, count(distinct o.id) from products p left join order_items oi on oi.product_id=p.id left join orders o on o.id=oi.order_id where p.id='dd990001-6000-4000-8000-000000000001' group by p.stock")
if [[ "$e1_stock" != "0" || "$e1_orders" != "1" ]]; then
  echo "E1 FAIL: stock=$e1_stock orders=$e1_orders" >&2
  exit 1
fi
echo "E1 OK: concurrent stock=1 produced exactly one sale"

# Helper: create a pending courier order and print its id.
create_pending() {
  local product_id="$1"
  local customer_sql="$2"
  ${PSQL[@]} -c "${sql_auth_prefix} select public.create_sale_with_items_v2(${customer_sql},'courier'::delivery_kind,'ff990001-6000-4000-8000-000000000001',0,'cash'::payment_method,'[{\"productId\":\"${product_id}\",\"qty\":1}]'::jsonb,'pending'::courier_state)->>'order_id';" | tail -n1
}

# ----------------------------------------------------------------------
# D-M14: concurrent partial vs full transition serializes on one row.
# Final result must be delivered_full with custody=100.
# ----------------------------------------------------------------------
order_m14="$(create_pending 'dd990002-6000-4000-8000-000000000002' "'ee990001-6000-4000-8000-000000000001'::uuid")"
test -n "$order_m14"
rm -f /tmp/g4-m14-partial.log /tmp/g4-m14-full.log
set +e
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.update_courier_outcome_v2('${order_m14}'::uuid,'delivered_partial'::courier_state,40,'ee990001-6000-4000-8000-000000000001'::uuid);" \
    > /tmp/g4-m14-partial.log 2>&1
) & p1=$!
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.update_courier_outcome_v2('${order_m14}'::uuid,'delivered_full'::courier_state,100,null);" \
    > /tmp/g4-m14-full.log 2>&1
) & p2=$!
wait "$p1"; r1=$?
wait "$p2"; r2=$?
set -e
if [[ $r2 -ne 0 ]]; then
  echo "D-M14 FAIL: delivered_full transition failed" >&2; cat /tmp/g4-m14-full.log >&2; exit 1
fi
read -r m14_state m14_custody < <(${PSQL[@]} -F' ' -c "select courier_state::text,collected_by_courier from orders where id='${order_m14}'")
if [[ "$m14_state" != "delivered_full" || "$m14_custody" != "100" ]]; then
  echo "D-M14 FAIL: state=$m14_state custody=$m14_custody r_partial=$r1 r_full=$r2" >&2
  cat /tmp/g4-m14-partial.log /tmp/g4-m14-full.log >&2
  exit 1
fi
if [[ $r1 -ne 0 ]] && ! grep -Eq 'invalid_transition|custody_cannot_decrease' /tmp/g4-m14-partial.log; then
  echo "D-M14 FAIL: partial loser failed for unexpected reason" >&2; cat /tmp/g4-m14-partial.log >&2; exit 1
fi
echo "D-M14 OK: concurrent transitions serialized to delivered_full/custody=100"

# ----------------------------------------------------------------------
# D-M15 / E2: concurrent delivered_full transition and settlement.
# Valid final shapes:
#   A) update wins, settlement wins after it -> direct/paid=100/custody=0/one payment
#   B) settlement runs first and rejects -> courier/delivered_full/custody=100/no payment
# No duplicate payment or lost/negative custody is allowed.
# ----------------------------------------------------------------------
order_m15="$(create_pending 'dd990003-6000-4000-8000-000000000003' 'null')"
test -n "$order_m15"
rm -f /tmp/g4-m15-update.log /tmp/g4-m15-settle.log
set +e
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.update_courier_outcome_v2('${order_m15}'::uuid,'delivered_full'::courier_state,100,null);" \
    > /tmp/g4-m15-update.log 2>&1
) & p1=$!
(
  ${PSQL[@]} -c "${sql_auth_prefix} select public.settle_courier_orders('ff990001-6000-4000-8000-000000000001'::uuid,array['${order_m15}'::uuid]);" \
    > /tmp/g4-m15-settle.log 2>&1
) & p2=$!
wait "$p1"; ru=$?
wait "$p2"; rs=$?
set -e
if [[ $ru -ne 0 ]]; then
  echo "D-M15 FAIL: delivered_full update failed" >&2; cat /tmp/g4-m15-update.log >&2; exit 1
fi
read -r m15_delivery m15_state m15_paid m15_custody m15_paycount m15_payamount < <(${PSQL[@]} -F' ' -c "select o.delivery::text,coalesce(o.courier_state::text,'NULL'),o.paid,o.collected_by_courier,count(p.id),coalesce(sum(p.amount),0) from orders o left join payments p on p.order_id=o.id and p.kind='courier_settlement' where o.id='${order_m15}' group by o.delivery,o.courier_state,o.paid,o.collected_by_courier")
if [[ "$m15_paycount" -gt 1 ]]; then
  echo "D-M15/E2 FAIL: duplicate settlement payments=$m15_paycount" >&2; exit 1
fi
if [[ "$m15_delivery" == "direct" ]]; then
  if [[ "$m15_paid" != "100" || "$m15_custody" != "0" || "$m15_paycount" != "1" || "$m15_payamount" != "100" ]]; then
    echo "D-M15/E2 FAIL: invalid settled shape delivery=$m15_delivery paid=$m15_paid custody=$m15_custody payments=$m15_paycount amount=$m15_payamount" >&2; exit 1
  fi
else
  if [[ "$m15_delivery" != "courier" || "$m15_state" != "delivered_full" || "$m15_paid" != "0" || "$m15_custody" != "100" || "$m15_paycount" != "0" ]]; then
    echo "D-M15/E2 FAIL: invalid unsettled shape delivery=$m15_delivery state=$m15_state paid=$m15_paid custody=$m15_custody payments=$m15_paycount" >&2; exit 1
  fi
  if [[ $rs -eq 0 ]]; then
    echo "D-M15/E2 FAIL: settlement reported success but no settlement effect" >&2; cat /tmp/g4-m15-settle.log >&2; exit 1
  fi
fi
echo "D-M15/E2 OK: concurrent transition/settlement preserved one valid financial state"

echo "GATE4_CONCURRENCY_GREEN: E1, D-M14, D-M15/E2 passed"
