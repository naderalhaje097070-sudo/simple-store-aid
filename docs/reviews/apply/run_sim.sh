#!/bin/bash
# Full rehearsal on a fresh restore of the production export. Usage: run_sim.sh <backup file>
S=/tmp/claude-0/-home-user-simple-store-aid/9348b4dd-0e1d-5cad-baa8-cd0e24d5861e/scratchpad/sim; R=/home/user/simple-store-aid/docs/reviews/rollback; P=/tmp/pg17/env/bin
PSQL="$P/psql -h /tmp -p 55432 -U postgres -v ON_ERROR_STOP=1 -At"; st(){ $PSQL -f $S/state.sql; }
su pgt -c "$P/pg_ctl -D /tmp/pgdata stop -m fast" >/dev/null 2>&1; rm -rf /tmp/pgdata; mkdir -p /tmp/pgdata; chown pgt /tmp/pgdata
su pgt -c "$P/initdb -D /tmp/pgdata -U postgres -A trust -E UTF8 >/dev/null 2>&1 && $P/pg_ctl -D /tmp/pgdata -o '-p 55432 -k /tmp' -l /tmp/pgdata/log.txt start >/dev/null"; sleep 2
$P/psql -h /tmp -p 55432 -U postgres -qc "do \$\$ declare r text; begin foreach r in array array['supabase_admin','anon','authenticated','service_role','authenticator','supabase_auth_admin','supabase_storage_admin','supabase_realtime_admin','supabase_replication_admin','supabase_read_only_user','dashboard_user','pgbouncer','pgsodium_keyholder','pgsodium_keyiduser','pgsodium_keymaker','sandbox_exec','supabase_functions_admin','supabase_etl_admin','cli_login_postgres'] loop if not exists (select 1 from pg_roles where rolname=r) then execute format('create role %I', r); end if; end loop; end \$\$;"
su pgt -c "$P/pg_restore -h /tmp -p 55432 -U postgres -d postgres $1" > /tmp/restore/restore.log 2>&1
echo "restore_errors=$(grep -c '^pg_restore: error' /tmp/restore/restore.log) (expected 38, platform extensions only)"
st > $S/F0.json; echo "F0 $(cat $S/F0.json)"
for k in 1 2 3 4 5; do
  b=$(st); out=$($PSQL -f $S/S${k}I.sql 2>&1); a=$(st)
  echo "S$k inject: $(echo "$out" | grep -o 'INJECTED_FAILURE_AT_END_OF_STAGE S[0-9]' | head -1) state=$([ "$b" = "$a" ] && echo UNCHANGED || echo CHANGED)"
  out=$($PSQL -f $S/S${k}.sql 2>&1); rc=$?; st > $S/F$k.json
  echo "S$k apply rc=$rc $(python3 -I -c "import json;a=json.load(open('$S/F$((k-1)).json'));b=json.load(open('$S/F$k.json'));print({x:b[x] for x in ['ledger','functions_public','policies_n','email_service_only','private_tables']}, 'data_same=', a['data_hash']==b['data_hash'])")"
done
echo "bodies_vs_files=$($PSQL -f $S/bodies_gate.sql)"
b=$(st); out=$($PSQL -f $R/R1_live_actor_1_2.sql 2>&1); a=$(st); echo "R1_out_of_order: $(echo "$out" | grep -oE 'ROLLBACK_ORDER_VIOLATION' | head -1) state=$([ "$b" = "$a" ] && echo UNCHANGED || echo CHANGED)"
i=5; for r in R5_webhook_7_8_9 R4_scanner_entitlement_5_6 R3_owner_closure_4 R2_truncate_3 R1_live_actor_1_2; do
  out=$($PSQL -f $R/$r.sql 2>&1); rc=$?; st > $S/RB$i.json
  python3 -I - "$S/F$((i-1)).json" "$S/RB$i.json" "$r" "$rc" "$((i-1))" <<'PY'
import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
keys=['ledger','fn_public','functions_public','policies','policies_n','table_acl','col_acl','default_acl','email_service_only','data_hash']
diff=[k for k in keys if a[k]!=b[k]]
print(f"{sys.argv[3]} rc={sys.argv[4]} vs state after stage {sys.argv[5]}: {'MATCH' if not diff else 'DIFF '+str(diff)}; private kept: tables={b['private_tables']} (stage state {a['private_tables']}), fn_private_same={a['fn_private']==b['fn_private']}, fn_acl_same={a['fn_acl']==b['fn_acl']}")
PY
  i=$((i-1)); done
b=$(st); out=$($PSQL -f $R/R1_live_actor_1_2.sql 2>&1); a=$(st); echo "R1_twice: $(echo "$out" | grep -oE 'STAGE_NOT_APPLIED' | head -1) state=$([ "$b" = "$a" ] && echo UNCHANGED || echo CHANGED)"
