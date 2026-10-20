# G0-BABEL-01 — bounded candidate handoff

All affected @babel/core copies are remediated without downgrading already-safe7.29.7 copies. The actual old root exposes two local outside-root sourcemap markers; all identical contracts pass on the corrected installed distribution. **The target advisory disappears; G0 remains open** for node-server/esbuild findings and inherited lint, and final-lock G1 acceptance remains unverified. Candidate status: Implemented/Tested, not Merged/Released.

Canonical repository naderalhaje097070-sudo/simple-store-aid, existing DraftPR72 abovePR54/57fb508b9d239aaf4676352dd97654341416c46a. Branch `test/g0-g1-acceptance-runtime-2026-10-14`. Start86d5a87bc8b38c1bd0c173a0fb28987c0291dfa0; sole claim55/6214726307 closes at final linked55/70 handoff. Executed source **1e80a33d5f0c766c89259aad9b9db4fce2492fdd**, tree4c28eb6b86369774f554f8cc1c16b097a34d813a. Later delivery is documentation/checkpoints/evidence only; final head/Quality receipt are in55/70. Main and PR48 remain unchanged.

## Root cause, official patch and version choice

Official [GHSA-4x5r-pxfx-6jf8](https://github.com/babel/babel/security/advisories/GHSA-4x5r-pxfx-6jf8) identifies <=7.29.0 as affected,7.29.6 as the first7.x patch. Untrusted compile input with a known external source-map path can disclose its sourcesContent through compiler output. No exposure of an application route is inferred. The official tagged [7.29.6 normalize-file](https://github.com/babel/babel/blob/v7.29.6/packages/babel-core/src/transformation/normalize-file.ts) and [map reader](https://github.com/babel/babel/blob/v7.29.6/packages/babel-core/src/transformation/read-input-source-map-file.ts) show package/root-limited automatic map resolution; legitimate same-directory/within-root maps remain supported. Tagged7.29.7 manifest was also verified (blob48fa8bd0e096528e202efe795beaf2451952b01c).

Starting bun.lock contains root7.29.0 and two nested7.29.7 copies under router/start plugins. Five direct parent declarations are ViteReact^7.29.0, dead-code-elimination^7.23.7, Workbox^7.24.4 and two TanStack^7.29.7. A single7.29.6 override would downgrade safe copies and violate the latter ranges.7.29.7 is the smallest compatible single pinned version already in the graph; the security guard independently accepts stable7.x>=7.29.6. Modern scoped overrides require lockformat3 incompatible with existing CI1.2.14, so no toolchain/lockformat migration is introduced. Published7.29.7 dependency minima and all parent ranges were checked. Existing npm package-lock.json is unchanged; its Babel7.29.7 was already safe and is not the active Bun source of truth.

## Approved whole-lock graph and necessary dependency effects

Only @babel/core7.29.7 is added to existing paired overrides/resolutions. No direct dependency and no Vite/TanStack/Workbox/node-server/esbuild upgrade. Complete official npm Bun1.4.0+34cbb9a40 output is adopted after integrity verification and review, from exact86d5lock plus unchangedbunfig in a temporary directory: `bun update @babel/core --lockfile-only --ignore-scripts`. No generated entry was hand edited. Git blob **9d67e2d531d27fc7e5204204526e01a71bc477b6**; SHA256 **c766c8793b8cd04c5c0e656c1eba816910d6595151210439584a828a12f929bf**, also retained in preparation/sha256.txt inside preparation.zip. Generator total959→953 including workspace; unique versions958→952.

**223 changed lock paths are hoisting/deduplication and necessary Babel resolution changes, not223 package upgrades.** There are zero new package versions, zero changes to retained version metadata/integrity, and zero changed non-@babel package records. All safe core7.29.7 remains; three physical distributions become one shared7.29.7 distribution, with all five parents resolving to it. No safe-copy downgrade.

Exactly six old unique versions are removed: core7.29.0, helper-compilation-targets7.28.6, helper-module-transforms7.28.6, helpers7.29.2, compat-data7.29.0 and helper-validator-option7.27.1. Core7.29.7's required^7.29.7 compiler internals reuse existing7.29.7/7.29.10; compilation-targets7.29.7 in turn requires the existing newer compat-data/validator-option. These are necessary dependency minima, not unrelated cleanup. Other old Babel versions still needed by independent consumers are retained and relocated. This scope was explained to the owner before adoption, and recorded in GRAPH_ANALYSIS.md with complete approved-graph-delta.json and version-comparison.json.

The verification checks both the exact approved path inventory and independent no-new-version/retained-metadata/non-Babel/exact-six-removal invariants. It also retains manifest/bunfig invariance, parent semver and prior Hono4.13.7/qs6.16.0/DOMPurify3.4.16 floors. Baseline has86parent declarations (5direct/81peer); corrected hoisted graph has80 (5direct/75peer), all admitting7.29.7. Actual parent versions remain fixed.

Only existing package.json/bun.lock/security-floor test change. Added paths are two read-only hosted workflows, actual-package tests/evidence helper and intake/impact/graph/evidence records. All122 application files,41 migrations,43SQLfiles and source-map/build configurations are byte-identical to start. No API/RPC/financial/authorization/schema/tenant/state contract change.

## Actual verification

| Run and source | Actual result |
| --- | --- |
| [Preparation38895947249/job116956318852](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38895947249/job/116956318852),73c1ed9e30e28465b61817dc2ceb4d54c99f6b94 | Frozen original Bun1.2.14 install, actual three-core presence/parent resolution and official generator PASS. Node18contracts:16PASS, exactly2targetedFAIL on old root7.29.0,0skipped, rawexit1 retained. Controller accepts only that exact expected-red set; safe nested7.29.7 copies each pass all6cases. |
| [Corrected38896279667/job116957405767](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38896279667/job/116957405767),1e80a33 | Frozen Bun1.2.14/whole graph/all actual parent/physical copies,6unique-distribution contracts,9guard controls,affectedCJS+TS lint,tracked-source invariance PASS. Full supported1.4.0 audit returns1 for remaining findings, so job correctly concludes **FAILURE at audit only**. |
| [Quality38896289565/job116957437990](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38896289565/job/116957437990) | **SUCCESS**:64unit/141expect including4existingMCP fixtures; typecheck/changedlint,8stub wrapper and67dummy browser containment cases, two approved isolated builds. Actual synthetic checkout9ba97d4324b266edd29cac2dc2a38b4d080c3cf8 has tree4c28eb6b86369774f554f8cc1c16b097a34d813a equal to tested source, confirmed via GitHub commit API. No actual merge or G1 acceptance. |

The actual Node fixtures use a temporary dummy package, source and small valid sourcemaps. Relative and absolute references outside the package must not expose LOCAL_ONLY markers in output.map.sourcesContent. Positive controls retain a sibling map, parent-directory map still inside the package, inline data-map and plain-source map. configFile/babelrc false isolate unrelated config; **inputSourceMap stays at its default automatic behavior and sourceMaps is true**. Application config is untouched. No external connection, real file/secret, plugin code execution, DB or financial write occurs; finally removes only the fixture temp directory.

Counts18→6 reflect three distinct installed distributions deduplicating to one; no test case or assertion is removed. All five actual parents resolve the same tested7.29.7 entry after correction. There are six cases per distribution and zero skips before/after. Raw TAP, map observations, versions and failed marker evidence are preserved. This proves scoped content-disclosure behavior, not complete filesystem-read telemetry, symlink/reachability coverage or production exploitability.

Every-copy stable7.x guard floor is7.29.6; absent/old/prerelease/major8/nested-old are rejected. Nine actual Bun mutant controls are patchedPASS and eight expected nonzero negatives, including retained Hono/qs/DOMPurify floors. Independent review additionally checks legitimate7.29.6 and mixed safe nested7.29.7 acceptance, distinguishing its Node assertion-adapter replay from actual Bun execution. No existing guard was weakened. No broad lint run/cleanup or new full-lint total.

## Full audit, review and remaining gates

Raw audit.stdout/audit.stderr/audit.receipt.json and audit-summary.json preserve complete supported `bun audit --json` stdout/stderr/hash and **exit1**. audit-comparison.json against the DOMPurify packet proves exactly GHSA-4x5r-pxfx-6jf8 removed and no new ID/Critical/High in this observation. No fixed count acceptance or risk waiver.

| Remaining | Severity | GHSA |
| --- | --- | --- |
| @hono/node-server | Moderate | GHSA-frvp-7c67-39w9 |
| esbuild | Low | GHSA-g7r4-m6w7-qqqr |

REVIEW.md records actual separate-agent review and exact reexecuted static/Python/Node/hash/semver/receipt/log checks. No independent Bun/compiler transformation/Playwright/DB rerun is claimed. Overall protocol outcome remains Blocked pending missing evidence, not human merge approval. Artifact index records retained ZIP hashes and a bounded secret-pattern scan; expected-red raw failure is retained.

No live G1 rerun; historical40/40 belongs todbc870/oldlock and is not this lock's acceptance. Source54 identity guard remains unchanged and fail-closed. Before integration acceptance, explicitly reconcile/freeze/review final manifest/lock/tests/checkpoints, then run affected actual runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof. Prior successful offline/wrapper/unit fixtures do not substitute. Remaining G0 lint/advisory and G2/release requirements stay open; PR48 remains open.

Rollback: additive revert of candidate constraints/whole generated lock/guard/fixtures with frozen/security/typecheck/build checks. Restoring the vulnerable baseline is not a production security remedy; production untouched, no data/migration compensation.

ONE NEXT: planning selects one separate remaining G0 disposition; preserve final-lockG1 prerequisites. Save final head and verified source in55/70, close claim and stop. No production/customer/Paddle/newcost/migration/merge/deploy/newPR or launch approval.
