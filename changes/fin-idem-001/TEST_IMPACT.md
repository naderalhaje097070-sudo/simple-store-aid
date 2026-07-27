# FIN-IDEM-001 — Test Impact

## Gate-4 safety net before implementation

### I1 — exact retry

Execute the same tenant/operation/key/canonical request twice after the first call commits.

Expected target:
- same logical result/order ID returned;
- one order;
- one tenant number consumed;
- stock decremented once;
- direct payment created once where applicable.

Current baseline is expected RED because FIN-COURIER E3 proves duplicate sale creation.

### I2 — conflicting retry

Same tenant/operation/key, different financially material request.

Expected:
- deterministic idempotency conflict;
- original result unchanged;
- no second financial effect.

### I3 — concurrent exact duplicate

Two sessions submit the same key/request concurrently.

Expected:
- one winner financial execution;
- loser/replayer receives the winner's committed result;
- exactly one order/payment/stock decrement.

### I4 — failed winner transaction

Inject a failure after reservation but before transaction commit.

Expected:
- financial changes roll back;
- idempotency reservation rolls back;
- later same-key retry can execute successfully once.

### I5 — tenant isolation

Two tenants may use the same textual idempotency key independently. A caller cannot read/replay the other tenant's result.

### I6 — operation isolation

Same tenant/key used for different protected operations does not collide unless the design explicitly scopes them together.

### I7 — canonical request normalization

Semantically equivalent request representation hashes/compares as equal; materially different amount/items/customer/courier/outcome compares as different. Exact canonicalization rules are frozen before implementation.

### I8 — replay audit effects

Financial mutation audit evidence is created once for the original execution; replay does not duplicate mutation events.

## Regression

- T1–T15 remain GREEN.
- FIN-COURIER approved financial contract remains GREEN.
- Stock/concurrency rules remain GREEN.

## Execution environment

Fresh isolated Supabase; no production credentials/data.