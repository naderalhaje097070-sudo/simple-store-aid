# Security impact

# C5-RESTORE-01 intake — 4 November 2026

Gate0 authorized by owner's «استمر» and canonical plan next step; claim55/6624766893, sole implementer root. Base be0f128f82e23da094ddce56d3f06dabef018dc9. Existing integration branch; main220fc206 and five original drafts unchanged. Type: isolated test/CI/admission only. Risk: moderate harness privileges and private logical archive; no product/schema contract change. No blocking owner input.

Goal: prove local nonempty logical backup→separate database restore preserves stored data, schema/privileges/RLS and collection idempotency. Reuse existing fresh/upgrade C5 financial/browser seed. Baseline actual a52ee17d passed C5/G0/G1/B1; restore not previously executed. No defect or production-recovery claim is assumed.

Acceptance: exact source admission before credentials; full pg_dump custom archive using the database container's matching tool version; restore into a newly created separate fixed-name DB using pg_restore --exit-on-error, never replace source; compare all public/private/Auth/migration relation rows and function/policy/owner/ACL metadata; replay an existing collection key under restored authenticated SQL-role claims with no mutation; deny foreign/payload conflict atomically; allow genuinely new20payment; originalDB unchanged; archive private0600 and removed in finally; publication guards/cleanup/zero-egress remain required. Inherited C5 assertions remain intact.

Boundaries: logical DB restore on same isolated cluster/roles, not managed backups, PITR, separate-host role recovery, restored HTTP/Auth services or full-app financial journey. Docker orchestration uses runner privilege as existing local stack setup; SQL auth tests use actual isolated token claims but do not verify JWT signature. No production data/secrets, remote backup upload, originalDB deletion, applied migration changes, merge/deploy/cost/PRclosure.

Source scope: one minimal capture dispatch plus four added test/CI files and committed delta manifest. Prior manifests/verifiers, app/SQL/dependencies unchanged. Nineteen negative source controls adapted from the existing guard passed locally; actual restore requires hosted Docker. Official Postgres pg_dump/pg_restore docs and current Supabase changelog checked; pinned CLI2.101.0/runtime preserved. Rollback: stop/remove disposable stack and private archive; revert test-only delta by new commit if needed.


Restore ownership requires the existing isolated supabase_admin LOGIN superuser, attested from pg_roles before use. Only pg_restore connects with that role; application replay/denial remains authenticated SQL-role context. No new grants, ownership edits, authentication bypass or production operation. Fail-fast restore and exact original/restored owners/ACL/RLS comparisons remain mandatory. Raw dump/private diagnostics never published.
