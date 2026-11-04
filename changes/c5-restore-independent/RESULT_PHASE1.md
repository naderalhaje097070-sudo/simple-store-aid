# C5 restore — phase 1 diagnosis, 4 November 2026

Status: **Implemented → Tested diagnostic; restoration acceptance FAILED/BLOCKED.** This is the first bounded stage requested by the owner after the prior conversation stalled. Full C5, C6, C7 and release acceptance remain open.

## Outcome and measured failure

Exact diagnostic source `14e729951b55570041c3f951147d943782793ddc`, tree99894990b9ea4675252e9e6f2ee48ea12192289e, on `integration/g0-g1-reconcile-2026-10-18`. Baseline `990b712a370c0aeb51fb6803ba30c40642b9fc8c`. Main220fc206 and all five original draft PRs27/35/39/49/50 remain unchanged; #50 remains tracking context rather than this integration branch's source PR.

The new native run [41898466686](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41898466686) FAILED in both fresh and upgrade at `pg_restore_all_remaining_entries`. In both, bounded diagnostics identify missing `graphql_public.graphql`, routine-name SHA256 b38c7d40bf3d778343fbd10c1bd99ac8bf42c4b7b450979843f45253dcc6834c. This supersedes the old unknown-function diagnosis; it does not repair the restore.

Original-image/roles/readiness/empty-target-database connection barriers pass. Each real restore reached38 passing setup/containment/bootstrap checks, then stopped before recovered row/catalog/RPC assertions. The separate intentionally injected post-role failure control passes30 checks per mode, with target/private-file removal and source invariance. Final cleanup and artifact publication pass in both, with zero unexpected IPv4/IPv6 probe egress. No error was ignored and no archive object or extension was removed to produce a pass.

## Cause and next investigation

Observed cause: the target lacks the named vendor GraphQL wrapper at the moment an archived command requires it. The exact failing SQL/TOC object is still withheld, and current source extension membership/archive inclusion have not yet been measured. Do not state that a financial RPC or production data defect was proved.

The pinned vendor [schema-17.sql at17.6.1.106](https://github.com/supabase/postgres/blob/17.6.1.106/migrations/schema-17.sql) defines `extensions.grant_pg_graphql_access`, which creates that wrapper when the GraphQL resolve function is created. This supports a vendor-bootstrap/extension restore-order hypothesis, not a measured conclusion that this exact source wrapper was omitted from the archive. Phase2 must inspect actual membership, source definition/owner/config/ACL and archive TOC before selecting the smallest faithful repair. Preserve original helper/extension ownership, permissions, definitions and full archive error handling; no dummy function, grant broadening, schema exclusion, advisory suppression or financial change.

## Changes and verification

The executable delta from990 contains exactly:
- restore.py: bounded failure metadata only; finite known-vendor names, routine-name hash, numeric TOC entry and fixed object kinds. Unknown identifiers, raw stderr and SQL remain withheld.
- test_restore.py:3 meaningful privacy/diagnostic regression tests, retaining18 existing safety controls.
- current source.json: hashes of those two files updated, prior source manifests frozen.
- MISSING_FUNCTION_DIAGNOSIS.md: scope and baseline evidence.

Actual local command: `python tests/c5-restore-independent/test_restore.py` →21/21 pass. AST parsing passes. An isolated temporary reproduction with original990 restore.py and the current tests yields exactly the3 expected missing-diagnostic errors while the18 existing controls pass; no Docker or database is accessed by this test. No full local repository/build/Docker execution is claimed; the local checkout is a connector-fetched test subset.

Exact-source native results:
| Gate | Run | Result |
| --- | --- | --- |
| G0 quality and audit | [41898466745](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41898466745) | SUCCESS, attempt1;97 unit tests/300 expectations, lint0errors/15warnings, types/build/source identity pass, raw full audit{} |
| B1 compatibility | [41898466712](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41898466712) | SUCCESS, attempt1 |
| Independent restore fresh/upgrade | [41898466686](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41898466686) | FAILED both; known missing GraphQL wrapper; cleanup/publication passed |

Existing collection UI/SQL/browser controls still pass108fresh/111upgrade before restoration. They are bounded collection acceptance and do not accept a restored database or the complete financial app journey. Source-identity receipt verifies485 protected blobs,55 migrations and unchanged prior manifests. Application/SQL/dependencies and original financial tests remain frozen. No G1 rerun is claimed for this diagnostics-only delta.

## Evidence and limitations

Seven original artifact ZIPs (baseline990 fresh/upgrade, current fresh/upgrade and current G0 identity/audit/quality diagnostics) were downloaded and SHA256-verified against GitHub's artifact digest, then preserved unchanged beside [manifest.json](evidence/phase1/manifest.json). These are original archive bytes, not reconstructed stdout receipts. Safe source-bound JSON summaries are in RESULT_PHASE1.json. Historical failed runs remain failed.

Source self-review covers diagnostic privacy and unchanged restore behavior; no independent C6 approval or merge readiness is claimed. Role passwords, provider encryption keys, restored Auth/HTTP services, every provider internal schema, PITR and operational RPO/RTO remain outside this drill. The source fixture had no master-key-dependent records. Existing15 lint warnings and45 database performance warnings remain recorded, not newly accepted.

## Resumption and compensation

**ONE NEXT — phase2: inspect and repair the measured vendor GraphQL bootstrap/archive dependency, then rerun the affected fresh/upgrade restore and source gates.** Continue with complete row/catalog/owner/ACL/role/sequence/cron comparison, restored key replay, cross-tenant/conflicting-payload denials, one genuine new payment and source/cleanup invariance. Only after this succeeds move to the remaining full financial app journey, independentC6, protected ownerC7 and RC/Pilot.

This stage ends at a documented handoff, not a new execution claim. No new financial decision or routine-test permission is needed. Any future product/financial contract change remains separately protected. Diagnostic compensation is a new forward commit removing only the scoped diagnostic delta and updating its current manifest; do not rewrite history or edit frozen original tests/SQL. No merge, deployment, production access, PR closure, new subscription or financial-policy action occurred.
