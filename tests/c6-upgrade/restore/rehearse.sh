#!/bin/bash
# Local only. Backup/restore rehearsal: source = running local replica, target = a second, fresh local
# Supabase instance (project_id restoretarget, db port 54422). Never point either URL at production.
# usage: rehearse.sh <supabase-cli> <workdir>
set -euo pipefail
SB=$1; W=$2; H=$(cd "$(dirname "$0")" && pwd)
# Transport fix (#99): prelude.sql and data_hash.sql are the documented helpers in tests/release/restore/, byte-identical
# to the copies this rehearsal was written with (blobs 82a109fa, 6117645c); refuse to run on any other content.
REL=$(cd "$H/../../release/restore" && pwd)
echo "1f17cd85080708a9ab3bf5a8987c4ebebf7204a26859ee27ad8c14e5d28a704f  $REL/prelude.sql
e908e848b803f3c998ff8320aa9f8c57a83c1648c0cd790ed3cf5afcd767d023  $REL/data_hash.sql" | sha256sum -c --quiet - \
  || { echo "REHEARSE_HELPER_MISMATCH: tests/release/restore helpers differ from the reviewed bytes" >&2; exit 2; }
SRC_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
SRC=supabase_db_dahzkekdirrngnkcxinv; T=supabase_db_restoretarget
mkdir -p "$W"
# 1. backup: the Supabase CLI split dump, plus the migration ledger, which the CLI dump does not contain
"$SB" db dump --db-url "$SRC_URL" -f "$W/roles.sql" --role-only
"$SB" db dump --db-url "$SRC_URL" -f "$W/schema.sql"
"$SB" db dump --db-url "$SRC_URL" -f "$W/data.sql" --use-copy --data-only
docker exec "$SRC" pg_dump -U postgres -d postgres -n supabase_migrations --no-owner --no-privileges > "$W/ledger.sql"
# 2. platform-owned storage/supabase_functions rows are not restorable as postgres; drop their COPY blocks
python3 - "$W/data.sql" "$W/data_app.sql" <<'EOF'
import re, sys
out, skip = [], False
for l in open(sys.argv[1]).read().split('\n'):
    # exactly these two schemas, quoted (CLI 2.101.0 output) or unquoted; similar names such as storage_x stay
    m = re.match(r'^COPY (?:"(?:storage|supabase_functions)"|(?:storage|supabase_functions))\.', l)
    if m:
        skip = True; continue
    if skip:
        skip = l != '\\.'; continue
    out.append(l)
open(sys.argv[2], 'w').write('\n'.join(out))
EOF
# 3. restore in ONE transaction. prelude.sql is required: without it every restored table and function
#    keeps the fresh instance's default grants (anon ALL, authenticated TRUNCATE/EXECUTE).
for f in roles schema data_app ledger; do docker cp "$W/$f.sql" "$T:/tmp/$f.sql"; done
docker cp "$REL/prelude.sql" "$T:/tmp/prelude.sql"
docker exec "$T" psql -U postgres -d postgres --single-transaction -v ON_ERROR_STOP=1 -q \
  -f /tmp/roles.sql -f /tmp/prelude.sql -f /tmp/schema.sql \
  -c 'SET session_replication_role = replica' -f /tmp/data_app.sql -f /tmp/ledger.sql
# 4. verify: per-table data hashes must be identical
for c in "$SRC" "$T"; do docker cp "$REL/data_hash.sql" "$c:/tmp/data_hash.sql"; docker exec "$c" psql -U postgres -At -q -f /tmp/data_hash.sql > "$W/data_$c.txt"; done
diff "$W/data_$SRC.txt" "$W/data_$T.txt" && echo "DATA identical: $(wc -l < "$W/data_$SRC.txt") tables"
