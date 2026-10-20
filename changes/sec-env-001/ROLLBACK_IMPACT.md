# SEC-ENV-001 — Rollback Impact

## Rollback scope

Build/runtime environment resolution only. No schema/data rollback.

## Rollback plan

If the new resolver blocks a valid explicitly configured production deployment:

1. Revert the focused resolver/config commit only.
2. Preserve all new safety tests and evidence where possible.
3. Diagnose the production-deployment signal/configuration mismatch.
4. Re-design before another implementation attempt.

## Prohibited rollback shortcut

Do not restore unconditional production fallback for missing variables as a permanent fix. If a temporary emergency workaround is ever required, it needs explicit human approval and a time-bounded compensating control.

## Data recovery

None required by this change. No production data mutation is part of implementation or verification.