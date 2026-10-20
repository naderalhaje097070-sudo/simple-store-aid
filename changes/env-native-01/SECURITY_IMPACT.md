# Authorization matrix and risk

High candidate: a banned owner retains own-tenant access with preissued JWT.
Confirmed historical metadata path; broader RPC/financial/admin impact is source
reachability requiring runtime reproduction, not an observed cross-tenant breach.

| Actor | API/RLS | Privileged RPC / MCP | History |
| --- | --- | --- | --- |
| Active owner A/B | Existing own-tenant permissions; foreign tenant denied | Existing role/tenant/resource constraints | Preserved |
| Active staff A/B fixtures | Only current schema-authorized scope; no new employee features | Preserve current staff/owner distinctions | Preserved |
| Banned owner or staff, old JWT | No protected rows or mutation | Explicit denial before work, no summary pretending zero | Preserved |
| Banned admin, old JWT | No protected admin data | No admin RPC execution | Preserved |
| Anonymous / missing actor / deleted identity | Denied | Denied | No mutation |
| Trusted internal service job | Only existing documented privilege | Explicit service-only path; no widening | Preserved |

Audit event: retain existing financial/audit history; Auth administrative ban audit
and additional app audit requirements must be verified, not invented as present.
No public lifecycle-mutating RPC, client disabled field, role escalation or exposure
of auth.users is proposed. Private helper may inspect only current actor and return
boolean, with safe search_path and explicit grants. Direct server errors5xx and
timeouts are harness failures, not authorized denial. Missing provider state fails
closed. Independent review outcome: pending; continuing-agent analysis is not approval.
