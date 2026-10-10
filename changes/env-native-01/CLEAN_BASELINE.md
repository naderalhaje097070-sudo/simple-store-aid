# ENV-NATIVE-01 — clean focused baseline execution

Approval: owner «انت المسؤول» follows the concrete PR57 intake approval request.
This authorizes routine Gates0–3 / L01–L15 isolated scope. Merge/deployment/new
cost/core financial-contract approval is not implied. Sole execution claim is in #55.

Baseline: PR57 fd2bed16a051a6d4de44f8b97c1a5ba9a36e50fc.
Main: 43d6edbccb66fb06ce0fcb93734ad59532d1aeae, untouched.
Branch: test/env-native-01-clean-baseline-2026-10-11. Status: test/workflow candidate, hosted run pending.

## Executable scope

Fresh GitHub-hosted Docker/Supabase stack, CLI2.101.0 and all41 exact source
migrations. Temporary CLI config, never the repository's project config.
Four dummy actors, two tenants, owner roles verified exactly once, staff roles
seeded once. Real password access/refresh tokens. Loopback-only HTTP and psql,
existing guard invoked before credential/file/network access; no proxy or redirects.
No financial fixtures or financial write RPCs. No cleanup RPC or public routes.

Checks: empty baseline; exact migration versions/hashes; effective public catalog
(function definitions, ACLs, policies/grants and Auth ban column type); active own
tenant and foreign read/update/reassignment denial; anonymous denial; read-only
tenant summary; owner/staff Auth ban and login/refresh denial; preissued JWT own
tenant/profile/roles/summary and direct SQL RLS; unaffected active tenant; exact
fixture counts; public row checksums retained; zero financial rows.

The runner succeeds only when all controls pass and the specifically named
banned owner old-JWT tenant read reproduces200 / one own row. This is
ENV_NATIVE_01_CLEAN_BASELINE_EXPECTED_RED, not security-fix success.
Infrastructure errors, generic500/non-JSON/redirects, incomplete controls,
duplicate checks or absence of the named regression fail the harness.
Sanitized result/catalog/progress artifacts expire in7 days; final summaries
and exact run/source identity must be archived in GitHub before closing the batch.
Disposable keys/status files and raw setup logs are not artifacts; stack stops
with no backup. No cloud project, Vercel resource, provider upgrade or billing change.

## Local verification

2026-10-11 Africa/Tripoli: five new unittest methods PASS. Denial classifier covers
nine cases; Auth classifier six; named-baseline rejection eight invalid scenarios.
Guard test proves rejection before status-file/network access; redirect test
proves external redirects are not followed. These are offline harness tests.
No historical test rerun and no local database execution.

## Hosted results and limitations

Pending actual GitHub execution; do not infer results from source or local units.
Not full L01–L15 acceptance: MCP transport, admin RPC, protected-field role/disabled
mass assignment, nonempty finance/audit history, deleted/expired-token cases,
postban writes, every table/RPC, concurrency, upgrade/performance and independent
review are explicitly unverified. No enforcement migration is included.
A baseline run cannot unblock financial writes or establish Gate6 independent review.

Rollback: revert additive candidate commits. Production and main were not changed.
ONE NEXT: record the exact hosted result and reconcile effective catalog before
the minimal forward-only lifecycle enforcement correction.

