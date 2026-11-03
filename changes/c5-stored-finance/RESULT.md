# C5-STORED-FINANCE-01 — partial collection retry-safety blocked

3 November 2026, Africa/Tripoli. **Diagnostic tests Implemented and Tested; financial acceptance FAILED. No product fix implemented. Owner contract decision required.**

## Proven outcome

On both a fresh and a populated isolated54-migration database, an authenticated operator collected20on a100invoice. The first committed reply was intentionally discarded to model response loss. Resending the same order/amount/method under the same actor returned HTTP200 and produced another20payment: stored paid/payment-sum20→40, payment-count1→2. The tester intended one logical collection. This fails the named retry-safety target, not a setup/runner/billing failure.

The existing API has no logical-operation identifier. Two genuinely distinct20payments can legitimately have the same existing request body; the server currently cannot distinguish them from a retry. The finding concerns missing logical retry identity, not a rule that equal amounts are always duplicates. Actual UI automatic retry and any real-customer incident were **not** observed. See [finding and reachability](FINDINGS.md) and the [unapplied concrete proposal](PROPOSAL.md).

| Mode | Positive/setup/financial controls | Retry target | Actual native job |
| --- | --- | --- | --- |
| Fresh54 | 63 passed | FAILED:20→40,1→2payments |125697199766, exit2 |
| Populated54 |66 passed, including retained prior-tenant data | FAILED:20→40,1→2payments |125697199654, exit2 |

Counts include fixture/Auth/setup checks; they are not unique financial scenarios or vulnerability counts. Populated mode uses nonempty data on the current54schema, not an older-schema migration upgrade or restore drill. Both native jobs cleaned up successfully with zero unexpected IPv4/IPv6 rejects and private credential/state removal verified by the console marker; the raw cleanup JSON predates the final private-file-marker field and is preserved unchanged.

## Exact source and CI

- Repository `naderalhaje097070-sudo/simple-store-aid`; branch `integration/g0-g1-reconcile-2026-10-18`.
- Exact executable `e0a75541b981eed0bf1715315f7e418e466330c6`; tree `4c76cb888aef2481ee0987107ce44fb30960b211`; base `0b6e17b7b90c19c803936f1690f75cab3e17f53d`.
- Sole claim [#55/6594150829](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55#issuecomment-6594150829).
- Main remains `220fc2066b4d6254b1803b5e32919c47d60a9c7e`; originals27/35/39/49/50 stay open/draft with unchanged heads.
- This result/evidence delivery is a documentation-only direct descendant with identical executable/manifest bytes. No runtime result is transferred to that descendant.

| Automatically affected workflow | Run | Conclusion, attempt1 |
| --- | --- | --- |
| Integrated G0 verification | [41568980107](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41568980107) | SUCCESS |
| C5 stored financial contracts | [41568980208](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41568980208) | FAILURE |
| G1 Bounded Acceptance Repair | [41568980367](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41568980367) | SUCCESS |
| B1 composition compatibility | [41568980137](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41568980137) | SUCCESS |

C5 failed solely at the native financial target; all preceding controls in both modes passed. The target failure is not waived or converted into an expect-red-success job, and no unchanged rerun was requested. G1's current41nonfinancial checks/54migration target/SSR/Auth/egress/cleanup remain successful. G0 and B1 pass97unit/300expectations, full types/lint0errors14warnings/builds and supported complete audit raw{}actualexit0; previous security/source/callback/browser controls remain intact. These green workflows do not accept C5.

## Stored financial controls that passed

The probe reuses C3 CompositionProbe/C2 QuantityProbe/lifecycle fixtures and current real RPCs. Expected values are explicit constants independent from the observed stored result:

| Contract | Expected persisted result / negative control |
| --- | --- |
| Direct fractional sale |0.25unit at100 → total25/paid25/payment25; exact stock9.75; close-day sales25/cash25/profit15 |
| Partial courier delivery |100invoice with40collected → paid0/payment0/custody40/customer debt60; close-day cash stays25 |
| Settlement and remaining debt |Staff settles40once, clears custody/assignment; retry adds no second cash; remaining60collection → paid100/two payments totaling100; close-day cash125/profit75 |
| Return |Zero-paid0.5unit courier return restores0.5stock, no cash; returned debt collection and duplicate return deny with unchanged stored relations |
| Authorization |Active staff succeeds; foreign tenant/anonymous/banned preissued staff token deny atomically; unaffected active staff still succeeds after ban |
| Concurrency |Distinct sales cannot oversell; same sale UUID posts one result; two20collections on a25balance yield one success/one remaining-limit denial |
| Partial logical-operation resend |**FAILED** even though neither request individually exceeds the balance; this is distinct from the successful overcollection/concurrency limit control |

The primary close-day observed/expected values are retained in native controls. JSON result receipts preserve every control and the exact failing target. No amount formula, revenue/cash definition, rounding policy or actual financial SQL changed by these tests.

## Change and preservation

One existing capture dispatch plus six new test/workflow paths and a small delta manifest are the executable change. The new guard derives the450-entry immutable baseline from Git and admits only that one capture before/after and exact six additions;456protected entries are verified. It reuses prior guard helpers and preserves all previous verifiers/manifests. All54migrations/75repository SQL files, app source, package/lock/approved patch and historical evidence remain byte/mode exact; no removed paths.

Local source-delta19/verdict5 tests pass; Python syntax and separate required YAML test commands checked. A draft YAML scalar-folding issue was corrected before publication and is recorded in TEST_IMPACT.md; no hosted result is claimed for that draft. Local Docker/psql unavailable, so only hosted real Auth→API/RPC→DB execution supplies the financial observation.

[Impact/scope documents](CHANGE_INTAKE.md) define the test-only authority and [rollback](ROLLBACK_IMPACT.md): forward-revert capture/admission/tests together, retaining evidence. No database migration, product fix, permission change, merge, deployment, production action, newPR, closure, new cost or history rewrite.

## Evidence, review and next decision

[hosted/index.json](hosted/index.json) preserves7raw provider ZIPs, SHA256-checked against API digests, and4complete non-native logs; safe original native financial/G1 markers and extracted financial result/cleanup JSON are included. Full native logs are not republished. Actual original failed jobs remain failed. Native publication scans and cleanup assertions passed.

Implementation-owner review only; C6 independent review and C7 merge decision remain open. Full financial UI→DB, historical populated upgrade, restore, broader financial audit/actor matrix and product readiness remain unverified. No real-user/payment-history correction is inferred or authorized.

**ONE NEXT: owner's specific approval of [PROPOSAL.md](PROPOSAL.md)**: keyed collection RPC using the existing transactional idempotency table, durable environment/tenant/actor-scoped identity in the actual collection UI, and coordinated closure of the authenticated unkeyed bypass while preserving existing accounting policies. [Decision scope](DECISION_SCOPE.json) is exact and unapplied. AGENTS.md reserves material financial-contract changes to the owner; ordinary verification is already complete. After approval implement and test this bounded fix, then resume remaining C5 browser/upgrade/restore and C6/C7. No merge or deployment approval is requested.
