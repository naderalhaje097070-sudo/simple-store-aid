# SEC-ENV-001 — Data Impact

## Production data

No intended production data access or mutation. The change exists specifically to reduce accidental production targeting from non-production contexts.

## Current risk

A misconfigured build with missing variables can receive the hardcoded production URL/key/project ID at build time. Any later app operation from that build may therefore reach production according to the production project's normal authorization/RLS rules.

## Target state

- Non-production builds cannot resolve production target implicitly.
- Missing configuration aborts build/startup before application data access.
- Isolated CI writes remain disposable and local.

## Migration/backfill

None.

## Data cleanup

None authorized. This change does not inspect production history for possible prior accidental preview/test writes.