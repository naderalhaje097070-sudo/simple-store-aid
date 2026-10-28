# Compatibility

All application endpoints and RPC/tool signatures unchanged.
GET own tenants, POST get_tenant_today_estimate, HTTP /mcp protocol are existing read-only paths.
Expired REST/RPC require401/PGRST303/exact JWT expired. MCP requires401/exact unauthorized+invalid_token
challenge plus supporting same-token crypto/source/no-downstream evidence, not account_inactive.
PKCE/session issuance via supported provider flows only; expiry of access token is distinct from session revocation.

