# Reproduction and Evidence

## Reference implementation

- Pull request: #17.
- Branch: `feature/employee-accounts-custody-v1`.
- Recorded head: `dd77ffcc3d5d3ba3f30d9d3485288c999264a297`.
- Base: `main`.
- Current comparison: diverged, 51 commits ahead and 25 commits behind `main`.

PR #17 must not be rebased, force-pushed, or treated as the approved implementation branch. It is retained as evidence and a prototype.

## CI baseline on the recorded head

### Quality

Result: Passed.

The recorded workflow completed type checking, linting, unit tests, and production build successfully.

### Ephemeral Financial Rules

Result: Failed.

Verified step results:

- Isolated Supabase startup: Passed.
- Test owner and tenant seed: Passed.
- Employee identity seed: Passed.
- Existing financial regression T1–T15: Passed.
- Employee account and custody isolation suite: Failed.
- Environment teardown: Passed.

The exact failing SQL assertion is not established by the retained summary evidence and must not be guessed. Reproduction requires running the employee-account suite against a clean isolated database and retaining a concise failure tail without secrets.

### Isolated Auth UI Smoke

Result: Failed.

Verified step results:

- Dependency installation: Passed.
- Isolated Supabase startup: Passed.
- Owner account creation: Passed.
- Employee and assigned-order creation: Passed.
- Production application build: Passed.
- Cloudflare production emulator: Passed.
- Playwright installation: Passed.
- Owner and employee authenticated smoke: Failed.
- Evidence upload and teardown: Passed.

The exact Playwright assertion or browser error is not established by the retained step summary and must be reproduced before design or implementation decisions rely on it.

## Security and financial review findings

### Finding EMP-BL-001

- Severity: High / P1.
- Contract: Employee order-state RPC.
- Evidence: Active unresolved review thread on `courier_update_my_order_state` in migration `20260715143000_courier_employee_accounts.sql`.
- Scenario: An assigned employee records full or partial collection, then directly calls the RPC again to replace the delivery result with zero or a smaller collection.
- Risk: Previously recorded `collected_by_courier` can be reduced before owner settlement; the UI hides controls but the server contract remains callable.
- Required design outcome: Employee delivery recording must be one-way from an allowed pre-delivery state, or corrections must use a separate owner-authorized audited contract.
- Verification: Database contract tests for repeated, lower-value, conflicting, and concurrent calls.

### Finding EMP-BL-002

- Severity: High / P1 in the reviewed implementation; thread is outdated but unresolved.
- Contract: Disable/unlink lifecycle and settlement UI availability.
- Evidence: Review identified that unlinking could mark a courier inactive while custody remained unsettled, while the existing settlement selector used active couriers.
- Risk: Owner may be unable to select the courier to settle collected cash, stranding custody operationally.
- Required design outcome: Disable and unlink semantics must preserve a settlement path. Either block unlink while custody exists, separate login disable from courier activity, or provide an explicit historical-courier settlement workflow.
- Verification: Integration and E2E tests for disable/unlink before and after settlement.

## Reproduction procedure

### Approved baseline verification

From a fresh branch based on current `main`:

```bash
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

Run the existing isolated financial workflow and authenticated UI smoke against `main` to establish that the approved baseline remains green.

### PR #17 failure reproduction

Use an isolated checkout or disposable worktree of the recorded PR #17 head. Do not connect to Production.

1. Start a clean local Supabase environment and apply the full migration chain.
2. Seed one owner, two employees, at least two assigned orders, and a second tenant.
3. Run `tests/financial-rules/run.sh` and record T1–T15 separately.
4. Run `tests/employee-accounts/run.sh` and retain the exact first failing assertion.
5. Build the production application against the isolated Supabase environment.
6. Run `tests/e2e/isolated-auth-smoke.py` and retain the first failing assertion, browser URL, role, and screenshot.
7. Stop and remove the isolated environment.

### P1 custody rewrite reproduction

1. Assign a pending courier order to Employee A.
2. Authenticate as Employee A.
3. Record `delivered_full` or `delivered_partial` with a positive collected amount.
4. Call the employee delivery RPC again for the same order using `delivered_none` or a smaller partial amount.
5. Verify whether stored `courier_state` or `collected_by_courier` is overwritten.
6. Verify that no UI assumption is used as the authorization boundary.

Expected secure result: The second call is rejected without changing the stored order or custody.

## Unverified items

- The exact SQL assertion causing the latest employee-account suite failure.
- The exact Playwright assertion causing the latest authenticated smoke failure.
- Whether later uncommitted or abandoned work addressed the outdated unlink finding.
- Concurrency behavior for repeated employee delivery updates and settlement requests.
- Compatibility of PR #17 migrations with current `main` after governance and other intervening commits.
