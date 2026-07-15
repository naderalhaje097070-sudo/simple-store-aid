# Database Change Policy

## Core rules

- Do not edit an applied migration.
- Use a new forward-only migration for every schema, function, trigger, policy, grant, or data correction.
- Separate large backfills from structural changes when possible.
- Clean existing data before adding stricter constraints.
- Test migrations from a fresh database and from a production-like prior schema.
- Document lock, index-build, storage, runtime, and compatibility impact.

## Data integrity

Prefer enforceable database invariants where appropriate:

- `NOT NULL`
- `UNIQUE`
- `FOREIGN KEY`
- `CHECK`
- Exact numeric money types
- Transactions
- Row locking or optimistic concurrency
- Idempotency keys
- Appropriate indexes
- RLS
- Audit history

Application checks do not replace database constraints when the database can enforce the rule safely.

## Financial changes

Any mutation of balances, payments, debt, custody, settlement, stock linked to a financial event, or day closing must be:

- Authorized on the server.
- Executed atomically in a transaction.
- Exact-decimal based; never floating point.
- Safe under retry and duplicate submission.
- Audited with actor, tenant, operation, entity, and outcome.
- Tested for concurrent execution and partial failure.
- Reversible or supported by an explicit compensating operation.

## RLS and grants

For tables reachable from the client:

- Enable RLS unless a documented server-only boundary makes it unnecessary.
- Deny access unless a narrow policy grants it.
- Review grants and RLS together; either layer can create an unintended path.
- Test direct table and RPC access, not only UI behavior.
- Security-definer functions must set a safe `search_path` and validate identity, tenant, role, ownership or assignment, and legal state transitions.

## Migration planning

Every database-impacting change documents:

- Current schema and invariant
- Target schema and invariant
- Data volume and affected rows
- Backfill or cleanup sequence
- Compatibility window
- Index and lock impact
- Deployment order
- Verification queries
- Rollback or compensating migration
- Backup or snapshot requirement

Use expand-and-contract for incompatible changes:

1. Expand schema while preserving existing consumers.
2. Deploy compatible writers and readers.
3. Backfill and verify.
4. Switch consumers.
5. Contract obsolete schema in a later reviewed change.

## Production safety

Agents and automated tests do not connect to Production or use Production secrets. Production migrations, backfills, destructive queries, restores, and compensating operations require explicit human approval and a reviewed runbook.
