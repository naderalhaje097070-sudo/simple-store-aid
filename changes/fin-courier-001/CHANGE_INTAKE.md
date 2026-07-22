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

- `create_sale_with_items` customer-requirement rule for `delivery = 'courier'`.
- Courier state derivation at sale-creation time, including a first-class
  `delivered_none` outcome that today cannot be expressed at creation.
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

1. **Settlement payment-method semantics.** `settle_courier_orders` currently
   hard-codes `method = 'cash'` (evidence in CURRENT_BEHAVIOR). The target
   separation of "transfer direct to shop" vs "paid to courier" vs "courier's
   later handover method" needs an approved contract before implementation.
2. **`delivered_none` at creation.** Recording a delivered-but-uncollected
   outcome at sale time requires disambiguating `paid = 0` (today always
   `pending`). This needs an approved parameter/contract decision
   (see COURIER_STATE_CONTRACT).
3. **Migration ordering vs baseline PR.** Whether FIN-COURIER-001 starts from
   current `main` (`906df4b`) or waits for the baseline PR (AUDIT-001 / PR #23)
   to merge first. Governance says start from an approved baseline.

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

Approve this intake and the target behavior in EXPECTED_BEHAVIOR so that Gates
2–3 (impact, contract, decomposition — already drafted here) can be reviewed and
implementation authorized as separate financial-first and UI-second PRs.
