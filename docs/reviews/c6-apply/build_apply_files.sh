#!/bin/bash
# C6 apply files, regenerated from the integration candidate 183dc50 (review fix 2026-11-19).
#   C1.sql..C10.sql          one stage each, with the exact-ledger precondition
#   BUNDLE_C1_C10.sql        C1..C10 in ONE transaction (review 2026-11-19b: C1 included, because C1 alone
#                            opens create_sale_with_items_v2 on integer stock). No intermediate state can
#                            ever be committed: any failure leaves the database exactly at C0.
#   BUNDLE_C1_C10_UNBLOCK.sql  the same, plus the legacy-frontend unblock inside the same transaction
#   EMERGENCY_unblock_legacy_frontend_revert.sql  refuses unless all ten C6 versions are in the ledger
# Every block checks the exact ledger versions AND content against EXPECTED (default: production's record).
# usage: build_apply_files.sh <repo-root> [EXPECTED_LEDGER_FILE OUT_DIR]   (the optional pair = test build)
set -euo pipefail
R=$1; D=${3:-$R/docs/reviews/c6-apply}; G=$R/docs/reviews/c6-apply; T=$(mktemp -d); mkdir -p "$D"
BASE=${2:-$R/docs/reviews/c6-ledger/prod_ledger_2026-11-16.txt}
M=(20260815170000_fin_courier_pr_a 20260815171000_fin_idem_sale_create 20261028213608_fractional_quantity_01
   20261029044024_c3_reconcile_financial_adapters 20261103060658_c5_keyed_debt_collection
   20261106145346_c5_day_close_profit_report 20261110090000_courier_settle_custody_01
   20261110130000_paddle_webhook_no_key_update_01 20261110140000_tenants_narrow_client_grants_01
   20261110150000_defpriv_function_execute_01)
for m in "${M[@]}"; do git -C "$R" show "183dc50:supabase/migrations/$m.sql" > "$T/$m.sql"; done
prior=""
for i in "${!M[@]}"; do
  n=$((i + 1))
  python3 "$G/make_stage_c6.py" "C$n" --base-ledger "$BASE" --prior "$prior" "$T/${M[$i]}.sql" > "$D/C$n.sql"
  prior="${prior:+$prior,}${M[$i]:0:14}:$(md5sum < "$T/${M[$i]}.sql" | cut -c1-32)"
done
all=(); for m in "${M[@]}"; do all+=("$T/$m.sql"); done
UNBLOCK="grant execute on function public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) to authenticated;
grant execute on function public.collect_order_debt(uuid, numeric, public.payment_method) to authenticated;"
for variant in plain unblock; do
  f=$D/BUNDLE_C1_C10.sql; [ $variant = unblock ] && f=$D/BUNDLE_C1_C10_UNBLOCK.sql
  {
    echo "-- C6 bundle C1..C10 ($variant). ONE transaction: any failure leaves the database exactly at C0."
    echo "-- Each block checks the exact ledger versions and content. Run as postgres, after the runbook identity checks."
    echo "BEGIN;"
    python3 "$G/make_stage_c6.py" "B" --base-ledger "$BASE" "${all[@]}"
    if [ $variant = unblock ]; then
      echo "-- legacy-frontend unblock, inside the same transaction (no gap). Revert only after the new frontend is live."
      echo "$UNBLOCK"
    fi
    echo "COMMIT;"
  } > "$f"
done
cat > "$D/EMERGENCY_unblock_legacy_frontend_revert.sql" <<'EOF'
-- Revert of the legacy-frontend unblock (review fix 2026-11-19: stage-aware).
-- Refuses unless ALL ten C6 versions are in the ledger, so the new idempotent sale (C2) and collection (C5)
-- paths exist before the legacy ones are withdrawn. The database cannot see the frontend: run this only after
-- the live site serves the new frontend and the shops have reloaded (runbook step).
DO $revert$
BEGIN
  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;
  IF (SELECT count(*) FROM supabase_migrations.schema_migrations WHERE version IN
      ('20260815170000','20260815171000','20261028213608','20261029044024','20261103060658',
       '20261106145346','20261110090000','20261110130000','20261110140000','20261110150000')) <> 10 THEN
    RAISE EXCEPTION 'REVERT_REFUSED: C6 is not fully applied; withdrawing the legacy paths now would stop sales or collection';
  END IF;
  REVOKE EXECUTE ON FUNCTION public.create_sale_with_items(uuid, public.delivery_kind, uuid, numeric, public.payment_method, jsonb) FROM authenticated;
  REVOKE EXECUTE ON FUNCTION public.collect_order_debt(uuid, numeric, public.payment_method) FROM authenticated;
END
$revert$;
EOF
# Read-only identity pre-check (review 2026-11-19c): same constants as the bundle's first block. Run it through
# the SAME tool as the apply (query_database), on the target, right before the bundle; expect both *_ok = true.
python3 - "$BASE" "$D/PRECHECK_target_ledger_read.sql" <<'PY'
import hashlib, sys
base = sorted(tuple(l.split()[:2]) for l in open(sys.argv[1]) if l.strip())
v = hashlib.md5(','.join(x for x, _ in base).encode()).hexdigest()
c = hashlib.md5(','.join(f'{x}:{m}' for x, m in base).encode()).hexdigest()
open(sys.argv[2], 'w').write(f"""-- C6 read-only pre-check of the TARGET database (no rows of application data are read).
-- Run through the same tool as the apply, right before BUNDLE_C1_C10*.sql. Both *_ok must be true.
begin transaction read only;
select json_build_object(
  'ro', current_setting('transaction_read_only'),
  'db', current_database(), 'usr', current_user, 'pg', split_part(version(), ' ', 2),
  'ledger_rows', (select count(*) from supabase_migrations.schema_migrations),
  'ledger_versions_ok', (select md5(coalesce(string_agg(version, ',' ORDER BY version), '')) from supabase_migrations.schema_migrations) = '{v}',
  'ledger_content_ok', (select md5(string_agg(version || ':' || coalesce(md5(array_to_string(statements, E'\\n')), '-'), ',' ORDER BY version)) from supabase_migrations.schema_migrations) = '{c}',
  'c6_versions_present', (select count(*) from supabase_migrations.schema_migrations where version in
     ('20260815170000','20260815171000','20261028213608','20261029044024','20261103060658',
      '20261106145346','20261110090000','20261110130000','20261110140000','20261110150000'))
) as c6_precheck;
rollback;
""")
PY
rm -rf "$T"
echo "built in $D: C1..C10, BUNDLE_C1_C10.sql, BUNDLE_C1_C10_UNBLOCK.sql, revert (expected ledger: $BASE)"
