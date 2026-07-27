# FIN-COURIER-001 — Gate 4 Safety-Net Evidence

Status: **IN PROGRESS — test/evidence only. No FIN-COURIER production implementation is authorized by this file or PR #27.**

## Frozen baseline

Gate 4 branch base:

`main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

This is the verified `main` merge commit produced by baseline-synchronization PR #26 after the exact PR #26 head passed Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke.

Gate 4 is developed in draft PR #27 from that frozen baseline. PR #27 is not an implementation PR and is not intended to be merged to `main` while the new target-contract probes are in expected-RED mode.

## Gate 4 objective

Before implementation, prove both:

1. the existing approved financial baseline remains GREEN;
2. every new FIN-COURIER contract has an executable test written before the corresponding implementation and is RED on the pre-implementation baseline for the expected reason rather than because of a broken harness.

A successful expected-RED probe means the harness reached the assertion and detected a known missing contract. It does **not** mean the feature is implemented.

## First verified expected-RED checkpoint

On PR #27 head:

`04618b2360e0b1ba6ac28ba31dc89e8d9ef69092`

GitHub run `30248157200` proved the first isolated checkpoint:

- existing T1–T15: GREEN;
- backend target: expected RED with the initial contract gaps — missing `create_sale_with_items_v2`, missing `update_courier_outcome_v2`, missing `orders_customer_required_when_debt`, and the two legacy blanket-customer constraints still present;
- mobile/desktop UI target: expected RED because the primary `فاتورة جديدة` CTA still opens quick sale (I1/J1);
- standard Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke also remained GREEN on that checkpoint.

An earlier attempt failed during fixture seeding before reaching assertions. That result was rejected as false RED; the isolated seed was corrected to the proven repository pattern (`ON CONFLICT` / profile upsert), and only assertion-reaching runs are accepted as Gate-4 evidence.

## Existing baseline — unchanged

The following protection is preserved and not weakened:

- `tests/financial-rules/rules.sql` — T1–T15;
- `tests/unit/invoice-selectors.test.ts` — canonical client debt/custody selector coverage;
- Quality workflow;
- Ephemeral Financial Rules workflow;
- Isolated Auth UI Smoke workflow.

## Authored Gate 4 safety net

### A/B/C — PR-A creation, schema, and historical-data contract

Artifacts:

- `tests/financial-rules/fin-courier-gate4-pr-a.sql`
- `tests/financial-rules/run-fin-courier-gate4.sh`
- `tests/financial-rules/fin-courier-gate4-create-aggregates.sql`
- `tests/financial-rules/fin-courier-gate4-constraints.sql`
- `tests/financial-rules/fin-courier-gate4-preflight.sql`

Coverage:

- exact seven-argument `create_sale_with_items_v2` contract;
- exact four-argument `update_courier_outcome_v2` contract;
- replacement `orders_customer_required_when_debt` CHECK exists and is initially `NOT VALID`;
- two legacy blanket-customer constraints are removed;
- courier-id and collected<=total constraints remain;
- B1..B9 creation/settlement behavior, including B5/B6 create-time debt states and B8 close-day aggregate (`debt=160`, `unsettled custody=140` for the fixed fixture);
- C-CK1..C-CK8 direct CHECK-shape matrix, independent of RPC validation;
- C-PF1 historical preflight detects a deliberately seeded violating legacy row;
- C-PF2 blind `VALIDATE` fails while that row exists and controlled validation succeeds only after the preflight returns zero.

### D — atomic transition and state machine

Artifacts:

- `tests/financial-rules/fin-courier-gate4-transitions.sql`
- `tests/financial-rules/fin-courier-gate4-atomicity.sql`

Coverage:

- D-T1..D-T7 transition/customer behavior;
- D-T8 forced AFTER UPDATE failure proves the entire v2 transition rolls back — state, custody, and customer remain unchanged;
- D-M1..D-M10 valid/invalid transition matrix;
- D-M11 custody reduction rejection;
- D-M12 same-state/same-value idempotent retry;
- D-M13 same-state higher custody accepted.

### D-R — returned-order baseline

Artifact:

- `tests/financial-rules/fin-courier-gate4-return-baseline.sql`

Coverage D-R1..D-R8:

- delivered-none customer debt can become returned after confirmed physical return;
- returned debt becomes zero;
- stock restores exactly once;
- repeated return is rejected and cannot restore stock twice;
- returned is terminal;
- settled order cannot be returned;
- debt collection on returned order is rejected;
- `financial_audit_log` contains before/after return evidence.

This is a true regression baseline and must be GREEN before PR-A and remain GREEN afterward.

### E — concurrency and retry baseline

Artifacts:

- `tests/financial-rules/fin-courier-gate4-concurrency.sh`
- `tests/financial-rules/fin-courier-gate4-retry-baseline.sql`

Coverage:

- E1 two concurrent sales for stock=1 → exactly one succeeds and the loser is `insufficient_stock`;
- D-M14 concurrent partial/full transition serializes to one valid final state with non-decreasing custody;
- D-M15/E2 concurrent delivered-full transition + settlement cannot lose/double custody or create duplicate settlement payment;
- E3 freezes the known non-idempotent sale-create baseline: duplicate logical calls create two orders; true request-key idempotency remains `FIN-IDEM-001`;
- E4 second settlement attempt is rejected and cannot create a duplicate payment.

Concurrency intentionally runs last in the consolidated backend harness because it spans multiple database sessions and can persist disposable rows once PR-A exists. All `close_day`/snapshot true-GREEN tests run before it so future implementation verification cannot be contaminated by concurrency fixtures.

### F — backward compatibility and five-state snapshot

Artifacts:

- `tests/financial-rules/fin-courier-gate4-compatibility.sql`
- `tests/financial-rules/fin-courier-gate4-readmodel-snapshot.sql`

Coverage:

- F1 legacy six-parameter create and v2 produce equivalent safe financial results for representative direct, pending-courier, and partial-courier flows;
- F1a safe legacy transition delegates successfully;
- F1b unsafe backward/custody-reducing legacy transition is intentionally rejected by v2 safety rules;
- F2 fixed five-state golden snapshot: customer debt=160 and unsettled custody=140, including `close_day`; the exact same test must remain GREEN after PR-A;
- F3 no customer-less `delivered_partial` / `delivered_none` rows exist.

### G — PR-B health and reporting

Artifact:

- `tests/financial-rules/fin-courier-gate4-reporting.sql`

Coverage G1..G8:

- valid customer-less pending/full courier orders do not trigger `courier_missing_refs` / `debt_without_customer`;
- a deliberately forced genuinely corrupt customer-less debt row is still detected;
- the corruption fixture explicitly re-adds the replacement CHECK as `NOT VALID` rather than relying on `pg_get_constraintdef()` to preserve validation state;
- detail RPCs use the corrected row sets;
- `get_platform_admin_overview.open_customer_debts` includes partial remainder + delivered-none total;
- `get_platform_tenants_health.open_debts` uses the same contract;
- `get_platform_day_close_health` remains `Matches` for the valid courier mix;
- admin and tenant debt totals equal the canonical per-order debt source of truth.

The reporting test is intentionally PR-A-dependent and is expected RED before the new valid row shapes/constraint exist.

### H — rollback contract

Artifacts:

- `tests/financial-rules/fin-courier-gate4-rollback-contract.sql`
- `tests/financial-rules/run-fin-courier-gate4-corrective-rollback.sh`

Coverage:

- H1 freezes the required rollback endpoint now: replacement CHECK absent, the two original CHECKs present as `NOT VALID`, v2 functions absent, legacy signatures present;
- H2 customer-less partial/none verification query must be zero;
- H3 legacy create path works;
- the current pre-change baseline is the golden rollback fingerprint;
- a generic corrective-rollback runner is already authored: once a real forward-only corrective migration exists, it applies that SQL on an isolated changed database, reruns T1–T15, then reruns the same rollback endpoint contract.

Gate 4 does **not** invent or claim execution of a corrective migration that does not yet exist. Actual execution becomes mandatory implementation/rollback evidence when that migration is authored.

### I/J — mobile and desktop UI

Artifacts:

- `tests/e2e/fin-courier-gate4-ui.py`
- `tests/e2e/fin-courier-gate4-ui-status.py`
- `tests/e2e/fin-courier-gate4-ui-success.py`

Coverage:

- I1/J1 primary `فاتورة جديدة` opens advanced sale; quick sale remains secondary;
- I2/J3 courier PaymentSheet exposes operational outcomes rather than the generic paid/partial/debt model;
- I3 `delivered_none` wording is `تم التسليم دون تحصيل`, the old `لم تُسلَّم (دين)` wording is forbidden, and not-delivered/returned is a separate path;
- J2 invoice list exposes the operational status set: `قيد التوصيل`, `عهدة كاملة`, `عهدة جزئية ودين`, `دين كامل`, `تمت التسوية`, `مرتجع`;
- I4 performs disposable isolated sales and requires type-aware success semantics: delivered-full identifies courier custody; pending identifies in-transit state and is not described as custody;
- desktop 1440×900 and mobile 390×844 are exercised;
- all writes are restricted to disposable isolated CI Supabase instances; no production environment is used.

## Consolidated Gate 4 execution

Gate-4 orchestration is intentionally consolidated into one workflow:

- `.github/workflows/fin-courier-gate4-probe.yml`

with:

- one isolated backend job;
- one isolated UI job.

Backend orchestration is centralized in:

- `tests/financial-rules/run-fin-courier-gate4-all.sh`

The backend runner executes all authored backend contracts on one isolated Supabase instance and classifies each explicitly as either:

- **expected RED** before its corresponding implementation; or
- **true GREEN** baseline that must already pass and remain passing.

The true-GREEN baselines are executed before the multi-session concurrency test to prevent later `close_day` snapshots from being contaminated by concurrency fixtures.

The UI job runs three independent probes so an I1 failure cannot hide I3/J2 or I4 evidence.

Earlier development used multiple per-slice workflows. That design was removed after it caused a GitHub Actions queue storm: `pull_request.paths` evaluates the cumulative PR diff, so every subsequent push retriggered all Gate-4 workflows. The test files remain independent, but orchestration is now single and deterministic.

Final intended exact-head workflow set is therefore:

1. Quality;
2. Ephemeral Financial Rules;
3. Isolated Auth UI Smoke;
4. FIN-COURIER Gate 4 Probe.

Expected-RED tests must fail internally with their named sentinel and then allow the consolidated workflow to succeed only when the reason is the approved missing contract. Any seed, build, SQL syntax, login, browser, or other harness failure is a Gate-4 failure and must not count as expected RED.

## Remaining execution boundary before Gate 4 approval

The safety-net assertions are authored across the approved TEST_PLAN. Before Gate 4 can be approved:

1. the four intended workflows above must be run and reviewed on one exact final PR #27 head;
2. standard Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke must be GREEN on that same head;
3. true-GREEN baselines — T1–T15, returned baseline, F2 snapshot, rollback endpoint — must actually pass rather than being converted to expected RED;
4. each expected-RED test must reach its named contract sentinel — no false RED from harness failures;
5. an independent review must inspect false-positive/false-negative risk, transaction isolation, tenant isolation, concurrency assumptions, and traceability to `TEST_PLAN.md`;
6. the future corrective rollback migration cannot be executed before it exists; when implementation supplies it, the already-authored corrective-rollback runner becomes mandatory evidence.

## Merge / implementation boundary

- PR #27 remains DRAFT and unmerged during Gate 4 evidence collection.
- PR #27 contains no FIN-COURIER production financial logic, no migration implementation, no RPC implementation, no RLS change, and no PR-C UI implementation.
- PR-A / PR-B / PR-C remain blocked until Gate 4 evidence is independently reviewed and explicitly approved.
- Expected-RED workflow success does not authorize merge or implementation by itself.
- After Gate 4 approval, PR-A should branch from the approved Gate-4 head — not from a stale earlier `main` — so the test commits remain chronologically before the implementation commits. Relevant probes then switch from expected-RED execution mode to GREEN verification without weakening or replacing their assertions.
- The approved implementation order remains PR-A → PR-B → PR-C, each with exact-head CI and a human merge boundary.
