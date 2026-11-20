#!/bin/bash
# Local only. Rebuild the production replica in the running local Supabase stack of a main (1c5276f) worktree.
# usage: build_replica.sh <main-worktree> <repo-root>
set -euo pipefail
W=$1; R=$2; SB=${SB:-supabase}
(cd "$W" && "$SB" db reset --local >/dev/null 2>&1)
C=$(docker ps --format '{{.Names}}' | grep supabase_db | head -1)
E=$(git -C "$R" ls-tree --name-only 183dc50 supabase/migrations/ | grep 20261107214500)
git -C "$R" show 183dc50:"$E" | docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -q >/dev/null
docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -q < "$R/docs/reviews/c6-apply/replica_drift.sql"
docker exec -i "$C" psql -U postgres -v ON_ERROR_STOP=1 -q < "$R/docs/reviews/c6-apply/replica_ledger_set.sql"
echo "replica ready in $C (ledger $(docker exec -i "$C" psql -U postgres -At -c 'select count(*) from supabase_migrations.schema_migrations'))"
