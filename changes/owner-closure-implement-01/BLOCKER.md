# OC-FIXTURE-01 — RPC-only product fixture boundary

Status: confirmed source/contract mismatch; blocks this batch before financial writes.
This is not a proven application exploit, financial failure or runtime closure defect.

## Authorized boundary

Planning #55/6151090438 says literally:

> أنشئ أقل سجل B ممثل وغير فارغ من منتج/طلب/بنود/دفعة/تدقيق، عبر RPCs المعتمدة وعلى المصدر المختار. لا SQL مباشر لكتابات مالية ولا استعارة وظائف من PR49/50 غير المدمجين. إن منع العقد الحالي بناء fixture سليمًا، وثّق العائق دون توسيع الدفعة إلى إصلاح المالية.

The earlier NEXT_BATCH.md says RPC/domain logic, but the newly authorized planning card
is narrower. Authorization for the isolated financial fixture already exists; the
issue is its allowed creation surface, not missing generic permission.

## Evidence

1. `src/lib/db.ts` / `useAddProduct` performs authenticated
   `supabase.from("products").insert(...)` with price, cost and stock. It is a REST table
   insert, not an RPC. Calling it through a test does not convert it into an approved RPC.
2. The retained native43 catalog inventories every public/private application function
   using `tests/account-lifecycle/owner_catalog.sql`. It has40 public functions; none
   inserts products. `create_sale_with_items` selects an existing product and rejects
   an absent product before creating an order. Its allowed mutations reduce existing
   stock and create order/items/payment; payment triggers create audit history.
3. All43 catalog-era migration hashes reconcile with the selected source. Migration44
   only revokes TRUNCATE/default privileges; it adds no product creation routine.
   Current source44 therefore supplies no selected-source product-creation RPC.
4. `delete_product_safe` deletes/archives; return/delete-order functions restore stock
   on existing products. They do not supply a product creation fixture.
5. The historical native43 stack was empty for products and all original finance7.
   No existing legitimate fake product can be assumed in a fresh acceptance run.

Pinned blob hashes and exact function inventory are in [SOURCE_EVIDENCE.json](SOURCE_EVIDENCE.json).
The current worker performed source checks, not a new DB run. Historic catalog evidence
remains native43 at9a5a58f6a8556f009880437c0cf95ac91c38c770; it is not re-labelled live44.

## Why execution stops

Inserting price/cost/stock through REST or SQL would depart from the literal RPC
fixture boundary; adding a product RPC or borrowing PR49/50 would widen the task.
An empty fixture would fail populated-history acceptance. None is taken silently.
No financial write, closure, ban, deletion or TRUNCATE was executed.

## One next for planning

Resolve the fixture surface with one explicit bounded amendment: permit creating
one synthetic product through the **existing authenticated owner REST/RLS product
path** on the disposable local stack, while order/items/payment/audit continue through
`create_sale_with_items` and its existing triggers only. No direct SQL financial seed,
new RPC, production data, changed financial contract or borrowed PR is proposed.
This amendment is a proposal for the planning conversation, not approval or execution.
After it is authorized, resume this same task from this packet and unchanged PR68;
complete cardinality/intake, failing safety net, narrow closure implementation and
fresh/upgrade/JWT/REST/RPC/full-route/idempotence/retention proof. Recheck source/claims.

## Separate remaining intake item

The44 migration source shows no standalone unique owner index, while the native43
catalog did not inventory indexes. That supports not assuming one store per account,
not a fresh live cardinality proof. Record actual pg_index before implementing.
No new account/store policy, reference choice or closure schema is fixed by this packet.
