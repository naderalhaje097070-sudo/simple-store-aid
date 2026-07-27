# SEC-ENV-001 — Security Impact

## Security boundary

Environment resolution determines which Supabase project receives authentication, database, storage, and RPC traffic. It is therefore a security and financial-data boundary, not merely build configuration.

## Current finding

When explicit variables are absent, build configuration substitutes production Supabase URL/key/project ID. This allows non-production intent to collapse into production targeting without an affirmative production signal.

## Threat scenarios

- Preview build performs authenticated reads/writes against production.
- Local developer build uses production unintentionally.
- CI/UI test writes reach production after an environment-resolution regression.
- A missing variable silently degrades into production rather than stopping.

## Required controls

- Deny-by-default environment mode.
- Explicit production-deployment intent.
- Non-production production-target rejection.
- Local/CI isolation sentinel and target validation before writes.
- No production service-role secret in client/build config.
- Clear error without printing secret material.

## Authorization/RLS

RLS remains required but is not a substitute for environment isolation. A valid production user could still mutate real tenant data from a preview accidentally.

## Independent review

Must inspect build-time and SSR/client paths together and attempt negative cases for missing, blank, mismatched, and production-target values.