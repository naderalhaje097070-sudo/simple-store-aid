# SEC-CI-001 — Migration Impact

## Database migration

None.

## Workflow migration

SEC-CI changes are delivery-pipeline configuration changes. The transition must preserve required check names and test commands while changing only:

- exact tool versions;
- reporting/redaction behavior;
- least-privilege token permissions;
- explicit isolation/failure-classification checks.

## Rollout strategy

1. Add policy/safety tests first.
2. Apply focused workflow edits.
3. Execute all affected workflows on one exact PR head.
4. Compare results with the last known good pre-change executions where available.
5. Keep merge manual.

## Backfill

None.

## Branch protection

No automated branch-protection changes. If required checks are renamed for any reason, a human must explicitly update repository settings; the preferred design is to keep names stable.