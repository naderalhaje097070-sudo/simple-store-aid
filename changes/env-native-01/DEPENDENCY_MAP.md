# Source dependency map — not an effective database catalog

source-inventory.json pins41 migration blobs and records67 function definitions,
83 policy creations,27 policy drops,199 privilege statements,4 function drops and
73 application discovery sites. Includes historical/dynamic declarations, table-call
lexical false positives and replaced overloads; do not implement from event counts.
Captured generator: inventory-generator.py. It requires the pinned tree and source
snapshot inputs described in VERIFICATION.md. pg_catalog reconciliation remains mandatory.

| Path / boundary | Dependencies and required coverage |
| --- | --- |
| 20260626142422… initial tenancy | tenants owner UID OR tenant helper; profile own UID; roles tenant helper. Direct UID policies need a separate mandatory guard. |
| current_tenant_id | profiles.id=auth.uid; feeds tenant table policies, timezone, summaries, onboarding and financial RPC guards. |
| has_role / has_owner_role / has_staff_or_owner_role | user_roles lookups; preserve tenant/role semantics and direct helper EXECUTE permissions. |
| _assert_staff / _assert_owner | tenant helper + role helper. Sale, debt collection, settlement, state/return, close_day and safe deletes flow through these. |
| is_platform_admin / _assert_platform_admin | platform_admins membership; privileged platform health/audit RPCs bypass RLS and require live actor guard. |
| get_tenant_today_estimate | current tenant + _assert_staff + timezone; application and MCP summary caller. Must explicitly deny disabled actor, not report zeros. |
| tenant_has_active_subscription / tenant_today | Parameterized helpers not necessarily caller-authorizing; reconcile EXECUTE and definer callers before deciding scope. |
| run_security_scan | Service-role OR platform-admin path; preserve trusted job operation while rejecting disabled authenticated admin. |
| Email queue functions | Service-role grants and historical dropped overloads; excluded from end-user lifecycle changes unless catalog proves a reachable route. |
| src/lib/db.ts | Direct table access and existing financial RPC adapters; no parallel financial implementation. |
| src/lib/mcp/tools/* | User-token table reads and summary RPC; direct MCP testing remains missing. |
| src/integrations/supabase/auth-middleware.ts | Generated JWT getClaims middleware; no consuming protected serverFn discovered in this scoped source. Do not edit generated files or claim live handler bypass without a caller. |
| src/routes/_authenticated/route.tsx | Browser-only getUser navigation guard; SSR beforeLoad returns early. Database enforcement cannot depend on this redirect. |

Grant changes are chronological: early helper revocations were restored in
20260626225100… because policies need EXECUTE. Preserve final minimal grants; don't
repeat an earlier revocation as a fix. __test_force_delete_e2e_order is historical
and dropped by later migrations; never restore a public cleanup RPC. RLS policies
are permissive unless declared restrictive; adding another permissive policy can
leave the existing owner OR path available. SECURITY DEFINER bypasses table RLS.

Before implementation export sanitized catalog definitions, policy expressions,
prosecdef/proconfig, identity arguments, table/function grants and enabled RLS for
public plus exposed schemas. Resolve every authenticated reachable function and
every direct-UID policy; classify triggers/internal/service jobs separately.
