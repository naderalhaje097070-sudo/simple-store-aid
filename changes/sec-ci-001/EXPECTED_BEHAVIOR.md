# SEC-CI-001 — Expected Behavior

## Deterministic tooling

- Release-blocking workflows use explicit tested versions for material runtimes/CLIs.
- Bun remains explicitly pinned.
- Supabase CLI must be pinned to one approved exact version; `latest` is not accepted for authoritative release evidence.
- Any future version change is an explicit dependency/CI change with verification.

## Secret-safe reporting

- PR comments, if retained, report only workflow name, exact commit SHA, high-level result, isolation statement, and named failing scenario/check.
- No raw Supabase startup output, environment dumps, DB URLs, publishable/service keys, passwords, tokens, or full unredacted application logs are copied into PR comments.
- Detailed diagnostics stay in access-controlled GitHub Actions job logs/artifacts and must still avoid secrets.

## Isolation

- Financial and authenticated UI workflows start an isolated local Supabase instance.
- Before any financial/auth write, the workflow proves it is in the approved isolated CI mode.
- Missing required isolated values fails closed.
- No production Supabase secret is required by these workflows.

## Failure classification

- Test assertion/build/migration failures are accepted only after the job reached executable steps.
- A job with no steps/logs is classified as `EXECUTION_INFRA_BLOCKED`, not application failure and not expected RED.
- Gate/release evidence must identify the exact commit and whether execution reached the test/assertion layer.

## Required-check contract

On a release-relevant exact head:

1. Quality executes and reports step-level result.
2. Ephemeral Financial Rules executes full isolated migration/T1–T15 evidence.
3. Isolated Auth UI Smoke executes against isolated Supabase.
4. Change-specific required workflows execute their approved safety-net contract.
5. No automatic merge or deployment follows passing checks.

## Acceptance boundary

SEC-CI is not complete merely because workflow YAML parses. It requires an exact-head run that reaches steps and passes the required checks, followed by independent review and explicit human approval.