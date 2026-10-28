# API compatibility

| Boundary | Existing accepted main | Old candidate target | Acceptance requirement |
|---|---|---|---|
| Sale | create_sale_with_items(6args), typed result, null check | create_sale_with_items_idempotent(8args)→v2(7args) | Typed bridge and generated schema truth; no any/silent fallback; no caller left on revoked entry |
| Creation | CreateSaleInput no courierState, UI infers payment status | explicit courierState with fallback inference | Honor approved outcome/customer matrix through both UI paths; no returned-at-create |
| Courier updates | legacy(text,numeric) currently direct setter after October | v2(enum,numeric,customer) + compatibility adapter | Forward C3 restores one canonical transition while preserving live checks and grants |
| Request replay | main has no logical key | tenant/op/key + exact JSON equality | Keep order/normalization decision explicit;35 normalization vs50 order-sensitive items remains an acceptance/design difference, not an invented hash vulnerability |
| Result/error | main rejects null result | old50 clears pending before reading data | Validate definitive result before clearing; uncertain/malformed result retains identity |

Full old db.ts is never substituted for accepted main. Primary source/API contracts are pinned in SOURCE_INPUTS.json. No new API is published by C1.
