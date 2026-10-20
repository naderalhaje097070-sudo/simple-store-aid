# SEC-CI-001 — Security Impact

## Trust boundary

GitHub Actions is an automated execution environment with access to repository contents, workflow token permissions, locally generated test credentials, logs, and artifacts. It must be treated as a sensitive delivery boundary.

## Current security findings

1. `Ephemeral Financial Rules` has `issues: write` and `pull-requests: write` solely to publish a PR comment.
2. That PR comment currently includes raw tails of Supabase startup and financial-rule logs.
3. Financial/Auth workflows resolve Supabase CLI through `version: latest`, reducing reproducibility and supply-chain determinism.
4. Local Supabase environment values and disposable credentials are valid only inside the job; they must not be copied to durable/public-facing surfaces.

## Proposed controls

- Least-privilege workflow token permissions.
- Exact pin for material CLI/runtime versions.
- No raw environment or infrastructure-log output in PR comments.
- Explicit isolation sentinel before sensitive test writes.
- Fail closed when isolated environment requirements are missing.
- Separate execution-infrastructure state from assertion state in evidence.

## Threat scenarios

- Credential/token leakage through PR comments or artifacts.
- Unreviewed CLI behavior change causing migrations/tests to behave differently on the same commit.
- A pre-step runner failure being mistaken for product failure or expected RED, weakening release governance.
- A workflow unexpectedly targeting non-isolated infrastructure because environment validation is absent.

## Residual risk

GitHub account billing/budget, hosted-runner availability, and repository Actions policy are external administrative controls. Repository code can detect/classify but cannot guarantee their availability.

## Review requirement

Independent review must inspect token permissions, output surfaces, pinning, isolation proof, and failure classification before merge.