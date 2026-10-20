# SEC-CI-001 — PR Decomposition

## PR-1 — Gates 0–3 documentation

Scope:
- baseline/current/expected behavior;
- impact analysis;
- security/data/test/rollback impact;
- change design and delivery boundaries.

No workflow implementation.

## PR-2 — Gate 4 safety net

Scope:
- static CI-policy tests only;
- prove floating Supabase CLI versions are rejected;
- prove raw PR-log publication patterns are rejected;
- prove unnecessary write permissions are rejected where no longer needed;
- prove isolation sentinel requirements;
- preserve existing application/financial tests unchanged.

Expected result before implementation: targeted policy tests RED for known current workflow defects while existing app tests remain unchanged.

## PR-3 — Focused CI hardening implementation

Scope:
- exact Supabase CLI pin;
- concise/redacted reporting or removal of PR-log comments;
- least-privilege workflow token permissions;
- isolation precondition enforcement;
- no product code.

Required: Gate-4 policy tests GREEN and full exact-head workflow execution.

## PR-4 — Independent review / operational closure

Prefer no code unless review finds a defect. Verify:
- no secret leakage;
- deterministic versions;
- required checks execute;
- workflow names/merge-path compatibility;
- runner/account failure classification;
- rollback readiness.

## External administrative task

In parallel, repository owner reviews GitHub Actions billing/usage/budget and repository Actions settings. This is not represented as a code PR because repository YAML cannot resolve an account-level usage restriction.

## Merge boundary

Each PR requires explicit human review. No automatic merge or deployment.