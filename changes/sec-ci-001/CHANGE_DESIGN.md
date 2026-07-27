# SEC-CI-001 — Change Design

## Root cause

There are two proven repository-level CI defects and one unresolved external execution blocker.

### Proven repository-level defects

1. Release-relevant financial/auth workflows resolve Supabase CLI from a floating `latest` version, so identical commits can execute against different CLI/runtime behavior.
2. Ephemeral Financial Rules copies raw startup/test-log tails into PR comments and therefore requires broader write permissions than the core test job needs.

### Unresolved external blocker

Recent Gate-4 exact-head jobs are created by GitHub but terminate before any step (`steps = None`) and have no downloadable job log. Repository evidence does not prove whether this is caused by Actions quota/budget, repository/account Actions policy, or hosted-runner scheduling. This change must classify that condition but must not claim to fix it through YAML without evidence.

## Smallest correct repository change

1. Pin Supabase CLI to one exact officially verified version in release-blocking workflows.
2. Replace raw PR log comments with no comment or a concise summary that contains no raw environment/log data.
3. Remove workflow-token write permissions that become unnecessary.
4. Add explicit isolated-CI preconditions before sensitive test writes.
5. Add policy tests that guard these contracts.
6. Preserve workflow/check names and existing test commands.

## Affected files — proposed

- `.github/workflows/ephemeral-financial-rules.yml`
- `.github/workflows/isolated-auth-smoke.yml`
- `.github/workflows/quality.yml` only if needed for a shared policy/evidence contract; no behavior change otherwise.
- FIN-COURIER Gate-4 workflow only in its own branch/PR or after it is legitimately integrated; SEC-CI must not silently rewrite PR #27 from this branch.
- New CI policy tests/scripts under `tests/ci/` or equivalent focused location.
- SEC-CI documentation.

## Contracts

### Tool contract

Material tools are exact-version pinned. A version upgrade is a deliberate reviewed change.

### Reporting contract

No raw environment dumps or raw infrastructure/test-log tails in PR comments. Status remains available through GitHub checks; detailed diagnostic logs remain inside protected Actions logs/artifacts.

### Isolation contract

Financial/auth writes run only after the workflow proves the approved isolated-CI sentinel and local target configuration.

### Failure-state contract

- reached executable step + failing command/assertion → test/build/migration failure;
- job created but no steps/logs → `EXECUTION_INFRA_BLOCKED` and not valid product evidence.

## Migration / backfill

None.

## Compatibility

Keep workflow names and core test commands stable to avoid breaking human-configured required-check settings.

## Rollout

1. Gate 4 policy tests first.
2. Focused workflow implementation.
3. Exact-head execution on the SEC-CI PR.
4. Verify no secret/raw-log leakage.
5. Independent review.
6. Human approval and merge.
7. Re-run FIN-COURIER Gate 4 on its then-current exact head after the external runner/account blocker is resolved.

## Administrative unblock procedure

The repository owner must inspect GitHub billing/usage/budget and repository Actions settings because the connected API cannot read them. If an account/repository restriction is found, resolve it without changing application tests; then re-run the unchanged exact head.

## Acceptance criteria

- deterministic material tools;
- concise secret-safe reporting;
- least-privilege permissions;
- explicit isolation preconditions;
- static policy tests protecting the above;
- exact-head Quality, Financial Rules, and Auth UI execution reaches steps and passes;
- independent review;
- explicit human merge only.