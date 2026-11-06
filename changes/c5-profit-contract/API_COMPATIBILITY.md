# Proposed compatibility contract

| Boundary | Legacy behavior retained | Additive behavior |
|---|---|---|
| day_closes.realized_profit | Recorded before-expense margin135 | No mutation |
| close_day(text) | Signature/guards/upsert/JSON gross135 unchanged | No new writer semantics |
| get_tenant_today_estimate | Existing result keys/gross meaning unchanged | Document legacy basis; no in-repo hook caller found |
| get_platform_day_close_health | Row shape/privileged scope unchanged | Admin label explicitly before expenses |
| day_close_profit_report (new) | Includes unchanged realized_profit for compatibility | Explicit realized_margin_before_expenses135 and realized_net_profit130 |
| DBDayClose.realizedProfit | Legacy before-expense property retained | Explicit margin/net properties; propagate actual DayCloseRow type |
| General ProfitScreen | Existing period-based estimate calculation retained | Label estimated net after expenses; not a universal cash-basis equality claim |

Source readers use a mixture of invoice-period estimates and payment-date day-close values. Same numeric135/130 in this fixture is not proof of equality for all dates/partial collections. Do not silently change a legacy property to net while retaining its old name. Missing/unavailable new view must surface an explicit read failure, not invented zero or a silent fallback. The current caller's dbDayCloses ?? [] must not turn a new report-read failure into an apparently open/healthy day: the approved implementation must reuse the existing financial read-state boundary for this dependency. Old client/RPC behavior must remain successful in compatibility tests. Generated View types come from actual schema tooling after adoption.
