# Impact

Products.stock changes integer→unconstrained numeric, and order_items.qty changes numeric(12,2)→unconstrained numeric. Explicit bounded two-decimal CHECKs reject unsupported precision before any typemod rounding. Existing legacy sale RPC uses uncoerced raw numeric and validates before numbering/inserts. Original50SQL remain immutable; current live actor/staff checks and all nonquantity body logic retained. No new RPC or grant.

Current stock form accepts decimal text without stripping its separator. Shared quantity parser/step/sum helpers and an editable cart field serve both sale paths, including stock below1 and exact decimal step/sum behavior. Current hooks reject invalid stock/line quantities before transport. Price, cost, monetary totals/formulas, debt/courier states and C4keys stay unchanged. Only three existing source files plus new helper/component and one additive migration. Existing integer stock converts exactly; no historical financial correction is attempted.
