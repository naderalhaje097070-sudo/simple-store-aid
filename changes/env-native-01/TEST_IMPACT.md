# Safety net execution specification

Offline code in tests/account-lifecycle audits the existing archive: named login,
active-own-tenant and ban controls, status types, counters and limitations. Its
regression assertion rejects the historical pre-ban access. It cannot execute,
prove or approve live RLS/RPC behavior. No application suite replaced or weakened.

After approval, build a fresh loopback-only disposable runner using existing isolation
preflight/guard. Verify exact tracked source, empty initial Auth/tenant/finance tables,
full migrations and effective grants. Dummy credentials only in memory; no tokens in
reports. Seed owner role through existing tenant trigger; verify one role instead of
duplicate insert. Any fixture/startup/counter/source failure is harness failure.

| ID | Required live assertion |
| --- | --- |
| L01 | Active owners A/B authenticate and read own metadata with real JWTs. |
| L02 | Both owners cannot read/update foreign tenant; stored names/ownership unchanged. |
| L03 | Owner/staff cannot rewrite protected tenant/role/disabled/assignment fields. |
| L04 | Issue B access/refresh tokens, prove own reads, then ban B through Auth admin. |
| L05 | B new login denied; refresh denied with provider-specific validated reason. |
| L06 | Exact pre-ban token cannot read own tenants/profiles/user_roles or each protected table. |
| L07 | Same token cannot insert/update nonfinancial metadata; trusted re-read proves no effect. |
| L08 | Direct SQL authenticated claims + RLS denies same actor; report separately from real HTTP JWT. |
| L09 | Read-only get_tenant_today_estimate denies B rather than healthy-zero output. |
| L10 | MCP table and summary paths deny same B token. |
| L11 | Disabled admin cannot execute platform read RPCs; active admin positive control. |
| L12 | Two existing-schema staff fixtures retain role rules and deny disabled staff; assignment-feature claims require actual approved assignment contract. |
| L13 | Anonymous, missing/deleted identity and expired token fail closed;5xx/timeouts never pass. |
| L14 | A remains active after B ban; no blanket deny mistaken for fix. |
| L15 | Trusted before/after hashes preserve tenant/profile/role/audit/history content and fixture financial counts. |

Gate4 baseline must reproduce L06 as exact expected-red on unchanged baseline with
clean fixtures; then final source must make it green while L01/L14 stay green. Existing
archive's2 seed conflicts block full baseline acceptance; don't use this oracle as
substitute. Do not invoke successful sale/settlement/return/day-close/rollback financial
write suites until isolation is independently accepted. Thereafter separately test
guarded financial RPCs, concurrent disable vs request, retries and transaction atomicity
on disposable fixtures. Current in-flight requests need explicit measured semantics;
proposed denial is for requests starting after committed ban, not retroactive rollback.

No new cloud project, production target or cleanup RPC. Initial/final aggregates,
source SHA, CLI/Auth/PostgREST/Postgres/browser versions, sanitized assertions and stop
receipt mandatory. Independent reviewer must reproduce negative and active controls.
