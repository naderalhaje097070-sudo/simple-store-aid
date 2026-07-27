# FIN-COURIER-001 — Gate 4 Safety-Net Evidence

Status: **IN PROGRESS — test-only branch. No production implementation is authorized by this file.**

## Frozen baseline

Gate 4 branch base:

`main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

This is the verified `main` merge commit produced by baseline-synchronization PR #26 after the PR #26 head passed:

- Quality;
- Ephemeral Financial Rules;
- Isolated Auth UI Smoke.

## Gate 4 objective

Prove two things before implementation:

1. the existing approved financial baseline remains green;
2. the new FIN-COURIER target contract is red on the pre-implementation baseline for the expected business/contract gaps, not because of a broken harness.

A green expected-red probe therefore means: **the probe successfully detected the known missing target behavior while the old baseline stayed healthy.** It does not mean FIN-COURIER has been implemented.

## Safety-net artifacts on this branch

### Existing baseline — unchanged

- `tests/financial-rules/rules.sql` — T1–T15. Must remain green and is not weakened.
- existing Quality workflow.
- existing Ephemeral Financial Rules workflow.
- existing Isolated Auth UI Smoke workflow.

### New PR-A backend contract probe

- `tests/financial-rules/fin-courier-gate4-pr-a.sql`
- `tests/financial-rules/run-fin-courier-gate4.sh`

Current authored coverage includes:

- exact `create_sale_with_items_v2` contract presence;
- exact `update_courier_outcome_v2` contract presence;
- replacement customer/debt CHECK presence and `NOT VALID` state;
- removal of the two blanket customer constraints;
- preservation of courier-id and collected<=total constraints;
- pending courier without customer;
- delivered-full courier without customer;
- partial/none courier debt without customer rejection;
- delivered-none / delivered-partial with customer;
- courier-id requirement;
- settlement of customer-less delivered-full custody;
- pending→delivered-full transition;
- atomic rejection of debt transition without customer;
- atomic same-tenant customer attachment;
- backward-transition rejection;
- monotonic custody / custody-reduction rejection;
- same-state/same-value retry;
- legacy transition adapter safety;
- approved historical-data preflight query.

The probe is deliberately structured so missing v2 functions are reported as approved contract gaps while later behavioral assertions automatically activate once the functions exist.

### New mobile + desktop UI contract probe

- `tests/e2e/fin-courier-gate4-ui.py`

Current authored coverage includes:

- I1 / J1: primary `فاتورة جديدة` opens advanced sale, not quick sale;
- I2 / J3: courier mode exposes operational courier outcomes rather than the generic payment-state trio;
- both desktop 1440×900 and mobile 390×844;
- no invoice is saved by this probe.

### Isolated expected-red execution

- `.github/workflows/fin-courier-gate4-probe.yml`

The dedicated workflow is separate from the existing required checks. It:

- starts fresh isolated Supabase instances;
- seeds disposable Gate-4 tenants/users only;
- reruns T1–T15 before the new backend target probe;
- requires T1–T15 to pass;
- requires the new backend target to fail with `GATE4_EXPECTED_RED` on this pre-implementation baseline;
- builds the application against isolated Supabase;
- runs the mobile/desktop UI target without writing a sale;
- requires the UI target to fail with `GATE4_UI_EXPECTED_RED` on this pre-implementation baseline;
- uploads evidence artifacts;
- never accesses production.

## Coverage still required before Gate 4 approval

The full approved `TEST_PLAN.md` is broader than the first executable slice above. Before Gate 4 can be approved, review must ensure executable coverage or an explicitly justified test location for the remaining clauses, especially:

- direct service-role CHECK shape cases C-CK2..C-CK8;
- historical preflight detection with a deliberately seeded violating legacy row and deferred `VALIDATE` proof;
- cross-tenant / nonexistent customer transition cases;
- full state-transition matrix D-M1..D-M10;
- delivered-none→returned D-R1..D-R8 including stock exactly once and audit evidence;
- concurrency D-M14/D-M15 and E1/E2;
- duplicate-create non-idempotent baseline E3 and double-settlement E4;
- complete backward compatibility F1/F2/F3;
- platform health/reporting G1..G8 (PR-B safety net);
- rollback H1..H3;
- courier custody wording/status and success-screen cases I3/I4/J2.

These items are **not waived** by the initial probe. Gate 4 remains open until the full safety-net review closes them.

## Merge / implementation boundary

- This Gate-4 branch must not contain production financial logic, migrations, RPC changes, RLS changes, or FIN-COURIER UI implementation.
- PR-A / PR-B / PR-C remain blocked while Gate 4 is in progress.
- Expected-red evidence does not authorize merge.
- After the complete Gate-4 safety net is independently reviewed and explicitly approved, implementation should preserve the test-first commits and proceed in the approved PR-A → PR-B → PR-C order.
