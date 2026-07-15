# Security Baseline

Apply these controls by default. Any exception requires an explicit documented decision and compensating controls.

## Trust boundaries

- Treat all client input as untrusted.
- Authentication establishes identity; it does not grant authorization by itself.
- Enforce authorization server-side and in the database where data access is involved.
- Use deny-by-default and least privilege.
- Keep production data, production secrets, and destructive production controls outside automated-agent access.

## Required controls

- Server-side input validation.
- Server-side authorization.
- Tenant isolation.
- Assignment-level isolation for employee-scoped resources.
- Secure session handling.
- Output encoding.
- Secret isolation and environment validation.
- Protection against injection, IDOR, mass assignment, and unsafe direct-object references.
- Rate limiting or abuse controls where authentication, invitations, password recovery, webhooks, or expensive actions require them.
- Security headers appropriate to the deployment platform.
- Dependency and secret scanning in the delivery pipeline where supported.
- Logging that excludes passwords, tokens, secret keys, full payment identifiers, and unnecessary personal data.

## Authorization design

For every protected operation record:

- Actor.
- Authentication requirement.
- Tenant requirement.
- Role requirement.
- Resource ownership or assignment requirement.
- Allowed state transition.
- Fields the actor may read.
- Fields the actor may write.
- Audit event.
- Failure response.

Create an authorization matrix for security-sensitive features.

UI visibility is not an authorization control. A user must receive the same denial when calling the API or database directly.

## Tenant isolation

- Every tenant-owned row must have an unambiguous tenant identity.
- RLS policies must use the authenticated identity and approved tenant-resolution functions.
- Security-definer functions must validate tenant and role explicitly and use a safe `search_path`.
- Test cross-tenant reads and writes using at least two tenants.
- Test cross-employee access using at least two employees when assignment restrictions exist.

## Sensitive operations

Financial, custody, settlement, return, day-close, permission, and account-link operations must be:

- Authorized.
- Validated.
- Transactional.
- Audited.
- Retry-safe or idempotent where duplicate execution is possible.
- Protected against illegal state transitions.
- Covered by positive and negative tests.

## Authentication and account lifecycle

- Disabled accounts must be denied server-side, not only redirected by the UI.
- Disabling or unlinking an employee must preserve financial and audit history.
- Account invitation/linking must prevent cross-tenant takeover and accidental role escalation.
- Users must not be able to change protected role, tenant, disabled, or assignment fields through generic profile updates.
- Passwords and tokens must never be placed in source control, logs, issue bodies, or test artifacts.

## Security review output

Record findings with:

- Severity.
- Affected file, policy, RPC, or contract.
- Evidence.
- Exploit or failure scenario.
- Required fix.
- Verification method.

A security change is not accepted solely because the UI behaves correctly or because the happy path passes.
