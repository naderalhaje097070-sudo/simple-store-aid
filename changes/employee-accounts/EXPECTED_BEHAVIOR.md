# Expected Behavior

This document normalizes the product intent from issue #16. It does not select the final data model or authorize implementation.

## Owner

The owner must be able to:

- Create or initiate an employee account through the approved authentication mechanism.
- Link an authenticated identity to a tenant-scoped employee or courier record.
- Assign and reassign orders.
- View all tenant orders, debts, custody, settlements, and employee-account states.
- Disable employee access without deleting financial or audit history.
- Complete and approve settlement through an owner-authorized financial transaction.

The owner must not be able to bypass financial invariants merely because the actor has the owner role.

## Employee

An enabled employee must be able to:

- Sign in with a personal account.
- Access only the employee workflow intended for the role.
- View only orders assigned to the employee.
- View only customer and order-item fields required to execute those assignments.
- View only personal unsettled custody and personal settlement-request history.
- Record only approved order-state transitions for an assigned order.
- Submit a settlement request without approving or posting the settlement.

An employee must not be able to:

- Read another employee's orders or custody.
- Read another tenant's data.
- Read products, profits, expenses, payments, day closes, subscription data, tenant billing metadata, or administrative audit data unless a future approved role explicitly requires it.
- Create or alter sales, payments, settlement postings, tenant membership, role, disabled state, or assignment through generic table access.
- Repeat or reverse a delivery result in a way that rewrites recorded custody without an approved owner correction workflow.
- Approve the employee's own settlement.

## Assignment

Required behavior:

- Each assigned order has one unambiguous current employee or courier assignment source.
- Reassignment removes the order from the previous employee's active view and adds it to the new employee's view.
- Reassignment must not rewrite historical financial events, actor audit data, or already recorded custody.
- Cross-employee reads and writes are denied by the server and database.

The final assignment model remains undecided between:

- Reusing `orders.courier_id` with a one-to-one authenticated courier link.
- Adding `assigned_user_id`.
- Introducing a dedicated assignment model.

This decision is deferred to Change Gates 2 and 3.

## Delivery state and collection

The allowed employee transitions must be explicit and one-way unless an owner-only correction contract is approved.

Expected outcomes include:

- Delivered with full collection.
- Delivered with partial collection.
- Delivered without collection.
- Returned.

Required invariants:

- Collected amount is non-negative and cannot exceed the order total.
- Delivery state cannot be replayed to reduce or replace previously recorded custody.
- Delivered does not mean settled.
- Employee collection updates custody only; it does not increase `paid` or create a payment row.
- Returned orders create no debt or custody and restore stock only through the approved return transaction.

## Settlement

- The employee may request settlement.
- The request is not a financial posting.
- The owner performs settlement through the existing authorized financial boundary.
- The owner may approve a request only after the financial settlement exists and matches the relevant custody.
- Duplicate requests and duplicate approvals must not double-post cash.
- Concurrent settlement attempts must be safe.

## Disable, unlink, and history

- Disabled employees are denied server-side and at the database/RPC boundary.
- Disabling or unlinking must not strand unsettled custody.
- A record that has represented an authenticated employee with order, custody, settlement, or audit history must not be hard-deleted.
- Historical actor and assignment references remain readable to authorized owners after account disable or unlink.

## Audit

Sensitive operations must record the authenticated actor and affected tenant/resource, including:

- Account link, disable, enable, and unlink.
- Assignment and reassignment.
- Employee delivery-state update.
- Collection amount update.
- Settlement request.
- Owner settlement and request approval or rejection.
- Approved correction or reversal.

## Acceptance baseline

At minimum, verification requires:

- Owner.
- Employee A.
- Employee B.
- Disabled employee.
- A user from another tenant.
- Assigned and unassigned orders.
- Full, partial, zero collection, and return outcomes.
- Duplicate, retry, concurrent, and illegal-transition scenarios.
- Direct RPC and direct table/RLS attempts, not only UI behavior.
