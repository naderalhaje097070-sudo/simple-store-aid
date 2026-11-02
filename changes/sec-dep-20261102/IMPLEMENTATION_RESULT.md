# SEC-DEP-20261102 — implemented and tested on the integration candidate

Date: 2 November 2026. Sole implementing agent; claim #55/6580198545. **Status: Implemented → Tested for this dependency batch only. Not Merged or Released.**

## Source and authority

- Repository: `naderalhaje097070-sudo/simple-store-aid`; existing branch `integration/g0-g1-reconcile-2026-10-18`.
- Exact executable tested: `552ce47b924dd90b6b8403670989eced07bb82cf`; tree `411b79dd616b75efe350274069750498c291af87`.
- Main remains `220fc2066b4d6254b1803b5e32919c47d60a9c7e`.
- Specific owner authorization: [#55/6581232804](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6581232804), following the proposal at `50530716ab3163199de4187d3776356a49813dda`. It covers glob 14.0.2 / minimatch 11.0.1 outside declared consumer major ranges, and the 1,783-byte local export interoperability patch SHA256 `1c2e49a5e9608bdf3b904c9f3ee62b02cc8677e46167ec9d70f117cd3dc07015`. This is a specific compatibility exception, not a finding suppression, general upgrade policy, or merge/release authorization.

## Implementation and complete graph

Paired exact overrides/resolutions and the approved Bun patch are applied. Official Bun 1.4.0 regenerated the existing v1/configVersion1 lock, from the exact prior full graph; no manual lock editing. Preparation run [41473986779](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41473986779) succeeded on `b40b397990d2db6900bf02660742cc32f6549992`. It installed the full project freshly with frozen Bun 1.2.14 (815 packages; preparation used ignore-scripts), verified official tarball integrity and all 37 minimatch engine file hashes, and returned a complete supported audit `{}` with actual exit 0.

Physical lock entries: 1099 → 1086. Only four new unique versions: glob 14.0.2, minimatch 11.0.1, path-scurry 3.0.0, @isaacs/nonrecursive-glob-match 1.0.3. Fourteen obsolete unique versions were removed. Every other retained version, metadata and integrity row remains exact; existing root brace/balanced versions are hoists, not new upgrades. The generated 360,583-byte lock is copied byte-exact: Git blob `b6d95a16bdc877db76595fb6f7ce9b33c3fbe80a`.

The approved patch changes four export/declaration files; 33 official engine files remain exact. The four modified files admit only the recorded bounded terminal-LF normalization in addition to export edits. New mandatory source, graph, installed-byte and actual-consumer guards preserve the old controls. The capture layer explicitly admits the new frozen SEC manifest; removing it falls back to the prior rejecting identity guard.

## Exact-source hosted results

All six affected workflows succeeded, attempt 1, on `552ce47b924dd90b6b8403670989eced07bb82cf`:

| Workflow | Run | Result |
| --- | --- | --- |
| Integrated G0 verification | [41492623283](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623283) | SUCCESS |
| B1 composition compatibility | [41492623366](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623366) | SUCCESS |
| B dependency and request boundary verification | [41492623489](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623489) | SUCCESS |
| SEC dependency and C source contracts | [41492623361](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623361) | SUCCESS |
| B7 dependency advisory regressions | [41492623515](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623515) | SUCCESS |
| SEC 20261102 matching engines and source contracts | [41492623491](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623491) | SUCCESS |

- Normal frozen Bun 1.2.14 installation, complete typecheck, lint (0 errors / 14 warnings), both builds, and 97 unit tests / 300 expectations passed.
- Original B 29, C 18 and C4 18 source mutation controls remained intact; new SEC source 23, graph 16 and installed engine 6 adversarial controls passed.
- Dependency security floors: 25 tests / 116 expectations. New actual consumer/security suite: 11 cases, including config-array CJS/ESM, eslintrc include/exclude, filelist, TypeScript-estree's actual selected matcher function, glob sync/async and the full Workbox getFileDetails module. TypeScript-estree matcher extraction is bounded evidence; the separate full lint/typecheck gates also passed.
- Security controls exercise the actual minimatch expansion cap/cutoff and cancellation through a real 15-directory tree (one read, zero reads after rejection), plus a negative control reproducing the unpatched CJS callable failure.
- Current C4 actual callbacks/history: 37 cases passed. The existing SDK/HTTP controls, native standalone SSR request boundary and prior serializer/router regressions passed. G0's 67 containment browser scenarios had zero failures. These are not a new complete financial browser→database acceptance.
- Complete supported Bun 1.4.0 audit: raw `{}`, actual exit 0, no suppression or accepted-risk waiver. This is the final application audit, distinct from the earlier prototype/preparation audit and historical failed audit.
- Source checks preserve 441 protected entries, all 54 migration SQL files (75 SQL files repository-wide), application `src/**`, frozen A/B/C4 manifests and old verifier/test bytes. Only the five expressly admitted existing paths and eleven additions implement this batch; historical documentation is retained.

## Automatic legacy G1 result and limits

[Legacy G1 run 41492623347](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41492623347) **FAILED** on the same source. Environment job 125439267816 passed. Runtime job 125439268497 failed at `exact41_migrations`; the preserved failure JSON reports `RuntimeError`, `after_exact41_migrations`, `integration_accepted=false`. The target remains the old 41-migration contract while the candidate contains 54 SQL files. The exact guard was not weakened or bypassed. This run was triggered automatically; no manual rerun.

The cleanup receipt passed: status and worker env removed, no processes, containers absent, exact source SHA. The full native G1 log is not republished; its existing scanned raw artifacts and bounded failure/cleanup JSON are preserved. No financial/SSR/browser acceptance is inferred from this failed run.

Independent review has not been performed for this batch. C5 complete financial/isolation/concurrency/replay/browser/restore acceptance, C6 independent review and C7 owner's protected merge decision remain open. Prior C4 native 58/59 and four browser fixtures remain evidence for their original source only, not newly executed here. Main and all five original draft PR heads (#27/#35/#39/#49/#50) are unchanged. No merge, deployment, production action, PR closure, new PR or spending.

## Evidence and resumption

[Evidence index](accepted-evidence/index.json) preserves ten raw ZIPs (one preparation plus nine final artifacts) and nine full non-native job logs in Git, including original provider SHA256 digests and verified Git blob IDs. Failure history and local test corrections are retained in [LOCAL_FAILURES.md](LOCAL_FAILURES.md); no failed attempt is relabeled green.

This report and raw receipts are delivered by a documentation-only descendant of the tested source. The delivery commit preserves all executable/protected bytes and the SEC manifest; no new runtime test result is attributed to that descendant.

**ONE NEXT: C5** — reconcile the old G1 41-target contract with the actual 54-migration history and approved financial contracts; then prove complete persisted sale/collection/customer-debt/courier-custody/settlement/return/stock behavior, concurrency/replay, tenant isolation, actual browser→API→database and restore on clean and upgraded test databases. Delivered does not mean Settled. Do not repeat C2's already-approved fractional weight/metre decision. Continue C6/C7 only after evidence resolves C5.
