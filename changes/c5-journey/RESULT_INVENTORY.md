# C5-FULL-JOURNEY-01 — inventory repair

Date: 2026-11-05, Africa/Tripoli. Sole implementer: /root. Owner explicitly requested execution of the fixed plan after the stalled session. Resumption claim: #55/6669906449, continuing #55/6653881228.

## Goal and scope

Remove the proven test-environment inventory blocker while preserving strict reviewed-source admission. Parent `2b6bef6000b5a1752dd5e5f9a1ea84d036b956e2`; executable candidate `14f00488bba4b2ad0b08103444c2521d6c6585e5`; existing branch `integration/g0-g1-reconcile-2026-10-18`. No new PR or financial workstream.

Only three source paths change: `.github/workflows/c5-journey.yml`, `tests/c5-journey/test_identity.py`, and their two declared blob identities in `tests/c5-journey/source.json`. All 2,740 other original blob/mode entries remain identical; all 55 migrations, application code, package/lock graph, frozen tests/manifests and the identity verifier are unchanged. Additional delivery changes are documentation/evidence only.

## Root cause and correction

Previous native run `42028716743` failed both modes before financial journey controls. The reported unknown-path SHA256 `39311e8e471fd5a9ce8665c60c63a3741ee1177f5f965562a22c97c236246d4d` exactly matches `supabase/.temp/cli-latest`. The workflow performed CLI discovery from the source checkout after initial admission and before copying the complete checkout to the restricted UID. That CLI state was included in the later exact-inventory check.

Discovery now runs in `$RUNNER_TEMP/monjez-c5sale-cli-probe`. Explicit assertions require the cache path to be absent in the checkout before and after discovery. No file is ignored, deleted, adopted into the manifest or exempted by the identity guard. There is no application/API/RPC/schema/permission/financial-contract change.

## Local verification

- New functional regression executes the actual workflow discovery shell with a cache-writing CLI surrogate: parent workflow produces 22 PASS / 1 FAIL, at the source-cache absence assertion. This models the observed cwd side effect; it is not official CLI evidence.
- Corrected workflow: `python3 tests/c5-journey/test_identity.py`, 23/23 PASS. Includes a second case requiring the unchanged strict guard to reject the same cache path with the exact logged digest.
- All 21 prior test methods are AST-identical; none removed or weakened.
- YAML syntax/matrix, Python AST syntax, available source-manifest blob hashes and the logged path digest match.
- GitHub tree comparison: exactly the three intended changed paths, zero additions/deletions, all other original blob/mode entries identical.

This environment has no authenticated Git clone or Docker. Exact source was read/published via the GitHub connector. Local execution used a partial source workspace and synthetic temporary git repositories, not a full native application checkout.

## Independent source review

Actual separate read-only agent `/root/inventory_review` personally ran 23/23 tests, fetched parent files, reproduced the new functional failure against the parent workflow, checked all 21 original test ASTs, unchanged verifier blob `abf8d9b1927074c2154bab41f6b5d67cafabc4a4`, manifest identities and the cache digest. The reviewer then independently inspected both completed native jobs and accepted the inventory repair only, with no blocking introduced finding. Whole-C5/head verdict remains **Blocked pending missing evidence**. See [bounded independent review](REVIEW_INVENTORY.md). This is not full C6 or merge approval.

## Native verification

Exact-source C5 `42112588038` completed FAILURE later in the actual financial journey; the inventory boundary passed in both modes. Both native jobs ran 23/23 admission tests, admitted 497 protected blobs / 55 unchanged migrations and matching reviewed HEAD, logged `C5F_CLI_SOURCE_CACHE_ABSENT`, passed restricted-copy admission and reached the actual app journey. Populated54 seed / forward55 upgrade also succeeded.

Fresh job `127543717858` stopped at `desktop_sale`, TimeoutError after 18 controls; upgrade job `127543716050` stopped at the same stage after 19. These counts include fixture/setup controls, not completed financial scenarios. The safe receipt does not identify the exact waiting locator or state, so neither a financial defect nor a harmless selector defect is established. Mobile/later journey, final balances and close-day acceptance remain unverified.

Cleanup, private-file/stack removal and publication succeeded in both jobs with zero unexpected IPv4/IPv6 egress. B1 `42112588006` SUCCESS. G0 `42112587955` audit and quality SUCCESS; executed required steps pass or normal conditional skips. Browser-tool installation eventually completed; no rerun was issued. Typecheck/lint/unit/wire/containment/financial-read UI/both builds/generated-source/source-identity checks pass.

See [machine-readable steps and bounded log excerpts](evidence/inventory-repair.json). Artifact IDs and GitHub digests are metadata, not claims of downloaded/archived raw ZIP bytes.

## Risks, rollback and next task

Full C5/integration acceptance remains false until the complete required evidence and independent C6 are accepted. Original failure evidence remains linked to run `42028716743`; this report does not claim a new durable copy of its raw ZIPs. No production, deployment, merge, PR closure, spending or financial-policy action.

If this isolated harness change must be withdrawn, use an additive revert of `14f00488` restoring the workflow/test/manifest together; never force-push or edit applied SQL. No database compensation is needed for this source change; all native writes are disposable fixtures.

Acceptance: inventory root-path identification PASS; regression and unchanged-guard negative control PASS; native source boundary in fresh/upgrade PASS; independent bounded review PASS. Full financial journey FAIL/BLOCKED at the newly reached desktop_sale timeout; full C6/C7/RC/Pilot NOT VERIFIED.

ONE NEXT: diagnose the exact desktop_sale wait using bounded step/locator/runtime receipts under the existing private-publication scanner, preserve the failed assertion, then fix only the proven harness/application defect within approved scope. Do not infer a financial-contract change or repeat an unchanged run. Continue the fixed full-journey → C6 → owner C7 → RC/Pilot path after the journey passes.
