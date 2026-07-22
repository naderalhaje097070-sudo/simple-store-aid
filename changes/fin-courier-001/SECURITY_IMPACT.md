# FIN-COURIER-001 — Security Impact (Gate 2)

Status: Proposed target based on product-owner direction; pending formal Gate
approval.

## Authorization model — unchanged

- All affected write RPCs are `SECURITY DEFINER` and call `_assert_staff` /
  `_assert_owner` (`20260626155319_...4e.sql:37+`). `create_sale_with_items_v2`
  and the transition RPC inherit the same asserts; the adapter delegates.
- Platform health/report functions call `_assert_platform_admin` and log via
  `_log_platform_admin_action` — the PR-B changes keep those asserts and logging.
- Direct table writes remain revoked from `authenticated`
  (`20260627201534_...c879.sql:511-513`); `get_platform_system_health` checks that
  financial RPCs are not granted to `anon`/`PUBLIC`. New `_v2`/transition RPCs
  must follow the same grant pattern: `REVOKE ... FROM PUBLIC, anon; GRANT EXECUTE
  ... TO authenticated`.

## Tenant isolation — strengthened, not weakened

- Tenant is derived server-side via `current_tenant_id()` inside every RPC; no
  client-supplied tenant.
- **New validation:** the atomic transition RPC, when a `p_customer_id` is
  supplied, must confirm the customer is same-tenant
  (`WHERE id = p_customer_id AND tenant_id = current_tenant_id()`), rejecting
  cross-tenant or nonexistent customers (`customer_not_found` / `forbidden_tenant`).
  This closes a path where a debt could be attached to a foreign customer. Covered
  by tests D-T5/D-T6.
- `_v2` create path must apply the same same-tenant customer check as today
  (customers are already tenant-scoped by RLS on read; the write RPC must not
  trust an arbitrary `p_customer_id`).

## RLS — unchanged

- No RLS policy is added, dropped, or altered. Financial tables keep RLS enabled;
  reads stay tenant-scoped.

## Constraint change — no security effect

- Replacing the customer CHECK constraints is a data-integrity change, not an
  authorization change. It does not expose data across tenants.

## Grants / new objects

- New functions (`create_sale_with_items_v2`, transition RPC) must be created with
  `REVOKE ALL FROM PUBLIC, anon` and `GRANT EXECUTE TO authenticated`, matching the
  existing financial RPCs, so `get_platform_system_health` continues to report
  them Healthy.
- No new table, no new column, no new public/anon surface.

## Secrets / production

- No production data or secrets accessed. All verification on isolated
  environments. No change to auth providers, tokens, or edge functions.

## Residual risks

- If the transition RPC's same-tenant customer check is implemented incompletely,
  a cross-tenant customer attach is possible — explicitly tested (D-T5).
- If PR-B ships after PR-C, platform admins would see valid orders as Critical
  during the gap — an operational (not data) risk; PR ordering (B before C)
  mitigates it.
