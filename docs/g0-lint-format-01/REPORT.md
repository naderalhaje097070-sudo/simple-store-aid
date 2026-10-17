# G0-LINT-FORMAT-01 — bounded formatting candidate

Date: 2026-10-17. Existing Draft PR72; no merge or deployment. Owner-approved intake is recorded in #55 comments 6233216181 and 6233219827. This implements only the largest handwritten application file's formatter cleanup. **The scoped reduction is proved; Quality FAILS and G0/integration remain open.**

## Change, root cause and scope

Current locked ESLint measured 323 prettier/prettier diagnostics in src/routes/_authenticated/app.tsx, the largest hand-authored application file. Dense source layout differed from the existing Prettier configuration; no runtime defect or new business decision was asserted.

Only application change: exact locked Prettier3.8.3 output for that file (1330 added / 326 removed lines). No eslint --fix, new tests, type/Hook/control-flow/import semantics, generated-file edits, rule/ignore changes or tool upgrades. Existing package.json, bun.lock, bunfig.toml, .prettierrc, .prettierignore and eslint.config.js blobs are unchanged. MCP/SDK/esbuild exception and every earlier security change remain intact.

Delivery additionally preserves evidence, root state/task checkpoints and the required change-impact records. The temporary preparation workflow is removed; no permanent diagnostic job, secret, permission or billing change remains.

## Source identity and reproducibility

- Intake: ff7a0daaa77659a86f86184131989cb3c2216143.
- Preparation source: 6e1bb93753a906ec63d5add06a98967579c6c39c; tree e0e9ed8de93151c972093602d646c8c31eeb2d35. Its only delta from intake was the temporary read-only workflow.
- Original app blob: 054c9640c5f7785e7fbac491108286d42e1c1c61.
- Formatted app blob: bd154115c1e782521fe4299cc7cc558e88eafff7; SHA2568210051ae70dce288a957a894f797ce902e335ed609bac588a4d47b726091dfd.
- Formatting commit: 3c6d611ce3f616c2c519a3acdc2a9f743837fab2; tree059dcc3cdd4898b0ae9c463159fd6ffae97fe783. Git tree reconstruction from the preparation tree with exactly that one app blob produces this same tree. Thus the preparation's post-format worktree source is bound to the published candidate; it is not described as a native run on the final documentation head.
- Final delivery changes after that commit contain only evidence/state/impact records and removal of the temporary workflow. Exact final head and tree are recorded in #70/#55 and PR72.

## Measured results

| Measurement | Before | After |
| --- | ---: | ---: |
| Full repository ESLint errors | 1210 | 887 |
| Full repository ESLint warnings | 13 | 13 |
| Full repository prettier/prettier errors | 1148 | 825 |
| app.tsx formatter errors | 323 | 0 |
| app.tsx other errors | 17 | 17 |
| app.tsx warnings | 1 | 1 |
| Actual full CLI lint exit | 1 | 1 |

All nonformat diagnostics match by file/rule/severity/message/messageId/nodeType; target positions move with formatting. Every other file's complete lint result is identical. Current counts replace historical1117 only for the source measured here; this is not a green full-lint gate.

app.tsx retains16 no-explicit-any errors,1 no-unused-expressions error and1 useMemo tenantTz dependency warning. No suppression or automatic nonformat fix was applied.

## Behavior proof and review

Preparation uses locked TypeScript5.9.3 and Babel parser7.29.7 to compare complete source/type AST and emitted JavaScript AST, preserving callbacks, expressions, control flow, literal values and comments. JSX whitespace follows rendered text rules; only contiguous literal text on intrinsic host elements is coalesced for comparison. Custom component and fragment segmentation is preserved. Emitted bytes and intrinsic host text-node segmentation are not falsely claimed identical.

The independent reviewer reproduces the exact formatter output/idempotence and confirms the source/runtime comparisons using TypeScript's own JSX text cooking. Meaningful whitespace/type/callback/custom-child negative controls reject altered behavior. Local corroboration uses parser7.29.2, distinguished from the locked CI parser; it is not a second frozen-install run. Review identifies no introduced blocker in this bounded formatting output. Wider protocol outcome is Changes required due inherited lint/Quality failure. See REVIEW.md and independent-review.zip.

