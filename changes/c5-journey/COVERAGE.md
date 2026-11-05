# One coverage ledger — C5 financial journey

All new rows are not-run until real exact-source workflow evidence is recorded. Synthetic setup may seed references; every business transition below uses actual application UI and SDK. Scope excludes route/auth entry, PDF, SW and restored HTTP/Auth. Old runtime evidence is reused only under exact executable and PostgreSQL image binding.

| ID | Actor / entry | Contract and independent oracle | Existing evidence | Gap disposition |
|---|---|---|---|---|
| J1 | Own active owner / real SaleQuickScreen | .25×100=25, cost10, stock9.75; hidden committed response then reload identical key/payload/actor gives one order/payment | C4 mock-transport UI + separate native hook | new actual app journey |
| J2 | Own active owner / SaleScreen, InvoiceDetailScreen, CollectionRecovery | debt100;20 commit + same-key reload no extra effect;80 completes paid100/two payments | C5 actual collection20+20 only | complete via actual UI |
| J3 | Own owner / courier screen | pending100→partial40: paid0/custody40/no cash; global cash125/debt60 | lower-layer RPC passes | actual UI intermediate oracle |
| J4 | Own owner / settlement screen | one settlement40→cash165/custody0/debt60, then collection60→cash225/debt0 | lower-layer RPC/idempotency | actual UI integration |
| J5 | Own owner / courier returned state | .5 return adds exactly.5 stock→7.75; no cash/debt/custody | lower-layer direct return RPC | UI existing update_courier_order_state adapter |
| J6 | Own owner / QuickExpenseSheet | actual SDK/RLS insert5; expenses5/cash220/realizedProfit130 | zero expenses only in baseline | nonzero UI and stored oracle |
| J7 | Own owner / MoneyDetails, ProfitScreen, DayCloseScreen | issued sales275 incl returned50, collections225, expenses5, realized130, debt0/custody0; stored close_day equals literals | earlier close_day checks predate return/final collections | final actual UI + stored snapshot |
| J8 | Other populated tenant / real product reads | foreign product invisible, foreign order/stock unchanged after all UI mutations | native RPC/RLS evidence | UI read scope + persisted unchanged control |
| J9 | Unauthorized/banned/other staff/concurrency/retry / RPC | deny with unchanged relations, exactly-once and balance/stock caps | a88d4fba collection108/111, frozen source/image | reuse; no rerun without drift |
| J10 | Independent recovery / SQL-role only | full selected rows/ACL/RLS, inactive denial, positive/replay/conflict/new payment/cleanup | a88d4fba native41993105090 77/77 each, original ZIPs | reuse; no restored HTTP/Auth claim |

Final oracle: initialstock10; cash sale25 + full debt100 + settled courier100 = collected225; total issued invoices25+100+100+returned50=275; margin135−expense5=130; stock10−.25−1−1−.5+.5=7.75. Values are literal test-case expectations, not copied from response or app financial formulas.
