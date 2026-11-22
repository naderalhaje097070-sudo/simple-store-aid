#!/usr/bin/env bash
# Synthetic GitHub-hosted runner only. No remote database URLs or secrets.
set -euo pipefail
umask 077
test "${CI:-}" = true
test "${GITHUB_REPOSITORY:-}" = naderalhaje097070-sudo/simple-store-aid
test "${GITHUB_REF:-}" = refs/heads/codex/c6-c7-supabase-rehearsal
test "$(supabase --version)" = 2.101.0
test "$(git rev-parse HEAD:supabase/migrations)" = 08d0c94e060d3ea44b23759e41ed193adf979c0e
command -v psql >/dev/null
test -z "$(docker ps -aq --filter 'name=^/supabase_')"
repo=$PWD
base=1c5276fae77cb71f49d868fe71d17d84c5d3c6b3
work=$(mktemp -d)
source_dir=$work/source
target_dir=$work/target
source_id=monjez-c6c7-source
target_id=monjez-c6c7-target
source=supabase_db_$source_id
target=supabase_db_$target_id
extensions=realtime,storage,imgproxy,inbucket,mailpit,meta,studio,edge-runtime,functions,analytics,vector,supavisor,pooler
fixture=$repo/tests/c6-upgrade
apply=$repo/docs/reviews/c6-apply
restore=$repo/tests/release/restore
export SUPABASE_HOME=$work/cli-home
mkdir -p "$source_dir" "$target_dir" "$SUPABASE_HOME"
cleanup() {
    supabase --workdir "$target_dir" stop --no-backup >/dev/null 2>&1 || true
    supabase --workdir "$source_dir" stop --no-backup >/dev/null 2>&1 || true
    rm -rf -- "$work"
}
trap cleanup EXIT

for stack in "$source_dir" "$target_dir"; do
    supabase --workdir "$stack" init >/dev/null
