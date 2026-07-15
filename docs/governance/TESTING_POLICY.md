# Testing Policy

Select tests according to the contracts affected by the change. Do not rely only on happy-path UI checks.

## Test layers

Use as applicable:

- Unit tests.
- Integration tests.
- Regression tests.
- API and RPC contract tests.
- Database contract tests.
- Authorization tests.
- Tenant-isolation tests.
- Migration tests.
- Concurrency tests.
- Idempotency and retry tests.
- E2E tests.
- Security tests.
- Performance tests.
- Smoke tests.

## Required scenarios

Test:

- Happy path.
- Invalid and boundary inputs.
- Missing data.
- Unauthenticated access.
- Authenticated but forbidden access.
- Cross-tenant access.
- Cross-employee or unassigned-resource access.
- Duplicate requests and retries.
- Concurrent requests.
- Partial failure and compensation.
- Illegal state transitions.
- Disabled-account behavior.
- Migration from a clean database and from representative prior state.

## Financial and custody changes

Financial tests must prove the stored data, not only displayed values. Verify:

- Transaction atomicity.
- Authorized actor and tenant.
- Correct debt and remaining balance.
- Correct courier custody.
- No receipt before settlement.
- Settlement records cash once.
- Return restores inventory without debt or custody.
- Duplicate execution does not double-post.
- Concurrent execution cannot exceed available balance, inventory, or custody.
- Audit events identify the actor and operation.

## Authorization changes

Use at least:

- Owner.
- Authorized employee A.
- Authorized employee B.
- Disabled employee.
- User from another tenant where the feature is tenant-scoped.

Verify both RPC/API behavior and direct database access under RLS. Hidden UI is not evidence of authorization.

## Regression discipline

- For a bug, add a regression test that fails before the fix when feasible.
- Do not weaken or remove an existing test solely to make new code pass.
- A changed contract requires a contract test or explicit compatibility verification.
- Test fixtures must be isolated, deterministic, and must not use production.
- Test cleanup must not require public production RPCs.

## Verification evidence

Record:

- Exact command or workflow.
- Commit SHA.
- Environment.
- Test count or scenarios.
- Actual result.
- Failure evidence.
- Artifacts or screenshots where useful.
- Items not tested.

Passing tests are necessary but not sufficient. Independent product, architecture, security, and rollback review remain required.
