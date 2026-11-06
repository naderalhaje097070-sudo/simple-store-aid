# Forward-only migration proposal

Only after owner contract adoption: discover the pinned2.101.0 CLI commands/help, generate one new migration with the official migration generator, then add the reviewed CREATE VIEW/ACL statements from DESIGN.md. This packet creates no migration file/timestamp. No latest-CLI install/CLI3 upgrade; no old migration edit.

Preflight exact source/target: local/disposable only, PG170006 and previously fixed image; confirm view name absent, actual day_closes columns/types/NOT NULL/RLS/grants and current definitions. Existing55SQL bytes stay exact; target is55→56. A name collision stops, not CREATE OR REPLACE of an unknown object.

A plain view has no data backfill/table rewrite, but DDL/catalog locks and query-plan cost are not zero or measured by this design. Bound lock timeout and inspect plan for the existing tenant/date ordered read on representative fixtures. Do not claim production duration without volume evidence. Verify fresh chain and populated upgrade, actual Data API exposure, generated types and no source drift. No remote production command, paid project or provider operation.
