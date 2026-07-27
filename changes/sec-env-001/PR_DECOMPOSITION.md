# SEC-ENV-001 — PR Decomposition

## PR-1 — Gates 0–3 documentation

Documentation-only baseline, impact, expected contract, design, rollback, and test strategy.

## PR-2 — Gate 4 safety net

Test-only:
- replace the current missing-env → production-fallback expectation with fail-closed target tests;
- add explicit production/non-production mode tests;
- add CI production-target rejection tests;
- no resolver implementation.

## PR-3 — Focused environment resolver implementation

- explicit mode-aware resolver;
- remove unconditional production fallback;
- preserve variable aliases/precedence;
- integrate verified production deployment signal;
- no business/schema/RPC change.

## PR-4 — Independent review and operational verification

Prefer no code unless review finds a defect. Verify:
- build and SSR consistency;
- preview/local/CI production rejection;
- intentional production build success;
- isolated auth/financial target proof;
- rollback readiness.

## External/human configuration task

Any deployment-provider variables or settings required to supply the explicit production signal/configuration are human-controlled and must be documented before merge.

## Merge boundary

No automatic merge/deploy. Each implementation stage follows explicit Gate approval.