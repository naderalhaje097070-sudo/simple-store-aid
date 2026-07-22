# FIN-COURIER-001 — Change Intake (NAADF-CMF Change Gate 0)

Status: Draft for human approval. Documentation only. No implementation authorized.

## Change goal

Make the advanced sale flow the primary sale path, and correct the courier
(delegate) sale flow so that the customer requirement, the courier state
contract, and the money-vs-order-vs-debt separation match real store
operations. Remove the standing conflict where the UI permits a fully-collected
courier order without a customer while the RPC rejects every courier order that
has no customer.

## Change type

- Business-rule change (courier state and customer-requirement contract).
- Database change (forward-only migration to the sale RPC contract).
- UI change (default sale flow, payment sheet, courier result wording, success
  screen, courier invoice status display).

This is a coherent, single-domain change: the courier/customer/custody sale
contract and the UI that drives it. It is **not** a performance change, an
employee-accounts change, an environment/CI change, or a refactor.

## In scope

- `create_sale_with_items` customer-requirement rule for `delivery = 'courier'`
  (via a named `create_sale_with_items_v2` + backward-compatible adapter).
- **Replacement of the effective CHECK constraints**
  `orders_customer_required_when_unpaid` and `orders_courier_requires_customer_id`
  with an outcome-based constraint (independent-review addition — the RPC guard is
  not the only enforcement layer; see CURRENT_BEHAVIOR §1a).
- Courier state derivation at sale-creation time, including a first-class
  `delivered_none` outcome that today cannot be expressed at creation.
- **Atomic post-creation courier-outcome transition** that attaches a same-tenant
  customer when the outcome creates debt (independent-review addition — closes the
  `update_courier_order_state` customer-less-transition hole).
- **Outcome-aware platform health/reporting** so valid customer-less courier
  orders are not reported as corrupt (independent-review addition).
- Courier collection recording (`collected_by_courier`) and its relationship to
  `payments` and settlement.
- Advanced sale (`SaleScreen`) becoming the default entry point; quick sale
  (`SaleQuickScreen`) demoted to a clearly-labelled secondary shortcut.
- Payment sheet courier result wording (replace generic "مدفوع/جزئي/دين" with
  explicit courier outcomes) and the mislabelled "لم تُسلَّم (دين)" control.
- Sale success screen wording for courier custody vs collected cash.
- Courier invoice operational status display (not `order.status` alone).

## Out of scope

- Performance work (PERF-APP-001): initial data loading, pagination, lazy
  routes, dynamic PDF import, dashboard summary RPC.
- General display bug fixes (BUGFIX-APP-001): `HomeScreen` `slice(-3).reverse()`
  latest-invoices ordering, midnight/timezone `useMemo` dependency, generic
  loading/error states. These are tracked separately and must not be bundled
  here, even though they are adjacent.
- Employee accounts (EMP-*), identity, RLS role model.
- Environment hardening, CI hardening, credential redaction (SEC-CI-001).
- Any global formatting or dependency upgrade.

## Urgency

Pilot-blocking. The current UI/RPC conflict causes real, reproducible sale
failures or forces creation of unnecessary customers. Pilot readiness depends on
a correct courier sale flow. Not an emergency hotfix; it must still pass the full
gate sequence before implementation.

## Risk level

High. It touches a financial write path (`create_sale_with_items`), the
customer-debt and courier-custody invariants, and the enum-derived courier state
machine. A forward-only migration is mandatory; existing applied migrations are
immutable. Backward compatibility with historical `orders` rows and the existing
RPC signature must be preserved.

## Owner

Product owner / human maintainer (approval and merge). Implementation to be
assigned after Gate 3 approval.

## Expected outcome

- A courier order may be created without a customer whenever the outcome creates
  no customer debt (pending, delivered-in-full).
- A customer is mandatory only when the outcome creates customer debt
  (delivered-partial, delivered-without-collection, and direct partial/debt).
- Pending courier orders appear immediately under courier orders but are never
  counted as financial custody.
- Money recorded as collected by the courier becomes `collected_by_courier`
  immediately; fully-collected orders are `delivered_full` and settlement-ready.
- "Delivered without collection" creates customer debt and requires a customer;
  "not delivered / returned" creates no debt and restores stock.
- Delivered and settled remain distinct states.
- UI defaults to advanced sale; quick sale remains a secondary shortcut.

## Missing / blocking information

1. **`delivered_none` at creation.** Recording a delivered-but-uncollected
   outcome at sale time requires disambiguating `paid = 0` (today always
   `pending`). Resolved by the explicit `p_courier_state` on
   `create_sale_with_items_v2` (see COURIER_STATE_CONTRACT §2) — pending Gate 3
   confirmation of the parameter name/order.
2. **Constraint-validation strategy.** Whether to `VALIDATE` the replacement CHECK
   in the same migration or defer (MIGRATION_IMPACT). Safe either way; Gate 4
   decision.
3. **Transition-RPC shape.** Named `resolve_courier_order_v2` vs an added optional
   `p_customer_id` on `update_courier_order_state` (COURIER_STATE_CONTRACT §3) —
   Gate 3 decision.

## Deferred to separate governed changes

- **FIN-SETTLEMENT-METHOD-001** — settlement payment-method semantics.
  `settle_courier_orders` hard-codes `method = 'cash'`
  (`20260627201534_...c879.sql:496`). Separating "transfer direct to shop" vs
  "paid to courier" vs "courier handover method" is its own governed change, not
  part of FIN-COURIER-001.
- **FIN-IDEM-001** — sale idempotency key (no idempotency today; TEST_PLAN E3).

## Baseline decision (finding 10)

- Documentation in this folder may be revised now on the PR #24 branch.
- **Implementation starts only after AUDIT-001 / PR #23 is merged**, with each
  implementation branch cut from the **approved `main` head** after that merge —
  not from the current pre-baseline head (`906df4b`). Recorded here and in
  PR_DECOMPOSITION §Baseline.

## Explicit assumptions

- Current `main` head is `906df4b`; the courier RPC/UI facts in
  CURRENT_BEHAVIOR were read from the working tree at that head.
- The `courier_state` enum already contains
  `pending | delivered_none | delivered_partial | delivered_full | returned`
  (confirmed in migrations and `src/domain/finance/invoice-selectors.ts`).
- The domain selectors in `src/domain/finance/invoice-selectors.ts` already
  encode the target debt/custody semantics and are the intended single source of
  truth for UI math; the change aligns the RPC and screens to them rather than
  redefining them.
- No production data or secrets are touched; all verification is on isolated
  environments.

## Gate decision requested

Approve this intake and the proposed target in EXPECTED_BEHAVIOR so that Gates
2–3 (impact, contract, decomposition — drafted here) can be reviewed and, after
AUDIT-001 / PR #23 is merged, implementation authorized as three scoped PRs:
PR-A (schema constraints + v2 sale RPC + atomic transition + SQL tests),
PR-B (outcome-aware platform health/reporting), PR-C (advanced-sale default +
courier UI). Nothing here asserts that any gate is already approved.
