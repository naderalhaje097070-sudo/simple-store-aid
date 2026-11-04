# Phase2 — guarded GraphQL archive-bootstrap ordering, 4 November2026

Owner continuation resumes c9559e1d; sole implementer root, claim55/6641120939. Existing C5 intake/impact boundaries apply: test/CI only, no financial/app/SQL/dependency change.

Baseline14e72995 native41898466686 failed both modes with missing graphql_public.graphql. Pinned Supabase postgres17.6.1.106 migrations/schema-17.sql defines extensions.grant_pg_graphql_access and issue_pg_graphql_access, which construct the public wrapper on CREATE FUNCTION of GraphQL resolve. This source supports the reorder design; live source membership/owners/hook and archive declarations are runtime prerequisites, not assumed facts.

Before creating a target, require actual source wrapper pg_graphql membership, exact expected vendor ownership and enabled helper trigger, and its original source definition. Require the archive to contain precisely one original helper FUNCTION, one original EVENT TRIGGER and pg_graphql EXTENSION, and no separate wrapper FUNCTION declaration. Any mismatch fails closed as unmeasured_graphql_archive_dependencies/source contract. Do not inject a handwritten wrapper or copy a routine into the restored database.

After existing database/schema restore, execute only those two archived prerequisite objects with their original definition/owner and fatal pg_restore errors, before the remaining archive (including pg_graphql creation). The vendor trigger recreates the extension-owned wrapper through its normal process. Every archive ID remains in exactly one execution partition; no object, ACL, comment or extension is excluded. Existing pgmq mixed-owner handling stays. Verify no dummy wrapper exists before extension and the restored archived helper equals source definition.

Strengthen snapshots with full function definition/owner/ACL/config/extension membership for extensions/graphql/graphql_public and every event trigger, in addition to all previous data/catalog/sequence/role/replay checks. These are private comparisons; publish fixed checks/booleans/hashes only.

Local safety regression:21existing tests pass;4new partition/rejection tests fail before implementation with missing helper, then all25pass. Duplicate/missing prerequisite, changed owner, explicitly archived wrapper, malformed/duplicate IDs and accidental ACL/data omission are rejected. AST passes. No native source measurement/restore acceptance claimed yet; existing workflow supplies hosted fresh/upgrade, failure cleanup and affectedG0/B1.

Primary references: https://github.com/supabase/postgres/blob/17.6.1.106/migrations/schema-17.sql ; https://www.postgresql.org/docs/17/app-pgrestore.html (--use-list ordering) ; https://www.postgresql.org/docs/17/event-trigger-definition.html .
Compensation: forward correction to only this test-driver delta/current manifest; never alter prior helpers/applied SQL/history. FullC5/C6/C7 remain open; no merge/deploy/production/closure/cost/financial-contract action.
