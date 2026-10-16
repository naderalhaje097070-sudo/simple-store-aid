# Approved generator graph analysis before adoption

Preparation73c1ed9e30e28465b61817dc2ceb4d54c99f6b94/run38895947249 uses original86d5lock, temporary paired @babel/core7.29.7 constraints and approved official Bun1.4.0+34cbb9a40. Whole output remains lockfileVersion1, compatible with CI1.2.14; no manually edited entries. Generated blob9d67e2d531d27fc7e5204204526e01a71bc477b6.

7.29.6 is the first security patch, but a single global7.29.6 pin would downgrade two already-safe7.29.7 copies and violate TanStack parents^7.29.7. Global7.29.7 is the smallest compatible single pin; it reuses a version already present. No parent version changes. The all-copy security floor remains7.29.6 within stable7.x, rather than requiring artificial version uniformity.

The complete generator output changes223 lock package paths because Babel packages are hoisted/deduplicated or moved to preserve other consumers' old requirements. This is not223 package upgrades. Unique locked versions change958→952 (generator total including workspace959→953). There are **zero newly introduced package versions**, zero metadata/integrity changes to retained versions, and **zero changes to non-@babel package records**. All old unaffected versions remain available to their consumers; no broad compiler-family version bump. Full path and before/after inventory: approved-graph-delta.json; unique-version proof: version-comparison.json.

Exactly six unique versions are removed:
- @babel/core7.29.0 — targeted vulnerable version.
- @babel/helper-compilation-targets7.28.6 — core7.29.7 requires^7.29.7; existing7.29.7 reused.
- @babel/helper-module-transforms7.28.6 — core7.29.7 requires^7.29.7; existing7.29.7 reused.
- @babel/helpers7.29.2 — core7.29.7 requires^7.29.7; existing7.29.10 reused.
- @babel/compat-data7.29.0 — helper-compilation-targets7.29.7 requires^7.29.7; existing7.29.7 reused.
- @babel/helper-validator-option7.27.1 — helper-compilation-targets7.29.7 requires^7.29.7; existing7.29.7 reused.

These necessary direct/transitive changes were explained to the owner before adoption. They are within the requested smallest compatible Babel security remediation and do not change Vite, TanStack, Workbox, node-server, esbuild or any other package versions. No application/source-map configuration/SQL source change. Both existing safe core7.29.7 copies retain that version, resolving to the deduplicated root after generation; no downgrade.

Frozen install, installed manifests/ranges, actual per-parent transform contracts, typecheck/two builds/Quality and full audit remain required. A successful generator is not verification or G0 acceptance. The final exact graph is checked against this inventory and independent version/metadata/non-Babel invariants.
