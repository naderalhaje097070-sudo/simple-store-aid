# FIN-COURIER-001 — Courier / customer / custody sale contract

NAADF-CMF change-gate documentation for correcting the courier (delegate) sale
flow and making advanced sale the primary path. **Documentation only — no
implementation is authorized until Gates 0–3 are reviewed and approved by a
human.**

Baseline: `main = 906df4b`. All current-behavior claims cite file:line read from
the working tree at that head.

## Documents

| Gate | Document | Purpose |
|---|---|---|
| 0 | [CHANGE_INTAKE.md](CHANGE_INTAKE.md) | Goal, scope, risk, blocking info, assumptions |
| 1 | [CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) | Evidenced baseline (RPC, UI, tests) |
| 1 | [EXPECTED_BEHAVIOR.md](EXPECTED_BEHAVIOR.md) | Approved target contract |
| 2 | [IMPACT_ANALYSIS.md](IMPACT_ANALYSIS.md) | Impact per area + caller/consumer map |
| 3 | [COURIER_STATE_CONTRACT.md](COURIER_STATE_CONTRACT.md) | State machine + creation-time contract |
| 3 | [CUSTOMER_REQUIREMENT_MATRIX.md](CUSTOMER_REQUIREMENT_MATRIX.md) | When a customer is mandatory |
| 3 | [BACKWARD_COMPATIBILITY.md](BACKWARD_COMPATIBILITY.md) | Signature, data, enum, read-model compat |
| 3 | [ROLLBACK_PLAN.md](ROLLBACK_PLAN.md) | Forward-only rollback strategy |
| 4 | [TEST_PLAN.md](TEST_PLAN.md) | Regression, new-behavior, concurrency, mobile, desktop, backward-compat |
| 5 | [PR_DECOMPOSITION.md](PR_DECOMPOSITION.md) | Financial-first, UI-second PR split |

## Core decision (for approval)

> A customer is mandatory **only when the operation creates customer debt** — not
> because a courier is involved. Pending courier orders appear immediately but are
> not financial custody; money becomes custody only when recorded as collected by
> the courier; delivered is not settled; "not delivered / returned" creates no
> debt and restores stock.

## Constraints honored by this change

- Forward-only migrations only; applied migrations immutable; no Lovable history
  rewrite.
- No performance, employee-accounts, environment, CI, or refactor work bundled in.
- Financial writes stay in approved RPCs; screens reuse `src/domain/finance/`.

## Next step

Human review and explicit approval of Gates 0–3. On approval, implement PR-A
(financial contract + SQL tests) before PR-B (UI), per PR_DECOMPOSITION.
