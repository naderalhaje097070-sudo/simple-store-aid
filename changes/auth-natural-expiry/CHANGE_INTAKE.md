# L13 natural provider token expiry — bounded test-only intake

Authorized by owner task and #55/6119851247; execution claim6119904934.
Base PR63 3cb0d82afe31eb2d81538fd7ae631c10fdfa0357; main43d6edbccb66fb06ce0fcb93734ad59532d1aeae.
One implementer, branch test/auth-natural-expiry-2026-10-12. Gate0 authorized within explicit task.
Goal: a genuine initially working unchanged B OAuth token naturally expires while fresh A/B still work.
Scope: real loopback HTTP REST/RPC/full Nitro/TanStack MCP, genuine PKCE and bounded real wait.
Risk: test harness identity/time/false-positive and credential evidence; production impact none.
No ban/delete/logout/revoke, token minting/exp/clock overrides, automatic refresh, financial writes,
application/auth-policy/proxy/dependency/migration changes, merge/deploy/cost/production/history rewriting.
Supported local CLI auth.jwt_expiry180 only in disposable config; verify actual signed exp-iat180.
Use source-inspected SDK/jose leeway0, Auth0, PostgREST30; wait to exp+35, compare monotonic/wall clocks.
Provider identity+cryptographic signature, exact own metadata/read-only summary, initialize/initialized/catalog
and4tools positive B; same B REST/RPC/initialize/4tools expired; fresh A same paths; new B same paths;
old B remains expired. Require known expired errors, signed identity, unchanged digest and active accounts/session.
22 public snapshots equal,7financeempty, UID/preload containment, no-leak/quarantine/cleanup all required.
Independent review and exact-source CI required; broader integration_accepted=false.
Expected acceptance named only "natural token expiry within tested scope". Block on unsupported contract
or actual application defect; propose separate smallest repair rather than modify app.

