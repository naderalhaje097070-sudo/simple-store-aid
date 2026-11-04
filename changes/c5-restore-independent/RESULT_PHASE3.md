# C5 independent restore — phase3 catalog diagnosis and validator correction

Date:5 November2026 (Africa/Tripoli). Sole implementer root, claim55/6643926058. **Diagnostic and scoped verifier correction Implemented → Tested on integration; full restoration acceptance FAILED/BLOCKED at genuine grant-tuple differences.** FullC5/C6/C7/RC/Pilot remain open.

## Exact sources and measured progress

Current executable `fe62a3cc1e290607afd9891720d6239adb2a3daf`, tree378f2891a9f89a83f56dcffbee21b0267bf0ae2a, existing `integration/g0-g1-reconcile-2026-10-18`. Phase start d78a818b; diagnostic source `e8f3ba9016353d1efd662815bed70c6b3c07a651`. Main220fc206 and five original draft PRs27/35/39/49/50 unchanged/open. #50 remains tracking context, not this integration branch's head PR.

Diagnostic [41927270178](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41927270178) retained the original literal failing assertion. Both modes observed49public/private functions,26tables,82policies,0missing/added. All function body/security/config/ACL/owner and policy fields matched exactly. Tables had identical identities/owners/RLS/forced-RLS; exactly1table ACL text differed while all actual expanded grantor/grantee/privilege/grant-option tuples matched. Object-key SHA2569b159b74ba10057a75bf0449931af550c14ff75716a90b7f76f81613806ad580. Thus that prior-catalog failure was a textual ACL representation mismatch. The earlier diagnostic remains FAILED, with original evidence preserved.

Current [41928863171](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41928863171) now passes prior_functions_RLS_owners_ACLs_restored in BOTH fresh/upgrade. It still fails metadata_restored_schemas. Real receipts46PASS/1FAIL (47total) per mode. All1039archive entries execute exactly once (13+2+1024), selected rows match, original GraphQL hook definition matches, and source containment/invariance/private-file/target cleanup/publication/zero unexpected egress pass. Separate intentional-failure canaries pass33controls per mode. Existing collection UI/SQL/browser controls108fresh/111upgrade pass before restore.

## Correction and security properties

PostgreSQL17 defines NULL ACLs through acldefault and exposes individual grantor/grantee/privilege/grant-option rows through aclexplode ([primary reference](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-ACLITEM)). Compare table ACL representations using complete logical grant multisets, preserving grantors and grant options. Functions and policies remain literal-equal; table identity/count/order/RLS/forced-RLS/owner remain exact. No privilege or database object was written to force a match.

PUBLIC is represented by an explicit type tag, distinct from any named role. ACL-object coverage is exact; missing/extra/duplicate identities, malformed grants and nonboolean grant options fail closed. Grant duplicates remain in the multiset. SQL NULL defaults expand correctly; explicit empty ACLs remain empty. Raw snapshots are not modified, and their prior literal mismatch is still recorded in current diagnostics. This is an evidence-backed verifier correction, not a waiver of an actual grant difference.

The observed schema/database sections now have the same canonical ACL observations plus fixed per-field diagnostics. Their comparison changes only ACL representation; every original owner/database/encoding/locale/provider/collation/version attribute must still match. Every other metadata section keeps its original literal predicate. No source-specific table exception, hand-copied privilege, ignored archive error or object exclusion was introduced. The original frozen tests/c5-restore/restore.py remains unchanged.

## Newly isolated blocker — grant records, not an assumed access exploit

Current private diagnostics show:
-16schemas and all identities/owners equal; exactly1schema ACL differs. Its stable key hash7ffe3af024af2cd5f335b4f18dd89ee409a7593f2c54ca37f5d859fa2afb4449 matches the predefined vendor schema graphql_public. Its expanded grant records differ.
-The fixed postgres database has identical owner, encoding, collations, locale/provider/rules/version; its ACL and expanded grant records differ. Database key hash66911f262dea5e809920fc370148343afb060103e3684c324d7b1365d4496740.
-All public/private function and policy fields still match; table actual grants still match. Raw extra differences remain confined to schemas/database.

