# SEC-DEP-20261102 — actual compatibility investigation,2November2026

The two findings remain in the project's current full audit. A concrete interop candidate is ready for an owner decision; it has not been applied to the application or accepted as a complete remediation.

Base: `b587742231287219e9302d6af70dc128e19e25e0`; main220fc206 and original five draft heads unchanged. Sole claim55/6580198545. No financial, SQL, app, package, lock, vendor or CI-source change in this investigation.

## Observed results

| Boundary | Actual result | Limit |
|---|---|---|
| Exact application audit | Bun1.4.0 exit1; two Moderate records, glob/minimatch | Exact Git blobs package2b01ba68 /lock6d017ff0; no suppression |
| Locked public source |37official archives verified;29also match the project's locked SHA512 | Other8archives are selected inspection/candidate packages, not an installed full app |
| Baseline consumers |8/8 pass | Locked config-array, filelist, glob and inspected eslintrc; Node24.22.1 Linux |
| Blind global11 |5/8 pass,3expected failures | Actual config-array/eslintrc ESM imports fail missing default; generic old callable contract fails |
| Scoped modern graph |8/8 pass | Manually materialized diagnostic graph, not a generated lock or complete remediation |
| Native patch prototype |8/8 pass; fresh frozenBun1.2.14 install pass; prototype audit{} exit0 |33-package public subset; not the1099-entry project graph or full PWA build |
| Vendor fallback prototype |8/8; fresh frozen install and subset audit pass | Extra maintained archive; not adopted/recommended |
| Nested/version-scoped rules |Generator1.4.0 succeeds, emits lockv3; old consumer rejects with exit1 | Both npm nested and version selector forms tested; no manual lock downgrade |
| Glob cancellation |Old11:15total/12after rejection; new14:1total/0after rejection |15dummy files/directories,100ms observation,pending0; instrumented real filesystem |
| Minimatch amplification guards |Old10 ignores configured8row cap and reaches32; new11stops at8. At1001rows old second phase invokes500500 comparisons, new0 |Five repetition maximum; comparison body counted/returned false;128MiB/3s process bounds, not an availability attack |

The40consumer cases comprise37passes and3specific expected red controls; they do not mean40independent product features. ConfigArray CJS and filelist actually pass the blind override in these cases; the report does not imply every legacy importer fails.

Actual TypeScript-estree match function was extracted without semantic edits and given the real resolved engine; it is not a full type-aware lint execution. Actual Workbox getFileDetails runs against real glob/files with explicit Node filesystem/path adapters for unrelated imports; it is not a complete Workbox build. Full application installed/types/lint/build/browser/native finance/Windows and independent review were not run in this diagnostic batch.

## Root causes and source review

[glob maintainer advisory](https://github.com/isaacs/node-glob/security/advisories/GHSA-3g3m-2fjr-6pw4) identifies missing returns after cancellation. The small-tree control reproduced continued reads on the exact locked11.1.0 and none after rejection on14.0.2.

[minimatch maintainer advisory](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249) describes optimization-level2 amplification. The registry reports a broader<11.0.1 range than the maintainer's stated10.2.6 reproduction. Locked3/5source does not contain firstPhasePreProcess/optimizationLevel; this is source-based scope evidence, not permission to suppress registry findings. Both locked10.2.5 paths do have that code; glob11 explicitly requests optimizationLevel2. The bounded controls prove the new cap/cutoff without exercising the100000row default cap or a denial of service.

Seven current direct dependency edges were found across dependencies/optionalDependencies/peerDependencies in all1099lock entries: ESLint/config-array/eslintrc→3;filelist→5;TypeScript-estree/glob→10;Workbox→glob11. Latest-parent snapshots from the preceding intake do not solve the declared-major mismatch. Source inspection and hashes for13relevant package files are retained.

## Concrete candidate and decision boundary

Recommend the standard Bun patch route in [PROPOSAL.md](PROPOSAL.md): official glob14.0.2/minimatch11.0.1 with four export-only interop additions. It crosses declared consuming ranges and changes third-party exports locally. Existing intake forbids a global major override; owner authorization of this exact exception is required before applying it to the integration project. No earlier esbuild permission is transferred.

The generated patch is1783bytes/SHA2561c2e49a5e9608bdf3b904c9f3ee62b02cc8677e46167ec9d70f117cd3dc07015. Four files change;33official engine files stay byte-exact. Current Bun1.2 applies the additions with only terminal-LF normalization; all installed bytes are independently accounted for. No matching algorithm patch, new Bun version, registry finding waiver, local vendor replacement or age-rule exception is proposed.

## Failed evidence and corrections preserved

- Initial safe tar extractor rejected FileList's legacy FileList-v1.0.6 archive root. Only this exact verified package/version root was admitted; traversal/regular-file/size/integrity checks remain.
- Fresh empty Bun1.4 prototype projects emittedv2 locks rejected by Bun1.2. This was a baseline mismatch, not evidence that the native patch itself is incompatible. Reproductions were corrected to start from a real Bun1.2-generatedv1 baseline, matching the project's existing-v1 situation; no lockfile text was edited.
- After that correction, the patch hash assertion failed on final-LF normalization. Preserved before/after inspection proves only one terminal LF differs on intended additions. The corrected safety check allows that exact difference only on the four declared files; all other bytes must match.
- A prototype audit was started while its lock was being regenerated and failed “missing lockfile”. It is retained as a scheduling mistake; the final audit ran sequentially after generation/frozen install and returned raw{}exit0.
- The first scratch application-audit replica contained an extra trailing LF. Both files were restored to their exact Git blobs and audited again; final exit1/two findings remain.
- The two-directory initial glob probe observed no work after rejection; a small15directory tree then reproduced12post-rejection reads. No exploitation claim relies on the initial inconclusive boundary.

The full project has not been repaired in this batch. Current exact audit failure, failed fixtures, prototype commands, v1/v2/v3 locks, engine inventories, official provenance and the proposal patch are retained in COMPATIBILITY_INVESTIGATION.zip and receipt JSONs. The archive excludes runtime binaries,node_modules and original library tarballs; pinned public sources are reproducible from the scripts/provenance. The top-level reproduce.py orchestrator was syntax-checked; individual stages were actually executed, not a new complete orchestrator rerun.

## ONE NEXT

Owner decision on the exact range/interop exception in PROPOSAL.md. If approved: prepare/apply the bounded candidate, generate/review the full lock, extend fail-closed SEC source admission and run full affected project gates. If rejected: keep current audit blocked and investigate publisher-supported alternatives; no silent global override or scan suppression. Then C5/C6/C7. No merge/deploy/production/newcost/newPR/closure/historyrewrite.
