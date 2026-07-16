# Current Behavior on `main`

## Authentication and routing

- Supabase Auth establishes the signed-in user.
- The authenticated layout reads `profiles.tenant_id`.
- A user without a tenant is redirected to `/onboarding`, except for the platform-admin route.
- A user with a tenant can continue to the normal application route.
- There is no role-specific redirect for `staff`.
- There is no `/employee` route and no `/employees` owner-management route in the generated route tree.

## Roles

- Generated Supabase types define `app_role` as `owner | staff`.
- The settings screen labels `owner` as صاحب المحل and `staff` as موظّف.
- README documentation is inconsistent and lists `owner`, `manager`, `cashier`, and `viewer`.
- The effective database role model must be treated as authoritative until the migration chain is inspected in Change Gate 2.

## Employee account lifecycle

- There is no approved owner workflow to invite, link, disable, or unlink an employee account.
- `profiles` contains tenant membership data but no `disabled_at` field in the generated types on `main`.
- `couriers` are operational delivery records, not authenticated user identities on `main`.
- No approved invariant currently preserves a courier record specifically because it was previously used as an authenticated employee identity.

## Assignment

- Delivery assignment is represented by `orders.courier_id` referencing `couriers.id`.
- There is no approved `assigned_user_id` field or separate assignment table.
- Reassignment behavior for authenticated employees is not specified on `main`.

## Orders and custody

Existing order data includes:

- `delivery`.
- `courier_id`.
- `courier_state`.
- `collected_by_courier`.
- `paid`.
- `status`.

Current financial invariants remain:

- Delivered does not mean settled.
- Courier-collected money remains custody until owner settlement.
- A returned order creates no customer debt or courier custody.
- Settlement is an owner-controlled financial operation.

## User interface

- The settings screen displays tenant name, business type, current role, tenant identifier, theme, and sign-out.
- The settings screen does not expose employee-account administration.
- There is no employee-specific assigned-order or personal-custody screen.

## Authorization baseline

- Existing tenant isolation and financial RPC behavior remain the approved baseline.
- No employee-assignment-level RLS contract is approved on `main`.
- UI visibility is not accepted as an authorization control.

## Baseline limitations

This document records repository behavior and generated contracts. It does not claim that every historical RLS policy or RPC has completed a new security audit; that work belongs to Change Gate 2.