The exact changed grant components (grantor, grantee, privilege, grant option), missing/extra grants and producing archive/bootstrap statement have NOT yet been measured. A differing grantor or delegation flag need not prove changed effective user access. Do not claim a production vulnerability, broadening of customer access, lost money or a harmless formatting difference for these two objects.

The schema gate correctly remains FAILED even after the table representation fix. Database grant mismatch is observed diagnostically; its acceptance gate and subsequent metadata/roles/cron/restored financial-RPC/new-payment checks are not reached after the schema refusal. No restored financial acceptance is claimed.

## Actual validation and scope

| Gate on exact fe62a3cc | Run | Result |
| --- | --- | --- |
| G0 quality/audit | [41928863138](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41928863138) | SUCCESS attempt1;97unit/300expectations, lint0errors/15warnings, types/builds/source guard, raw full audit{} |
| B1 compatibility | [41928863250](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41928863250) | SUCCESS attempt1 |
| Independent restore fresh/upgrade | [41928863171](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41928863171) | prior application catalog PASS; vendor schema grants FAIL; cleanup/publication PASS |

Local41safety/privacy/comparison tests and AST pass. On the phase baseline,26existing tests pass while7new diagnostic tests fail; on diagnostic e8,33existing pass while8new comparison tests fail. All33prior test methods have exact AST equality after adding the8new tests. Negative controls cover owner/RLS/forced-RLS, exact function/policy values, every grant component, PUBLIC/name separation, schema/database owner/locale/rights, missing/extra/duplicate/malformed coverage and ordering without dropping grants. Snapshots stay immutable.

Current485protected blobs/55migrations/prior manifests verify. Application/financial SQL/dependencies/prior frozen helpers remain unchanged. Executable scope is the independent restore driver, safety tests/current hashes and phase3 design/correction notes. Local checkout is a connector-fetched subset; no local Docker/full build/native execution is claimed. A local copied frozen helper's extra terminal LF was resynchronized to its known Git blob9f3d671168ccf16e886f2b47d40e673526702510 before the last41-test run; the remote frozen helper never changed. No G1/advisor rerun or independentC6 approval is claimed. Inherited15lint/45database performance warnings remain recorded; advisor was skipped after restore failure.

## Evidence and resumption

Ten original ZIPs were downloaded and verified against GitHub SHA256, then preserved unchanged in [phase3 manifest](evidence/phase3/manifest.json): diagnostic failed fresh/upgrade plus itsG0 identity/audit/quality, and current failed fresh/upgrade plus currentG0 identity/audit/quality. They are original bytes, not reconstructed stdout. All phase1/phase2 and prior failures remain retained. RESULT_PHASE3.json provides safe source-scoped summaries.

**ONE NEXT — phase4 within this same C5 restore task:** measure missing/extra grant tuples and changed components for graphql_public and postgres, using private queries and bounded fixed-vocabulary/hash/count receipts. Trace the original bootstrap/archive/initial-privilege ordering before changing recovery behavior. Restore the original source grant records faithfully on the isolated target only; never widen source policy, normalize away actual grant differences or modify original financial SQL. Require all existing metadata/vendor/role/sequence/cron and restored replay/tenant/conflict/new-payment assertions to pass in fresh/upgrade. Then full financial app journey → independentC6 → owner-protectedC7 → RC/Pilot.

Role passwords, provider encryption keys, restored HTTP/Auth services, all provider internal rows, managed backups/PITR and operational RPO/RTO remain outside this drill. Source self-review is not independent acceptance; C6 remains required. No new routine-test permission needed. Compensation is a forward correction limited to this test driver/current manifest; never edit published migrations, frozen helpers or Git history. No merge/deploy/production/PR closure/newcost/financial-policy action. This is the staged phase3 handoff, not a successful full recovery.
