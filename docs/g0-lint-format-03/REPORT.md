# G0-LINT-FORMAT-03 — ten-file formatter candidate

Canonical repository `naderalhaje097070-sudo/simple-store-aid`, existing Draft72.
Base `3b4a312a40a471b6968db000a86bee468bd07cd7`; executable formatted source
`8916bec5ed6f14159b9323d860ee388b3b485a27`, tree
`fe63a2de6f1c17c442247a66250b47975c96d613`. Later final documentation-head identity
is recorded in the linked #70/#55 delivery, not equated to the tested source tree.
Candidate only; no main-branch fix, merge, deployment or release acceptance.

## Current scoped measurements

Selection reuses `docs/g0-lint-format-01/preparation.zip:handwritten-ranking.json`.
Previously completed app.tsx and FORMAT-02 five files, generated files, and saved
mixed-rule/warning files are excluded. Only candidate files were freshly linted;
no global classification or current whole-project count was produced.

| Accepted file | Formatting errors before | After | Other visible errors / warnings before→after |
| --- | ---: | ---: | --- |
| src/features/shop/ShopHubScreen.tsx | 22 | 0 | 0/0 → 0/0 |
| src/routes/index.tsx | 21 | 0 | 0/0 → 0/0 |
| src/features/reports/CollectedScreen.tsx | 13 | 0 | 0/0 → 0/0 |
| src/features/settings/SettingsScreen.tsx | 12 | 0 | 0/0 → 0/0 |
| src/features/customers/AddCustomerInline.tsx | 9 | 0 | 0/0 → 0/0 |
| src/features/customers/CustomersScreen.tsx | 9 | 0 | 0/0 → 0/0 |
| src/features/reports/ProfitScreen.tsx | 9 | 0 | 0/0 → 0/0 |
| src/features/invoices/InvoicesScreen.tsx | 8 | 0 | 0/0 → 0/0 |
| src/features/shared/types.ts | 7 | 0 | 0/0 → 0/0 |
| src/routes/_authenticated/onboarding.tsx | 7 | 0 | 0/0 → 0/0 |
| **Accepted scope only** | **117** | **0** | **0/0 → 0/0** |

Existing suppressed diagnostics: AddCustomerInline2 and ShopHub2, identical before
and after by rule/severity/message/messageId/nodeType/suppression reasons excluding
positions. Other selected files have none. Disable comments, project rules,
ignores and configuration remain exactly unchanged. Continued suppression does
not approve that inherited debt; no new/wider suppression was used to pass.

## Excluded guide and baseline provenance

The initial ten candidates included guide.tsx23, totaling133. The diagnostic proof
could not establish its source/JSX equivalence: artificial JSX-cooking transpile
reported one diagnostic (assertion1!=0). The guide file was never written; it
remains the exact base blob. This is a proof-method limit, not a demonstrated
application bug or an accepted formatter output. Under the explicit exclusion
rule, it was removed and replaced with the next eligible saved candidate,
onboarding.tsx7, after a separate fresh pre-format ESLint call.

Original candidate diagnostic records are retained (JSON was reserialized after
parsing; not byte-identical CLI stdout). Accepted baseline JSON comprises
exactly the nine accepted records from that actual initial pre-format CLI output
plus the actual replacement pre-format record; both CLI calls exited1. It is not
falsely described as a single fresh ten-file baseline CLI run. Initial candidate
133 is not the final117 or a global count. The first post-format lint call still
included untouched guide and exited1; no later checks from that command were
credited as executed. The corrected accepted-ten lint call exited0. The initial
per-file proof exclusion and diagnostic outputs are archived without rewriting
the application to satisfy a comparator. No candidate beyond the necessary
replacement was measured, and no eleventh file was formatted.

## Change and preservation proof

Exact pinned Prettier3.8.3 output with existing project configuration only.
Ten source files change; shared/types.ts is a handwritten type declaration module,
not generated output. No types, logic, literals, Hook dependencies, finance/data/
API/RPC/auth/SQL contracts, dependencies/lock/esbuild exception, configuration,
lint rules/ignores, tests/workflows, app.tsx, completed FORMAT-02 files, guide or
other generated source changes. No eslint --fix or nonformat-rule repair.

The diagnostic runner verifies exact formatter output/check/idempotence, full
source/type AST including literals/operators/callbacks/Hook arrays, emitted
runtime AST, and comment type/order/content equality. JSX strings are cooked by
TypeScript itself; only adjacent literal strings on intrinsic host elements are
combined for comparison. Custom-component/fragment child segmentation, meaningful
spaces, expressions, attribute values and order remain significant. This proves
meaningful text/executable/type structure, not byte-identical emitted JS or every
native DOM text-node boundary. Comparator controls are diagnostic evidence, not
new application behavioral tests.

