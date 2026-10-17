# MONJEZ — G0-LINT-FORMAT-01 independent focused review

Reviewer: independent agent `/root/lint_review`; implementation and GitHub writes were excluded from this review. Review requirement: AGENTS.md → NAADF-CMF Change Gate 6 and REVIEW_PROTOCOL.md. This review covers the single formatted application file and its evidence; it neither grants merge approval nor closes G0 or integration acceptance.

## Source and evidence boundary

- Assigned baseline: `ff7a0daaa77659a86f86184131989cb3c2216143`.
- Authoritative preparation source recorded in artifact: `6e1bb93753a906ec63d5add06a98967579c6c39c`, tree `e0e9ed8de93151c972093602d646c8c31eeb2d35`.
- Before file: `src/routes/_authenticated/app.tsx`, Git blob `054c9640c5f7785e7fbac491108286d42e1c1c61`, SHA256 `e7616b1338a3b645f40f9df067d31295a48ffa4cb49bc24247d865bca50baade`. It matches the supplied exact baseline file byte-for-byte.
- Formatted file: Git blob `bd154115c1e782521fe4299cc7cc558e88eafff7`, SHA256 `8210051ae70dce288a957a894f797ce902e335ed609bac588a4d47b726091dfd`.
- `g0-lint-preparation.zip` independently hashed to `8861b25472921b04d5e94453c8210f691244d2a20fd00d1104e69d483da30e26`.
- Preparation run supplied by implementer: `39071094844`, job `117508696886`; its local raw artifact/logs were inspected. I did not independently request the remote run metadata.
- Implementer subsequently reports application commit `3c6d611ce3f616c2c519a3acdc2a9f743837fab2` publishes the same formatted blob and Quality run `39071253858` / job `117509170666` FAILS at changed-file lint after frozen install/typecheck PASS; later Quality steps are SKIPPED. Those remote identity/status reports are explicitly attributed, not independently fetched in this review. They must be retained in final exact-source reconciliation.

## Independent verification performed

`node lint-independent-proof.cjs` passed. Its script and machine-readable result are local review artifacts, not application tests or added repository coverage.

1. Prettier `3.8.3` with the existing `.prettierrc` produces the artifact exactly from baseline, and formatting is idempotent. No formatter/rules change is needed.
2. TypeScript/source AST comparison retains types, callbacks, member expressions, literals, control flow and JSX expressions. Raw formatting changes in JSXText were interpreted using TypeScript `5.9.3` itself, independently of the implementation's handwritten whitespace-cooking algorithm. Meaningful text is preserved.
3. Emitted JavaScript AST comparison also passes. Only contiguous literal text on intrinsic host elements is coalesced; custom component and fragment child segmentation is not coalesced. This is a visible-text/behavior comparison, not a false claim of byte-identical emitted JavaScript or identical host text-node segmentation.
4. Comments retain their type, order and exact contents.
5. Negative controls correctly reject changed TypeScript types, changed custom-component child segmentation, removed meaningful host text whitespace and changed callback behavior. This guards against a comparison that simply strips all JSX text or drops type nodes.
6. Raw CLI lint evidence independently confirms **1210 errors / 13 warnings → 887 errors / 13 warnings**. Both raw CLI exit codes remain **1**. In `app.tsx`, **323 formatter errors → 0**, with **17 nonformat errors and 1 warning unchanged**. The remaining errors are sixteen `no-explicit-any` and one `no-unused-expressions`; warning is `useMemo` missing dependency `tenantTz`.
7. All project nonformat diagnostics match by path, rule, severity, message, message ID and node type after excluding source positions that necessarily move during formatting. Every one of the 140 other lint file result records is deeply identical, including positions. No rules are disabled or diagnostics concealed by this change.
8. Supplied local protected source hashes for package.json, bun.lock, eslint.config.js, .prettierrc and .prettierignore match the artifact records. The preparation workflow checks all six protected files including bunfig.toml; the supplied local baseline does not contain bunfig.toml, so that sixth local comparison was not independently repeated.
9. Preparation raw logs record frozen install, typecheck, existing **66 passing unit tests / 174 expectations**, and both isolated builds. These are preparation-source results. They must not be described as all stages of the later failing Quality run passing. Its post-build app blob remains exactly `bd154115...`.

## Findings and limitations

### F1 — existing lint debt remains a gate

- Severity: Medium, inherited, outside this formatting-only batch.
- File/contract: full project lint; `src/routes/_authenticated/app.tsx` changed-file gate.
- Evidence: raw CLI exits 1 before and after; 887 project errors remain, including the unchanged 17 nonformat errors in the formatted file. Implementer reports the actual Quality job FAILS on those inherited errors.
- Risk: representing the preparation success or 323-error reduction as a green Quality gate would conceal a real acceptance blocker.
- Required fix: accurately report Quality FAIL and schedule separate scoped lint/rule work; do not broaden this formatting change or suppress rules to force green.
- Verification: compare raw diagnostics and preserve actual Quality step statuses on the exact published source.

### L1 — local corroboration is not the locked CI environment

- Severity: Low, evidence limitation; no change requested to application.
- Evidence: independent local replay used Prettier 3.8.3 and TypeScript 5.9.3 matching artifact, but Babel parser **7.29.2**, versus artifact's locked **7.29.7**. The primary artifact itself includes raw/normalized ASTs produced with 7.29.7.
- Risk: falsely claiming a second locked-install verification.
- Required fix: retain this version distinction in evidence; no installation, dependency update or repeated CI is justified solely to conceal it.
- Verification: `lint-independent-proof.json` and `formatter.json`.

### L2 — final exact-source reconciliation remains required

- Severity: Low, delivery boundary.
- Evidence: this reviewer verified the exact before/after file artifacts, not a newly fetched final remote tree after evidence packaging and temporary workflow retirement.
- Risk: promoting evidence from a different tree or implying all later commits are reviewed.
- Required fix: implementer must bind the final app blob, unchanged dependency/security blobs, removed temporary workflow, Quality outcome and relevant preparation source in the final delivery. Any application change after this review invalidates the affected proof until reviewed.
- Verification: exact final Git tree/blob comparison and recorded run identities; no additional historic security or G1 execution needed for formatting.

## Rollback

Revert only the formatting commit or restore `src/routes/_authenticated/app.tsx` from baseline blob `054c9640c5f7785e7fbac491108286d42e1c1c61` in a new commit. Do not reset the branch to the old baseline or revert prior dependency/security fixes. Recheck that rollback touches only this file and restores its expected blob. No data, migration, provider or production rollback is involved.

## Bounded conclusion

No introduced blocking defect was found in the exact formatter output reviewed. The evidence supports a behavior-preserving formatting-only reduction of 323 diagnostics in the largest handwritten application file. Custom component children, types, hooks and other nonformat diagnostics are preserved.

Overall review outcome under the repository protocol: **Changes required** for wider G0/acceptance because inherited lint errors and the failing Quality gate remain; this does not require broadening or undoing the narrowly reviewed formatter change. Exact-source reconciliation and final delivery evidence remain the implementer's responsibility. No merge, deployment, G0 closure or integration acceptance is approved.
