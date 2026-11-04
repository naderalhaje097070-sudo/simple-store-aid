# C5 independent restore — phase2 GraphQL bootstrap correction

Date:4 November2026. Sole implementer root; execution claim55/6641120939. Owner requested staged continuation. **Bounded GraphQL restore correction Implemented → Tested on candidate; complete restoration acceptance FAILED/BLOCKED at a newly reached catalog-equality barrier.** No whole C5/C6/C7/release acceptance.

## Source and observed result

Exact tested source `febfca66dc331c6071c235ccfec1256f91b88770`, tree45ebfd1bdeadf2c8a8659c8a94ce51a4889f404d, on `integration/g0-g1-reconcile-2026-10-18`. Phase start c9559e1d; preceding source a58802f3. Main220fc206 and all five original draft PRs27/35/39/49/50 remain unchanged. #50 is tracking context, not this integration branch's head PR.

Native [41906845470](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41906845470) FAILED in both fresh and upgrade at `prior_functions_RLS_owners_ACLs_restored`. This is later than the original missing GraphQL function. Both modes now successfully execute the entire archive:1039entries, partitioned13database/schema +2original GraphQL prerequisites +1024remainder. Every original ID appears once and pg_restore errors remain fatal. The original helper definition matches source before extension creation; there is no handwritten/dummy wrapper.

All selected rows in public, monjez_private, auth and supabase_migrations compare exactly after restore, including financial/idempotency/audit fixtures. That is selected-table proof, not proof of every provider internal table. Real restore receipts contain44passing checks and1catalog-equality failure per mode (45total). Separate injected post-role failure controls pass33checks per mode. Cleanup/private-file removal/source invariance/safe publication and zero unexpected probe IPv4/IPv6 egress pass. These outcomes do not accept the restored security/catalog or execute the subsequent restored financial RPC tests.

## Root cause addressed and correction

The exact source measures graphql_public.graphql as a pg_graphql extension member, with expected vendor owner and enabled issue_pg_graphql_access hook. Its own FUNCTION declaration is absent from the archive, while the original helper FUNCTION, hook EVENT TRIGGER and extension are each present once. Source helper-definition SHA256:c3a126f9bf8958b3af27e6bec128aca58627df257259003b59511fdd3af82333.

The original raw-initdb target lacked the vendor hook when pg_graphql was installed. Moving precisely the two archived prerequisite objects before extension creation allows the normal vendor process to create the wrapper; full archive execution now passes. Source ownership/hook/membership are measured gates before any target is created. Target-wide vendor-function/member/event-trigger equality is still unaccepted because the earlier prior-catalog check fails first.

Initial candidate a58802f3/run41905909940 confirmed the source contract, then failed strict TOC admission before creating a target (21passing checks). A local regression proved empty-owner trailing separators break literal descriptor comparison. The current parser trims comparison descriptors only and preserves exact original archive execution lines/IDs. Native inventory confirms16trailing-separator entries and exact1helper/1hook/1extension/0wrapper declarations. Missing/duplicate prerequisites, unexpected owners, separately archived wrappers and malformed/duplicate IDs remain rejected. The a588 failure stays failed, with original artifacts preserved.

## New open barrier — no speculative catalog repair

`prior.catalog` compares public/monjez_private function identities/bodies/security-definer flags/config/ACL/owner; table RLS/forced-RLS/ACL/owner; and policy definitions. At least one compared value differs. The current receipt does not identify which collection/object/field differs. This may be a semantic difference or a representation/order difference; neither explanation is proved. Do not assert a production vulnerability, altered financial rule or merely harmless ACL ordering.

The original failing assertion remains unchanged and active. No grant broadening, comparison normalization, mock value, waived check, excluded object or ignored error was added. Source stayed exact during both failures.

**ONE NEXT: the same C5 restore work, phase3 catalog diagnosis** — add bounded private field-level comparison diagnostics while preserving this exact assertion; identify function/table/policy category and mismatching fields/semantic owner+privilege differences without emitting SQL, arbitrary identifiers, role configurations or rows. Reproduce on fresh/upgrade; select a narrow faithful recovery correction only after evidence. Then complete all restored catalog/vendor/role/sequence/cron equality and original replay/cross-tenant/conflict/new-payment assertions. Full financial application journey follows successful recovery, then independentC6, owner-protectedC7 and RC/Pilot. No new routine-test permission is required.

## Changes and actual validation

Executable file scope: restore.py, its test_restore.py and current source.json hashes; PHASE2_DESIGN.md and PHASE2_TOC_CORRECTION.md document preparation and the failed attempt. All application code,55migrations, dependencies, prior restore helper/verifiers and prior manifests remain unchanged.

Actual local validation:26safety/privacy/TOC tests pass; AST parsing passes. Four new reorder/rejection tests fail before their implementation while21existing tests pass; the later trailing-separator test fails on a588 while25existing pass. Eight original safety functions have exact AST equality to the preserved baseline:cleanup/sql/roles/snapshot/prepare_roles/private_file/validate_target/partition_toc. Local work uses a connector-fetched subset; no full local checkout/build/Docker/native verification is claimed.

| Current gate | Run | Outcome on exact febfca66 |
| --- | --- | --- |
| G0 quality/audit | [41906845589](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41906845589) | SUCCESS attempt1;97unit/300expectations, lint0errors/15warnings, types/builds and raw full audit{} |
| B1 compatibility | [41906845491](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41906845491) | SUCCESS attempt1 |
| Full archive/rows plus restore acceptance | [41906845470](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41906845470) | Full execution/selected rows PASS; prior-catalog FAIL both modes; cleanup/publication PASS |

Current485protected blobs/55migrations and frozen prior manifests verify exactly. Existing collection UI/SQL/browser108fresh/111upgrade controls pass before restore; they do not prove restored RPC behavior. Restored original-key replay, conflict/tenant denial, new intentional payment and all later metadata checks are NOT executed after the catalog failure. No current G1 rerun or independent C6 review is claimed. Advisor step was skipped after restore failure; the inherited45performance warnings remain outside this batch's acceptance.

## Evidence, limits and compensation

Ten original artifact ZIPs are preserved unchanged with GitHub SHA256 validation in [phase2 manifest](evidence/phase2/manifest.json): a588 failed fresh/upgrade, its G0 identity/audit/quality diagnostics, current failed fresh/upgrade and current G0 identity/audit/quality diagnostics. These are original archive bytes, not reconstructed stdout receipts. RESULT_PHASE2.json records source-scoped safe summaries. The7phase1 artifacts and all older evidence remain untouched.

Role passwords, master encryption keys, restored Auth/HTTP services, production backup/PITR/RPO/RTO, managed service internals and complete product acceptance remain unverified. No new dependency, financial-policy or privilege contract is proposed. Source self-review covers test parsing/privacy/containment and unchanged failure assertion; independent C6 remains a later gate.

Compensation is a new forward correction confined to this test-only bootstrap/descriptor delta and its current source manifest; do not edit published SQL, frozen prior helpers or Git history. No merge, deploy, production access, PR closure, new subscription or financial-policy action. This staged handoff releases phase2 implementation, not the still-open full recovery acceptance.
