# Security Baseline

Mongezz handles personal, commercial, and financial data. Security controls are part of the business contract, not optional UI behavior.

## Default principles

- Deny by default.
- Least privilege.
- Server-side validation and authorization.
- Tenant isolation on every tenant-owned resource.
- RLS for direct client database access.
- No trust in client-supplied tenant, role, amount, state, ownership, or settlement data.
- No secrets in source control, client bundles, logs, screenshots, fixtures, or PR descriptions.

## Authentication and sessions

- Use the approved authentication provider and verified server-side identity.
- Do not authorize from email, display name, local storage, or client-provided role claims alone.
- Disabled users must lose protected read and mutation access.
- Session errors must be explicit and traceable without exposing tokens.

## Authorization

Every protected operation must verify:

1. Authenticated identity.
2. Active account state.
3. Tenant membership.
4. Required role or capability.
5. Ownership or assignment of the target resource.
6. Legal state transition.

The UI may hide unavailable actions, but database or server authorization remains mandatory.

## Tenant isolation

- Every tenant-owned table has a tenant identifier or a documented equivalent boundary.
- Cross-tenant identifiers supplied by the client are rejected.
- Authorization and RLS tests use at least two tenants and two users where relevant.
- Security-definer functions set a safe `search_path` and validate tenant and role explicitly.

## Data and input protection

- Validate input types, ranges, formats, state, and ownership server-side.
- Protect against injection with parameterized operations and safe dynamic SQL practices.
- Protect against IDOR by resolving access from the authenticated identity, not only object identifiers.
- Protect against mass assignment by explicitly allowing writable fields.
- Encode untrusted output in the relevant rendering context.
- Avoid sensitive data in logs and error messages.

## Financial and high-risk operations

Financial mutations must be:

- Transactional
- Authorized
- Idempotent where retry is possible
- Audited
- Exact-decimal based
- Protected from duplicate and concurrent execution
- Reversible or compensatable

## Platform controls

Use or document, as applicable:

- Dependency scanning
- Secret scanning
- Security headers
- Rate limiting and abuse controls
- Error monitoring
- Audit trails
- Backup and restore procedures

## Required security verification

Changes to authentication, authorization, RLS, roles, employee accounts, assignments, money, or tenant data require:

- Unauthorized and forbidden tests
- Cross-user tests
- Cross-tenant tests
- Direct API or database bypass tests
- Invalid state-transition tests
- Disabled-account tests
- Mass-assignment tests where writable models change
- Independent adversarial review
