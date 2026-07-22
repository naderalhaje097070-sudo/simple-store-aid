# FIN-COURIER-001 — Test Impact (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. See TEST_PLAN for the full case list; this maps suites to changes.

## Suites affected

| Suite | File | Change |
|---|---|---|
| Financial rules (SQL) | `tests/financial-rules/rules.sql` | **Extend**: add B, C-CK*, D-T*, E, F, G, H. Keep T1–T15. |
| Unit selectors | `tests/unit/invoice-selectors.test.ts` | Add cases if UI centralizes debt derivation via selectors (PR-C). |
| E2E | `tests/e2e/sale-dashboard-close.py` | Extend for advanced-default flow + courier outcomes. |
| E2E auth smoke | `tests/e2e/isolated-auth-smoke.py` | Re-run as regression; sale path must still work. |
| Visual/mobile RTL | `tests/visual/mobile-rtl-smoke.py` | Add I1–I4 (mobile wording + default flow). |

## Existing tests that must be kept (not weakened)

- **T3** direct debt without customer must still be rejected.
- **T5/T6** courier-with-customer cases stay; the no-customer path is **added
  alongside**, not by editing T5/T6 to drop the customer.
- **T7/T8/T9/T10** settlement/return invariants unchanged.

## Corrections captured from independent review

- **A10:** `get_tenant_today_estimate` returns no debt/custody; assert it only on
  sales/collected/expenses. `close_day` remains the debt/custody regression
  surface.
- **E4 (was C4):** second `settle_courier_orders` on the same order → reject
  `order_not_in_courier_custody`, no duplicate payment (guard
  `20260627201534_...c879.sql:473-474`).
- **E3 (was C3):** relabeled as a **known non-idempotent baseline**; true
  idempotency is FIN-IDEM-001, out of scope.

## New coverage required by findings

- Effective CHECK constraints: C-CK1..5.
- Customer-less pending → full: B2, D-T1, C-CK4.
- Customer-less pending → partial/none rejection: B3, B4, D-T2, D-T3, C-CK3.
- Atomic same-tenant customer attachment: D-T4.
- Cross-tenant / nonexistent customer rejection: D-T5, D-T6.
- Platform health checks outcome-aware: G1..G6.
- Admin overview debt totals: G4.
- Rollback of constraints and RPCs: H1..H3.

## Environments & commands

- SQL: `tests/financial-rules/run.sh` against isolated Supabase (Ephemeral
  Financial Rules workflow). Authoritative source: GitHub checks on the head.
- Unit: `bun test tests/unit`.
- E2E/visual: `tests/e2e/run.sh`, `tests/visual/mobile-rtl-smoke.py` on isolated
  accounts.

## CI note

- Quality lints only changed JS/TS; SQL correctness is proven by the isolated
  financial-rules workflow. Both must be green on the branch head for each of
  PR-A, PR-B, PR-C. No workflow files are modified by this change.
