# FIN-COURIER-001 — Gate 4 Safety-Net Evidence

Status: **IN PROGRESS — test/evidence only. No FIN-COURIER production implementation is authorized by this file or PR #27.**

## Frozen baseline

Gate 4 branch base:

`main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

This is the verified `main` merge commit produced by baseline-synchronization PR #26 after the exact PR #26 head passed Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke.

Gate 4 is developed in draft PR #27 from that frozen baseline. PR #27 is not an implementation PR and is not intended to be merged to `main` while its dedicated probes are in expected-RED mode.

## Gate 4 objective

Before implementation, prove both:

1. the existing approved financial baseline remains GREEN;
2. every new FIN-COURIER contract has an executable test written before the corresponding implementation and is RED on the pre-implementation baseline for the expected reason rather than because of a broken harness.

A successful expected-RED workflow means the test harness reached the assertion and detected a known missing contract. It does **not** mean the feature is implemented.

## First verified expected-RED checkpoint

On PR #27 head:

`04618b2360e0b1ba6ac28ba31dc89e8d9ef69092`

GitHub run `30248157200` proved the first isolated checkpoint:

- existing T1–T15: GREEN;
- backend target: expected RED with exactly the initial contract gaps — missing `create_sale_with_items_v2`, missing `update_courier_outcome_v2`, missing `orders_customer_required_when_debt`, and the two legacy blanket-customer constraints still present;
- mobile/desktop UI target: expected RED because the primary `فاتورة جديدة` CTA still opens quick sale (I1/J1);
- the standard Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke checks also remained GREEN on that checkpoint.

An earlier Gate-4 attempt failed during test fixture seeding before reaching assertions. That result was rejected as false RED; the isolated seed was corrected to use the already-proven project pattern (`ON CONFLICT` / profile upsert), and only the later assertion-reaching run above is accepted as evidence.

## Existing baseline — unchanged

The following pre-existing protection is preserved and not weakened:

- `tests/financial-rules/rules.sql` — T1–T15;
- `tests/unit/invoice-selectors.test.ts` — canonical client debt/custody selector coverage;
- Quality workflow;
- Ephemeral Financial Rules workflow;
- Isolated Auth UI Smoke workflow.

## Authored Gate 4 safety net

### A/B/C — PR-A creation and schema contract

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
- B1 pending courier without customer;
- B2 delivered-full courier without customer;
- B3 partial courier debt without customer rejected;
- B4 delivered-none debt without customer rejected;
- B5 delivered-none with customer at creation;
- B6 delivered-partial with customer at creation;
- B7 missing courier id rejected;
- B8 close-day aggregate from pending/full/none/partial created through v2 — expected debt 160 and unsettled custody 140 for the fixed fixture;
- B9 settlement of customer-less delivered-full custody;
- C-CK1..C-CK8 direct CHECK-shape matrix, exercising the database constraint independently of RPC validation;
- C-PF1 historical preflight detects a deliberately seeded violating legacy row;
- C-PF2 blind `VALIDATE` fails while that row exists and controlled validation succeeds only after the preflight returns zero.

### D — atomic transition and state machine

Artifacts:

- `tests/financial-rules/fin-courier-gate4-transitions.sql`
- `tests/financial-rules/fin-courier-gate4-atomicity.sql`

Coverage:

- D-T1 pending/no-customer → delivered-full;
- D-T2/D-T3 debt transitions without customer rejected and row unchanged;
- D-T4 same-tenant customer attachment + state/custody update in one transaction;
- D-T5 cross-tenant customer rejection with no partial write;
- D-T6 nonexistent customer rejection;
- D-T7 returned transition delegates to the approved return transaction;
- D-T8 forced AFTER UPDATE failure proves the whole v2 transition rolls back — state, custody, and customer remain unchanged;
- D-M1..D-M10 valid/invalid transition matrix;
- D-M11 custody reduction rejection;
- D-M12 same-state/same-value idempotent retry;
- D-M13 same-state higher custody accepted.

### D-R — returned-order baseline

Artifacts:

- `tests/financial-rules/fin-courier-gate4-return-baseline.sql`
- `.github/workflows/fin-courier-gate4-return-probe.yml`

Coverage D-R1..D-R8:

- delivered-none customer debt can become returned after confirmed physical return;
- returned debt becomes zero;
- stock restores exactly once;
- repeated return is rejected and cannot restore stock twice;
- returned is terminal;
- settled order cannot be returned;
- debt collection on returned order is rejected;
- `financial_audit_log` contains before/after return evidence.

This is a regression baseline and is expected GREEN before PR-A and after the adapters are introduced.

### E / concurrency / retry baseline

Artifacts:

- `tests/financial-rules/fin-courier-gate4-concurrency.sh`
- `tests/financial-rules/fin-courier-gate4-retry-baseline.sql`

Coverage:

- E1 two concurrent sales for stock=1 → exactly one succeeds and the loser is `insufficient_stock`;
- D-M14 concurrent partial/full transition serializes to one valid final state with non-decreasing custody;
- D-M15/E2 concurrent delivered-full transition + settlement cannot lose/double custody or create duplicate settlement payment;
- E3 explicitly freezes the known non-idempotent sale-create baseline: two duplicate logical calls create two orders; true request-key idempotency remains `FIN-IDEM-001` and is not silently claimed here;
- E4 second settlement attempt is rejected and cannot create a duplicate payment.

Concurrency is executed through the proven main Gate-4 backend workflow rather than a separate workflow because creation of a separate concurrency workflow was blocked by the connector. The test itself remains isolated and test-only.

### F — backward compatibility / read-model snapshot

Artifacts:

- `tests/financial-rules/fin-courier-gate4-compatibility.sql`
- `.github/workflows/fin-courier-gate4-compatibility-probe.yml`
- `tests/financial-rules/fin-courier-gate4-readmodel-snapshot.sql`

Coverage:

- F1 legacy six-parameter create and v2 produce equivalent safe financial results for representative direct, pending-courier, and partial-courier flows;
- F1a safe legacy transition delegates successfully;
- F1b unsafe backward/custody-reducing legacy transition is intentionally rejected by v2 safety rules;
- F2 fixed five-state golden snapshot: customer debt=160 and unsettled custody=140, including `close_day`; the exact same test must be rerun unchanged after PR-A to prove no read-model drift;
- F3 no customer-less `delivered_partial` / `delivered_none` rows exist.

### G — PR-B health / reporting

Artifacts:

- `tests/financial-rules/fin-courier-gate4-reporting.sql`
- `.github/workflows/fin-courier-gate4-reporting-probe.yml`

Coverage G1..G8:

- valid customer-less pending/full courier orders do not trigger `courier_missing_refs` / `debt_without_customer`;
- a deliberately forced genuinely corrupt customer-less debt row is still detected;
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
- `.github/workflows/fin-courier-gate4-rollback-probe.yml`

Coverage:

- H1 freezes the required rollback endpoint now: replacement CHECK absent, the two original CHECKs restored as `NOT VALID`, v2 functions absent, legacy signatures present;
- H2 customer-less partial/none verification query must be zero;
- H3 legacy create path works;
- the current pre-change baseline is used as the golden rollback fingerprint;
- a generic corrective-rollback runner is already authored: once a real forward-only corrective migration exists, it must apply that SQL on an isolated changed database, rerun T1–T15, then rerun the same rollback endpoint contract.

Gate 4 does **not** invent or claim execution of a corrective migration that does not yet exist. Actual application of the future corrective rollback remains an implementation/rollback verification step, but its assertions and runner are written before implementation.

### I/J — mobile + desktop UI

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

## Gate 4 workflows

Dedicated Gate-4 workflows currently include:

- `.github/workflows/fin-courier-gate4-probe.yml` — PR-A core/CHECK/concurrency + independent UI probes;
- `.github/workflows/fin-courier-gate4-create-aggregate-probe.yml` — B5/B6/B8;
- `.github/workflows/fin-courier-gate4-preflight-probe.yml` — C-PF1/C-PF2;
- `.github/workflows/fin-courier-gate4-transition-probe.yml` — transition matrix + D-T8 atomicity;
- `.github/workflows/fin-courier-gate4-return-probe.yml` — returned baseline;
- `.github/workflows/fin-courier-gate4-retry-probe.yml` — E3/E4;
- `.github/workflows/fin-courier-gate4-compatibility-probe.yml` — F compatibility;
- `.github/workflows/fin-courier-gate4-reporting-probe.yml` — G1..G8;
- `.github/workflows/fin-courier-gate4-rollback-probe.yml` — F2 golden snapshot + H rollback endpoint fingerprint.

Expected-RED workflows must fail internally with their named sentinel and then report workflow success only when the reason is the approved missing contract. Any seed, build, SQL syntax, login, browser, or other harness failure is a Gate-4 failure and must not be counted as expected RED.

## Remaining execution boundary before Gate 4 approval

The safety-net assertions are now authored across the approved TEST_PLAN. Before Gate 4 can be approved:

1. all dedicated Gate-4 workflows must be run and reviewed on one exact final PR #27 head;
2. standard Quality, Ephemeral Financial Rules, and Isolated Auth UI Smoke must also be GREEN on that same head;
3. actual-GREEN baselines (T1–T15, returned baseline, F2 snapshot, rollback endpoint) must pass rather than being converted to expected RED;
4. expected-RED tests must reach the named contract assertion/sentinel — no false RED from harness failures;
5. an independent review must inspect the tests for false positives/negatives, transaction isolation, tenant isolation, and whether the assertions actually match `TEST_PLAN.md`;
6. the future corrective rollback migration itself cannot be executed before it exists; when implementation supplies it, the already-authored corrective-rollback runner becomes mandatory evidence.

## Merge / implementation boundary

- PR #27 remains DRAFT and unmerged during Gate 4 evidence collection.
- PR #27 contains no FIN-COURIER production financial logic, no migration implementation, no RPC implementation, no RLS change, and no PR-C UI implementation.
- PR-A / PR-B / PR-C remain blocked until Gate 4 evidence is independently reviewed and explicitly approved.
- Expected-RED workflow success does not authorize merge or implementation by itself.
- After Gate 4 approval, PR-A should branch from the approved Gate-4 head (not from a stale earlier `main`) so the test commits remain chronologically before the implementation commits. The relevant probes then switch from expected-RED execution mode to GREEN verification without weakening or replacing their assertions.
- The approved implementation order remains PR-A → PR-B → PR-C, each with its own exact-head CI and human merge boundary.
