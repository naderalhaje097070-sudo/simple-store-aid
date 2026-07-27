# FIN-COURIER-001 — Courier / customer / custody sale contract

NAADF-CMF change-gate documentation for correcting the courier (delegate) sale
flow and making advanced sale the primary path. **Documentation only — Gates 0–3
are NOT approved; no implementation is authorized until they are reviewed and
approved by a human, and until the baseline condition below is met.**

Baseline evidence: `main = 906df4b`. All current-behavior claims cite file:line
read from the working tree at that head. This revision incorporates independent-
review findings (effective CHECK constraints, the state-transition hole,
outcome-aware reporting, and the RPC-compatibility design).

## Documents

| Gate | Document | Purpose |
|---|---|---|
| 0 | [CHANGE_INTAKE.md](CHANGE_INTAKE.md) | Goal, scope, risk, blocking info, baseline |
| 1 | [CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) | Evidenced baseline (RPC, constraints, health, UI, tests) |
| 1 | [EXPECTED_BEHAVIOR.md](EXPECTED_BEHAVIOR.md) | Proposed target (pending Gate approval) |
| 2 | [IMPACT_ANALYSIS.md](IMPACT_ANALYSIS.md) | Gate-2 **summary**, links to the artifacts below |
| 2 | [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md) | Callers/consumers of every affected contract |
| 2 | [DATA_IMPACT.md](DATA_IMPACT.md) | Data shapes, historical rows, integrity |
| 2 | [SECURITY_IMPACT.md](SECURITY_IMPACT.md) | Authz, tenant isolation, RLS, grants |
| 2 | [API_COMPATIBILITY.md](API_COMPATIBILITY.md) | v2 RPC + adapter, client contract |
| 2 | [MIGRATION_IMPACT.md](MIGRATION_IMPACT.md) | Forward-only migration steps |
| 2 | [TEST_IMPACT.md](TEST_IMPACT.md) | Suites changed, corrections captured |
| 2 | [ROLLBACK_IMPACT.md](ROLLBACK_IMPACT.md) | Reversal per layer + data verification |
| 3 | [COURIER_STATE_CONTRACT.md](COURIER_STATE_CONTRACT.md) | State machine, constraint replacement, atomic transition |
| 3 | [CUSTOMER_REQUIREMENT_MATRIX.md](CUSTOMER_REQUIREMENT_MATRIX.md) | When a customer is mandatory |
| 3 | [BACKWARD_COMPATIBILITY.md](BACKWARD_COMPATIBILITY.md) | Signature, constraint, data, enum compat |
| 3 | [ROLLBACK_PLAN.md](ROLLBACK_PLAN.md) | Forward-only rollback strategy |
| 4 | [TEST_PLAN.md](TEST_PLAN.md) | Regression, new-behavior, constraints, transition, health, concurrency, mobile, desktop, rollback |
| 5 | [PR_DECOMPOSITION.md](PR_DECOMPOSITION.md) | Three-PR split (schema/RPC → reporting → UI) |

## Gate-3 decisions recorded in these docs (not yet gate-approved)

- **5A** `create_sale_with_items_v2` with explicit final
  `p_courier_state public.courier_state` (no DEFAULT); `returned` rejected at
  creation; six-param RPC kept as adapter.
- **5B** Replacement CHECK added `NOT VALID`; validation is a separate,
  preflight-gated step (historical rows are not proven clean).
- **5C** Named canonical `update_courier_outcome_v2` (transition matrix +
  monotonic custody); old `update_courier_order_state` kept only as adapter.

These are proposed resolutions pending formal Gate approval; nothing here approves
a gate.

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

Human review and explicit approval of Gates 0–3. On approval **and after
AUDIT-001 / PR #23 is merged**, implement in order per PR_DECOMPOSITION:
**PR-A** (schema constraints + v2 sale RPC + atomic transition + SQL tests) →
**PR-B** (outcome-aware platform health/reporting) → **PR-C** (advanced-sale
default + courier UI). Settlement payment-method redesign is a separate governed
change, **FIN-SETTLEMENT-METHOD-001**.
