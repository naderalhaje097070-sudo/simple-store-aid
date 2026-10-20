## Forward compensation after isolated profile failure — 2026-10-11

Initial correction source `0c9689dd814e5ce8220d15ed5dcad6b0deb75efe`:
Quality347 passed, but focused run38092565324 failed in BOTH fresh/upgrade modes.
Fresh stopped after25 controls; upgrade after117. Neither is a green correction.
Raw sanitized progress/failure evidence is retained under evidence/correction-initial.

Candidate root cause: profiles' existing UPDATE check selects profiles; adding a
SELECT SubLink in its restrictive ALL policy triggers PostgreSQL17 recursive RLS
expansion. Verified source: postgres/postgres REL_17_STABLE rewriteHandler.c,
hasSubLinks / activeRIRs / ERRCODE_INVALID_OBJECT_DEFINITION. New live regression
must prove exact42P17 + profiles recursion, rather than assume the masked500 code.

Migration42 is immutable after isolated application. Add generated migration43,
20261010225012_avoid_profile_policy_sublink_recursion.sql, changing ONLY the new
profiles policy to the same direct private predicate. Preserve all58 prior policies.
Fresh43 and representative41→43 upgrade now required; no history rewrite/retry of
historical source. Upgrade/rollback apply both additive migrations. Add real active
profile edit, safe SQLSTATE-only diagnostics, lookup plan/runtime image/advisor
capability records. No5xx is permission success and no linked/cloud advisor fallback.
Exact final results are recorded in PR59 and #55; Gate6/broad isolation remain open.

Prior candidate descriptions below are retained chronological evidence.

---

# Correction verification record

Baseline PR58 b8fd5e95ab1f6eee07bb6198da3169cd46916962; named57 controls/10
regression failures and original effective catalog retained. No historical manual rerun.
Migration filename created by available official CLI2.120.0 migration-new command
(metadata/file only, no DB); test runtime remains pinned CLI2.101.0, no repo upgrade.

Local:5 new contract unittest methods PASS. They reject generic/5xx permission
errors, require all10 named regressions plus active/history controls, validate the
exact30 exposed RPC payload surface, reject a wrong catalog digest, and preserve
nested financial function body statements while injecting one outer guard only.
Python AST/YAML permissions/matrix/shell syntax and scoped whitespace pass.
Generator renders22 policies/33 guards with no financial formula changes.
Rollback is static, source-pinned and human-gated; never production-executed.

Hosted final exact SHA, job steps, fresh/upgrade results and sanitized JSON are
recorded in this batch draft PR and issue #55 after actual execution. Their source
SHA is authoritative; pending/failing jobs must never be labeled pass. Each mode
uses independent Docker resources, four dummy actors/two tenants,42 versions,
zero active financial writes/finance fixtures, cleanup stop/key removal/no backup.
Uploaded artifacts expire7 days; summarized raw result JSON will be copied into
GitHub PR comments for durable source-linked evidence without another code commit.

An expected-green candidate requires all its controls, all30 RPC denials for both
banned actors,22 table checks per actor,10 original regressions, active accounts,
nonfinancial write denial, original58 policies/40 ACLs/432 grants, private security,
expiry/unban/missing caller/spoof/trusted-service, rollback exact40 definitions and
reapply. Upgrade mode also preserves existing fixture rows/committed bans while
CLI applies migration42 over exact41. Harness failures are not permission proof.

Independent review NOT performed by implementer. Not full L01–L15 acceptance,
financial isolation or merge readiness. MCP transport, actual deleted account,
expired signed JWT, nonempty financial history, active financial effects,
concurrent disable and production-scale performance remain unverified.
Known prior queue/scanner active-caller authorization risks remain separate.
