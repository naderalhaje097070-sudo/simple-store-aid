# FIN-COURIER-001 — Courier Sale Workflow Correction

## Status

Change Intake only. No implementation is authorized in this pull request.

## Reported defects

1. A courier sale currently requires a customer even when no customer debt exists.
2. A courier sale with money collected by the courier does not reliably appear in courier settlement until the order state is updated manually.
3. The application opens the quick-sale flow by default, while the advanced-sale flow is the required primary workflow.

## Current evidence

- The advanced payment UI describes courier-entered money as custody held by the courier.
- The settlement screen only includes orders in `delivered_full` or `delivered_partial` state.
- The default navigation actions currently open `sale_quick`.
- Historical database constraints and RPC validation require a customer for all courier orders, even when no debt exists.

## Approved business interpretation proposed for design

### Customer requirement

- Direct sale, fully paid: customer optional.
- Direct sale with remaining debt: customer required.
- Courier order still pending delivery: customer optional.
- Courier delivered and fully collected: customer optional.
- Courier delivered with partial or zero collection that creates customer debt: customer required.

### Courier custody and settlement

- Money explicitly recorded as already collected by the courier must be stored as `collected_by_courier`, not as store cash.
- A fully collected courier sale must enter `delivered_full` and appear immediately in settlement.
- A partially collected courier sale must enter `delivered_partial`, appear in settlement for the collected amount, and create customer debt only for the remainder.
- A pending courier delivery must remain outside settlement until its delivery outcome is recorded.
- Delivered remains distinct from settled.

### Sale interface

- Advanced sale becomes the primary/default flow from desktop, mobile navigation, and post-sale “new sale”.
- Quick sale remains available only as an explicit secondary shortcut for direct, fully paid cash sales.
- When courier delivery is selected, the payment section must use courier-specific language and states instead of the generic direct-sale labels.

## Required design before implementation

1. Confirm the effective latest definitions of:
   - `create_sale_with_items`
   - `update_courier_order_state`
   - courier/customer CHECK constraints
2. Define the state mapping at sale creation:
   - pending
   - delivered_full
   - delivered_partial
3. Define when customer selection becomes mandatory.
4. Define backward compatibility for existing courier orders.
5. Add a forward-only migration; do not edit applied migrations.
6. Update UI and navigation in a separate focused implementation PR.

## Mandatory tests

- Courier pending sale without customer succeeds and stays outside settlement.
- Courier fully collected sale without customer succeeds, creates custody, and appears immediately in settlement.
- Courier partial collection without customer is rejected.
- Courier partial collection with customer succeeds; collected portion is custody and remainder is customer debt.
- No courier sale creates a payment row before settlement.
- Settlement moves only stored courier custody into store receipts.
- Existing T1–T15 remain green.
- Mobile and desktop default sale actions open advanced sale.
- Quick sale remains direct, cash, fully paid, and customer-free.

## Out of scope

- Employee accounts.
- Courier employee authentication.
- Payroll, commissions, GPS, or attendance.
- Financial idempotency beyond preserving compatibility with the planned `FIN-IDEM-001` change.
- General application refactoring.