done
sed -i "s/^project_id = .*/project_id = \"$source_id\"/" "$source_dir/supabase/config.toml"
sed -i "s/^project_id = .*/project_id = \"$target_id\"/" "$target_dir/supabase/config.toml"
git archive "$base" supabase/migrations | tar -x -C "$source_dir"
test "$(find "$source_dir/supabase/migrations" -name '*.sql' | wc -l)" -eq 50
start() {
    local dir=$1 container=$2
    if ! supabase --workdir "$dir" start -x "$extensions" >"$work/start.log" 2>&1; then
        echo "Supabase startup failed for $container" >&2
        grep -Ei '(failed|fatal|error|unhealthy|no matching manifest)' "$work/start.log" | head -15 >&2 || true
        return 1
    fi
    local image
    image=$(docker inspect --format '{{.Config.Image}}' "$container")
    case "$image" in
        supabase/postgres:17.6.1.106|*/supabase/postgres:17.6.1.106) ;;
        *) echo "Unexpected Supabase image $image" >&2; return 1 ;;
    esac
    docker image inspect --format 'Runtime image {{.Id}} {{join .RepoDigests " "}}' "$image"
}
psql_db() {
    local container=$1
    shift
    docker exec -i "$container" psql -X -U postgres -d postgres -v ON_ERROR_STOP=1 -Atq "$@"
}
src() { psql_db "$source" "$@"; }
fail_as() {
    local error=$1
    shift
    if "$@" >"$work/refusal.out" 2>"$work/refusal.err"; then
        echo "Expected refusal: $error" >&2
        return 1
    fi
    grep -F "$error" "$work/refusal.err" || { cat "$work/refusal.err" >&2; return 1; }
}
capture() {
    local db=$1 name=$2
    psql_db "$db" -f - <"$restore/fingerprint.sql" >"$work/$name.catalog"
    psql_db "$db" -f - <"$restore/data_hash.sql" >"$work/$name.data"
    test -s "$work/$name.catalog" && test -s "$work/$name.data"
}
compare() {
    diff -u "$work/$1.catalog" "$work/$2.catalog"
    diff -u "$work/$1.data" "$work/$2.data"
}
ledger() {
    psql_db "$1" -c "select version, md5(array_to_string(statements, E'\\n')) from supabase_migrations.schema_migrations order by version" \
        | tr '|' ' '
}
sequence_state() {
    psql_db "$1" -c "select last_value, is_called from public.orders_number_seq"
}
backup_c6() {
    local url=postgresql://postgres:postgres@127.0.0.1:54322/postgres
    supabase db dump --db-url "$url" -f "$work/roles.sql" --role-only
    supabase db dump --db-url "$url" -f "$work/schema.sql"
    src -f - <"$restore/app_triggers_outside.sql" >"$work/triggers.sql"
    docker exec "$source" pg_dump -U postgres -d postgres --schema-only \
        -n supabase_migrations --no-owner --no-privileges >"$work/ledger-schema.sql"

    # Synthetic only. Match the documented export format and cover all schemas
    # checked by data_hash.sql. Keep the archive and its inventory on this runner.
    docker exec "$source" pg_dump -U postgres -d postgres --format=custom --compress=zstd \
        --strict-names -n auth -n public -n monjez_private -n supabase_migrations >"$work/rehearsal.backup"
    docker exec -i "$source" pg_restore --list <"$work/rehearsal.backup" >"$work/archive.toc"
    for item in "TABLE DATA auth users" "TABLE DATA public orders" "TABLE DATA public payments" \
        "TABLE DATA supabase_migrations schema_migrations" "SEQUENCE SET public orders_number_seq"; do
        grep -Fq "$item " "$work/archive.toc"
    done
    sha256sum "$work/rehearsal.backup" | awk '{print "Synthetic archive SHA-256 " $1}'
    sequence_state "$source" >"$work/source.sequence"
}
restore_c6() {
    start "$target_dir" "$target"
    test "$(psql_db "$target" -c "select to_regclass('public.orders') is null")" = t
    # Restore the reviewed schema and the archived rows together. The explicit
    # data-only restore preserves sequence values and leaves platform DDL intact.
    docker exec -i "$target" pg_restore --data-only --no-owner --no-privileges --file=- \
        <"$work/rehearsal.backup" >"$work/archived-data.sql"
    {
        cat "$work/roles.sql" "$restore/prelude.sql" "$work/schema.sql" "$work/triggers.sql" "$work/ledger-schema.sql"
        printf '\nSET session_replication_role = replica;\n'
        cat "$work/archived-data.sql"
    } | psql_db "$target" --single-transaction -f -
    sequence_state "$target" >"$work/target.sequence"
    cmp "$work/source.sequence" "$work/target.sequence"
}
start "$source_dir" "$source"
test "$(src -c 'select count(*) from supabase_migrations.schema_migrations')" = 50
pin_hotfix=$(git ls-tree --name-only 183dc50 -- supabase/migrations/ | grep '/20261107214500_')
git show "183dc50:$pin_hotfix" | src -f -
src -f - <"$apply/replica_drift.sql"
src -f - <"$apply/replica_ledger_set.sql"
python3 "$fixture/make_replica_ledger.py" "$repo" "$work/fixture.sql" "$work/c0.expected"
src -f - <"$work/fixture.sql"
python3 "$fixture/harness.py" "$source" seed >/dev/null
ledger "$source" >"$work/c0.ledger"
diff -u "$work/c0.expected" "$work/c0.ledger"
capture "$source" c0
fail_as LEDGER_CONTENT_MISMATCH src -f - <"$apply/BUNDLE_C1_C10.sql"
capture "$source" c0-refused
compare c0 c0-refused
bash "$apply/build_apply_files.sh" "$repo" "$work/c0.expected" "$work/test-apply"
c6=$work/test-apply/BUNDLE_C1_C10.sql
guard_line="LEDGER_CONTENT_MISMATCH"
cmp <(grep -v "$guard_line" "$c6") <(grep -v "$guard_line" "$apply/BUNDLE_C1_C10.sql")
src -f - <"$c6"
ledger "$source" >"$work/c6.ledger"
test "$(wc -l <"$work/c6.ledger")" -eq 62
test "$(cut -d ' ' -f 1 "$work/c6.ledger" | paste -sd, | tr -d '\n' | md5sum | cut -d' ' -f1)" = 8eec91642011d297ca5504cebda430ef
capture "$source" c6
backup_c6
echo 'PASS C6 zstd custom-format archive contains Auth, orders, payments, migration ledger and order sequence'

c7a=supabase/migrations/20261120140000_guard_courier_custody_settlement.sql
c7b=supabase/migrations/20261120150000_close_day_courier_debt_balance.sql
printf '%s  %s\n' e14b9f03582b79b83e4334bb8c8ae32eb2ecde6e0669c20a872cb74060e0a2a7 "$c7a"     4f48a50379a0a215d52069f0062049c833b4d255e35ea65ec4370e1bdeacf8a5 "$c7b" | sha256sum -c
stage() {
    printf 'BEGIN;\n'
    python3 "$apply/make_stage_c6.py" C7 --base-ledger "$work/c6.ledger" "$@" "$c7a" "$c7b"
    printf 'COMMIT;\n'
}
stage >"$work/c7-stages.sql"
test "$(grep -c '^-- stage C7.2$' "$work/c7-stages.sql")" = 1
awk -v injection="DO \$\$ BEGIN RAISE EXCEPTION 'ISOLATED_C7_FAILURE'; END \$\$;" \
    '/^-- stage C7.2$/{print injection} {print}' "$work/c7-stages.sql" >"$work/c7-fail.sql"
