# Security boundary

Proposed view uses security_invoker=true so authenticated queries use base-table privileges and RLS, including monjez_live_actor restrictive policy. No SECURITY DEFINER helper, tenant-policy replacement or new write RPC.

Explicitly REVOKE ALL on new view from PUBLIC/anon/authenticated, then GRANT SELECT to authenticated only. A simple view may be automatically updatable; computed columns alone do not make its base columns unwritable. Verify view write privileges and actual INSERT/UPDATE/DELETE refusals, plus catalog reloptions/ACLs and exact active-own/foreign/inactive/anon row visibility. Default future-object grants must not silently widen access. Test actual Data API exposure/cache behavior on the isolated project, with no remote fallback.

Current base owner direct DML is unchanged and must not be advertised as RPC-only. Admin cross-tenant RPC remains separately guarded and unchanged; do not grant its scope through the new tenant view. Service-role positive checks do not substitute for authenticated RLS evidence. Existing source/credential/publication/egress guards and all financial assertions remain.
