# Independent pre-implementation review

Reviewer: `/root/closure_scope_review`, separately spawned non-implementing agent.
Source: PR68 `00923287d804f99faa1b70d28cece17f9f33eac3`, verified local source,
and exact fixture text in planning #55/6151090438. Review date2026-10-13 Africa/Tripoli.
Not a native GitHub account APPROVE or human merge authorization.

## Outcome: Blocked pending missing evidence / scope resolution

OC-FIXTURE-01 is a confirmed literal scope mismatch, not technical impossibility.
The reviewer independently searched all44 migration sources and read relevant effective definitions,
product/sale callers, original product
RLS/grants and retained native43 function catalog. No product creation RPC exists;
`useAddProduct` uses REST with price/cost/stock. The sale RPC requires an existing
valid stocked product. REST would be consistent with the earlier broader RPC/domain
proposal, but not the subsequently authorized RPC-only planning card. Do not silently
exclude product values from financial fixture scope, add a new RPC or borrow PR49/50.

The reviewer independently found no unique owner cardinality declaration in44 source
migrations; native43 catalog lacks standalone indexes. No single-store assumption or
final account-scope approval is made. Source and historic structural evidence stay separate.

Evidence paths:
- src/lib/db.ts / useAddProduct;
- supabase/migrations/20261010223557_enforce_live_account_state.sql / create_sale_with_items;
- supabase/migrations/20260626143241_8c05ee08-2167-458f-8092-777dcc86d8fe.sql / product grants;
- supabase/migrations/20260626151932_a2de7094-5740-498d-9437-09680527c275.sql / owner insert RLS;
- supabase/migrations/20260627201534_c35b8581-3304-41cf-86c6-b36bc6c6c879.sql / payment audit;
- changes/owner-retention-verify/evidence/native-9a5a/catalog.json and owner_catalog.sql.

## Explicit limits

Reviewer performed read-only source searches/inspection and independently reproduced
48 Git blob matches plus43 historical migration SHA256 matches. No DB, CI, financial fixture,
closure, old/new-token, live route, TRUNCATE/delete or independent runtime replay.
No file/GitHub mutation by reviewer. Existing16 offline oracle tests were run by implementer;
no reviewer test rerun is claimed. This verdict supports the blocker disposition only.
