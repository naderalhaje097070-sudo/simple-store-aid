# C5 independent restore — Phase 4 scoped ACL capture and recovery

Date: 2026-11-05 (Africa/Tripoli). Repository: naderalhaje097070-sudo/simple-store-aid.
Diagnostic source: 0727e6923d33b1fd09b3875efb4d5a455c2084a9.
Native diagnostic run: 41988824420 (fresh and populated upgrade).
Full C5/integration acceptance remains false.

## Measured blocker

Both real paths preserve all selected rows and application functions, owners, RLS and policy catalogs. The complete archive leaves three USAGE grants missing on graphql_public (owner supabase_admin to anon, authenticated and service_role) and five owner-postgres database grants missing. There are zero extra grants in these two scopes. The bounded archive observer found zero matching schema/database ACL entries; the graphql vendor hook restores one original postgres USAGE grant but does not restore the three missing named-role grants. No claim is made about an unmeasured upstream cause or vulnerability.

## Narrow correction

Capture full logical ACLs for exactly graphql_public schema and postgres database into an exclusive mode-0600 JSON backup companion. Capture occurs before creating the target, from the original pre-dump snapshot, and binds the companion to source SHA, archive SHA256 and role dump SHA256. Publish only its digest, never private role identifiers or SQL.

Read the saved companion during recovery rather than copying current source permissions. Validate integrity and all bindings before planning writes. Plan only missing owner-issued, non-grantable privileges for existing named roles on those two fixed objects. Reject extra grants, grant-option shifts, PUBLIC additions, delegated grantors, duplicates, invalid identities and more than eight missing tuples before the first write. Quote all role identifiers. Use ordinary transactional GRANT under the original owner in the independently attested target, then verify the complete saved scopes exactly. No REVOKE, catalog UPDATE, source write or owner-policy change.

Every TOC entry still executes exactly once; prior equality gates remain intact. Re-snapshot target after the companion and run the existing full metadata, roles, cron and financial SQL-role replay gates. Cleanup removes archive, role dump and ACL companion on success and failure.

## Validation

57 local safety/comparison unit cases pass (48 diagnostic cases preserved, 9 recovery cases added). Tests cover additive-only recovery, grantors, typed PUBLIC, grant options, quoting, all-plan-before-write behavior, digest/source/archive/roles tamper rejection, original backup use, post-apply equality and companion cleanup. These are mocked safety tests, not native Postgres proof. Exact-source native fresh/upgrade plus G0 and B1 checks are pending on the correction commit.

## Boundaries

No production connection, financial contract change, migration edit, merge or deployment. SQL authenticated-role replay does not verify restored HTTP/Auth or password/encryption-key recovery. Full C5 acceptance, C6 independent review, protected owner merge and Pilot remain separate pending gates.
