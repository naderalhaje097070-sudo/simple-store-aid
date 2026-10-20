# Compatibility

Preserve existing public RPC names/signatures and financial return shapes for active
callers. No v2/idempotency adapter adoption here. Disabled actors intentionally lose
access previously allowed by stale JWT. RLS SELECT may return200 with empty rows;
that is accepted only after positive controls and explicit protected-row checks.
RPC must deny before business work; define stable authorization SQLSTATE/error mapping
in implementation design without leaking private Auth state. Never use500 as denial.
MCP must surface authorization error rather than successful empty financial summary.
Generated middleware/routes/types stay untouched; any necessary app-owned hook must
be traced to a real caller and tested. Service-only integrations require catalog
classification before guard changes. No session/JWT-expiry setting change is proposed.