## Commands and actual execution

[Preparation39071094844](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39071094844), job117508696886, attempt1: **SUCCESS**.

- bun install --frozen-lockfile with CI Bun1.2.14: PASS.
- Existing ESLint CLI . --format json before/after: actual exit1/1, raw stdout/stderr retained; API diagnostics/ranking comparison agrees.
- Existing Prettier.format/check with resolved .prettierrc: exact output, check and idempotence PASS. API call performs formatting of one selected file; no wholesale project format command.
- Source/type/runtime JSX AST and comment comparison: PASS.
- bun run typecheck: PASS.
- bun run test:unit: 66PASS,0FAIL,174expectations.
- bun run build and bunx --no-install vite build --mode sec-env-contract: PASS with explicit loopback ci fixtures.
- Post-build tracked-source check: only formatted app remains changed, exact formatted blob retained; protected dependency/config files unchanged. No generated tracked edits.

[Quality39071253858](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39071253858), job117509170666, attempt1, published source3c6d611c: **FAILURE**.

Frozen install and typecheck PASS. Changed-file lint FAILS on the unchanged17errors/1warning in app.tsx. Later Quality unit/boundary/browser/mode-file-build/build/source-invariance steps are SKIPPED. Unit and build success above comes from the separately recorded preparation; it is not credited to these skipped Quality steps. No rules or workflow conditions were weakened to force green.

Initial preparation39027933909 failed its exact emitted-AST comparison on JSX literal segmentation before application publication; later checks were skipped. Its raw archive is retained as preparation-first-failed.zip. The corrected comparator handles intrinsic contiguous text while keeping meaningful whitespace/custom-component segmentation checks. No application workaround was added.

## Evidence

- preparation.zip: exact1483760-byte Actions archive, SHA2568861b25472921b04d5e94453c8210f691244d2a20fd00d1104e69d483da30e26; artifact12115511068.
- preparation-first-failed.zip: exact201670-byte archive, SHA25626cc4fed1f3461c2cc86e90120e8705588baee6c248c47b5d8b2f3af05d9ec5b; artifact12098568809.
- quality-diagnostics.zip: exact777-byte archive, SHA256d00988d779a5b2b209ffc6dc6dcddacc36d27872f9db1225dc0bc1821fe413fa; artifact12115003401.
- preparation.log, quality.log: original decoded job logs. Archives retain raw commands/harness, baseline/ranking/formatter, both lint outputs/exits, before/after app, ASTs/comments, diff, typecheck/unit/build logs and post-build hash.
- RECEIPTS.json binds official run/job/artifact/source identities and final protected blobs. Independent reviewer script/results are archived as evidence, not new application tests.

## Contracts, security and data

No API/RPC/schema/state/auth/tenant/finance contract changes. No migration, database access, external app calls, production data or secrets. Inputs for builds are explicit loopback ci placeholders. No historical security exploit replay, audit rerun or liveG1 was performed. Existing source54 fail-closed identity guard and final integration requirements remain unchanged.

## Acceptance, limitations and one next

PASS: current target selection, exact locked formatter output,323target formatter errors removed, behavior proof, unchanged other diagnostics/dependencies/config, existing standalone typecheck/unit/two builds, focused independent review, preserved failures and rollback.

FAIL/remaining: full lint887errors/13warnings and actual Quality failure. Existing .cjs coverage gap and nonformat rule work remain separately declared. No new overall audit, runtime/auth/DB/browser/G1/release acceptance is inferred. G0 and integration stay open.

ONE NEXT for planning: select the next bounded lint batch using this current inventory; do not reconcile final-source identity or rerun G1 until source cleanup is stable.

## Rollback

Use an additive commit restoring only src/routes/_authenticated/app.tsx from ff7a0daaa77659a86f86184131989cb3c2216143 (expected blob054c9640c5f7785e7fbac491108286d42e1c1c61), or revert only formatting commit3c6d611c. Inspect the one-file delta. Never reset the branch to intake or revert prior dependency/security changes. No data or production rollback is involved.
