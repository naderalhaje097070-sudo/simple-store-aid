# FIN-COURIER-001 — Courier / customer / custody sale contract

NAADF-CMF change-gate documentation for correcting the courier (delegate) sale flow and making advanced sale the primary path.

**Current governance status (2026-07-27): Gates 0–3 are formally APPROVED by the product owner and their documentation contract was merged through PR #24. Gate 4 is next. No PR-A, PR-B, or PR-C implementation is authorized until Gate 4 evidence is authored, independently reviewed, and explicitly approved.**

Approval evidence:
- synchronized PR #24 head: `a652de164e3efeae707038f1769aee12a9e2474a`;
- Quality: PASS on that exact head;
- Ephemeral Financial Rules: PASS on that exact head;
- Isolated Auth UI Smoke: PASS on that exact head;
- PR #24 merge commit: `cc1f9e5beb8f5fa73ef44125925fe54a6d1a8858`.

Baseline evidence for the Gate 0–3 analysis remains `main = 906df4b`. All current-behavior claims cite file:line read from the working tree at that historical evidence head. That evidence SHA is intentionally preserved and must not be confused with the current `main` head.

Some individual Gate 0–3 artifacts retain pre-merge authoring labels such as “Draft” or “pending formal Gate approval.” Those labels describe the state in which the artifact was authored and reviewed; they are superseded for **current governance status** by the explicit approval record above, DEC-014, `PROJECT_STATE.md`, and `TASKS.md`. Gate 4 and Gate 5 artifacts remain unapproved until their own approval boundaries are satisfied.

## Documents

| Gate | Document | Purpose / current role |
|---|---|---|
| 0 | [CHANGE_INTAKE.md](CHANGE_INTAKE.md) | Approved intake: goal, scope, risk, baseline |
| 1 | [CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) | Approved evidenced baseline (RPC, constraints, health, UI, tests) |
| 1 | [EXPECTED_BEHAVIOR.md](EXPECTED_BEHAVIOR.md) | Approved target contract |
| 2 | [IMPACT_ANALYSIS.md](IMPACT_ANALYSIS.md) | Approved Gate-2 summary linking the detailed artifacts below |
| 2 | [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md) | Approved callers/consumers map |
| 2 | [DATA_IMPACT.md](DATA_IMPACT.md) | Approved data-shape and historical-data impact |
| 2 | [SECURITY_IMPACT.md](SECURITY_IMPACT.md) | Approved authz, tenant-isolation, RLS, and grants impact |
| 2 | [API_COMPATIBILITY.md](API_COMPATIBILITY.md) | Approved v2 RPC + adapter client contract |
| 2 | [MIGRATION_IMPACT.md](MIGRATION_IMPACT.md) | Approved forward-only migration strategy |
| 2 | [TEST_IMPACT.md](TEST_IMPACT.md) | Approved test-impact analysis |
| 2 | [ROLLBACK_IMPACT.md](ROLLBACK_IMPACT.md) | Approved reversal/data-verification impact |
| 3 | [COURIER_STATE_CONTRACT.md](COURIER_STATE_CONTRACT.md) | Approved state machine, constraint replacement, atomic transition contract |
| 3 | [CUSTOMER_REQUIREMENT_MATRIX.md](CUSTOMER_REQUIREMENT_MATRIX.md) | Approved customer-required matrix |
| 3 | [BACKWARD_COMPATIBILITY.md](BACKWARD_COMPATIBILITY.md) | Approved safe-flow compatibility contract |
| 3 | [ROLLBACK_PLAN.md](ROLLBACK_PLAN.md) | Approved forward-only rollback strategy |
| 4 | [TEST_PLAN.md](TEST_PLAN.md) | Mandatory safety net to author/review next; not yet Gate-4 approved |
| 5 | [PR_DECOMPOSITION.md](PR_DECOMPOSITION.md) | Proposed implementation split after Gate 4 approval |

## Approved Gate-3 decisions

- **5A** `create_sale_with_items_v2` with explicit final `p_courier_state public.courier_state` and no DEFAULT; `returned` rejected at creation; the six-parameter RPC is retained as an adapter.
- **5B** Replacement CHECK is added `NOT VALID`; validation is a separate preflight-gated operation because historical rows are not proven clean.
- **5C** `update_courier_outcome_v2` is the named canonical transition RPC with the approved transition matrix and monotonic custody; the old `update_courier_order_state` is retained only as a compatibility adapter delegating to v2 safety rules.

These decisions define the approved target contract. They do not themselves constitute implementation.

## Approved core decision

> A customer is mandatory **only when the operation creates customer debt** — not because a courier is involved. Pending courier orders appear immediately but are not financial custody; money becomes custody only when recorded as collected by the courier; delivered is not settled; “not delivered / returned” creates no debt and restores stock.

## Constraints honored by this change

- Forward-only migrations only; applied migrations immutable; no Lovable history rewrite.
- No performance, employee-accounts, environment, CI, idempotency, billing, or refactor work bundled into FIN-COURIER-001.
- Financial writes stay in approved server-side/RPC transaction boundaries; screens reuse `src/domain/finance/` for read-model financial definitions.
- Passing tests do not authorize merge; each gate and implementation PR keeps an explicit human review/merge boundary.

## Current sequencing boundary

AUDIT-001 / PR #23 is merged. FIN-COURIER-001 Gates 0–3 / PR #24 are approved and merged.

A documentation-only baseline synchronization now records the actual repository state. After that synchronization PR is explicitly reviewed and merged, verify the resulting `main` SHA and cut Gate 4 from that exact head.

Gate 4 must author and review the mandatory safety-net tests in `TEST_PLAN.md` **before** production financial implementation. The intended later implementation order remains:

**PR-A** (schema constraints + `create_sale_with_items_v2` + atomic `update_courier_outcome_v2` + SQL tests) →
**PR-B** (outcome-aware platform health/reporting) →
**PR-C** (advanced-sale default + courier UI/wording/status).

Settlement payment-method redesign remains a separate governed change, **FIN-SETTLEMENT-METHOD-001**. Financial write idempotency remains a separate P0 governed change, **FIN-IDEM-001**.