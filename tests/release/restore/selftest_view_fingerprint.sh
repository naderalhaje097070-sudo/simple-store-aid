#!/bin/bash
# Self-test for the restore fingerprint (review fix #98, Graphify P2): a view or materialized view whose defining
# query changes while its columns stay the same must change its fingerprint line. Synthetic only: it creates and
# drops its own throwaway database (default fp_view_selftest) on the server named by the PG* variables; nothing else
# is touched. Optional second argument: an alternative fingerprint.sql to test (used to show the pre-fix file misses it).
# usage: PGHOST=.. PGPORT=.. PGUSER=.. PGPASSWORD=.. selftest_view_fingerprint.sh [DBNAME] [FINGERPRINT_SQL]
set -euo pipefail
DB=${1:-fp_view_selftest}; FP=${2:-$(dirname "$0")/fingerprint.sql}
case "$DB" in fp_*_selftest) ;; *) echo "refusing: database name must match fp_*_selftest" >&2; exit 2 ;; esac
q() { psql -X -v ON_ERROR_STOP=1 -At -q -d "$DB" "$@"; }
psql -X -v ON_ERROR_STOP=1 -q -d postgres -c "drop database if exists $DB" -c "create database $DB"
trap 'psql -X -q -d postgres -c "drop database if exists '"$DB"'" >/dev/null 2>&1 || true' EXIT
fp() { q -f "$FP" | grep -E '^rel\|public\.(sv|sm)\|'; }
q -c "create view public.sv as select 1::int as a, 'x'::text as b" \
  -c "create materialized view public.sm as select 1::int as a, 'x'::text as b"
f1=$(fp)
q -c "create or replace view public.sv as select 2::int as a, 'y'::text as b"                      # same columns
f2=$(fp)
q -c "drop materialized view public.sm" -c "create materialized view public.sm as select 2::int as a, 'y'::text as b"
f3=$(fp)
q -c "create or replace view public.sv as select 1::int as a, 'x'::text as b" \
  -c "drop materialized view public.sm" -c "create materialized view public.sm as select 1::int as a, 'x'::text as b"
f4=$(fp)
line() { grep "^rel|public.$1|" <<<"$2"; }
r() { [ "$1" ] && echo PASS || echo FAIL; }
v_changed=$([ "$(line sv "$f1")" != "$(line sv "$f2")" ] && echo 1 || true)
m_unchanged_by_view=$([ "$(line sm "$f1")" = "$(line sm "$f2")" ] && echo 1 || true)
m_changed=$([ "$(line sm "$f2")" != "$(line sm "$f3")" ] && echo 1 || true)
same_def_same_fp=$([ "$f1" = "$f4" ] && [ "$(wc -l <<<"$f1")" = 2 ] && echo 1 || true)
echo "view_query_change_same_columns_changes_fingerprint $(r "$v_changed")"
echo "matview_line_unaffected_by_view_change $(r "$m_unchanged_by_view")"
echo "matview_query_change_same_columns_changes_fingerprint $(r "$m_changed")"
echo "same_definitions_same_fingerprint $(r "$same_def_same_fp")"
[ "$v_changed" ] && [ "$m_unchanged_by_view" ] && [ "$m_changed" ] && [ "$same_def_same_fp" ]
