#!/usr/bin/env bash
# FIN-IDEM-001 two-session concurrency proof.
# Destructive test: disposable local Supabase/PostgreSQL ONLY.
set -euo pipefail

fail() {
  echo "FIN_IDEM_CONCURRENCY_BLOCKED: $*" >&2
  exit 64
}

[[ "${CI_ISOLATED_SUPABASE:-}" == "1" ]] || fail "CI_ISOLATED_SUPABASE=1 is required"
[[ "${PGPORT:-}" == "54322" ]] || fail "PGPORT must be 54322"
[[ "${PGUSER:-}" == "postgres" ]] || fail "PGUSER must be postgres"
[[ "${PGDATABASE:-}" == "postgres" ]] || fail "PGDATABASE must be postgres"

case "${PGHOST:-}" in
  127.0.0.1|localhost|::1) ;;
  *) fail "PGHOST must be loopback" ;;
esac

if [[ -n "${PGHOSTADDR:-}" ]]; then
  case "$PGHOSTADDR" in
    127.0.0.1|::1) ;;
    *) fail "PGHOSTADDR must be unset or loopback" ;;
  esac
fi
[[ -z "${PGSERVICE:-}" ]] || fail "PGSERVICE is forbidden"
[[ -z "${PGSERVICEFILE:-}" ]] || fail "PGSERVICEFILE is forbidden"

PSQL=(psql -X -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -v ON_ERROR_STOP=1)
PRODUCT_ID="fade4000-0000-0000-0000-000000000001"
IDEM_KEY="fade5000-0000-0000-0000-000000000001"
OUT_A="$(mktemp)"
OUT_B="$(mktemp)"

cleanup() {
  set +e
  "${PSQL[@]}" -qAt <<SQL >/dev/null 2>&1
DELETE FROM public.payments
 WHERE order_id IN (
   SELECT DISTINCT oi.order_id FROM public.order_items oi WHERE oi.product_id = '$PRODUCT_ID'::uuid
 );
DELETE FROM public.order_items WHERE product_id = '$PRODUCT_ID'::uuid;
DELETE FROM public.orders o
 WHERE NOT EXISTS (SELECT 1 FROM public.order_items oi WHERE oi.order_id = o.id)
   AND o.id IN (
     SELECT (result->>'order_id')::uuid
       FROM public.financial_idempotency
      WHERE operation = 'sale.create.v2' AND idempotency_key = '$IDEM_KEY'::uuid
   );
DELETE FROM public.financial_idempotency
 WHERE operation = 'sale.create.v2' AND idempotency_key = '$IDEM_KEY'::uuid;
DELETE FROM public.products WHERE id = '$PRODUCT_ID'::uuid;
SQL
  rm -f "$OUT_A" "$OUT_B"
}
trap cleanup EXIT

read -r TID OWNER < <("${PSQL[@]}" -At -F' ' -c \
  "SELECT id::text, owner_user_id::text FROM public.tenants WHERE owner_user_id IS NOT NULL ORDER BY created_at ASC LIMIT 1;")
[[ -n "${TID:-}" && -n "${OWNER:-}" ]] || fail "no isolated tenant/owner fixture"

# Remove only this test's fixed fixture from a previous interrupted isolated run.
"${PSQL[@]}" -qAt <<SQL
DELETE FROM public.payments
 WHERE order_id IN (
   SELECT DISTINCT oi.order_id FROM public.order_items oi WHERE oi.product_id = '$PRODUCT_ID'::uuid
 );
DELETE FROM public.order_items WHERE product_id = '$PRODUCT_ID'::uuid;
DELETE FROM public.financial_idempotency
 WHERE tenant_id = '$TID'::uuid
   AND operation = 'sale.create.v2'
   AND idempotency_key = '$IDEM_KEY'::uuid;
DELETE FROM public.products WHERE id = '$PRODUCT_ID'::uuid;
INSERT INTO public.products(id, tenant_id, name, price, cost, stock, is_active)
VALUES ('$PRODUCT_ID'::uuid, '$TID'::uuid, 'FIN-IDEM-CONCURRENCY', 100, 60, 10, true);
SQL

CALL_SQL="
SELECT set_config('request.jwt.claims', json_build_object('sub','$OWNER','role','authenticated')::text, false);
SELECT public.create_sale_with_items_idempotent(
  '$IDEM_KEY'::uuid,
  NULL,
  'direct'::public.delivery_kind,
  NULL,
  100,
  'cash'::public.payment_method,
  '[{\"productId\":\"$PRODUCT_ID\",\"qty\":1}]'::jsonb,
  NULL
)::text;
"

"${PSQL[@]}" -qAt -c "$CALL_SQL" >"$OUT_A" &
PID_A=$!
"${PSQL[@]}" -qAt -c "$CALL_SQL" >"$OUT_B" &
PID_B=$!
wait "$PID_A"
wait "$PID_B"

RESULT_A="$(tail -n 1 "$OUT_A")"
RESULT_B="$(tail -n 1 "$OUT_B")"
[[ -n "$RESULT_A" && "$RESULT_A" == "$RESULT_B" ]] || {
  echo "FIN_IDEM_CONCURRENCY_FAIL: result mismatch" >&2
  echo "A=$RESULT_A" >&2
  echo "B=$RESULT_B" >&2
  exit 1
}

"${PSQL[@]}" -qAt <<SQL
DO \$verify\$
DECLARE
  v_stock numeric;
  v_orders int;
  v_payments int;
  v_keys int;
BEGIN
  SELECT stock INTO v_stock FROM public.products WHERE id = '$PRODUCT_ID'::uuid;
  SELECT COUNT(DISTINCT oi.order_id) INTO v_orders
    FROM public.order_items oi WHERE oi.product_id = '$PRODUCT_ID'::uuid;
  SELECT COUNT(*) INTO v_payments
    FROM public.payments p
   WHERE p.order_id IN (
     SELECT DISTINCT oi.order_id FROM public.order_items oi WHERE oi.product_id = '$PRODUCT_ID'::uuid
   );
  SELECT COUNT(*) INTO v_keys
    FROM public.financial_idempotency
   WHERE tenant_id = '$TID'::uuid
     AND operation = 'sale.create.v2'
     AND idempotency_key = '$IDEM_KEY'::uuid;

  IF v_stock <> 9 OR v_orders <> 1 OR v_payments <> 1 OR v_keys <> 1 THEN
    RAISE EXCEPTION 'FIN_IDEM_CONCURRENCY_FAIL: stock=% orders=% payments=% keys=%',
      v_stock, v_orders, v_payments, v_keys;
  END IF;
END
\$verify\$;
SQL

echo "FIN_IDEM_CONCURRENCY_GREEN"
