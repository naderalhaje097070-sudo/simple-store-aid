# PRIMARY-ENV-001 — Runner feasibility assessment

Date: 2026-10-10. Outcome: **Blocked by runtime prerequisites; no integration acceptance**.

## Goal, scope and acceptance

Determine whether PR54 can reach a fresh isolated test database without changing billing, touching production, restoring unknown data or running financial harnesses. This is runtime investigation plus documentation, not an application/schema change. The owner authorized this bounded continuation. Success for this packet is an evidence-backed suitability decision and one executable next step; success for ENV acceptance still requires real integration evidence and review.

## Verified source

- Repository: `naderalhaje0970-droid/simple-store-aid`.
- PR54: open draft, not merged; source head `0e616d0013fd72de244686f10c8de5a12488f312`.
- Branch: `sec/primary-env-001-reconcile-2026-10-10`.
- Base PR53: `54c930166a776828566876771efdec86a997fa53`.
- Main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
- This packet appends documentation to that remote head; it does not promote the scratch Git commit to remote ancestry.

## Results

| Boundary | Actual evidence | Decision |
| --- | --- | --- |
| Old cloud validation project | `ckshkqqwqzlgiikxlhpa` / mongezz-pr35-validation, INACTIVE, created2026-06-18; organization Free | Not accepted. Name/plan do not prove provenance, migrations or safe test scope. No restore attempted. |
| Container runtime | No docker/dockerd/podman, socket or configured Docker host; CapEff0, NoNewPrivs1 | Current Docker-based workflow cannot execute here. |
| Unprivileged container alternative | `unshare -Ur true` returns1 / Operation not permitted | Rootless setup not demonstrated; no installation attempted. |
| Native runtime alternative | Official docs require experimental stack and CLI>=2.119.0; verified scratch CLI2.120.0 exists | Feasible product option, not a capability established here; existing pinned CLI unchanged. |
| Native bootstrap | Empty scratch directory, clean env, actual start exits1: PostgreSQL cannot be run as root | No database service, migration or test started. |
| Non-root transition | UID and GID maps both `0 0 1`; setuid1001 returns EINVAL | Cannot satisfy native Postgres prerequisite in this runtime. |
| Hosted Quality | run38073032780 / job114274195972, failure, runner_id0, steps[] | No hosted test execution. Current exact startup cause not newly established; no rerun. |

## Commands actually executed

- Git status/log/hash-object; direct GitHub PR, main, commit/tree and current workflow-run/job reads. Local four edited documentation blobs match the remote source before modification.
- Executable/socket/capability/UID-map and localhost54321/54322/8080 inventory (all three ports closed).
- `unshare -Ur true`: failed, preserved as capability evidence.
- Python non-root transition: setgid1001 and later setuid1001 both fail EINVAL; inspection of UID/GID maps explains the failure. No persistent process identity changed.
- Fetched `https://supabase.com/changelog.md` successfully by curl after web retrieval rejected markdown content type; scanned breaking-change entries. Current docs and official CLI release metadata checked before the probe. No provider API convention inferred from older memory.
- Downloaded official CLI2.120.0 Linux amd64 archive; SHA256 `7074584113aa00495beeac661c41fb09f1ddd0a483cd7333894b0d080086dc6e` matched release asset digest. Initial extraction failed on unmapped archive ownership; scratch extraction with `--no-same-owner` succeeded. No repository dependency changed.
- Actual CLI `--version`, `stack --help` and `stack start --help` with experimental setting.
- Native probe command in an empty scratch directory, with only PATH/experimental/task-specific SUPABASE_HOME env:

```text
supabase stack start --runtime native --preparation on-demand --exclude realtime,storage,functions,studio,mail,analytics,pooler
```

Actual exit1, stdout empty, stderr210bytes:

```text
PostgreSQL cannot be run as root
Set SUPABASE_NATIVE_POSTGRES_USER=<user> to run PostgreSQL as a non-root user, creating one if needed (on Linux, for example `useradd --system --user-group supabase-postgres`).
```

Only telemetry.json was created in the task-specific Supabase state. No stack data or service exists. No application configuration, production credentials or cloud access token was supplied.

## Verification limits

No unit/browser suite was repeated because no implementation changed. The earlier67 transport cases remain bounded previous evidence. Fresh application/Auth/RLS/tenant/disabled-user/migration/financial/concurrency/rollback tests remain **Not verified**. No service key retrieval, SQL, database writes, restore/provisioning, billing/spending change, merge or deployment occurred. Supabase project metadata reads are not production database access.

## One next task

Obtain one capable disposable runner for the exact candidate. Prefer the existing Docker-compatible Ubuntu workflow with CLI2.101.0 once hosted capacity returns. If choosing native, provide a supported non-root Linux runner and separately assess CLI2.120.0 experimental configuration/services; do not silently replace the pinned acceptance toolchain.

Then: fresh migration startup -> isolated Auth -> production-built app with matching loopback identity -> two-tenant/RLS/disabled-user negative checks -> exact-source independent isolation acceptance. Financial write tests remain after that gate; matching hosted checks and final review remain required for merge.

A runner request must contain the immutable candidate SHA, no production secrets, no linked remote database, no cloud project creation/restore and no billing or automatic deployment. Record real failure logs with secrets redacted. This packet's rollback is an additive revert of documentation only; the scratch CLI/state can be discarded.

## Sources

- https://supabase.com/features/native-local-runtime
- https://supabase.com/docs/guides/local-development/docker-and-native-runtimes
- https://supabase.com/docs/guides/local-development/running-multiple-local-projects
- https://github.com/supabase/cli/releases/tag/v2.120.0
- https://supabase.com/changelog.md

The documentation-search backend returned older90-day restoration guidance while current public platform pages report1year. No restoration eligibility decision is made from that conflict: the pause timestamp was unavailable and suitability remains unverified.
