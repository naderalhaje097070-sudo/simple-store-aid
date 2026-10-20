# MONJEZ financial and dependency source review — 2026-10-19

Outcome: **Changes required**. Reviewer is the project lead, who did not implement financial49/50. Financial FIN-01/02 were also challenged independently by the account/security reviewer; see that report's final addendum. This review adds no code/migration/lock/provider/production change and runs no SQL/CI.

## Exact scope

Current original72:6da4dadbe9391bb48c8c4c41dcb688728003fb81; foundation823cbcaf4a83ae8b4bea44e314df4c1215a9ba3b/docs1028441558e7db7b0b25390f2b8ee452b702774b; main43d6edbccb66fb06ce0fcb93734ad59532d1aeae unchanged. Financial49 head3106b4710fb9214d6f406d5a3fe7bf44fa2823e6 adds317line migration, blob1e6654acdad1591229df91b77981de264612d738. Financial50 head193412a01938d752a98689d85acd727664e4dc8e adds Idempotency migration blobc6a97b4af3b43fc7d6ed2e5b67890aeed77f79d7, clientdb blob44c6c3ce7983139686dcff847c197cc5aaf2c357, behavior/concurrency tests. October59 sourcefd95ad2e1966362719965ef282de1e2eb66cb070 migration blobd632a985f2330c8f969cd49aa9a7d5fba2e38bfe remains the same in final71. No current single source composes foundation+71+49/50.

Fetched actual financial migration/client/test files and exact supporting design35, readiness39, Gate427, contracts22/31; read source all41 baseline migrations. All41 local SQL bytes were matched to a fresh remote823 Git tree. Twenty historical local cache files initially differed only in EOF bytes; only candidate bytes whose full Git blob SHA matched the immutable remote SHA were copied to this review's own schema directory. No working repository/CI source or comparison rule was normalized/changed. Four material financial/October source files were also exactly SHA-matched. schema-identity.json records the cache limitation.

## FIN-01 — fractional quantities do not preserve integer stock

Severity: **High**, inherited before49 and carried by49/core,59 and the foundation. Claim: confirmed source/schema incompatibility and deterministic PostgreSQL cast-semantics counterexample; **not a live database execution or proven production incident**.

Files: initial schema20260626143241_8c05ee08-2167-458f-8092-777dcc86d8fe.sql:13,82;49 migration20260815170000_fin_courier_pr_a.sql:40,77–90,144–150; October59:338,357–363,401–405. Existing nonnegative stock check20260626155319:7–10 is preserved.

products.stock is integer while order_items.qty and RPCv_qty are numeric(12,2). Quantity validation checks only positive/non-null, not whole units. The inserted line retains fractional quantity but each stock update implicitly assigns its numeric subtraction into the integer column. The only relevant product trigger updates updated_at; no later stock-type migration, whole-unit guard or other constraint prevents this combination.

Source-derived valid example: stock10, price100,cost0, direct sale/no customer/paid25, one lineqty0.25. The line and total25 pass guards; numeric9.75 becomes integer10 on stock assignment, so the stored line consumes0.25 while stock does not fall. Four separate quarter lines similarly leave stock10 rather than9. The nonnegative check does not prevent rounding loss. This remains true through50's Idempotency wrapper because it delegates the same49core; Idempotency cannot repair the quantity contract. Independent account reviewer rechecked final constraints/triggers and exact blobs.

