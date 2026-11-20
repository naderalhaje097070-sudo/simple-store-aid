#!/bin/bash
# Real-tree rejection cases for the candidate63 verifier, each in a fresh local clone of the branch head.
# usage: real_negatives.sh WORKTREE OUTDIR
set -uo pipefail
W=$1; O=$2; export PYTHONDONTWRITEBYTECODE=1
M=supabase/migrations/20261013120223_sec_truncate_01.sql      # a B50 file
A=supabase/migrations/20260626142422_e1e5cd70-ffee-4f24-b2ae-eebd0db18705.sql   # an original41 file
regen() { git add -A && git -c user.name=n -c user.email=n@x.invalid commit -qm t --allow-empty && python3 tests/g01-acceptance/candidate_identity.py --print-manifest > tests/g01-acceptance/candidate-63-source.json && git add -A && git -c user.name=n -c user.email=n@x.invalid commit -qm m; }
run() {   # $1 case  $2 shell mutation
  local d="$O/$1"; git clone -q "$W" "$d" && cd "$d" && git remote set-url origin https://github.com/naderalhaje097070-sudo/simple-store-aid
  eval "$2"
  local out; out=$(python3 -c "import sys;sys.path.insert(0,'tests/g01-acceptance');from candidate_identity import verify;print('ACCEPTED',verify('.')['migration_count'])" 2>&1 | tail -1)
  echo "$1 => $out"; cd - > /dev/null
}
run unchanged_head ':'
run b50_file_corrupted_worktree "printf -- '-- x\n' >> $M"
run b50_file_corrupted_committed_regenerated "printf -- '-- x\n' >> $M; regen"
run a41_file_corrupted_committed_regenerated "printf -- '-- x\n' >> $A; regen"
run b50_file_deleted_worktree "rm $M"
run b50_file_deleted_committed_regenerated "git rm -q $M; regen"
run same_count_b50_swapped_for_new_regenerated "git rm -q $M; printf 'select 1;\n' > supabase/migrations/20261231000000_swap.sql; regen"
run extra_untracked_path "printf 'x\n' > src/extra.ts"
run extra_migration_committed_regenerated "printf 'select 1;\n' > supabase/migrations/20261231000000_extra.sql; regen"
run b50_mode_worktree "chmod +x $M"
run b50_mode_committed_regenerated "chmod +x $M; git update-index --chmod=+x $M; regen"
run frozen_b50_manifest_edited "printf ' ' >> tests/g01-acceptance/integrated-b-source.json; regen"
run verifier_source_edited_unreviewed "printf '\n' >> tests/g01-acceptance/candidate_identity.py; git commit -qam t"
