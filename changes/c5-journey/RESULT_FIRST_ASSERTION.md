# C5-FIRST-FAILED-ASSERTION-01 — first failed condition and actual values

Date: 2026-11-06 Africa/Tripoli. Owner explicitly requested extraction/comparison before any financial modification. Sole implementer /root, #55/6671950951. Read-only evidence diagnosis; no new native run, application/SQL/migration/financial policy or test-expectation change.

## Verified original evidence

Repository `naderalhaje097070-sudo/simple-store-aid`, existing `integration/g0-g1-reconcile-2026-10-18`. Read head `5c8328a3b96c94c5a4a52b9693483604c3bac70b`; original executable `122d8aa4f33ba1e54a08ce90a5c2db16a4ab5560`, native run `42125234643`.

A newly available artifact-download connector read the original ZIPs, so no test rerun or diagnostic source edit was needed. Downloaded ZIP bytes match the GitHub artifact SHA256 exactly:

| Mode | Artifact | SHA256 |
|---|---:|---|
| Fresh | 13460626236 | `fb16e988ff802e433e1771ccfe6cc077d62eedfe02b342f6d6d1a10814025a89` |
| Upgrade | 13460512159 | `110a8bdda4669135d7f51b2fd9aff575b133319c6b21cab3150470657e7223e4` |

Original archives are preserved byte-for-byte in this packet under `evidence/first-assertion/`. They contain only the listed JSON receipts; JWT/publishable-key pattern and sensitive-key scan pass. This is a new durable archive claim for this packet; earlier metadata-only reports remain historical and are not rewritten.

## First and sole failed row

**`desktop_final_day_close_independent_oracle`** is the first and only false row:
fresh row58, with57 earlier PASS; upgrade row59, with58 earlier PASS. Row counts include fixture/setup controls, not distinct product scenarios.

Both modes have identical numeric comparison:

| Field | Expected by current test | Stored observation | Difference |
|---|---:|---:|---:|
| sales | 275 | 275 | 0 |
| collected | 225 | 225 | 0 |
| expenses | 5 | 5 | 0 |
| realized_profit | **130** | **135** | **+5** |
| customer_debts | 0 | 0 | 0 |
| unsettled_custody | 0 | 0 | 0 |

The preceding `desktop_actual_profit_display_after_expense`, `desktop_real_UI_expense_stored` and `desktop_close_day_success` rows pass. Settlement and return-stock/debt/custody controls also pass. Thus the close_day call succeeded; this failure compares its stored profit definition with the test's net-profit expectation. It is not the previous selector timeout.

## Source trace and independent arithmetic

All55 applied-source migration files were inspected in order. Seven define `close_day`; the LAST definition is `supabase/migrations/20261010223557_enforce_live_account_state.sql`, lines189–274. No later migration even mentions close_day.

That function computes the payment-weighted item margin into `v_realized_profit` (lines240–251) and inserts it unchanged into `day_closes.realized_profit` alongside the separately collected `v_expenses` (lines253–258). It never subtracts expenses. Historical July definitions are superseded by this October definition; this diagnosis does not mistake an earlier body for the effective source.

By contrast, `src/routes/_authenticated/app.tsx:370` and `2546–2553` subtract expenses for the profit display and day-close preview. The existing comment claiming that preview mirrors close_day is inaccurate about expense subtraction.

The frozen fixture has unit price100/cost40. Recognized paid quantities are0.25+1+1, so collected225 less allocated item cost90 gives135 before expenses. The returned0.5 has no payment. Net after the stored expense5 is **135 − 5 = 130**. The exact difference is the expense, not floating-point noise.

## Conclusion and limits

Confirmed defect class: **stored-versus-displayed profit semantics are inconsistent**. The test's130 matches the net UI definition; stored135 matches the SQL's before-expense margin. This evidence does not prove missing cash, incorrect collection or a lost expense: all those observed fields match.

The reviewed DECISIONS and current C5 INTAKE do not explicitly approve a resolution of gross-versus-net meaning for the persisted field. Therefore this read-only task does NOT silently choose SQL subtraction, change the test to135, rename a field, alter historical snapshots or claim financial-contract approval.

Both paths reach this final desktop oracle; mobile has not executed because the harness stops on the desktop failure. The later zero-external/script-error control is still unexecuted; earlier blocked-external attempts remain unresolved. WholeC5/integration, fullC6/C7/RC/Pilot remain unaccepted.

## Verification and review

Actual commands verified original ZIP SHA256, parsed all controls, selected the first false row, required exactly one false row and one differing field, checked all earlier PASS rows, scanned JSON members and traced all55 migration bodies. No source/build/financial test was rerun because no executable changed.

A separate actual read-only agent `/root/assertion_review` independently verified both original archives/digests, first false row, all55 migrations, latest SQL body, UI subtraction and decision-semantic limits. Diagnosis accepted within extraction/source-review scope only; not a fullC6 or merge approval. See REVIEW_FIRST_ASSERTION.md and `evidence/first-assertion/comparison.json`.

## Next and rollback

ONE NEXT: prepare a bounded contract-alignment design stating exactly whether the stored field means margin before expenses or net profit after expenses, and how UI/API/history remain compatible. Then choose the reviewed resolution before implementation. Preserve the failing evidence and existing130 expectation while the mismatch remains unresolved; use forward-only migrations if a later authorized design needs SQL changes. Do not waive the network or mobile gates.

Delivery is documentation and original evidence only; no DB compensation is needed. If its publication must be withdrawn, use an additive documentation revert, not history rewriting. Main and the five original drafts remain unchanged; no merge, deployment, production access, PR closure, new cost or financial modification.
