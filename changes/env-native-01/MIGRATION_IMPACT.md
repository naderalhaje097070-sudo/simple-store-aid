# Forward-only migration proposal

No migration created or executed in this batch. After intake approval, use the
repository CLI's migration-new command to generate a filename; applied41 files remain
immutable. Add a private current-actor live-state helper (verify auth.users ban fields,
ban expiry semantics and Auth version). Missing identity denies; live ban denies.
No generic public authorization fields or auth-schema ownership changes.

Inspect all effective RLS policies before choosing restrictive authenticated guard
policies or tightening every relevant existing expression. Preserve active policies
and direct owner clauses. Separately guard privileged entry points that bypass RLS;
shared _assert helpers are useful but not proof all endpoints are covered. Privilege,
search_path and RPC caller tests are mandatory. No table grants on auth.users to clients.

DDL locks and policy/function invalidation require a small transaction and measured
prior-state upgrade; query-plan cost must be recorded. No indexes/backfill approved
yet. Full fresh41-migration chain plus new migration and representative upgrade test
required on disposable DB. Catalog differences must stop implementation, not be hidden.
