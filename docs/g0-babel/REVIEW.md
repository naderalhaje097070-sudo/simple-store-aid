# Independent focused review — G0-BABEL-01

2026-10-16. Read-only review by separate agent `/root/babel_review`; no candidate or GitHub changes. Reviewed baseline PR72 `86d5a87bc8b38c1bd0c173a0fb28987c0291dfa0`, preparation `73c1ed9e30e28465b61817dc2ceb4d54c99f6b94`, tested source `1e80a33d5f0c766c89259aad9b9db4fce2492fdd` / tree `4c28eb6b86369774f554f8cc1c16b097a34d813a`.

**Protocol outcome: Blocked pending missing evidence.** The bounded Babel remediation has no new implementation finding requiring correction. This is not approval for merge, G0 acceptance, G1 acceptance, deployment or production readiness. Residual audit findings and existing full-lint/G1/final-source requirements remain open. Final delivery commit reconciliation follows separately.

## Root cause and minimum scope

Independently opened the official Babel advisory: https://github.com/babel/babel/security/advisories/GHSA-4x5r-pxfx-6jf8 . It identifies stable versions through 7.29.0 as affected and 7.29.6 as patched. The defect concerns loading external source maps while transforming controlled source; this review makes no claim that the application accepts attacker-controlled build source or is exploitable.

The initial active Bun graph contains root core7.29.0 plus two already-safe nested core7.29.7 copies. TanStack parents require ^7.29.7; a single7.29.6 pin is incompatible and would lower already-safe copies. The paired global7.29.7 pin is justified under the existing override mechanism, without a lock-format/toolchain migration. Existing core7.29.7 records are reused, not downgraded. Package-lock.json is unchanged and already records safe core7.29.7.

Independently parsed both whole Bun graphs, calculated the Git blob hash, compared against the approved generator inventory, and checked invariants without relying only on that inventory:

- Exact generated lock blob `9d67e2d531d27fc7e5204204526e01a71bc477b6`.
- 223 changed lock paths are hoisting/deduplication/path placement; they are not223 new package versions.
- Zero new unique versions, zero non-Babel records changed, zero metadata/integrity changes among retained unique versions.
- Exactly six unique old versions removed: core7.29.0, helper-compilation-targets7.28.6, helper-module-transforms7.28.6, helpers7.29.2, compat-data7.29.0, helper-validator-option7.27.1.
- Replayed semver against all80 post-dedup parent declarations (75peer/5direct). Every range accepts7.29.7. Separately proved each of the five old transitive versions fails the new published ^7.29.7 minimum declared by core or helper-compilation-targets. Their replacement is necessary dependency resolution, not unrelated cleanup.
- Hono4.13.7, qs6.16.0 and DOMPurify3.4.16 floors remain. Vite/TanStack/Workbox/node-server/esbuild versions do not change.

Baseline manifest hash comparison covers605 prior blobs; no missing file. Only existing package.json, bun.lock and dependency-security.test.ts differ at tested source. The remaining additions are scoped Babel workflows, test recorder/contracts and intake/graph evidence docs. Independently matched all622 tested-source blobs to the provided GitHub tree manifest. No application, SQL, finance, authorization, source-map application configuration, source54 identity guard or existing workflow file changed.

## Behavioral tests and negative controls

Inspected actual Node test source and all raw old/new TAP and map observations. The fixture writes only dummy package/source/map files beneath a temporary directory, uses actual parent-resolved installed Babel distributions, keeps automatic inputSourceMap behavior and enables output maps. Relative and absolute external-map references must not expose an exact marker. Sibling, parent-within-package and inline maps must retain it; plain source must retain its ordinary sourcesContent.

Preparation evidence:18cases across three actual installed distributions,16PASS/2FAIL/0skipped. Exactly the two outside-root contracts fail for vulnerable7.29.0; the same six contracts pass for each safe nested7.29.7 copy.