Primary technical references consulted: [PostgreSQL numeric source](https://doxygen.postgresql.org/backend_2utils_2adt_2numeric_8c_source.html) numeric_int4_safe/numericvar_to_int32→numericvar_to_int64 round_var at scale0; [numeric types](https://www.postgresql.org/docs/current/datatype-numeric.html). The Python Decimal illustration is explicitly a model of those semantics, not substitute SQL evidence.

Risk: silently inconsistent inventory and line quantities, including repeated fractional submissions. Required fix: choose/confirm the supported unit contract, then consistently reject nonwhole quantities for integer inventory or introduce an approved forward schema/RPC migration supporting fractional stock. Do not silently round line quantities or financial amounts. A business-contract/schema change remains owner-controlled.

Verification: disposable fresh and populated upgrade, authenticated real RPC, qty1/control,0.25/0.5/negative/zero, repeated sameproduct lines, replay/return/concurrency; assert persisted stock change equals summed accepted line quantity and rejected input leaves all order/item/payment/numbering/audit state unchanged. No native result is claimed by this review.

## FIN-02 — October migration overwrites the financial transition adapter

Severity: **High**, confirmed source-level composition regression; unmerged branches are not currently composed. It is not a new change to current823, nor a claim of live lost money.

Files:49 migration249–263/300–317;59 migration1209–1257;50client src/lib/db.ts605–619.49's old signature update_courier_order_state delegates to update_courier_outcome_v2, which enforces monotonic custody/legal transitions.59 recreates the same signature with its prior direct state setter and no v2 delegation or previous-state transition validation. Final71 does not restore it.50client still calls that legacy signature, so this is reachable through an actual consumer.

Valid source-derived fixture: active same-tenant staff/owner, customer+active courier, ordertotal100,paid0,statusdebt,deliverycourier,statedelivered_full,collected100. Requestpending:49v2 rejects invalid_transition; later59legacy writespending/collected0. All checked constraints allowpending0 with the validcustomer; the financial audit trigger records rather than rejects. Auth staff/lifecycle checks still pass. The existing EXECUTE grant remains;50 revokes only the two sale entrypoints, not this courier routine. **CREATE OR REPLACE does not itself resurrect revoked sale permissions**; that separate hypothesis is rejected.

Chronological fresh application uses August49/50 then October59 and loses the adapter. An upgrade applying backdated49 after59 can end with a different definition. Actual fresh/upgrade behavior must be tested, not inferred from separate green branches. [PostgreSQL CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html) documents replacement and retained permissions.

Required fix: one bounded forward migration after the actual latest source restores a single canonical adapter/transition implementation while retaining live-actor/tenant/role controls and Idempotency grants. Do not edit historical migrations. Verification: same final definition/ACL/RLS in fresh+populatedupgrade, deliveredfull→pending and custodydecrease reject with no state changes, valid partial→full and settlement/return controls work, concurrent transition/settlement and retry safe. Native SQL not run here.

## FIN-03 — an unresolved sale retry silently receives a new key after30minutes

Severity: **High before FIN-IDEM acceptance**. Introduced in unmerged50 client, not imported into the foundation. Confirmed actual client callback behavior with a synthetic compliant server; no database/provider calls.

File:50 src/lib/db.ts453–454,481–514,519–540. loadPendingSaleIdempotency unconditionally removes a pending key after30minutes; the next identical request creates a new UUID. The storage item can represent an unresolved, already-committed sale whose response was lost. Expiry does not reconcile or distinguish that case from a genuinely new sale.

The approved35 design's Client contract says one logical submission reuses the same key after an ambiguous result; Retention forbids correctness based on a timing window. Issue31 requires safe lost-response retry. Here the server still retains the original key, but the client stops using it.

Executed actual PR50 source with Node24.19 builtin stripTypeScriptTypes in an isolated VM: actual mutationFn/getOrCreate/loadPending executed with synthetic tabstorage/clock/UUID and a recording transport. The transport models the first write as committed but returns an error; the second uses the recorded key contract. After1second keys equal/model effects1; after1,800,001ms keys differ/model effects2. No waiting, real financial write or network occurred. client-retry-result.json records exact behavior. Initial helper expected the raw transport error text; actual rpcMessage normalizes unknown errors to Arabic. Corrected the helper oracle to assert that exact existing generic error, without changing the app, and retained this preparation limitation.

Required fix: persist the identity of the unresolved logical operation until a definitive result or explicit reconciliation/new-operation action. Expired session time must not silently transform a retry into a new operation. Keep genuinely new identical sales possible with explicit new operation identity. Review tab/session/storage-failure behavior and the single-pending-item replacement boundary.

Verification: lost response then retry within/beyond TTL/reload, definitive failure, multiple pending submissions, explicit new identical sale, server same-key conflict and concurrency. Use real isolated persisted counts/stock/payment effects after the focused client regression. Current wrapper's same-key contract appears structurally sound (unique tenant/op/key, exact JSON equality, one transaction); that does not rescue key continuity.

## Rejected or limited hypotheses

- Direct authenticated DML bypass on orders/order_items/payments: **disproved**,20260627201534:511–513 explicitly revoke INSERT/UPDATE/DELETE, native43 ACL corroborates read-only; retained RLS write policies do not grant privileges. An initial source search that stopped before the revoke was corrected before final findings. No actual unauthorized write occurred.
- Duplicate integerSKU rows oversell: **not proven**. Two-loop per-line validation does not aggregate a repeated product, but existing stock>=0 CHECK still applies to new rows even though NOT VALID; transaction rollback can prevent the alleged negative stored stock. Keep repeatedSKU/atomicity tests, do not report proven overselling from the first loop alone. Fractional rounding FIN-01 is different and survives that check.
-59 sale ACL resurrection: **disproved as asserted**; CREATE OR REPLACE retains existing ACL and59 does not regrant the sale signature. The real adapter collision is FIN-02.
- MD5 weakness: no standalone finding;50 also compares exact JSON payload, so a hash collision alone cannot authorize altered input.
- Existing35 design normalizes logically unordered representations while50 deliberately preserves array order. This policy/version difference should be reviewed before acceptance; it was not turned into an extra exploit claim.

## Actual checks and exclusions

10 source assertions plus arithmetic illustration passed (financial-source-result.json). Actual client callback2clockcases passed with fake transport and zero DB/provider calls. All41baseline SQL Gitblob identities and four material remote files matched. Independently inspected27/35/39 safety-net/design/status contracts and all28open PR relationships. Native PostgreSQL/psql/Docker/Bun are absent here; no new install/CI/native/production/provider/financial transaction was performed. Existing SQL/concurrency scripts were read, not executed. Source proof and modeled state are not persisted-data acceptance.

Overall no FIN-COURIER/FIN-IDEM/RC/Pilot approval. Sale, receipt, customer debt, courier custody, settlement and stock remain separate; Delivered≠Settled. Retain candidate/history and repair through focused gates rather than rewrite49/50 from scratch.
