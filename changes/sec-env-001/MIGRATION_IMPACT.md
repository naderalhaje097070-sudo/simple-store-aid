# SEC-ENV-001 — Migration Impact

## Database migration

None.

## Configuration migration

The change migrates deployment/build configuration from implicit production fallback to explicit environment intent.

Before implementation:
- identify the supported production deployment signal;
- identify required variables for Lovable production;
- identify preview/staging/local/CI signals and ensure they cannot be mistaken for production.

## Rollout

1. Add mode-aware safety tests.
2. Introduce explicit resolver contract while preserving current variable aliases.
3. Verify local/CI/preview fail closed without explicit non-production configuration.
4. Verify intentional production build succeeds with explicit production signal/configuration.
5. Independently review before human merge.

## Backfill

None.

## Deployment settings

Any required GitHub/Lovable environment-variable configuration is a human-controlled deployment action and must be documented separately from repository code.