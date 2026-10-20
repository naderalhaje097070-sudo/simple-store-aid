# SEC-ENV-001 — Impact Analysis

## UI

No intended visual behavior change. Preview/local builds may fail earlier with an explicit configuration error instead of loading against production.

## API / RPC

No application API/RPC contract changes. The target Supabase endpoint chosen before client creation changes from implicit fallback to explicit environment intent.

## Database / data

No schema or migration. Risk reduction is preventing non-production clients/tests from reading or writing production data accidentally.

## Authentication / authorization

No role/RLS change. Auth requests must use the same approved environment target as all other Supabase traffic.

## Tenant isolation

No policy change, but accidental production targeting could bypass test-environment expectations; preventing that is part of the security boundary.

## Business / financial rules

No rule changes. Financial writes in CI remain on disposable local Supabase only.

## External integrations

Affected integration surfaces:
- Vite/Lovable build environment;
- generated Supabase client;
- GitHub Actions isolated environments;
- deployment environment variables.

## Performance

Negligible runtime impact.

## Tests / CI

High impact. Existing fallback unit test must be replaced by fail-closed mode-aware tests. Isolated workflow environment proof becomes mandatory.

## Deployment / rollback

Production deployment contract must be explicitly documented and verified before removing fallback. Rollback is a focused resolver/config revert only if the new contract blocks valid production deployment; never re-enable unsafe preview-to-production fallback as an unreviewed workaround.

## Backward compatibility

Intentional breaking change for undocumented/misconfigured non-production builds that relied on absent variables. Valid explicit CI/staging configurations remain supported.