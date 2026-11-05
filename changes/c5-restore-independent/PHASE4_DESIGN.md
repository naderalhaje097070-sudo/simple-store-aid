# Phase4 — grant provenance before recovery correction, 5 November2026

Owner continuation from a827c434; sole implementer root, claim55/6652483601. Existing integration/g0-g1-reconcile-2026-10-18; main220fc206/five original drafts unchanged. Baselinefe62/run41928863171: application catalog/1039archive/selected rows pass; graphql_public schema and postgres database grant tuples differ. Components and producing stage remain unmeasured.

Add immutable Counter-based missing/extra grant diagnostics scoped only to graphql_public/postgres, preserving typed PUBLIC/grantor/grantee/privilege/grant option and multiplicities. Publish known fixed vendor role/privilege names only; unknown names are hashes/withheld. Bound tuple samples8per direction and retain total counts; never emit arbitrary names, SQL/config/row values.

Observe ACL states after existing database/schema restore, archived GraphQL-hook restore, pgmq bootstrap and full archive. This is read-only. Select only the two relevant ACL TOC objects and render their SQL into private memory with pg_restore --file=- and no -d; never execute a second copy of an archive ID. Publish statement-category counts and hashes only; empty selections never render the unfiltered archive. All existing equality/owner/RLS/actual-grant gates remain unchanged and blocking.

Local48tests/AST pass;7new privacy/tuple/options/unknown-role/fixed-stage/render-only/empty-list controls fail on exact parent while41existing pass. No native provenance or recovery correction claimed yet. After evidence, choose the smallest faithful isolated-target bootstrap/archive correction and complete all restore/financial assertions; do not broaden source policy or normalize away grant differences. FullC5/C6/C7 remain open. Compensation is a forward test-only correction/current manifest; no production/history/financial SQL action.

Primary references: https://www.postgresql.org/docs/17/sql-grant.html (GRANT adds to existing privileges); https://www.postgresql.org/docs/17/sql-revoke.html ; https://www.postgresql.org/docs/17/app-pgrestore.html . No app/55migration/dependency/original frozen helper change or protected merge/deploy/closure/newcost.