Patched evidence: all five parents resolve the same actual core7.29.7 distribution; physical enumeration agrees there is one installed copy. All six unique-distribution contracts PASS/0skipped. The reduction18→6 follows proven deduplication3→1 and does not remove a case or parent. Observations independently show both outside markers absent, all three legitimate map markers preserved, and ordinary source maps retained.

Reviewed all-copy dependency guard logic and nine actual Bun mutation receipts: patched passes; old/prerelease/major8/nested-old/missing and old Hono/qs/DOMPurify fail. In addition, independently executed the existing TS test logic under a Node VM assertion adapter across11variants: patched, first-patched7.29.6 and nested-safe7.29.10 pass all18security tests; each of eight invalid variants fails exactly its relevant test. This is an assertion-adapter replay, **not execution under Bun and not an independent installed-package transform**.

## Hosted evidence and raw failure preservation

Reviewed preparation log and artifact, plus bounded verification38896279667/job116957405767 at tested source. Frozen Bun1.2.14+6a363a38d installation, graph proof, installed parent/copy ranges, actual transforms, nineguardcontrols, affected CJS/TS lint and final tracked-source invariance pass. Audit uses supported Bun1.4.0+34cbb9a40. The verify job correctly fails only at full audit.

Independently validated fourteen raw stdout/stderr receipt hash pairs (two baseline and twelve patched), all48 files against the verification ZIP, and its SHA256 `1169fc232b43d51f312ee4e266611c51143f4b7e616ffe8a6326ea4a4e426eb8`. Source receipt is1e80a33. Parsed raw audit JSON rather than accepting its summary alone; comparison with the prior preserved raw audit removes exactly GHSA-4x5r-pxfx-6jf8, adds no ID, and retains:

- GHSA-frvp-7c67-39w9 — @hono/node-server, Moderate.
- GHSA-g7r4-m6w7-qqqr — esbuild, Low.

Audit's actual exit is1; no clean-scan claim or waiver. G0 remains open.

Reviewed raw Quality38896289565/job116957437990 log and source-identity receipt:64unitPASS/0FAIL/141expectations,4MCP/8wrapper checks,67dummy browser containment scenarios, typecheck, changed-source lint and both approved builds finish successfully. Its synthetic PR merge source9ba97d4324b266edd29cac2dc2a38b4d080c3cf8 has the same tree4c28eb6b86369774f554f8cc1c16b097a34d813a as1e80a33, according to the provided GitHub commit-tree receipt; the implementer separately retrieved the successful job conclusion. Existing build warnings do not imply a security or financial release acceptance.

## Actual independent execution and limits

Executed read/search commands; Python whole-graph, blob, source-tree, JSON, raw-receipt, ZIP, map-observation and audit-set checks; Python AST parse; `node --check tests/g0-babel/contracts.test.cjs`; Node semver replay for80parentranges and five necessary transitive replacements; Node VM assertion-adapter replay for11guardvariants. Opened the official advisory independently. The official release-tag page retrieval failed; the advisory plus the implementer's tagged-manifest retrieval are the version-source evidence, not a successful independent release-page read.

Did **not** independently execute Bun generator/frozen/unit/MCP, actual installed Babel transformations, ESLint, typecheck, builds, audit CLI, browser, database or live G1. Bun and installed project dependencies are absent locally. Hosted outcomes above were inspected, not independently rerun. No production data/secrets, financial writes, migration, merge or deployment.

No new Critical/High/Medium/Low implementation defect was identified in this bounded review. Existing blockers retain their prior dispositions: residual audit, inherited lint and final-lock G1 integration evidence are not waived. Exact final-source/lock identity reconciliation and affected real runtime/transport/SSR/Auth/isolation/state/counter/secrets/cleanup proof remain required; historic40/40 belongs only to its original source. Preserve the unchanged fail-closed source54 guard.

Rollback is an additive candidate revert of paired constraints, generator-owned lock and scoped guard/fixture/docs, followed by frozen/typecheck/build verification; restoring a vulnerable graph is not a production security remedy. No DB compensation applies. ONE NEXT: planning reviews the bounded handoff and chooses a separate residual-G0 disposition; no automatic broader upgrades or G1 rerun.
