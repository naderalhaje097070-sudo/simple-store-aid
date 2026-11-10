# FIN-IDEM-001 — Financial write idempotency and retry safety

Status: **Gates 0–3 proposed for review. No production financial implementation is authorized by this documentation.**

Issue: #31

Baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

## Goal

Prevent duplicate financial effects when a successful request is retried after a lost/late response or when duplicate requests arrive concurrently.

## Proven baseline

Current sale creation has no request-level idempotency key. FIN-COURIER Gate-4 E3 intentionally freezes the current non-idempotent behavior: the same logical sale request executed twice creates two independent orders and decrements stock twice. This is not fixed inside FIN-COURIER.

## Target contract

For a tenant-scoped financial operation:

- same operation + same idempotency key + same canonical request hash → return the original committed result;
- same operation + same key + different request hash → deterministic conflict;
- concurrent duplicate calls → one financial effect and one canonical result;
- failure before commit → no committed success record that poisons future retry;
- idempotency is enforced server-side in the same transactional boundary as the financial write.

## Initial implementation target

The canonical `create_sale_with_items_v2` produced by FIN-COURIER PR-A. The legacy adapter should delegate rather than own a second idempotency implementation.

## Sequencing

Design and safety net can be approved now. Production implementation waits for FIN-COURIER PR-A so idempotency wraps the canonical v2 sale write instead of duplicating logic on the current legacy RPC.