# Phase3 — private catalog diagnosis, 5 November2026

Owner continuation resumes d78a818b, existing integration/g0-g1-reconcile-2026-10-18; sole implementer root, claim55/6643926058. Baselinefebfca66 native41906845470 restores all1039archive entries and selected rows, then fails the prior.catalog equality gate. The precise field has not yet been observed.

Add read-only private snapshots of canonical object ACL grants via PostgreSQL17 aclexplode/coalesce(acldefault), retaining grantor, grantee, privilege and grant option; explicit empty ACLs stay empty. These tuples are diagnostic observations only. Public/private function, table and policy equality still uses the identical existing failing assertion. No snapshot normalization, privilege write or altered acceptance is implemented.

Compute fixed category/field mismatch counts, missing/added counts, list-order-only flags and bounded SHA256 object-key identifiers. Report semantic ACL equality booleans and fixed extra-metadata section labels. Never serialize SQL/rows/config/role values, arbitrary object names or unknown field labels. Compared snapshots remain immutable.

Local33tests/AST pass. Seven new privacy/field/owner/RLS/grant-option/missing/ordering/shape diagnostics tests fail on the exact baseline while26existing pass. The original failing check line remains unchanged. No local Docker/full repository build or actual SQL grant observation is claimed; native fresh/upgrade/currentG0/B1 must supply that evidence.

Next within this bounded phase: observe exact mismatch, then choose a narrow faithful restore or validator correction only if evidence proves it. Never waive owner/RLS/privilege differences. Preserve raw failures and all earlier source/helper/55migration/dependency bytes. No merge/deploy/production/closure/newcost/financial-policy action; completeC5/C6/C7 stay open.

Primary reference: https://www.postgresql.org/docs/17/functions-info.html (aclexplode and acldefault), https://www.postgresql.org/docs/17/ddl-priv.html . Compensation: a forward correction limited to this test driver/current manifest, never a history rewrite.
