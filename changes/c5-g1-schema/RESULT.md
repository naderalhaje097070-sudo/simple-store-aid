# C5-G1-SCHEMA-01 — migration-target reconciliation passed

3 November 2026, Africa/Tripoli. **Implemented → Tested for this bounded C5 subtask. Overall C5 remains In Progress. Not Merged or Released.**

## Outcome and exact source

The old G1 test-target mismatch is resolved on the integration candidate. Its original literal41 condition rejected a workflow that already copied/applied all54 approved migrations. The new contract pins all54 filenames, Git blobs and modes to immutable base `836de635e2920480059f3d4dbbd00690c61c080a`, preserves the41 original migration identities from frozen A, and compares real database migration history with that exact list. It rejects missing/extra/renamed/changed/symlink/executable SQL and count-preserving substitutions. No SQL, financial contract, application or dependency changed.

- Repository: `naderalhaje097070-sudo/simple-store-aid`.
- Branch: `integration/g0-g1-reconcile-2026-10-18`.
- Exact executable tested: `96ad7996a647eb6716ab36d050c96e72ad9963e1`; tree `3afb8cf6ffc0cf2150b12c3e3a13a31d009215f2`.
- Sole implementation claim: [#55/6591212966](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6591212966); owner's standing continuation authorizes isolated development/testing.
- Main remains `220fc2066b4d6254b1803b5e32919c47d60a9c7e`; original draft PRs27/35/39/49/50 remain unchanged/open.
- This evidence packet is delivered as a documentation-only direct descendant. Runtime results belong to the executable above; no CI/runtime result is attributed to the documentation commit.

## Hosted acceptance

All three automatically affected workflows passed, attempt1, on the exact source:

| Workflow | Run | Actual result |
| --- | --- | --- |
| Integrated G0 verification | [41547084637](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41547084637) | SUCCESS |
| B1 composition compatibility | [41547084623](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41547084623) | SUCCESS |
| G1 Bounded Acceptance Repair | [41547084595](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41547084595) | SUCCESS |

G1 native job125625187015 passed **41 checks** (setup, contracts and runtime checks, not financial scenarios). Environment job125625187235 passed.

- Fresh isolated local database has exactly the pinned54 migration versions. The41 original migration blobs are preserved; this is not merely a41→54 literal edit.
- Real synthetic Auth users/tenants, own-tenant positive and foreign metadata denial controls pass.
- Actual default Cloudflare build and local SSR matching-target response pass.
- Existing actual Auth browser UI passes on desktop/mobile.
- Real conflicting runtime target returns HTTP500 **with the exact expected build/runtime Supabase mismatch guard**. Generic500 is not accepted.
- Public fixture digests are unchanged; financial tables remain empty; `financial_flow_executed=false`, `integration_accepted=false`.
- Native canary was denied before credentials. IPv4/IPv6 reject counters remain `1/0` before and after the runtime phases (the1 is the intentional canary). Both bounded egress traces complete, process mapping succeeds, no unmapped nonloopback thread IDs. This is bounded observed-runtime evidence, not a universal future-egress assertion.
- Cleanup passes: temporary status/worker env removed, no remaining app processes, containers absent. Credential publication scan passes. Full native job log is not republished; original scanned ZIP, JSON receipts and safe exact markers are preserved.

G0 and B1 passed normal frozen Bun1.2.14 reproduction, complete types, lint **0errors/14warnings**, **97unit tests/300expectations** and builds. G0 also retained the original B29/C18/C4-18 and SEC23/graph16/installed6 negative controls, actual current consumer/security tests, C4 callbacks/history, financial-read fixtures,67browser-containment scenarios with0failures, and final source identity. Supported complete security audit remains raw `{}`, actual exit0, no suppression. Native G1 retains its pinned existing installer/emulator/browser versions; no tool upgrades.

## Change and safety boundary

Exactly3 existing test/CI files changed: runtime.py imports the pinned target contract before temporary credentials and verifies actual DB versions; capture.py selects the new explicit C5 source layer; g01-runtime-retry.yml runs target/source negative tests in both jobs and triggers on target/migration changes. Five target/admission/test files and one frozen source manifest are additive. No old verifier or manifest is edited. Removing C5 admission falls back to the prior SEC source guard that rejects these unadmitted changes.

Source evidence proves449 protected entries and frozen A/B/C/C4/SEC identity, all54 migrations/75 repository SQL files, app `src/**`, package.json, bun.lock, approved minimatch patch and all historical source/evidence bytes exact except the3 declared test/CI edits. No paths removed. New C5 source21 and target19 tests pass both locally and in hosted G1; old G1 contracts17/cleanup6/integrated identity29/process-map10/egress9 remain intact.

No database migration/backfill/permission/account lifecycle/business-state change. The stale G2 descriptive field is now labeled historical rather than claiming a current unresolved finding; no old account test is imported as current acceptance. [Impact/safety documents](CHANGE_INTAKE.md) and [rollback](ROLLBACK_IMPACT.md) define the boundary. Rollback is a forward commit reverting only this test/admission change; no production or financial data action.

## Failure history, evidence and review

Prior hosted41492623347/exact41_migrations remains failed and preserved in the SEC evidence; it was not relabeled or rerun unchanged. A new local regression failed against the old wiring before the correction (18target tests pass,1wiring failure), then19/19passed. The initial local egress run had2setup errors because unchanged DNS tracer files had not been fetched into scratch; exact GitHub files were fetched and9/9passed without editing assertions. See [TEST_IMPACT.md](TEST_IMPACT.md). Tool-output size limits during evidence assembly were handled by bounded reads; no source/assertion changed to hide them.

[Evidence index](hosted/index.json) preserves5raw provider ZIPs with API SHA256 digest verification and Git blob identity,4complete non-native logs, extracted native result/cleanup and safe native markers in Git. Native build records the existing zero-precache warning; PWA/offline readiness is not accepted here. Lint warnings remain14.

Implementation-owner review only; no independent C6 review. The successful G1 flow is explicitly nonfinancial and fresh-schema only. It does **not** prove full persisted money/stock/courier settlement/returns, populated upgrade, browser→financial database or backup/restore acceptance. Prior C3/C4 evidence remains source-bound; no native financial tests were rerun in this batch. No merge/deploy/production/secrets/newcost/newPR/closure or history rewrite.

## ONE NEXT

Complete the remaining **C5 integrated financial/browser/restore acceptance**, reusing existing C3/C4/native harnesses and approved contracts on the final integrated source. [Coverage and evidence limits](C5_COVERAGE.md) identify the current proof gaps: sale/revenue/collection/debt/courier custody/settlement/return/inventory, atomicity/replay/concurrency, active/disabled/foreign actors and tenant isolation, actual desktop/mobile browser→API→DB, and safe restore with nonempty prior state. Delivered does not mean Settled. Fractional weight/metre units are already approved. Resolve any demonstrated defect in a bounded change; C6 independent review and C7 owner's protected merge decision follow evidence.
