# FIN-IDEM-001 — Security Impact

## Trust boundary

The idempotency key originates from an untrusted client. It identifies a logical retry but does not grant authorization or ownership.

## Required controls

- Resolve tenant and actor server-side before idempotency lookup/replay.
- Scope uniqueness by tenant and operation.
- Prevent direct client insert/update/delete of idempotency records unless an explicitly safe policy exists; preferred ownership is through security-definer transactional RPCs with explicit tenant/role checks.
- Use a safe `search_path` in security-definer functions.
- Bound key length/format to prevent abuse and pathological index/storage use.
- Do not expose another tenant's result when a key collides across tenants.
- Request hashes/canonical payloads must not include secrets unnecessarily.

## Threat scenarios

- Attacker guesses another tenant's key and retrieves/replays a result.
- Same key reused with altered amount/items/customer to smuggle a different financial request.
- Concurrent duplicate requests both commit because reservation is not protected by a unique database constraint.
- Client tampers with an idempotency row to force replay or bypass execution.
- Unbounded random keys create storage abuse.

## Audit

The financial audit trail should identify the original committed operation. Replays should not generate duplicate financial mutation audit events; optional replay telemetry may be recorded separately if useful.

## Deny-by-default

Any ambiguous mismatch in operation, tenant, or canonical request must reject rather than execute a new financial write under an existing key.