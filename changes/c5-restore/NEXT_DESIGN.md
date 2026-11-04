# C5 restore — next bounded design

The standing plan and owner continuation authorize isolated test work. No new financial-contract decision is needed. Preserve current failed evidence and use46373de6 as the diagnostic baseline.

1. Discover the exact source container image digest, PostgreSQL major/tool versions, extension settings and original owners/roles without publishing credentials.
2. Create a distinct disposable recovery cluster/container from that compatible image, with database name postgres and matching extension requirements. Verify a distinct identity before any restore. Never replace/drop the source database.
3. Use no host-published ports and an isolated Docker network boundary. Keep scheduled jobs disabled on the target during recovery while preserving their definitions; record that scheduler execution itself is outside this acceptance.
4. Provision equivalent isolated roles and memberships/owner identities before restore. If a global-role dump is required, treat it as private synthetic credential material: never publish it. Resolve expected bootstrap-role identity explicitly; never ignore arbitrary role/schema errors.
5. Restore the existing full custom archive with correct operator credentials and --exit-on-error. Keep owner/ACL data and every extension; do not filter pg_cron or exploit a special regression database name. Do not modify source HBA, roles or configuration.
6. Reuse the current row/catalog and authenticated SQL-role replay/tenant/payload/new-payment assertions. Add relevant sequence/constraint/schema coverage as needed for the actual new target; clearly distinguish SQL role tests from a restored Auth/API deployment.
7. Attest original data/catalog remain unchanged, private archive/global-role files removed even on failures, target identity/resources removed, no external credential-bearing traffic and safe publication.
8. Record actual source/run/image/versions/results; retain any failure. Only then mark bounded logical restore Tested. Full app financial journey, managed backup/PITR, operational recovery objectives and independentC6/C7 remain separate acceptance work.

This design is prepared, not implemented or tested. Review the target bootstrap and cleanup before execution; routine isolated steps proceed under the existing owner authorization.
