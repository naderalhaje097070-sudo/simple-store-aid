# FIN-COURIER-001 — PR Decomposition

Status: Draft for review. One coherent goal per PR (DEC-009, Architecture
Rule 6). Financial contract first, UI second. Nothing here is authorized until
Gates 0–3 are approved.

## Ordering & dependencies

```
(baseline: AUDIT-001 / PR #23 merged) 
        │
        ▼
PR-A  Financial contract + migration + SQL tests   (backend, forward-only)
        │
        ▼
PR-B  UI: advanced-sale default + courier flow      (frontend, depends on PR-A)
        │
        ▼
(separate tracks, NOT part of this change)
   BUGFIX-APP-001 · PERF-APP-001 · settlement-method follow-up
```

## PR-A — Financial contract (backend)

Goal: correct the courier customer-requirement rule and enable create-time
courier outcome, without any UI change.

Includes:
- New forward-only migration:
  - Replace blanket courier customer guard with outcome-based rule
    (`customer_required_for_debt`; `courier_requires_courier` for missing courier).
  - Add create-time courier outcome (overload with `p_courier_state`, default
    NULL = today's paid-derived mapping) — see COURIER_STATE_CONTRACT.
- Client contract update in `src/lib/db.ts` (`CreateSaleInput`, `useCreateSale`)
  to pass the outcome; safe default preserves old behavior.
- SQL tests added to `tests/financial-rules/rules.sql`: B1–B9, C1–C4, D1–D3
  (TEST_PLAN). Existing T1–T15 kept and must stay green.
- `DECISIONS.md` entry for the outcome-parameter and customer-rule decision.

Excludes: any screen change, any wording change, default-flow change.

Acceptance: TEST_PLAN A, B, C, D pass on isolated Supabase; no existing test
weakened; backward-compat proven.

Risk: High (financial write path). Requires independent adversarial review
(Gate 6) focused on transaction boundaries, the customer-rule branch, and
create-time state derivation.

## PR-B — Sale UX (frontend)

Goal: make advanced sale the default and align the courier UI to the PR-A
contract.

Includes:
- Default-flow routing: `app.tsx:291,302,329,1124` → advanced `sale`; add a
  labelled secondary quick-sale shortcut.
- `PaymentSheet`: courier-outcome selector when delivery=courier; outcome-based
  `needsCustomer` reusing `getCustomerDebtForInvoice` (`app.tsx:929-1073`).
- `CourierCustodyScreen`: rename "لم تُسلَّم (دين)" → "تم التسليم دون تحصيل";
  ensure "not delivered" routes to `returned` (`app.tsx:484,566,579`).
- `SaleSuccessScreen`: type-aware wording (`app.tsx:1112`).
- Courier invoice **operational status** display via selectors (not
  `order.status` alone).
- UI tests: TEST_PLAN E (mobile RTL) and F (desktop).
- Optional feature flag gating default-flow + courier-outcome UI (ROLLBACK_PLAN).

Excludes: `HomeScreen.slice(-3).reverse()` and midnight/timezone dependency
(BUGFIX-APP-001); any pagination/lazy-load/PDF/dashboard-RPC work (PERF-APP-001).

Acceptance: TEST_PLAN E, F pass on mobile and desktop smokes; no financial logic
duplicated in screens (Architecture Rule 2); Quality + isolated smokes green.

Risk: Medium. Large shared route file; keep the diff scoped to the sale path.

## Explicitly separate follow-ups (NOT in FIN-COURIER-001)

- **Settlement method separation** (`settle_courier_orders` hard-coded `'cash'`,
  `20260627201534_...c879.sql:496`): additive, forward-only; may be PR-A2 or a
  distinct change once its contract is approved (CHANGE_INTAKE §Missing info).
- **BUGFIX-APP-001**: latest-invoices ordering, midnight/timezone `useMemo`
  dependency, generic loading/error states.
- **PERF-APP-001**: initial-load reduction, pagination, lazy routes, dynamic PDF
  import, dashboard summary RPC, post-sale cache patching.

## Merge boundary

- Passing tests do not authorize merge (NAADF-CMF merge boundary).
- No automated merge or deploy; a human reviews evidence and merges.
- PR-A must be merged and verified on `main` before PR-B is reviewed, so the UI
  never ships ahead of its contract.
