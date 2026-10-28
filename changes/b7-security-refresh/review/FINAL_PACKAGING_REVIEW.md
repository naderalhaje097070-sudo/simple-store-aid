# Independent B7 packaging and compatibility review

Reviewer: `/root/b7_packaging_review`, independent from the sole implementer. Read-only source/artifact review; only reviewer receipts under `reviewer-b7-packaging/` were written. No application source, GitHub state, live environment, database or new test payload was changed.

**Verdict: Approved for human merge within the reviewed packaging and dependency compatibility scope.** No introduced Critical, High or Medium finding was identified in this scope. This is not whole-B, release, security-audit or deployment approval. The lead must combine it with the other required current-head evidence and owner decision.

## Exact source

- Canonical repository: `naderalhaje097070-sudo/simple-store-aid`, repository ID1281463067.
- Reviewed candidate: `086986fd5ab36a4718e38e7a86a84705cc6fdc7e`, actual tree `83ccbf2dc504b4f51b1e1b3f84174b42da65862b`.
- Independently fetched PR71 is open/draft/unmerged at this SHA; accepted main is still `18700dee8ecdda2e457c0aa18c4f83a81b042019`.
- Independently fetched full, nontruncated remote candidate tree and source manifest: the exact protected path set, blob SHA and modes match all388 entries. All `src/**`, `vite.config.ts` and all50 migration bytes/modes match baseline `32af64252c1b5a3d305826c1b731d654c9231fd9`.
- Candidate086 differs from625 only in formatting `qs.cjs` and `rollup-parent.cjs`, plus their manifest hashes. The latter was verified against the actual current remote tree, rather than inferred from the manifest's earlier snapshot-tree reference.

## Archive and reproducer

Independently read `scripts/prepare-b7-rollup.py`, original preserved registry metadata/pack receipt, all original/local tar members, and the complete three-file readable diff. Ran the existing reproducer twice against the preserved official source tar, writing only reviewer outputs. Both archives are byte-identical to one another and the checked-in vendor tar.

- Original SHA256: `7d25e2b297ecf73542673e8ce4ca150443c3caf40269406371b94d883e0a7ced`; its SHA512 integrity and SHA1 shasum match the preserved registry metadata.
- Vendor SHA256: `65b6a7601477e78935f6f65f4bb1a256511a4d705ccd6520b79937ac30cbcbcf`.
- Original eight regular members normalize to seven canonical paths. `package/./dist/cjs/index.js` and `package/dist/cjs/index.js` contain identical bytes. The reproducer explicitly checks equality before deduplication; conflicting contents fail. No source link/device member was present; unsafe path forms are rejected.
- Output has the same seven canonical files, sorted names, regular0644 members, uid/gid0, timestamp0 and deterministic gzip metadata.
- Exactly three canonical files differ: `package/package.json`, `package/dist/cjs/index.js`, `package/dist/es/index.js`.
- `package.json` changes only removal of `deepmerge:^4.2.2` from dependencies. Genuine package name/version `@rollup/plugin-node-resolve@16.0.3`, MIT license, exports, entry points, engines, peers and every other package field are unchanged.
- Each distribution changes only removal of its deepmerge import and replacement of the sole `deepMerge({}, defaults)` call with `JSON.parse(JSON.stringify(defaults))`. `deepFreeze`, option handling and all resolver code remain exact. LICENSE, README, TypeScript declarations and ESM package metadata remain byte-identical.

## Compatibility and graph

The cloned object is internal and static: five arrays containing strings or no elements, plus two booleans. For this exact value, JSON cloning preserves all values/arrays and their order. It does not involve functions, undefined, prototypes, Dates, cyclic values or caller options. Existing shallow option spread is unchanged. The exported clone remains separate from internal defaults and recursively frozen; public exports/types are unchanged by inspection of the complete byte delta.

Independently parsed the preparation baseline and final lock. The additional graph delta is exactly `qs6.16.0→6.16.1`, replacing the Rollup parent with the local vendor tar, and removal of the sole deepmerge node. No package is added and no other package tuple changes in this additional delta. Parent dependency metadata removes only deepmerge. Root manifest changes from that preparation source are exactly the qs override/resolution and local Rollup parent override/resolution. Current package.json and bun.lock are byte-identical to the successful final preparation candidates.

Read the existing `rollup-parent.cjs` and `qs.cjs` contracts without adding or running attack experiments. The resolver test independently specifies expected DEFAULTS, checks nested freezing and instance isolation, and uses both published CommonJS and ESM APIs in an actual Rollup resolution. The fixture itself is an ESM package; it is not exhaustive coverage of every resolver option or CommonJS input shape. The unchanged resolver bytes and real application build provide the complementary compatibility evidence.

## Current native evidence inspected

Independently fetched actual run status, attempt and all job steps for current-head PR runs40683442408 and40683442436: both completed SUCCESS, attempt1, candidate086. Independently fetched artifact metadata and matched downloaded ZIP SHA256 to GitHub's digest for the following artifacts:

| Artifact | Run | SHA256 | Inspected result |
|---|---|---|---|
|12814500555|40683442408|56ed4ff59745c342b60134b7746c4a2b5ebdcc1f2f1d64684322c80864619a8d|Actual source086;388 protected/50SQL identity; expected CJS+ESM DEFAULTS, freezing, isolation and real package resolution pass; qs ordinary compatibility and retained bounded baseline/current receipts pass.|
|12814211505|40683442436|4ae86a5568ef04a54d0449933cd0dac2f300955e569bdeda3673a288fedc1e13|Frozen native install/build steps pass; before/after identity source086 and388/50 exact; actual Node HTTP and installed sanitizer receipts pass.|
|12813747404|40683442436|122b0b743d5a2eec442677153d4af16e5cb8797bcd4f6694c33abb5bd444dd30|Supported complete current audit step succeeds; raw.json is exactly an empty object.|

The Node HTTP/sanitizer receipts' `source` field is `f3088b7111b7497838e25e6ae89cbe7199301d49`, the PR event's GITHUB_SHA value. Their scripts read GITHUB_SHA directly; this is not the checked-out source identity. The workflow explicitly checks out the PR head and the separate before/after identity receipts establish actual source086. This label distinction is retained rather than rewritten.

No native test was rerun by this reviewer. Existing native receipts and successful steps were inspected. Earlier preparation and625 results were not relabeled as086 runtime results, and previous independent approvals were not adopted as this reviewer's new approval.

## Limitations and handoff

- The local materialized directory is not a Git checkout and is incomplete/stale outside this review's exact files:339 protected bytes match current remote,45 protected files are absent,4 differ. Full local `verify()` was therefore not claimed or run. Exact388 path/blob/mode verification instead used independently fetched current remote tree/manifest plus current native identity receipts. Reviewed package/script/test/lock files match the current remote blob identities.
- Integrity matches the preserved registry records; this review did not re-fetch the live npm registry or independently validate its signature key chain.
- This review does not establish production exploit reachability, exhaustive API behavior, whole-application security or release readiness. It does not repeat prior broad B6 review.
- The lead owns the remaining current-head lifecycle/expiry/general CI evidence, overall PR readiness record and the protected human merge decision. No merge or deployment was performed or authorized by this review.

Supporting receipts: `PACKAGING_CHECKS.json`, `SOURCE_CHECKS.json`, `GRAPH_CHECKS.json`, `REMOTE_TREES.json`, `REMOTE_SOURCE.json`, `NATIVE_RUNS.json`, `NATIVE_ARTIFACTS.json`, and the two reproduced archives/patch receipts.
