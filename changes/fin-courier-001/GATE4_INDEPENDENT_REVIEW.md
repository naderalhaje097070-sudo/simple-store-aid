# FIN-COURIER-001 — Gate 4 Independent Review

Status: **REVIEWED WITH CORRECTIONS — exact-head execution still required.**

This review is limited to Gate-4 tests, harnesses, evidence, and workflow behavior. It does not authorize PR-A, PR-B, PR-C, production access, deployment, or merge.

## Review baseline

- Frozen implementation baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`.
- Gate-4 review PR: #27.
- Static/adversarial review covered the Gate-4 backend contract suites, transition/concurrency design, rollback/preflight behavior, reporting coverage, UI probes, and expected-RED classification rules through PR head `d484399d62fde5f4220c351d47992970279780f4`.

## Material findings corrected

### R1 — CHECK tests could pass on the wrong constraint

Previous risk:

`C-CK5`, `C-CK6`, `C-CK7P`, and `C-CK7N` accepted any PostgreSQL `check_violation`. An unrelated CHECK could therefore reject the test row and create a false PASS for `orders_customer_required_when_debt`.

Correction:

- capture `CONSTRAINT_NAME` with `GET STACKED DIAGNOSTICS`;
- require the exact constraint `orders_customer_required_when_debt` for each negative shape;
- report the actual rejecting constraint when it differs.

Result: the matrix now proves the intended database enforcement layer rather than generic rejection.

### R2 — Courier UI probe scanned unrelated page text

Previous risk:

The I2/J3 probe searched the entire page body for the words `مدفوع`, `جزئياً`, and `دين`. Legitimate debt/payment summaries could contain those words after PR-C even when the courier outcome selector was correct.

Correction:

- continue requiring the four approved operational courier outcomes;
- reject the legacy generic states only when they still exist as exact outcome **buttons/controls**.

Result: the probe targets the interaction contract instead of unrelated copy.

### R3 — Success-screen probe could misclassify runtime failures as expected RED

Previous risk:

A broad `except Exception` around sale saving converted browser timeouts, backend errors, login/runtime failures, or other harness faults into `GATE4_UI_SUCCESS_EXPECTED_RED`.

Correction:

- unexpected save/browser/runtime exceptions are now re-raised unchanged after evidence screenshot capture;
- only explicit known contract assertions emit the expected-RED sentinel.

Result: infrastructure/runtime failures can no longer satisfy Gate-4 expected-RED evidence.

### R4 — Rollback fingerprint checked legacy constraint names but not semantics

Previous risk:

H1 verified that the two legacy constraints existed and were `NOT VALID`, but an incorrectly defined constraint with the correct name could pass.

Correction:

The rollback endpoint now also proves the original behavior:

- direct partial debt without customer must be rejected specifically by `orders_customer_required_when_unpaid`;
- a fully-paid courier row without customer must be rejected specifically by `orders_courier_requires_customer_id`.

Result: H1 fingerprints rollback semantics, not only catalog names.

### R5 — F1 compared payment counts, not payment effects

Previous risk:

Legacy and v2 create paths could each create one payment row with different `kind`, `method`, `amount`, customer, or courier fields and still pass F1.

Correction:

F1 now compares normalized payment-effect multisets containing:

- `kind`;
- `method`;
- `amount`;
- `customer_id`;
- `courier_id`.

Record IDs and timestamps are intentionally excluded.

Result: safe-flow compatibility now covers the actual cash/payment effect.

### R6 — B9 only proved that settlement did not throw

Previous risk:

A settlement RPC could return successfully while leaving custody, courier assignment, paid amount, or payment rows incorrect.

Correction:

B9 now requires after settlement:

- `delivery = direct`;
- `courier_id IS NULL`;
- `paid = 200` for the fixed fixture;
- `collected_by_courier = 0`;
- exactly one `courier_settlement` payment;
- settlement payment amount = `200`.

Result: B9 now proves the full custody-to-receipt financial effect.

## Reviewed areas without a material correction

### Transition / atomicity

- debt-creating transitions require a customer and verify rejection atomicity;
- same-tenant customer attachment and cross-tenant/nonexistent customer rejection are exercised;
- custody monotonicity and backward transitions are covered;
- forced AFTER UPDATE failure verifies state/custody/customer rollback as one transaction.

The cross-tenant fixture was checked against the existing `handle_new_tenant` trigger. The trigger adds the second-tenant owner role but only rewrites a profile whose `tenant_id IS NULL`; therefore the test user's existing profile remains on the original tenant and the cross-tenant customer remains a valid isolation probe.

### Concurrency

- stock=1 concurrent sale requires exactly one success;
- partial/full concurrent transitions must serialize to the valid full state;
- transition/settlement concurrency accepts only valid settled or valid unsettled end states;
- duplicate settlement payment is explicitly forbidden.

The multi-session suite intentionally runs last because it cannot share the transaction rollback model used by the single-session SQL suites.

### Historical preflight

- replacement CHECK must begin `NOT VALID`;
- a deliberately injected legacy violation must be detected;
- blind `VALIDATE` must fail while the violation exists;
- controlled validation is permitted only after preflight returns zero.

### Retry baseline

E3 intentionally freezes the current duplicate-create behavior and does **not** claim sale idempotency. Request-key idempotency remains the separate pilot blocker `FIN-IDEM-001`. E4 independently proves settlement retry cannot create duplicate settlement payments.

### Returned/read-model coverage

The returned-order suite overlaps T15 for stock, collection blocking, and zero custody. The separate F2 five-state snapshot executes the real `close_day` path and freezes `customer_debts = 160` and `unsettled_custody = 140`, so returned/debt behavior is not accepted solely from a local CASE expression.

### Reporting

G1–G8 exercise both false-positive avoidance for valid customer-less pending/full courier rows and positive detection of a deliberately corrupt customer-less debt row. Admin and tenant debt totals are reconciled to the fixed canonical expected total.

### CI versioning boundary

The Gate-4 workflow currently uses the same `supabase/setup-cli@v1` with `version: latest` convention as the existing Ephemeral Financial Rules workflow. Gate 4 does not broaden scope to fix that pre-existing nondeterminism; version pinning and PR-report redaction remain governed by `SEC-CI-001`.

## Runner-acquisition blocker

Several recent exact-head attempts created GitHub Actions jobs but failed before any workflow step started (`steps = None`) across both pre-existing workflows and the Gate-4 jobs. Those runs are rejected as PASS/FAIL evidence.

A previously verified Gate-4 checkpoint did reach the assertions and proved T1–T15 GREEN plus initial expected-RED contract gaps. However, the corrected final head still requires a fresh exact-head run after the review changes above.

## Gate-4 approval conditions remaining

Gate 4 remains **NOT APPROVED** until one exact final PR head proves all of the following:

1. Quality = GREEN.
2. Ephemeral Financial Rules / T1–T15 = GREEN.
3. Isolated Auth UI Smoke = GREEN.
4. FIN-COURIER Gate 4 Probe reaches all true-GREEN baselines and all approved expected-RED sentinels without harness/runtime substitution.
5. The final diff remains test/evidence/workflow only with no FIN-COURIER production implementation.
6. A human explicitly approves Gate 4 after reviewing the exact-head evidence.

Until then, PR-A / PR-B / PR-C remain blocked.
