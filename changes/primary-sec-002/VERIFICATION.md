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
| `bun test tests/unit` | Initial candidate: 40 pass, 0 fail, 86 expectations |
| Production build with local Supabase fixture env | Pass |
| Changed-file lint: `tests/unit/dependency-security.test.ts` | Pass |
| `git diff --check` | Pass |
| Hosted Quality on PR53 | Failure before runner execution; `runner_id:0`, empty steps |

## Open Gates

- Hosted CI has no usable application result yet; Quality failed before runner execution.
- A source/evidence review exists; independent acceptance of the remediated final candidate remains pending.
- Remaining Moderate/Low audit records are not fixed here.
- Runtime MCP/auth/tenant/financial gates remain pending.

## Review Follow-up (2026-10-10)

See `REVIEW.md` for the reviewed PR53 SHA, source identity and findings.
Four synthetic adapter/SDK compatibility checks passed in
`review-mcp-compatibility.test.ts`; changed-file lint for that fixture passed.
Independent clean generation corroborated all four brace-expansion lock entries,
but its broader graph was not adopted. Review outcome: Changes required.
Hosted verification, generated-lock process disposition and final-candidate
review remain open. No application auth/tenant or financial gate was closed.
Combined local run of `tests/unit` and the new compatibility fixture passed
44/44 with 94 expectations; `git diff --check` passed after the documentation edits.

## Generator Remediation and CI Diagnosis (2026-10-10)

`LOCK_REGENERATION.md` and `remediation-evidence.json` supersede the manual-lock
method and the previously unknown CI startup cause. The four compatibility tests
now live in `tests/unit/mcp-dependency-compatibility.test.ts`.

| Current check | Result |
| --- | --- |
| Original PR52 lock identity | Remote/local blob match: `b8e19f98189e3a285964b8e75559da27bc01e98b` |
| Bun 1.4.0 generator reproduction | Identical lock, blob `efbffd2d5d0073978c374bb27b1f6398a322b8c6` |
| Bun 1.2.14 frozen install | Pass |
| Bun 1.3.14 frozen install | Pass, no changes |
| Bun 1.2.14 unit suite | 44 pass, 0 fail, 94 expectations |
| Bun 1.2.14 typecheck | Pass |
| Bun 1.2.14 build, explicit local fixture configuration | Pass |
| Lint both unit-test sources | Pass |
| Bun 1.3.14 audit | Exit 1; 0 Critical, 0 High, 11 Moderate, 5 Low |
| Diff check | Pass |
| GitHub startup annotation | Account recent-payment failure or spending-limit restriction; no runner/test execution |

Current generator, frozen-install, unit, typecheck, build and audit outputs are
saved in `remediation-proofs/` with the `remediation-` prefix.
No account billing action, successful hosted CI, final review, merge or deployment
is claimed. Historical results above remain attributed to their original source.
