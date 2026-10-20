# Historical esbuild proof lifecycle — A8 CI correction

The automatic push run39396201730 failed on c789ce2, on both Linux and Windows at tests/g0-esbuild/evidence.py:48. Frozen installation and the dependency graph assertions had passed; the original whole-package-manifest assertion rejected the already reviewed build-wrapper and format-generated script changes. Package dependencies, overrides, resolutions and the lock were unchanged from the original accepted esbuild candidate73e133b.

The workflow was an esbuild-only change proof against1b7a1a0, not a general acceptance gate for later integrated application changes. Keep all its graph, package, security, native Windows, compatibility and audit assertions byte-identical. Make it manual and pin checkout to its original tested73e133b source. Its name explicitly identifies it as historical. No arbitrary source input or current-head success is implied. Current source acceptance remains the integrated G0/G1 and normal PR workflows.

Scope/risk: bounded CI lifecycle correction; workflow trigger/checkout/name and its exact manifest entry only. No app/domain/SQL/package/lock/provider/policy change. This does not remove current security unit tests or current full audit. The original automatic failure remains a failure; the documented historical Windows/Linux proof remains attached to its actual source.

Verification: parsed YAML has only workflow_dispatch; exactly one checkout pins73e133b; the same288 protected path set and all41 original migration identities remain. Existing historical proof assertions and runtime files are unchanged. Affected native acceptance is collected on the new committed candidate; do not promote earlier421 results as executions on that candidate. Independent reviewer checks the cause, trigger scope, preserved assertions and source identities before A8 handoff.

Rollback is additive: restore only the workflow and exact source-manifest entry together to c789ce2, preserving the failure/history. That restores the demonstrated stale automatic push failure; it is not a production rollback. Owner merge/deploy/closure boundaries and B/C remain unchanged.

