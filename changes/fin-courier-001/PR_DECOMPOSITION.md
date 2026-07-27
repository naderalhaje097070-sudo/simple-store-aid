# FIN-COURIER-001 — PR Decomposition

Status: Proposed target based on product-owner direction; pending formal Gate
approval. One coherent goal per PR (DEC-009, Architecture Rule 6). Nothing here
is authorized until Gates 0–3 are approved **and** the baseline decision
(§Baseline) is satisfied.

## Ordering & dependencies

```
(baseline: AUDIT-001 / PR #23 merged; impl branch cut from approved main head)
        │
        ▼
PR-A  Financial schema constraints + v2 sale RPC + atomic transition + SQL tests
        │
        ▼
PR-B  Outcome-aware platform health / report functions + regression tests
        │
        ▼
PR-C  Advanced-sale default + courier UI + wording + success screen + status
        │
        ▼
(separate governed change) FIN-SETTLEMENT-METHOD-001
```

PR-B depends on PR-A (health checks must match the new valid-order shapes). PR-C
depends on PR-A (UI drives the v2 contract) and should land after PR-B so the
platform console does not scream Critical while the UI starts producing
customer-less courier orders.

## PR-A — Financial schema + RPC (backend)

Goal: make the schema and RPC layer accept the outcome-based customer rule and
close the transition hole, without any UI or reporting change.

Includes:
- **Forward-only migration** replacing the CHECK constraints:
  drop `orders_customer_required_when_unpaid` + `orders_courier_requires_customer_id`;
  add the NULL-safe, `returned`-aware `orders_customer_required_when_debt`
  **`NOT VALID`** (COURIER_STATE_CONTRACT §1). **Do not `VALIDATE` in this
  migration** (decision 5B). Keep `orders_courier_requires_courier_id` and
  `orders_collected_not_over_total`.
- **Historical-data preflight** query/test (MIGRATION_IMPACT step 2); the separate
  `VALIDATE CONSTRAINT` step is a **later controlled operation**, gated on the
  preflight returning zero rows — not part of PR-A.
- **`create_sale_with_items_v2`** (canonical) with explicit final
  `p_courier_state public.courier_state` (**no DEFAULT**; decision 5A);
  direct requires courier_state/courier_id NULL; courier requires both, rejects
  `returned` at creation; outcome-based customer rule
  (`customer_required_for_debt`, `courier_requires_courier`).
- **Six-param `create_sale_with_items` adapter** delegating to `_v2` (no
  independent financial logic) — backward compatibility.
- **`update_courier_outcome_v2`** (canonical) per COURIER_STATE_CONTRACT §3:
  transition matrix, monotonic custody, forbidden backward/reduction,
  idempotent same-value retry, atomic same-tenant customer attachment; old
  `update_courier_order_state` kept only as a compatibility adapter; `returned`
  stays delegated to `return_courier_order`.
- Client contract update in `src/lib/db.ts` to call `_v2` (createSale and the
  transition).
- SQL tests added to `tests/financial-rules/rules.sql`: TEST_PLAN B, C-CK*, C-PF*,
  D-T*, D-M*, E, F. Existing T1–T15 kept and must stay green.
- `DECISIONS.md` entries for decisions 5A/5B/5C and the outcome-based customer
  rule.

Excludes: platform health/report changes, any screen change, wording, default
flow.

Risk: High (financial write path + schema constraint). Requires independent
adversarial review (Gate 6) on transaction boundaries, the customer-rule branch,
the transition atomicity, and constraint safety.

## PR-B — Outcome-aware platform health & reporting (backend)

Goal: stop the platform console from reporting valid customer-less courier orders
as corrupt.

Includes:
- Make `get_platform_financial_health` `courier_missing_refs` (Critical) and
  `debt_without_customer` (Warning) **outcome-aware**: flag only rows that carry
  genuine customer debt with no customer (courier `delivered_partial` /
  `delivered_none` with `customer_id IS NULL`, and direct partial/debt with null
  customer), not every customer-less courier order. Update the matching
  `get_platform_financial_health_rows` detail queries in lock-step.
- **Fix debt under-reporting (finding 4):** make
  `get_platform_admin_overview.open_customer_debts` and
  `get_platform_tenants_health.open_debts` **outcome-aware** so they **include**
  courier `delivered_partial` (remainder) and `delivered_none` (total) customer
  debt, instead of excluding all courier orders.
- **Single-source strategy:** use the same per-order customer-debt contract as
  `close_day` / `getCustomerDebtForInvoice` — preferably one canonical SQL
  expression/immutable helper reused by all consumers — rather than re-inlining a
  divergent CASE (Architecture Rule 2; DATA_IMPACT §Single-source).
- Review `get_platform_day_close_health`, `get_platform_courier_custody_health`,
  `close_day`, `get_tenant_today_estimate`; adjust only where a valid new order is
  misreported (CURRENT_BEHAVIOR §5/§5a).
- Regression tests TEST_PLAN G1..G8 (including source-of-truth equality) and
  re-run A10/B8 aggregates.
- Forward-only migration (`CREATE OR REPLACE` on the reporting functions).

Excludes: UI, sale-path RPC changes.

Risk: Medium. Read-only reporting functions; no write path.

## PR-C — Sale UX (frontend)

Goal: advanced sale default + courier UI aligned to the PR-A contract.

Includes:
- Default-flow routing: `app.tsx:291,302,329,1124` → advanced `sale`; labelled
  secondary quick-sale shortcut.
- `PaymentSheet`: courier-outcome selector when delivery=courier; outcome-based
  `needsCustomer` reusing `getCustomerDebtForInvoice` (`app.tsx:929-1073`).
- `CourierCustodyScreen`: rename "لم تُسلَّم (دين)" → "تم التسليم دون تحصيل";
  ensure "not delivered" routes to `returned` (`app.tsx:484,566,579`).
- `SaleSuccessScreen`: type-aware wording (`app.tsx:1112`).
- Courier invoice **operational status** display via selectors.
- UI tests TEST_PLAN I (mobile RTL) and J (desktop).
- Optional feature flag gating default-flow + courier-outcome UI (ROLLBACK_IMPACT).

Excludes: `HomeScreen.slice(-3).reverse()` and midnight/timezone dependency
(BUGFIX-APP-001); pagination/lazy-load/PDF/dashboard-RPC (PERF-APP-001).

Risk: Medium. Large shared route file; keep the diff scoped to the sale path.

## Deferred to separate governed changes (NOT in FIN-COURIER-001)

- **FIN-SETTLEMENT-METHOD-001** — settlement payment-method redesign
  (`settle_courier_orders` hard-codes `method='cash'`,
  `20260627201534_...c879.sql:496`; separate "transfer to shop" vs "paid to
  courier" vs "courier handover method").
- **FIN-IDEM-001** — sale idempotency key (TEST_PLAN E3 baseline).
- **BUGFIX-APP-001** — latest-invoices ordering, midnight/timezone dependency,
  loading/error states.
- **PERF-APP-001** — initial-load, pagination, lazy routes, dynamic PDF,
  dashboard summary RPC, post-sale cache patching.

## Baseline (finding 10)

- Documentation (this folder) may be revised now on the PR #24 branch.
- **Implementation starts only after AUDIT-001 / PR #23 is merged**, and each
  implementation branch (PR-A/B/C) is cut from the **approved `main` head** after
  that merge — not from the current pre-baseline head.

## Merge boundary

- Passing tests do not authorize merge (NAADF-CMF merge boundary).
- No automated merge or deploy; a human reviews evidence and merges.
- PR-A → PR-B → PR-C land and verify in order so no layer ships ahead of its
  contract.
