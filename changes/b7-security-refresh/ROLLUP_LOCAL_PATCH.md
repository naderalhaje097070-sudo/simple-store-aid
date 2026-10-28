# Local Rollup package patch

The only resolved deepmerge consumer is @rollup/plugin-node-resolve 16.0.3. The official package uses it once to clone its static DEFAULTS object: five arrays of strings and two booleans. Resolver options already use the unchanged shallow spread of defaults and supplied options. No caller-controlled value enters this clone.

The current deepmerge advisory has no upstream patched release. The local package is therefore a transparent patch of the official Rollup package, rather than a dependency-version change or advisory exemption. Its genuine name/version and license stay intact. The deterministic reproducer scripts/prepare-b7-rollup.py changes only the package dependency list and the two published CommonJS/ESM distribution files: remove the unused deepmerge import and replace its one static clone with JSON.parse(JSON.stringify(defaults)). Deep freezing remains unchanged. All other tar members remain byte-identical; the receipt records every hash and the full readable diff.

The package override points to the repository vendor tar. The official whole-lock generator must remove deepmerge from the graph, and the existing Bun consumer must accept the frozen lock. No version is relabeled as a security fix. The current complete audit remains mandatory.

Acceptance includes exact official tar integrity, reproducibility, three-file delta, license retention, independently expected CJS/ESM DEFAULTS, nested freezing and independence from per-instance settings; the actual package resolver must still resolve ordinary CommonJS/ESM modules. Existing real application Node and default Cloudflare builds and lifecycle/expiry tests run on the final source. A successful preparation is not final application acceptance.

Rollback restores the official parent package and prior lock additively; doing so restores the known deepmerge audit blocker. No application financial contract or SQL is modified.
