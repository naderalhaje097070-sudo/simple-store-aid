# Database Change Policy

## General rules

- Applied migrations are immutable.
- Every correction uses a new forward-only migration.
- Separate schema changes from large backfills.
- Clean incompatible data before adding constraints.
- Test migrations on an isolated environment that applies the full migration chain from a clean database.
- Analyze locks, table scans, index creation, and deployment-time impact.
- Use expand-and-contract for incompatible changes.
- Prepare rollback or a compensating migration before release.

## Data integrity

Use database constraints when the rule can be enforced there:

- `NOT NULL`.
- `UNIQUE`.
- `FOREIGN KEY`.
- `CHECK`.
- Exclusion constraints where appropriate.
- Transaction boundaries.
- Row locking or optimistic concurrency.
- Idempotency keys.
- Indexes that support validated access paths.
- RLS for tenant and assignment isolation.
- Audit records for sensitive state changes.

Application validation supplements database integrity; it does not replace it.

## Financial data

- Never use floating-point types for money.
- Use PostgreSQL `numeric`/decimal semantics or integer minor units.
- Financial changes must be transactional, authorized, auditable, and retry-safe where duplicate execution is possible.
- Define compensation or reversal behavior before rollout.
- Add concurrency and idempotency tests for sensitive operations.
- Do not derive settled receipts from delivery state alone.
- Returned orders must not create debt or custody.

## Migration design record

Every database change must document:

- Current schema and behavior.
- Target schema and behavior.
- Data volume and affected tenants.
- New constraints and indexes.
- Backfill requirements.
- Compatibility window.
- Lock and performance impact.
- RLS and privilege impact.
- Audit impact.
- Test plan.
- Rollout order.
- Rollback or compensation procedure.

## RLS and privileges

- Deny by default.
- Grant the minimum table and function privileges required.
- Security-definer functions must validate actor, tenant, resource assignment, and state.
- Set a safe `search_path` in privileged functions.
- Do not assume an RLS policy name; inspect all policies and grants before replacing or tightening access.
- Test direct table access as well as RPC behavior.
- Test cross-tenant and cross-employee reads and writes.

## Production boundary

- Automated work must not apply migrations to production.
- Automated tests use isolated or disposable databases.
- Production migration, backup, restore, and rollback actions require explicit human approval.