cp "$work/c7-stages.sql" "$work/c7.sql"
psql_db "$source" -f - <"$work/c7.sql"
ledger "$source" >"$work/$source.ledger"
capture "$source" "$source-c7"
supabase --workdir "$source_dir" stop --no-backup >/dev/null
restore_c6
capture "$target" c6-restored
compare c6 c6-restored
echo 'PASS C6 separate Supabase archive restore matches application catalog, hashed tables and order sequence'
fail_as ISOLATED_C7_FAILURE psql_db "$target" -f - <"$work/c7-fail.sql"
capture "$target" c7-aborted
compare c6 c7-aborted
psql_db "$target" -f - <"$work/c7.sql"
ledger "$target" >"$work/$target.ledger"
capture "$target" "$target-c7"
{
    cat "$work/c6.ledger"
    printf '20261120140000 %s\n' "$(md5sum <"$c7a" | cut -d' ' -f1)"
    printf '20261120150000 %s\n' "$(md5sum <"$c7b" | cut -d' ' -f1)"
} | LC_ALL=C sort >"$work/c7.expected"
test "$(wc -l <"$work/c7.expected")" -eq 64
diff -u "$work/c7.expected" "$work/$source.ledger"
diff -u "$work/c7.expected" "$work/$target.ledger"
compare "$source-c7" "$target-c7"
diff -u <(grep -v '^supabase_migrations.schema_migrations|' "$work/c6.data")     <(grep -v '^supabase_migrations.schema_migrations|' "$work/$target-c7.data")
diff -u <(grep -Ev '^fn\|(public\.)?(update_courier_outcome_v2|settle_courier_orders|close_day)\(' "$work/c6.catalog")     <(grep -Ev '^fn\|(public\.)?(update_courier_outcome_v2|settle_courier_orders|close_day)\(' "$work/$target-c7.catalog")
fail_as LEDGER_STATE_MISMATCH psql_db "$target" -f - <"$work/c7.sql"
capture "$target" c7-refused
compare "$target-c7" c7-refused
echo 'PASS C7 failure rollback, logical recovery replay, row preservation and rerun refusal'

supabase --workdir "$target_dir" status -o json >"$work/status.json"
env -i PATH="$PATH" CI_ISOLATED_SUPABASE=1 PYTHONDONTWRITEBYTECODE=1 \
    MONGEZZ_DEPLOY_TARGET=ci MONGEZZ_E2E_WRITE_TEST=1 VITE_SUPABASE_URL=http://127.0.0.1:54321 \
    VITE_SUPABASE_PUBLISHABLE_KEY=monjez-isolated-placeholder PGHOST=127.0.0.1 PGPORT=54322 \
    PGUSER=postgres PGDATABASE=postgres PGPASSWORD=postgres python3 - "$work" "$GITHUB_SHA" <<'PY'
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path("tests/c5-journey").resolve()))
from native import prior, profit_contract

work = Path(sys.argv[1])
p = prior.FinanceProbe(work / "status.json", work / "controls", sys.argv[2])
profit_contract.check_courier_debt_close(p, {"actors": {}}, work / "actors.json")
seller = p.fixture("restored_sale_owner")
foreign = p.fixture("restored_foreign_owner")
product = p.seed_product(seller)
foreign_product = p.seed_product(foreign)
foreign_order = p.order(foreign, foreign_product, .25, 25)
foreign_before = p.effect(foreign_order)
key = str(uuid.uuid4())
first, second = [p.sale(seller, product, .25, 25, key=key) for _ in range(2)]
p.control("restored_quarter_sale_retried_once", first[0] == second[0] == 200
          and first[1]["order_id"] == second[1]["order_id"]
          and p.stock(product) == 9.75 and p.effect(first[1]["order_id"])["payment_sum"] == 25)
p.control("restored_other_tenant_unchanged", p.effect(foreign_order) == foreign_before
          and p.stock(foreign_product) == 9.75)
print(f"PASS {len(p.controls)} restored Supabase Auth, PostgREST and stored-finance assertions")
PY
