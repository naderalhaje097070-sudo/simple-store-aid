# Migration impact and ordering

Observed accepted baseline50 files (including October auth/closure/entitlement/billing). Original49/50 add20260815170000 and20260815171000. The direct-CREATE source trace compares main50, sorted52 fresh, and hypothetical main50 then August2 append.

Two final legacy definitions differ by sequence: create_sale_with_items and update_courier_order_state. On sorted fresh52, October20261010223557 recreates both old bodies; legacy courier no longer delegates v2. On hypothetical append-after50, August adapters are last. This is actual source ordering, NOT a successful Supabase upgrade or a pg_catalog observation.

Planned C3: preserve exact old50 and original August2 blobs; add one forward-only correction later than the current accepted latest migration. Restore canonical sale/transition compatibility deliberately, keep live actor/tenant/staff checks and idempotency grants/revokes. Test chronological fresh, true populated upgrade from supported prior states and final definitions/ACL/RLS equality. Generate the new migration with pinned CLI in an isolated environment. Do not make migration-order tolerance depend on re-running modified applied files or relaxing source manifests.

No applied SQL, schema, grants, data, index or backfill changes in C1. Future locks/scans/constraints/validation timing and rollback compensation require their actual C2/C3 design; do not pretend a backdated source append is an executed migration strategy.
