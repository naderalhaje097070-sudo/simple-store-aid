# SEC-CI-001 — Change Design

## Root cause

There are two proven repository-level CI defects and one unresolved external execution blocker.

### Proven repository-level defects

1. Release-relevant financial/auth workflows resolve Supabase CLI from a floating `latest` version, so identical commits can execute against different CLI/runtime behavior.
2. Ephemeral Financial Rules copies raw startup/test-log tails into PR comments and therefore requires broader write permissions than the core test job needs.

### Unresolved external blocker

Recent exact-head jobs are created by GitHub but terminate before any step (`steps = None`) and have no downloadable job log. Independent documentation-only control heads reproduce the same condition. Repository evidence does not prove the exact account-level cause; this change must classify that condition but must not claim to fix it through YAML without evidence.

## Smallest correct repository change

1. Move release-blocking Supabase setup to the maintained `supabase/setup-cli@v2` action line.
2. Pin Supabase CLI to one exact stable version that is first proven against this repository's migrations/tests.
3. Replace raw PR log comments with no comment or a concise summary that contains no raw environment/log data.
4. Remove workflow-token write permissions that become unnecessary.
5. Add explicit isolated-CI preconditions before sensitive test writes.
6. Add policy tests that guard these contracts.
7. Preserve workflow/check names and existing test commands.

## Supabase tool-selection decision

Official Supabase sources establish two design requirements:

- `supabase/setup-cli@v2` supports an explicit CLI `version` input;
- Supabase recommends pinning a specific CLI version when reproducibility matters because service-image dependencies can change behavior even within a CLI major line.

### Candidate pin for execution validation

At design time, the current verified stable candidate from the official Supabase CLI release source is:

- action line: `supabase/setup-cli@v2`
- CLI candidate: `2.101.0`

This is a **candidate, not yet the approved repository pin**. The final pin must be whichever exact stable version first passes the repository's isolated migrations, T1–T15, and auth smoke on a real runner after OPS-GHA-001 is resolved. Do not use `latest` as the validation target.

If `2.101.0` fails due to a genuine CLI/runtime incompatibility, choose another explicit stable version with recorded evidence; never fall back to a floating version.

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

## Gate 4 safety-net expectations

Before changing workflow implementation, static/policy tests must prove:

1. release-blocking workflows do not contain `version: latest` for Supabase CLI;
2. the setup action uses the approved maintained action line;
3. financial workflow PR reporting cannot publish raw log tails/environment dumps;
4. workflow permissions are read-only unless a narrowly documented write is required;
5. isolated target assertion executes before financial/auth writes;
6. workflow/check names remain unchanged.

Runtime validation then proves the selected exact CLI version on a real hosted runner.

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
- exact CLI pin validated on repository tests;
- concise secret-safe reporting;
- least-privilege permissions;
- explicit isolation preconditions;
- static policy tests protecting the above;
- exact-head Quality, Financial Rules, and Auth UI execution reaches steps and passes;
- independent review;
- explicit human merge only.