# FIN-IDEM-001 — API and Compatibility Impact

## Canonical RPC

The future canonical sale RPC must accept or be wrapped by an idempotency contract without duplicating the financial implementation.

Preferred direction:

- canonical v2 sale write owns the financial transaction;
- one idempotent entry point accepts `p_idempotency_key` in addition to the financially material request;
- compatibility adapters delegate to the canonical path according to an explicitly documented policy.

## Request compatibility

Adding a required idempotency key is a contract change for modern callers. The rollout must define whether:

1. a new RPC signature/version is introduced; or
2. the canonical v2 signature is extended before broad use.

Do not add an unsafe default that silently generates a new server key on each retry, because that would defeat request deduplication.

## Result compatibility

Replay returns the same stable logical result as the original committed request. Consumers should not need a separate “replay” response shape to continue normal navigation.

## Error contract

Add a deterministic conflict sentinel for same key/different canonical request, e.g. a governed `idempotency_conflict` error contract. Exact naming is finalized before implementation and added to client error mapping/tests.

## Legacy behavior

Existing callers without keys remain non-idempotent unless explicitly migrated or safely adapted. That limitation must remain visible until all pilot-critical write paths use the idempotent contract.