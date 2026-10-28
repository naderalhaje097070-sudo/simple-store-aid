# FIN-IDEM-001 — Gate 4 Evidence

Status: **PARTIALLY PREPARED / DEPENDENCY_BLOCKED / EXECUTION_INFRA_BLOCKED**

Gates 0–3 were approved by the project owner on 2026-07-28.

## Evidence prepared now

The rollback-only SQL probe executes the same current direct-sale request twice and requires proof of the known unsafe retry baseline: two order results, two payment effects, and two stock decrements. The intended sentinel is `FIN_IDEM_G4_E1_EXPECTED_RED`.

The target-readiness probe does not treat a missing canonical sale API as an idempotency failure. It emits `FIN_IDEM_G4_D1_DEPENDENCY_BLOCKED` until FIN-COURIER PR-A provides `create_sale_with_items_v2`. Once that dependency exists, absence of an idempotency-key client contract becomes `FIN_IDEM_G4_E2_EXPECTED_RED`.

## Full Gate after FIN-COURIER PR-A

The database safety net must cover exact-request replay, conflicting reuse of a key, concurrent duplicates, transaction rollback/retry, single financial effect, tenant authorization, and original-result fidelity.

## Blockers

- FIN-COURIER PR-A cannot start before FIN-COURIER Gate 4 exact-head evidence and human approval.
- OPS-GHA-001 #36 still prevents GitHub-hosted jobs from reaching workflow steps.

Dependency-blocked or pre-step runner failure is not Gate-4 PASS.

No idempotency implementation, migration, merge, production access or deployment is included here.
