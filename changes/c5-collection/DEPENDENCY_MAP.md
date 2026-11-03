# Call chain

InvoiceDetailScreen creates immutable input/UUID/current expected actor → AppCtx/actual app callback → useCollectDebt → executeCollection durable environment/tenant/actor slot → collect_order_debt_idempotent → existing collect_order_debt → orders/payments. Global CollectionRecovery invokes the same hook for retained requests even if current outstanding balance has changed. Query invalidation reads authoritative invoices/payments; stored original reply never overwrites current balance.

No new npm dependency or lock update. Existing financial_idempotency PK serializes identical keys, canonical order FOR UPDATE serializes distinct keys.
