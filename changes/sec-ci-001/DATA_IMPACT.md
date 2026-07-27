# SEC-CI-001 — Data Impact

## Production data

None. SEC-CI neither reads nor writes production business data and requires no production database access.

## Test data

- Financial and auth workflows create disposable local Supabase state.
- Test tenants/users/orders must remain isolated to the local CI stack.
- Run-specific credentials are ephemeral and must not be copied into PR comments or committed artifacts.

## Artifacts and logs

CI logs/artifacts are data surfaces for this change.

Required handling:
- no passwords, tokens, secret/service keys, DB connection strings, or unnecessary PII;
- avoid environment dumps;
- store detailed diagnostics only where access follows repository permissions;
- PR comments contain summarized evidence only.

## Migration/backfill

None.

## Retention

No new retention requirement. Existing GitHub artifact/log retention applies; this change should minimize stored sensitive output rather than rely on retention deletion as a security control.