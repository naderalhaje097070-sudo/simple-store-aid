# Impact — Gate 2

| Surface | Proposed effect and boundary |
| --- | --- |
| UI | Active owner behavior unchanged; forbidden API responses must remain errors, not healthy zero finance. No new lifecycle screen. |
| Direct API | Banned user loses own-tenant and own-profile access despite valid JWT; empty-row RLS denial must be proved with positive controls and stored-state checks. |
| Helpers / RPC | Guard caller lifecycle before data access in privileged entry points; preserve role, tenant and resource checks. |
| Database | New forward-only authorization migration only after approved catalog reconciliation; no history deletion/backfill. |
| Finance | Authorization may deny existing reads/writes; formulas, transactions and idempotency contracts unchanged. Financial writes stay gated. |
| MCP | Three table reads use user token/RLS; today_summary calls privileged summary RPC. Issuer authentication alone is insufficient. |
| Jobs/email | Service-role queue functions and maintenance scanner need explicit role classification; no blanket deny of trusted jobs. |
| Performance | Indexed Auth user PK lookup per request/statement; measure query plans and representative policy reads, avoid per-row expensive lookups. |
| CI | New offline regression oracle is run explicitly; existing Quality does not automatically discover Python lifecycle tests. No workflow edit in this batch. |
| Deployment | Draft stack only. Fresh and representative prior-state migration proof and independent review precede human release decisions. |

No application/schema/RLS/RPC contracts changed in this preparation batch.