After accepting nine original files, the runner's write precondition was adjusted
to accept either the captured base or its exact already-proven formatter output.
This permits revalidation with the replacement file and rejects unrelated work;
no code output was relaxed or manually altered. All final ten pass. The independent
reviewer used a separate TypeScript-node/source/runtime comparator and nine
negative controls, independently checked raw baseline assembly, exact formatter,
suppressed diagnostics, saved ordering and every committed source blob. See
REVIEW.md for actual methods, versions, checks and limits.

## Local checks and native Quality

Actual local commands, repository root, Bun1.2.14:

```bash
# Existing ESLint CLI: initial candidates, replacement only, accepted-ten after.
node_modules/.bin/eslint <explicit-candidate-paths> --format json
node /workspace/.format03/proof.cjs
node_modules/.bin/eslint <explicit-final-ten-paths> --format json
bun install --frozen-lockfile
bun run typecheck
git diff --check
```

Accepted lint117→0/0warnings; frozen/typecheck/diff checks PASS. Actual resolved
Prettier3.8.3, TypeScript5.9.3, Babel7.29.7 and ESLint9.39.4 match locked tools.
No new behavioral tests or workflow. Existing native unchanged Quality owns its
unit/boundary/browser/build checks; no old packet's local results/counts are
promoted to this source. No historical advisory/audit/G1/production/database
journey was executed and no rerun is justified solely by inaccessible logs.

Native source/run/step and current synthetic-ref reconciliation follow below.

## Native source and result

Existing unchanged [Quality39123211326](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39123211326),
attempt1/job117662896770: **COMPLETED SUCCESS** on executable source8916bec5,
2026-10-18T11:26:01Z–11:27:56Z. Parent and independent reviewer verified actual
API run/job metadata: every listed19 setup, required and post step is successful,
including frozen install, typecheck, changed-file lint, unit tests, offline server
boundary, pinned browser tooling, containment regression, mode-specific build,
normal build and tracked generation invariance. None was merely started/skipped
or credited from an older source. The workflow and existing tests are unchanged.

The reviewer owned one raw-job-log download attempt; it failed exit1 at redirected
productionresultssa1.blob.core.windows.net, with0outputbytes. No exact HTTP status
was established and no signed URL/raw sensitive stderr was saved. Thus no native
exact test counts, stdout or log-derived runner checkout SHA are claimed; previous
packets'403/counts are not promoted here. No job/log retry solely for this limit.
Sanitized failure, successful API receipts and actual local targeted proof/lint/
typecheck outputs are retained separately.

Current synthetic PR mergec4f6a7bf738cfc87024bb5880a6fc3be6b0dc5b2 tree
`fe63a2de6f1c17c442247a66250b47975c96d613` independently equals executable source
8916bec5's tree. This is current-ref reconciliation, not an actual merge or a
log-derived proof of a specific runner checkout. After-test delivery changes are
documentation/evidence/checkpoints only; no native final-doc-head rerun claimed.

## Delivery, rollback and remaining work

User explicitly authorized this batch. Live OPEN/DRAFT72/head3b4a312 and all109
#55/23 #70 comments inspected, previous claim CLOSED/no newer competitor. Sole
claim55/6249300481 registered before formatting, then updated transparently for
excluded guide/replacement117 scope. Head/claim rechecked before fast-forward
uploading source8916bec5 to the existing same draft branch. No new PR/history
rewrite; only Quality was triggered.

Rollback is an additive commit restoring only the ten accepted table paths from
3b4a312. Preserve untouched guide, app's missing-customer remedy, earlier FORMAT-02
and security/dependency changes, configs, evidence and history. Restores117formatter
diagnostics; no data/schema compensation. Do not reset or force-push.

This reaches ten accepted files; eligible files were not exhausted. Remaining
categories are lower-ranked saved handwritten formatter candidates not measured
here, excluded guide needing a supported equivalence proof, mixed other-rule/type/
Hook-warning work, inherited suppressions, generated-source handling and .cjs
coverage. No fresh remaining-project total is inferred from117 or historical
counts. ONE NEXT belongs to planning another bounded G0 disposition; stable-source
identity and affected G1 follow cleanup stabilization. G0/integration/release gates
remain open. No automatic next batch, G1, merge or deployment.
