#!/usr/bin/env bash
set -euo pipefail

base="${BASE_SHA:-}"
if [[ -z "$base" || "$base" =~ ^0+$ ]]; then
  base="$(git rev-parse --verify HEAD^)"
fi

names_file="$(mktemp)"
trap 'rm -f "$names_file"' EXIT
# Capture git's exit status before filtering. A failed diff is not an empty diff.
git diff --name-only --diff-filter=ACMR -z "$base" HEAD -- > "$names_file"
files=()
while IFS= read -r -d '' path; do
  case "$path" in
    *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs) files+=("$path") ;;
  esac
done < "$names_file"

if (( ${#files[@]} == 0 )); then
  echo "No changed JavaScript or TypeScript files to lint."
  exit 0
fi
printf '%s\n' "${files[@]}" | tee /tmp/lint-files.txt
bunx eslint -- "${files[@]}" 2>&1 | tee /tmp/lint.log
