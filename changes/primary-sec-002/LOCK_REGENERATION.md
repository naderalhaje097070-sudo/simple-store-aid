# PRIMARY-SEC-002 Generator Provenance

This procedure replaces the manual generated-lock edits identified by SEC2-R2.
It does not change the security floors or approve merge/release.

## Input and Tool

- Original PR52 commit: `13d81250122c890a98b0c94e4f07f2745bdb40ed`.
- Original lock blob: `b8e19f98189e3a285964b8e75559da27bc01e98b`, matched to
  PR52's remote tree and the local source snapshot before generation.
- Final manifest blob: `293395a676487cfc742caa642517f2c2323bdbac`.
- Generator: official npm package `@oven/bun-linux-x64-baseline@1.4.0`,
  Bun build `34cbb9a40`; published 2026-08-20, older than the 24-hour guard.
- Tool integrity: `sha512-bX4PG7rWFkBL9laVJP8ESdQxkngLUyUiDEgYKohY+WtGQ2n8GSlA/2S5o394eEnacjQ/WC8+gebali7KoNvEpw==`.
- Existing `bunfig.toml` release-age configuration/exclusions stayed unchanged.

Primary sources: [Bun 1.4 transitive-update support](https://bun.com/blog/bun-v1.4),
[update command](https://bun.com/docs/pm/cli/update).
Bun 1.3.14's direct update added a root dependency and left old nested copies;
that diagnostic result was discarded, not applied to the project.

## Bounded Reproduction

From a normal clone containing the PR52 commit, use Bun 1.4.0 and the final
manifest/config. Work in a temporary directory; do not edit generated entries.

```sh
test "$(bun --version)" = "1.4.0"
regen_dir="$(mktemp -d)"
git archive 13d81250122c890a98b0c94e4f07f2745bdb40ed bun.lock | tar -x -C "$regen_dir"
cp package.json bunfig.toml "$regen_dir/"
cd "$regen_dir"
bun update brace-expansion --lockfile-only --ignore-scripts
```

The generator applies the manifest's security overrides and updates all matching
brace-expansion copies within their existing parent ranges. The final manifest
pins the already-resolved Lovable MCP 0.20.1 and omits unsupported brace path rules.
All three major lines remain 1.1.21 / 2.1.7 / 5.0.12; no new direct brace dependency.

A second independent run from the original lock produced the identical output:
Git blob `efbffd2d5d0073978c374bb27b1f6398a322b8c6`. The first generated file was
copied whole into the candidate. No generated entry was manually patched or merged.
The registry can change later: a future regenerated graph must be reviewed and
tested rather than assumed identical. Frozen installation uses the saved artifact.

## Graph Impact

Compared with the previous PR53 candidate, no package version was added; all
retained package metadata and integrity values are identical. Bun pruned 30 unique
optional/orphan package versions: esbuild 0.25.12 and its 26 platform packages,
tsx 4.21.0, get-tsconfig 4.14.0 and resolve-pkg-maps 1.0.0. Vite's optional tsx peer
is not a root dependency or used by the project's scripts. The used esbuild 0.27.7
version is retained and satisfies Vite/MCP ranges. Generated deduplication also
changes some package paths; it is not an application-source refactor.

Generator-reported package count changed from 989 to 959. Text lock version stays
1; frozen installs passed with the existing Bun 1.2.14 CI version and Bun 1.3.14.
No workflow toolchain change, runtime feature, schema or financial rule changed.

## Verification and Remaining Boundary

44/44 unit tests under Bun 1.2.14, typecheck, explicit local-fixture build and
changed-source lint passed. Audit remains 0 Critical / 0 High / 11 Moderate / 5 Low.
The compatibility fixture now runs through the existing unit suite.
Raw generator, install, test, typecheck, build and audit outputs are retained in
`remediation-proofs/`; structured source identities are in `remediation-evidence.json`.

Hosted startup is blocked by the observed GitHub payment/spending annotation;
account resolution and final-candidate independent review remain required. The
engineering fix does not authorize billing changes, deployment or merge.
