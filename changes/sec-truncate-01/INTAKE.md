# SEC-TRUNCATE-01 — approved bounded implementation intake

Owner command2026-10-13 authorizes planning task #55/6139631421; sole implementation
claim6144887293. Rechecked main43d6edbccb66fb06ce0fcb93734ad59532d1aeae, baseDraft
PR66/9d30064d0d42667bf4b1de6469c319e625b9f33d, all open/recent PRs/branches/claims.
No existing truncate candidate or competing implementation found. PR49/50 patches
contain no TRUNCATE/default-ACL correction; no duplicate migration is introduced.

Gate0 approval is the owner's explicit current command and the planning scope.
Sensitive security/database change, one outcome: remove unused client TRUNCATE while
retaining all data, other rights, service/owner/maintenance and provider objects.
No financial contract, closure/ban/delete/ownership or nonempty financial fixture work.

## Baseline/root cause and dependencies (Gates1–2)

Reuse PR66 immutable actual catalog:22app public tables, ownerspostgres, authenticated
directTRUNCATE21 (tenant_counters exception); anon/PUBLIC no observedTRUNCATE. There
is no client inheritance path to owner/service privileges in that catalog. postgres
public table defaultACL grants authenticatedTRUNCATE; postgres global client table
defaultgrant absent. supabase_admin/public and all auth/storage defaults are separate,
not modified by this correction. Current migration creatorpostgres is verified live.

119immutable app/server sources fetched: only CSS `truncate` classes match the word;
no application SQL/TRUNCATE/default-grant caller found.43migration chain has no SQL
TRUNCATE command; prior anon defaultREVOKEs leave authenticated untouched. Existing
maintenance/testing uses trusted owner/service identities or disposable CLI stacks;
no ordinary-clientTRUNCATE requirement identified. This is privilege excess, not a
proved API exploit or production incident. Future explicit broadGRANTs remain outside
default protection and must be reviewed in future changes.

PostgreSQL17 default privileges are current-creator specific; schema defaults add to
global defaults. A schemaREVOKE cannot defeat global/inherited grants. Primary source:
https://www.postgresql.org/docs/17/sql-alterdefaultprivileges.html . Existing table rights
and ownership: https://www.postgresql.org/docs/17/ddl-priv.html . Supabase changelog
reviewed; pinned CLI2.101.0/runtime stay unchanged, no adoption of new features.

## Design/compatibility (Gate3)

One CLI-generated forward migration, exact REVOKE_TRUNCATE.sql content: explicit22
public app table list; REVOKE TRUNCATE only fromanon/authenticated/PUBLIC; ALTERDEFAULT
FORROLEpostgres INSCHEMApublic REVOKE TRUNCATE only. Atomic transaction; fail preflight
on unexpected creator or global/inherited client table defaultTRUNCATE. No global
default fix, auth/storage/provider-role/membership/owner change, REVOKEALL/CASCADE,
compensatory broadGRANT, API/function/RLS/FK/trigger/index change or row operation.
If the effective denial needs broader authority, retain failure and stop.

## Safety net and CI strategy (Gate4)

Focused15offline tests cover missing matrix, inherited/PUBLIC permission, service/owner
or unrelatedright change, provider/globaldefault mutation, identity switch, SQL scope
and destructive statement. An initial missing-delimiter IndexError was corrected before
publication; incomplete source must fail with HarnessFailure, not be accepted.

Existing CLI temporary setup, environment guard, UID network barrier, readonly catalog,
public22 snapshots, credential quarantine andcleanup are reused without edits. Dedicated
push workflow onthis branch, before creatingPR: first generate filename using CLI's
migrationnew (no DB), then commit exact generated migration and run fresh44/upgrade43→44
plus unchanged Qualitysteps (only BASE_SHA fixed toPR66 for push). No duplicative fixture
system, destructive statement, identity switch or historical lifecycle suite.

Default proof: currentpostgres creates one fixed emptypublictable withinBEGIN/ROLLBACK;
no data insertion/drop/delete/truncate. Confirm absence afterward, samecreator/session/
owner and all-role rights. Upgrade measures actualbefore43 baseline andafter44; compare
all-role table matrices/expanded ACL/defaultACL, schema digests/data invariants. All
nonclient and nonTRUNCATE rights, provider ACLs/functions/RLS/FKs/triggers unchanged.
Fresh44 compares relevant baseline and creator/public default semantics. Capture
MAINTAIN too forPG17. Proof is catalog rights, not executed destructive permissions.

Migration glob would trigger old lifecycle workflows onPR. Do not openPR until live
push evidence/review complete. Publish final additive docs/state[skip ci], then open
Draft overPR66; original runnable blobs/migration remain exact. Only dedicatedpush
workflow runs; oldworkflows unchanged. CopiedQualityjob executes exact existing13step
sequence; required actualresults are separately recorded, not skipped-as-green or a
mergegate waiver. Final check status must be stated honestly.

## Acceptance/rollback/stopping

Fresh and upgrade agree: clientsTRUNCATE=false on22tables; no directPUBLIC or inherited
client right. Defaults protectpostgres-created futurepublictables only; preserve all
othercreator/schema/objectdefaultACL and futuretable nonTRUNCATE/service/owner rights.
All43old migrations immutable; only44forward patch. App22fingerprints stable, original
finance7empty, nofixtures, scopednetwork/secrets/cleanup pass. Independent sensitive
review onsource/evidence with exact offline/live replay disclosure. Actual CI/artifact
IDs/source/version/remainingcoverage/failedreceipts are reported atclosure.

Rollback is NOT automatic regrant of clientTRUNCATE. Keep unmerged candidate inactive;
if later deployed with authorization, use an independently justified forward corrective
migration preserving client denial. No production restore/historyrewrite. Temporary
stackstop--no-backup; test objectROLLBACK. No merge/deploy/cost/production access.
closure_verified=false; integration_accepted=false. Stop afterDraft and handoff; ONE NEXT
is planning's bounded closure design/fixture intake after reviewing this dependency.
