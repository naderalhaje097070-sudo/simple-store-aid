# PR #17 Scope Map

PR #17 combines multiple independently reviewable contracts. This map records why it is not an acceptable release unit.

## CI and test infrastructure

Files:

- `.github/workflows/ephemeral-financial-rules.yml`
- `.github/workflows/isolated-auth-smoke.yml`
- `.github/workflows/quality.yml`
- `tests/e2e/isolated-auth-smoke.py`

Contracts affected:

- Required PR checks.
- Isolated database lifecycle.
- Authenticated owner and employee smoke behavior.
- CI reporting and artifacts.

These changes should not be bundled with the complete feature implementation unless they are strictly required for a single safety-net PR.

## Employee UI and client data access

Files:

- `src/features/employees/EmployeeAccountCard.tsx`
- `src/features/employees/EmployeeAccountsList.tsx`
- `src/features/employees/EmployeeOrderCard.tsx`
- `src/features/employees/EmployeePortal.tsx`
- `src/features/employees/employee-db.ts`
- `src/features/settings/SettingsScreen.tsx`

Contracts affected:

- Owner employee-account administration.
- Employee assigned-order and custody presentation.
- Client RPC calls and error handling.
- Disable/unlink workflow.

These files depend on approved database, authorization, lifecycle, and state-transition contracts and must not define those contracts themselves.

## Routing and authenticated session behavior

Files:

- `src/routes/_authenticated/employee.tsx`
- `src/routes/_authenticated/employees.tsx`
- `src/routes/_authenticated/route.tsx`
- `src/routeTree.gen.ts`

Contracts affected:

- Role-based route entry.
- Owner and staff redirect behavior.
- Disabled-account behavior.
- Generated routing output.

The generated route tree is an output, not an independently designed source file.

## Database identity, authorization, and financial rules

Files:

- `supabase/migrations/20260715143000_courier_employee_accounts.sql`
- `supabase/migrations/20260715144000_employee_policy_hardening.sql`
- `supabase/migrations/20260715144500_employee_guard_error_codes.sql`
- `supabase/migrations/20260715145500_courier_account_column_guards.sql`
- `supabase/migrations/20260715145600_employee_admin_data_isolation.sql`

Contracts affected:

- Courier-to-user identity link.
- Role and tenant resolution.
- Account disable and unlink lifecycle.
- Assignment-level RLS.
- Employee delivery-state transitions.
- Custody calculation and settlement requests.
- Owner-only financial and administrative data access.
- Error codes, grants, and protected-column guards.

This is the highest-risk part of the feature and requires its own approved design, migration review, and database contract tests.

## Employee database regression tests

Files:

- `tests/employee-accounts/account-link-guards.sql`
- `tests/employee-accounts/admin-data-isolation.sql`
- `tests/employee-accounts/rules.sql`
- `tests/employee-accounts/run.sh`
- `tests/employee-accounts/seed-auth-users.sql`
- `tests/employee-accounts/tenant-escape.sql`

Contracts affected:

- Cross-employee isolation.
- Cross-tenant isolation.
- Account-link and protected-column guards.
- Delivery, custody, request, and disabled-account rules.

These tests are valuable evidence, but the latest recorded suite fails. They must be evaluated against approved contracts rather than copied without review.

## Required decomposition

### EMP-001 — Specification and safety baseline

Documentation only:

- Actors and roles.
- Current and expected behavior.
- Business rules and state transitions.
- Authorization matrix.
- Database invariants.
- Threat model.
- Acceptance criteria and test strategy.

### EMP-002 — Identity and authorization foundation

One coherent database/security change:

- Employee identity relationship.
- Tenant and role resolution.
- Owner-controlled link, disable, enable, and unlink.
- Historical identity preservation.
- RLS and authorization tests.

No employee delivery or settlement feature logic.

### EMP-003 — Assignment, delivery, custody, and settlement contracts

One coherent domain/database change:

- Assignment source of truth.
- Legal state transitions.
- Collection and custody rules.
- Settlement-request lifecycle.
- Audit, idempotency, concurrency, and financial regression.

### EMP-004 — Owner and employee UI

- Owner management UI.
- Employee portal.
- Typed client contracts.
- Role-based routing.
- RTL, desktop, and mobile behavior.

No security rule may exist only in this PR.

### EMP-005 — E2E and pilot readiness

- Owner, Employee A, Employee B, disabled employee, and second-tenant scenarios.
- Production-like isolated smoke.
- Pilot checklist and rollback verification.

## Reuse decision

No PR #17 file is approved for direct cherry-pick at Gate 1. Change Gate 2 and Change Gate 3 will determine which concepts, tests, and implementation fragments can be reused safely.
