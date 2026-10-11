# Independent-review verification hardening — 2026-10-11

## Gate0 and authority

Owner explicitly «قم بذلك» approves the concrete followup to independent PR59
review5482207278 / execution-index comment6106344113. Sole implementer claim in
issue55. Active repository naderalhaje097070-sudo/simple-store-aid; base exact
fd95ad2e1966362719965ef282de1e2eb66cb070. Main43d6edbccb66fb06ce0fcb93734ad59532d1aeae
unchanged. Branch test/env-native-01-review-evidence-2026-10-11; candidate only.

Goal: close bounded E1/E2/E4 evidence defects and supply independent E3 live
controls. Medium risk because harness semantics matter; not an application or
authorization-contract implementation. No migration/app/dependency/provider
upgrade, financial formula/data/write, production/cost/merge/deploy change.

## Baseline and root cause

Prior Quality348 and focused201/203 pass on fd95 only. Independent review found
no introduced Critical/High code defect but remained Blocked pending missing
evidence. Retain all original raw reports and review findings; never relabel
the upgrade baseline41 advisor artifact as final43. No historical manual rerun.

E1: advisors preceded the probe that applies42+43 in upgrade mode. E2: first
stored snapshot followed active foreign mutations, so it could not prove their
no-effect window. E4: consumed rollback/catalog/inherited transport/guard paths
were absent from workflow filters. E3: independent reviewer did not execute live
controls, actual deleted-account and expired signed-token evidence was missing.

## Impact, dependencies and design (Gates1–3)

Only focused correction workflow/probe/unit tests, a separate independent oracle
and documentation change. Original41+2 migrations, baseline oracle, private guard,
public functions/grants/policies, rollback and source-pinned catalog are preserved.
Dependencies are the pinned CLI2.101.0, local Docker stack, psql, original safety
guard and actual Auth/PostgREST runtime. No implicit linked/project target.

E1 captures actual initial/final local advisor reports inside the probe, asserting
exact versions before each capture. Fresh initial43; upgrade initial41; both
final43. Provenance includes sourceSHA, phase, versions, raw SHA256 and severity
counts. Invalid/unknown/duplicate findings and ERROR fail closed; old warning keys
must remain unchanged across the roundtrip. Preserve raw ERROR evidence on failure.

E2 snapshots all22 public tables and expected tenant names/owner IDs/profile
tenant IDs BEFORE foreign attempts; trusted checks after every actor and after
the window prove no stored effect. HTTP assertions remain separate.

E4 includes every consumed rollback/catalog/base-probe/guard and independent-oracle
path. Existing quality/baseline workflows and tests are not weakened or disabled.

Independent reviewer owns separate expected assertions and execution receipt;
shared CorrectionProbe transport/safety/fixture plumbing is declared. Its oracle
uses separate four actors/two tenants and evidence directory after correction,
then checks active/foreign controls, committed ban owner/staff oldJWT table/summary/
RLS denial, unaffected active actor, real Auth-admin soft-delete of an UNBANNED
owner with deleted_at/history assertions, and valid locally signed expiredJWT.
The expiry pair uses the actual issued token's verified HS256 signature and local
status secret; a future twin positive control and tampered-signature negative
control distinguish expiry from invalid credentials. Fail closed on other key
contracts. Not a claim about naturally elapsed Auth-issued-token expiration.

Verified pinned contracts: Auth2.188.1 [admin DELETE](https://github.com/supabase/auth/blob/v2.188.1/internal/api/admin.go)
and [SoftDeleteUser](https://github.com/supabase/auth/blob/v2.188.1/internal/models/user.go),
CLI2.101.0 [private local status key](https://github.com/supabase/cli/blob/v2.101.0/apps/cli-go/internal/status/status.go),
PostgREST14.10 [303 expiry /301 signature errors](https://github.com/PostgREST/postgrest/blob/v14.10/src/PostgREST/Error.hs)
and [30-second expiry skew](https://github.com/PostgREST/postgrest/blob/v14.10/src/PostgREST/Auth/Jwt.hs).
Supabase changelog/docs checked; no provider/runtime upgrade proposed.

## Safety and verification (Gates4–6)

Eight implementer unit methods include ERROR/malformed advisor rejection, wrong
schema provenance refusal before CLI I/O and raw ERROR preservation. Reviewer
owns separate focused cryptographic/classifier checks. Python/YAML/shell/path
verification and source-diff preservation precede publication.

Run only the current focused fresh43/representative41-to43 workflow and automatic
checks on the new source, not the full historical workflow archive. Four original
actors plus four reviewer actors stay dummy-only; zero seven finance tables.
No public cleanup RPC, harddelete, real credentials or production fallback.
CLI status keys and JWT secrets stay memory/private transient status only; artifact
upload includes sanitized results/provenance, never raw status or setup logs.
Stop/key removal/no-backup receipts are mandatory.

After source audit, the independent reviewer initiates targeted replay of a current
focused job on finalSHA with fresh resources and inspects its actual result,
negative/positive controls and cleanup. Merely reading implementer output cannot
fulfill independent live execution. A separate reviewer verdict is required; the
implementer does not self-approve Gate6.

Final actual commands/source/jobs/counts/artifact digests/reviewer receipt are
recorded in the batch draft PR and issue55 after execution. Tests here can pass
without broad L01–L15 acceptance: MCP transport, harddelete/cascade history,
nonempty financial history, concurrent/in-flight transactions, active finance,
production-scale performance and prior active-user queue/scanner authorization
remain explicit open gates. Review success does not imply merge or release.

## Rollback and ONE NEXT

This test-only batch can be closed or additively reverted; no schema compensation
is applied by rollback of this batch. Existing disposable compensation tests stay
unchanged and human-gated for any real target. No history rewriting.

ONE NEXT after verification: reconcile independent receipt and explicit remaining
lifecycle/isolation gaps against L01–L15 before opening financial write execution.
If a new failure appears, diagnose retained source-linked evidence rather than
repeat unchanged tests. Main remains unchanged until separate human approval.
