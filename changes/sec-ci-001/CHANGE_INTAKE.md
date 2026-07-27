# SEC-CI-001 — Change Intake

## Change goal

Harden release-blocking GitHub Actions so CI evidence is deterministic, concise, secret-safe, isolated from production, and capable of distinguishing execution-infrastructure failures from assertion failures.

## Change type

Security / CI / delivery-pipeline change under NAADF-CMF.

## In scope

- Quality, Ephemeral Financial Rules, Isolated Auth UI Smoke, and the FIN-COURIER Gate-4 workflow contract.
- Material CLI/runtime version determinism.
- PR-comment/log redaction policy.
- Fail-closed isolated test-environment checks.
- Runner/account/infrastructure failure classification.
- Required-check exact-head evidence.

## Out of scope

- FIN-COURIER production implementation.
- Client/build environment resolution owned by SEC-ENV-001.
- Financial idempotency owned by FIN-IDEM-001.
- Product features, general refactors, deployment, production data, or production secrets.

## Urgency

P0 pilot blocker. Gate-4 approval is also currently blocked by pre-step GitHub Actions failures, making this the highest-value independent workstream that can proceed without violating FIN-COURIER sequencing.

## Risk level

High delivery/security significance; medium implementation complexity if kept to focused workflow policy changes.

## Owner

Nader — product and repository owner.

## Expected outcome

A focused, reviewable CI-hardening change that preserves isolated financial/auth tests, removes raw sensitive reporting, pins material tooling, and produces reliable exact-head execution evidence.

## Missing blocking information

The connector cannot read the account's GitHub Actions billing/minute budget or repository Actions settings. Current `steps = None` failures therefore cannot yet be attributed conclusively to quota/budget, repository policy, or hosted-runner scheduling.

## Explicit assumptions

- `main = 983b746e5c6639dcdc5e6557381ad5619abaa046` is the baseline for this change.
- PR #27 remains separate and unmerged.
- No automated agent merges or deploys.
- Production credentials remain outside automated work.
- Workflow hardening must not weaken existing test assertions.