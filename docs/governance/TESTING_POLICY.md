# Testing Policy

Tests are selected from the risk and contracts of the change. Green happy-path tests alone are insufficient for financial, authorization, tenant, or state-transition changes.

## Test categories

Use the applicable categories:

- Unit tests
- Integration tests
- Regression tests
- API and RPC contract tests
- Database contract tests
- Authorization tests
- Tenant-isolation tests
- Concurrency tests
- Idempotency and retry tests
- Migration tests
- E2E tests
- Security tests
- Performance tests
- Post-deployment smoke tests

## Required scenarios

Test as applicable:

- Happy path
- Invalid input and boundary values
- Missing data
- Unauthenticated access
- Authenticated but forbidden access
- Cross-user and cross-tenant access
- Duplicate request
- Concurrent request
- Partial failure
- Retry after ambiguous failure
- Illegal state transition
- Disabled account
- Direct API or database bypass
- Backward compatibility

## Financial and custody changes

Changes to payments, debt, custody, settlement, returns, stock linked to a sale, or closing require tests that prove:

- Exact amounts and rounding behavior
- Atomicity under failure
- No duplicate accounting entry on retry
- Correct row ownership and tenant
- Correct actor authorization
- Legal state transitions only
- Correct audit record
- Correct rollback or compensation behavior
- Concurrency safety

## Authorization and RLS changes

Use at least:

- Owner
- Authorized employee A
- Authorized employee B
- Disabled or unassigned user
- A second tenant when tenant scope is relevant

Prove both positive access and denied access. Query or call the protected resource directly; hiding a button is not a security test.

## Baseline commands

The repository minimum application baseline is:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Database and E2E commands are change-specific and must be documented in the change plan and completion report.

## Test integrity

- Do not weaken or remove a valid test to obtain a green result.
- Fix flaky tests by identifying nondeterminism, isolation failures, time dependence, race conditions, or invalid fixtures.
- Do not use Production data or secrets.
- Test fixtures must be isolated, deterministic, and cleaned by environment teardown or transaction rollback.
- Record actual command output or CI results and the exact commit tested.

## Acceptance

A change is not accepted when any required test is failed, skipped without approved rationale, or not verified. Use explicit statuses: Passed, Failed, or Not verified.
