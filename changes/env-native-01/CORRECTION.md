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

# ENV-NATIVE-01 — authorized bounded correction

Owner explicitly instructed «قم بذلك» after the concrete database/RPC correction,
isolated final tests and independent-review scope. Gate0 approval is satisfied;
merge/deploy/cost/core financial-contract approval is not implied. Sole claim in #55.
Baseline PR58 b8fd5e95ab1f6eee07bb6198da3169cd46916962. Main is unchanged.
Recorded baseline:57 controls PASS /10 named denial failures, CLI2.101.0,
PostgreSQL17.6,41 migrations,40 public functions/58 policies/432 grants.

## Design before implementation

Use private caller-bound predicate on auth.users(id, banned_until, deleted_at).
Missing/deleted identity or future ban denies. No user/JWT metadata authorizes.
Private functions have empty search_path, no public/anonymous execute or CREATE;
authenticated gets only schema USAGE and two caller-bound function EXECUTEs.
No client SELECT on Auth tables. Role/tenant arguments cannot substitute caller ID.

Add22 RESTRICTIVE authenticated ALL policies (USING and WITH CHECK) AND existing58
policies, covering the owner direct-UID arm. Preserve every prior policy and grant.
Guard all30 authenticated-executable public SECURITY DEFINER functions and the
three internal assertion helpers before body execution. SQL scalar helpers become
PL/pgSQL scalar returns around their exact original query. Existing PL/pgSQL bodies
gain one guard at outer BEGIN; no calculation/state/transaction rewrite. Generator
is pinned to the archived effective catalog digest and fails on unexpected shape.
The migration is static reviewable SQL; no dynamic public RPC/cleanup entry point.

The assertion permits actual service_role/supabase_admin connection roles and
trusted direct postgres/supabase_admin sessions with role=none; it never tests the
definer's current_user or user-editable JWT role. Preserve trusted worker paths.
Existing active-user queue/scanner authorization scope is NOT newly approved;
their current broad grants/definer-role checks require separate security review.

## Data, API, migration and rollback impact

One additive forward-only migration, no applied-file edits, rows/indexes/backfill,
Auth schema changes or billing/config/dependency/app changes. Public RPC signatures,
returns, ACLs and active-account calculations remain. Inactive RPCs return42501 /
account_inactive, rather than healthy-zero or generic server error. Direct RLS may
return empty rows or42501. Auth ban expiry restores live-account eligibility;
existing JWT lifetime/session semantics remain, no global session-revocation claim.

Private lookup uses Auth PK; per-statement policy initplan. Statement snapshots
deny requests starting after committed ban; no retroactive rollback of in-flight
requests/repeatable-read transactions. Record timing and query plan on disposable
fixtures. Policy DDL takes table locks; release requires reviewed rollout/backup
and human approval. No bypass feature flag. Unexposed private schema is not API.
Rollback artifact restores exact33 prior function definitions and drops only22 new
policies/private helpers; never changes rows. It reopens the known risk and requires
human approval; isolated roundtrip only. No automatic/production fallback.

## Safety net and acceptance limits

Retain baseline workflow/oracle unchanged; add separate correction workflow/probe.
Fresh42-chain and representative41→42 upgrade, four dummy actors/two tenants;
ten original targets must deny while active own/foreign boundaries remain correct.
Check all22 table reads, all30 RPCs for banned owner/staff, nonfinancial writes,
caller spoofing, missing identity, ban expiry/unban, trusted service and private
ACLs, catalog preservation and rollback roundtrip. Blocked financial RPC attempts
use dummy parameters and require42501/account_inactive before any financial work;
no active financial write suite or finance fixtures permitted. Zero finance rows
and before/after public history hashes required. Active read-only admin control
uses existing platform_admin fixture membership; no admin feature added.

MCP transport, actual deleted-account history, expired signed JWT, nonempty financial
history, concurrent transactions/full financial effects and independent review
remain unverified. Gate6 cannot be self-approved. Candidate never equals main fix.
ONE NEXT after final evidence: independent adversarial review and remaining isolation
coverage, before financial writes. No merge/deploy in this batch.
