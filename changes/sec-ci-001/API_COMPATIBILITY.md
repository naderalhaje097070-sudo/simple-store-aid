# SEC-CI-001 — API and Compatibility Impact

## Application contracts

No application API, RPC, database function, schema, route, or UI contract changes.

## CI contract compatibility

The following identities should remain stable unless a human intentionally updates branch protection:

- Workflow name `Quality`.
- Workflow name `Ephemeral Financial Rules`.
- Workflow name `Isolated Auth UI Smoke`.
- Existing test commands invoked by those workflows.

## Intentional behavior changes

- Raw PR log comments may be removed or reduced to concise status summaries.
- Workflow token write permissions may be removed if no longer required.
- Supabase CLI resolution changes from floating `latest` to an exact approved version.
- Failure evidence gains an explicit infrastructure/execution classification.

## Consumer impact

- Reviewers still receive authoritative status through GitHub checks.
- Detailed logs remain available in GitHub Actions when jobs execute.
- Branch protection must not be silently broken by renaming required checks.

## Compatibility rule

Security/reproducibility hardening may reduce verbose output but must not reduce test coverage or change application business behavior.