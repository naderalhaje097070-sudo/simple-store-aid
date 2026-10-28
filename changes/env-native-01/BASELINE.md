# Baseline and reproduction — Gate 1

Prior actually executed disposable non-root runner used source
84c3444fcdf5fa2825809192cda5b15561c950cf, experimental CLI2.120.0, PostgreSQL/Auth/
PostgREST and 41 fresh migrations. It was stopped; no credentials/snapshot retained.
Repository Docker/CLI2.101.0 pins are unchanged. See PR54's NATIVE_RUNNER_VERIFICATION.md.

Recorded reproduction: create dummy B and tenant; real password login returns200;
pre-ban JWT reads exactly one own tenant; admin ban returns200; new login returns400;
same preissued JWT reads own tenant via PostgREST200. No foreign tenant exposure was
observed. Archive: ../primary-env-001/native-runner/auth-tenant-probe.json, Git blob
3d46821edf9fdeae9f4f9b8299904c107bc3b7a9. Keep 22 passes and2 owner-role seed409
conflicts; the tenant trigger already created those roles. Do not relabel as24 passes.

Current candidate source: all41 migration blobs, app/test/governance source checked
against the PR56 tree. 195 selected local source blobs matched; AGENTS was read from
GitHub because the older local copy differs. No code is promoted from another repo.
Original lifecycle report is historical evidence, not a fresh run on PR56.

Source explains the observed path: tenants SELECT permits owner_user_id=auth.uid()
OR current_tenant_id(); current_tenant_id reads profiles by auth.uid without live
ban state. Role/admin helpers likewise have no account-state predicate. Existing
profile tenant-reassignment guard must remain. A current_tenant_id-only correction
leaves the direct owner OR arm open. UI route getUser is not direct API enforcement.

Official docs checked 2026-10-10: https://supabase.com/docs/guides/auth/signout
documents unexpired access-token persistence; https://supabase.com/docs/guides/auth/
server-side/advanced-guide distinguishes JWT validation from current session lookup;
https://supabase.com/docs/guides/auth/sessions describes optional session_id validation.
These support the risk model, not a claim that every banning/session API behaves
identically on the pinned stack. Exact ban/refresh semantics still require live tests.
Changelog.md fetch failed content-type handling; HTML changelog was checked instead,
including Sep25 Postgres15.19/17.11 breaking changes. No provider upgrade is proposed;
no listed custom-operator/ltree/legacy-cipher declarations found in scoped migrations.

Current scratch runtime is UID0; docker/podman/psql/postgres/bun not on PATH. No DB
bootstrap was retried and no cloud target touched. Existing Quality342 attempt2 and
343 success remain their own exact-head evidence; historical suites were not rerun.
