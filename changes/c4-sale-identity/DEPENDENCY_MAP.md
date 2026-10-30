# DEPENDENCY MAP

UI SaleScreen/PaymentSheet + SaleQuickScreen -> useCreateSale -> executeSale -> typed create_sale_with_items_idempotent -> C3 live actor/staff guard + tenant scoped idempotency -> create_sale_with_items_v2 -> canonical core -> orders/items/payments/stock. SaleRecovery -> actual Auth getUser/onAuthStateChange + scope-localStorage -> same hook. Historical G0 AST/legacy callback remains explicitly historical via C4 snapshot bridge; mandatory actual C4 tests enforce new caller. Existing Supabase SDK2.110.5, React19.2.5 and Bun lock unchanged.
