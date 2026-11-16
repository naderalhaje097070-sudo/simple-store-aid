# C6-MAIN-SYNC: merge `main` into integration (C6/C7 plan, item 1.1)

- **Date:** 2026-11-16
- **Owner decision:** «موافق» ("agreed") on 2026-11-16, given to start C6/C7. Under docs/reviews/C6C7_PLAN.md, each production item still needs the owner's approval of its own exact scope. This change does not touch production or `main`.
- **Target:** `integration/g0-g1-reconcile-2026-10-18` at b32d591. Merged in: `main` 1c5276f.

## Why
`main` is 16 commits ahead of integration: the Lovable sync #80 and the gate bootstrap #73/#74. The C6 candidate must contain `main`, otherwise the integration → `main` PR would revert Lovable's sync. Plan item 1.1 requires a normal merge through a PR.

## What the merge brings from `main`
- `@lovable.dev/vite-tanstack-config` 2.9.1 → 2.26.5. The lock follows: `lightningcss` 1.32 → 1.33 hoisting, the ajv helper re-hoisted under workbox-build, and the two `@lovable.dev/vite-plugin-*` packages that 2.9.1 depended on removed.
- `src/integrations/supabase/client.ts` and the new `previewAuthStorage.ts`: Lovable's preview auth storage, reviewed in #80.
- `src/integrations/supabase/types.ts`: added parentheses only, from the generator; no type change.
- `scripts/generated-format-manifest.json` and `tests/g01-acceptance/integrated-b-source.json`: the identity refresh from #80.
- `.lovable/plan/…2026-11-09.md`: a Lovable plan note; documentation only.

## Conflict resolution
| File | Resolution |
|---|---|
| package.json | `main`'s Lovable pin, plus integration's hono 4.13.16 and @hono/node-server 2.1.6 (SEC-DEP-HONO-01). |
| bun.lock | `main`'s lock, byte-exact, with exactly the four reviewed hono lines replaced. This is the #93 method. It installs with `--frozen-lockfile` on Bun 1.2.14 and on 1.4.0. |
| tests/release/gate.py, test_gate.py | Integration version. It is a strict superset of `main`'s: FINANCIAL_CORE, PRIVILEGED_MARKERS and the out-of-order migration check. |
| tests/unit/dependency-security.test.ts | Integration floors (@hono/node-server 2.1.6). |
| evidence/g0-*/**.json | **Not taken.** Lovable's bot committed these test outputs to `main` (f01540c). On integration they are untracked run output: integrated-quality moves them out of the checkout, then requires a clean checkout. |

Neither lock is a fixed point of `bun install --lockfile-only`: `main`'s rewrites 16 lines and b32d591's rewrites 82. So a regenerated lock would also change unrelated bytes. Keeping `main`'s bytes plus the reviewed lines is the smallest reviewed delta.

## Dependency admission (layered, no earlier control weakened)
- **20261102:** unchanged. It still proves 50530716 → 2e4c8cc from its prepared directory.
- **20261116:** `graph.py` is unchanged. `test_graph.py` gains an optional prepared-directory argument, the same as the 20261102 harness has. CI now runs it on the exact b32d591 inputs it reviewed: 24/24 pass.
- **New, `tests/sec-dep-c6-main/`:** admits exactly b32d591 → head.
  - `package.json`: b32d591 with only the Lovable pin changed. Checked both semantically and byte-exact.
  - `bun.lock`: byte-exact `main` lock plus the four 20261116 lines.
  - An independent row-delta pin: 1086 → 1070 entries, with 13 added, 29 removed and 13 changed paths, listed by name. Every added or changed row, except the Lovable package itself, must be byte-identical to a row already reviewed at b32d591.
  - The hono rows must remain exactly in place.
  - `--installed` checks hono 4.13.16, @hono/node-server 2.1.6, vite-tanstack-config 2.26.5 and lightningcss 1.33.0.
  - 24 adversarial controls.
- **Release age:** bunfig keeps 24h. The npm publish times are 2026-10-09 for vite-tanstack-config 2.26.5 and 2026-07-20 for lightningcss 1.33.0, both older than 24h. `@lovable.dev/vite-tanstack-config` is already in `minimumReleaseAgeExcludes`; that list is unchanged.
- **Registry:** the `lovable-core-prod` mirror URLs are not new. b32d591 already had 483 of them, and the head has 478. The integrity hashes are pinned.

## Local verification (actual commands and results, before push)
- `bun install --frozen-lockfile`: Bun 1.2.14 exit 0, and Bun 1.4.0 exit 0.
- `python tests/sec-dep-c6-main/graph.py --installed`: pass.
- `python tests/sec-dep-c6-main/test_graph.py`: 24 OK.
- `python tests/sec-dep-20261116/test_graph.py <b32d591 inputs>`: 24 OK.
- These passed:
  - `test_identity` for g01, c-source, c4-sale and 20261102;
  - 20261102 `installed`, `test_installed` and `contracts.cjs`;
  - `dependency-security.test.ts`;
  - `tests/release/test_gate.py`.
- `bun run typecheck`, `bun run lint` and `bun run test:unit`: pass.
- Wire replays passed: webhook-bridge, webhook_handler, c4-sale contracts, g0-node-server contracts, 20261029 regressions, current-contracts and test_build_entry.
- `bun run build` with the CI env: pass, and the checkout stays clean.
- **Not run locally:** release-finance, audit and the browser suites. They run in CI.

## Risks and unverified items
- The Lovable build plugin version changes for the integration build. Production, fin-biz.shop, is built by Lovable from `main`, which already uses 2.26.5, so this change does not alter what production builds with.
- JOURNEY-FLAKE-01 is still open.

## Rollback
Revert the merge commit on integration with `git revert -m 1 <merge>` through a PR. No production state is involved.
