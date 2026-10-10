# PRIMARY-SEC-002 Verification

## Summary

The remaining current Critical/High registry audit records from PRIMARY-SEC-001 were triaged and patched in the candidate tree.

`bun audit` result changed from 65 records with 2 Critical and 33 High records to 16 records with 0 Critical and 0 High records.

## Evidence Files

Local evidence is saved under `/workspace/scratch/ef360bbe5cf9/sec-evidence`:

- `sec2-npm-chains.json`
- `sec2-npm-chains-stderr.log`
- `sec2-candidate-audit.json`
- `sec2-candidate-audit-stderr.log`
- `sec2-bun12-frozen-install.log`
- `sec2-typecheck-final.log`
- `sec2-unit-final.log`
- `sec2-build.log`
- `sec2-changed-lint-final.log`
- `sec2-diff-check.log`

## Commands

| Check | Result |
| --- | --- |
| Bun 1.3.14 `install --frozen-lockfile` | Pass |
| Bun 1.2.14 `install --frozen-lockfile` | Pass |
| Bun 1.3.14 `audit --json` | Exit 1 because Moderate/Low findings remain; 0 Critical/High |
| `bun run typecheck` | Pass |
| `bun test tests/unit` | Pass: 40 pass, 0 fail, 86 expectations |
| Production build with local Supabase fixture env | Pass |
| Changed-file lint: `tests/unit/dependency-security.test.ts` | Pass |
| `git diff --check` | Pass |

## Open Gates

- Hosted CI has not been rechecked for this new candidate.
- Independent review has not been completed.
- Remaining Moderate/Low audit records are not fixed here.
- Runtime MCP/auth/tenant/financial gates remain pending.
