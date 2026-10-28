# Dependency and caller map

| Path / caller | Current dependency | Reconciliation requirement |
|---|---|---|
| src/routes/_authenticated/app.tsx:218,572 | useCreateSale / CreateSaleInput | Keep A error/loading/completeness; integrate one canonical sale input |
| app.tsx:1507–1719 and2135–2231 | two cart entry paths, numeric qty, PaymentSheet | Same quantity contract for both; no silent rounding |
| app.tsx:1732–1900 | PaymentSheet outcome/customer rule | Explicit pending/full/partial/none under approved policy; returned only after creation |
| src/lib/db.ts:594–624 | main legacy sale RPC | Candidate50 revokes that entry for authenticated; migrating only SQL would break caller |
| src/lib/db.ts:694–717 | update_courier_order_state | Later October replacement loses49 v2 delegation on fresh chronological composition |
| src/domain/finance/invoice-selectors.ts | canonical debt/custody selectors | Reuse; do not implement another UI debt formula |
| 49 legacy/core/v2 → _assert_staff/current_tenant_id | accepted October live checks | Preserve transitively, and prove actual new RPC authorization/privileges |
| 50 idempotent wrapper → v2 → core | one transaction and private reservation storage | Retain unique tenant/operation/key, exact request comparison and rollback; no direct-write bypass |
| 35 design /39 baseline /27 Gate4 | historic predecessor contracts/tests | Retain exact bytes and failed/pending labels, adapt only through scoped C safety nets |

All127 current src blobs were available in the exact selective materialization, with50 current SQL and accepted financial T1–T15 files. This is caller/source discovery, not a complete installed checkout or runtime import graph. Full identities and source references are in SOURCE_INPUTS.json / replay.zip.
