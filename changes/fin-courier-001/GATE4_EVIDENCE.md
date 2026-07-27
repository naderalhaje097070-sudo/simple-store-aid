# FIN-COURIER-001 — Gate 4 Safety-Net Evidence

Status: **IN PROGRESS — test-only branch. No production implementation is authorized by this file.**

## Frozen baseline

Gate 4 branch base:

`main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

This is the verified `main` merge commit produced by baseline-synchronization PR #26 after the PR #26 head passed Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke.

## Gate 4 objective

Before implementation, prove both:

1. the existing approved financial baseline remains green;
2. the new FIN-COURIER target contract is red on the pre-implementation baseline for expected contract gaps, not because of a broken harness.

A green expected-red probe therefore means the probe correctly detected missing target behavior while the old baseline stayed healthy. It does **not** mean FIN-COURIER is implemented.

## Existing baseline — unchanged

- `tests/financial-rules/rules.sql` — T1–T15. Must remain green and is not weakened.
- existing Quality workflow.
- existing Ephemeral Financial Rules workflow.
- existing Isolated Auth UI Smoke workflow.

## New executable Gate 4 slice

### PR-A backend contract

Artifacts:

- `tests/financial-rules/fin-courier-gate4-pr-a.sql`
- `tests/financial-rules/run-fin-courier-gate4.sh`

Authored coverage currently includes:

- exact `create_sale_with_items_v2` contract presence;
- exact `update_courier_outcome_v2` contract presence;
- replacement `orders_customer_required_when_debt` CHECK presence and initial `NOT VALID` state;
- removal of the two blanket customer constraints;
- preservation of courier-id and collected<=total constraints;
- B1 pending courier without customer;
- B2 delivered-full courier without customer;
- B3 partial courier debt without customer rejection;
- B4 delivered-none debt without customer rejection;
- B7 missing courier-id rejection;
- B9 settlement of customer-less delivered-full custody;
- D-T1 pending→delivered-full;
- D-M11 backward/custody-reducing transition rejection;
- approved historical-data preflight query.

The runner first executes unchanged T1–T15 and requires them to pass. It then executes the new target probe. In Gate-4 baseline mode, the target must fail with the explicit `GATE4_EXPECTED_RED` sentinel. In later PR-A verification mode, the same test can be run with `GATE4_EXPECT=green` and must pass without changing its assertions.

### Mobile + desktop UI contract

Artifact:

- `tests/e2e/fin-courier-gate4-ui.py`

Authored coverage currently includes:

- I1 / J1: primary `فاتورة جديدة` opens advanced sale rather than quick sale;
- I2 / J3: courier mode exposes operational outcomes rather than the generic payment-state trio;
- desktop 1440×900 and mobile 390×844;
- no invoice is saved by this probe.

### Isolated execution

Artifact:

- `.github/workflows/fin-courier-gate4-probe.yml`

The dedicated Gate-4 workflow is deliberately separate from the existing required checks. It starts fresh isolated Supabase instances, seeds disposable Gate-4 data, proves unchanged T1–T15 are green, proves the new backend target is red for the expected contract gap, builds the application against isolated Supabase, proves the UI target is red for the expected flow gap, uploads evidence, and never accesses production.

## Coverage still required before Gate 4 approval

The full approved `TEST_PLAN.md` is broader than this first executable slice. Gate 4 remains open until review closes or explicitly locates executable coverage for at least:

- C-CK2..C-CK8 direct constraint-shape cases;
- C-PF1/C-PF2 seeded historical violation detection and deferred `VALIDATE` proof;
- D-T2..D-T8, including same-tenant atomic customer attachment, nonexistent/cross-tenant rejection, and rollback atomicity;
- the full D-M transition matrix and same-state retry/increase cases;
- D-R1..D-R8 returned-order behavior, stock exactly once, and audit evidence;
- D-M14/D-M15 and E1/E2 concurrency;
- E3 duplicate-create non-idempotent baseline and E4 double-settlement rejection;
- F1/F2/F3 backward compatibility;
- G1..G8 platform health/reporting source-of-truth tests for PR-B;
- H1..H3 rollback;
- I3/I4/J2 wording, success-screen, and operational-status behavior.

None of these are waived by the initial probe.

## Merge / implementation boundary

- This Gate-4 branch must not contain production financial logic, migrations, RPC changes, RLS changes, or FIN-COURIER UI implementation.
- PR-A / PR-B / PR-C remain blocked while Gate 4 is in progress.
- Expected-red evidence does not authorize merge.
- After the complete Gate-4 safety net is independently reviewed and explicitly approved, implementation should preserve the test-first commits and proceed in the approved PR-A → PR-B → PR-C order.
