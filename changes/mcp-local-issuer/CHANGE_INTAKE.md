# MCP local issuer repair — intake (2026-10-11)

Authorized by owner bounded instruction and issue55/HQ6109138304; sole claim6109194766.
Base PR61/315751c46678fa18ffc35dae1e8d6e2cb9b30335, main43d6 unchanged.
Type: medium-risk authentication configuration defect in isolated local verification.
Goal: strict SDK authentication on approved local target, then active/ban/unaffected controls.
No financial, schema, dependency, production, merge/deploy/cost or history rewriting.

Baseline PR61 actual run38139406844: 0/8 active tools (500),24 guarded cloud discovery attempts; 22 setup controls passed. Ban/handshake were not executed. Preserve permanent raw receipt6109074795.

Blocking input: exact installed SDK0.20.1 OAuth/discovery/JWKS/HTTP/session contract.
Local git clone is denied by environment403; registry also403; no Bun/Docker executable.
Use existing authorized GitHub disposable runner; inspect installed source before selecting API.
No application fix has been applied. Next: source contract inspection and a failing regression.

Impact/callers under review: config resolver->vite injected public identity; server entry baked/runtime match before generated route; src/lib/mcp/index.ts->SDK auth; generated TanStack route->protocol; four tools->user bearer Supabase/RLS/summaryRPC. No admin client substitution.
Compatibility: retain direct approved production URL and authenticated audience.
Data: dummy tenants only; all seven finance tables remain empty;22 public hashes checked.
Rollback: close draft or additive revert after owner-controlled merge; no schema compensation.
Acceptance: red/green regression, strict signature/issuer/audience negatives, initialized protocol plus eight active/four banned/four unaffected calls, zero outbound escape, stored invariance and cleanup; independent review required before acceptance.
