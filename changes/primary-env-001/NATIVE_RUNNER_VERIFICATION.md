# Disposable native runner verification — 2026-10-10

Outcome: a capable isolated runner was obtained and bounded real integration executed. **Isolation/release acceptance remains blocked.** This supersedes the previous inability to start a database; it does not replace matching hosted checks or independent acceptance.

## Source and environment

Repository: naderalhaje0970-droid/simple-store-aid. Executed source is PR54 head84c3444fcdf5fa2825809192cda5b15561c950cf, treeb31c19755779c1d2101abee9c3ad1b1e42def9a5, preserving reviewed implementation0e616d0013fd72de244686f10c8de5a12488f312. All356 tracked file blobs matched GitHub before execution and after build/tests; source-match.json contains zero mismatches. Main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. This evidence save changes documentation and archived probes only; no app, migration, lock, or CI pin change.

Vercel disposable sandbox sbx_Efpz90k5MLJoNiv6n3PSSOwGbTqy ran as UID/GID1000 on amd64 Ubuntu/glibc2.43, 4vCPU/8GB, no public routes. Existing Vercel project mongezz was only its compute binding; no code/environment/deployment from that project's repository was used or changed. The runner loaded the exact simple-store-aid snapshot. No production keys/data or old Supabase cloud project were accessed. Local config retains its tracked project_id as metadata, without remote linking.

The billing capability returned plan_not_supported for Pro/Enterprise-only rolling releases, supporting a Hobby inference rather than a direct plan field. Official Sandbox documentation describes a bounded free Hobby quota with no paid overage. No upgrade, payment, budget, billing or deployment action was performed; no actual invoice total is asserted.

The supported non-root runner resolved the earlier root-only runtime failure. Downloaded Supabase CLI2.120.0 and Node22.16.0 were checked against official SHA256 files. CLI native mode is experimental and differs from repository Docker/CLI2.101.0. Bun1.2.14, Playwright1.62.0 and its matching Chromium151.0.7922.34 ran; Wrangler resolved to4.149.0 through bun x. This does not approve CI reproducibility or adopt these runtime pins.

## Actual sequence and results

Start command (SUPABASE_HOME=/vercel/supabase-state, SUPABASE_EXPERIMENTAL_STACK=1, API54321/DB54322):

```sh
supabase --workdir /vercel/candidate stack start --runtime native --preparation on-demand --exclude realtime,storage,functions,studio,mail,analytics,pooler
```

Only PostgreSQL/Auth/PostgREST were enabled. Before dummy fixtures:41 applied migrations, zero Auth users, tenants and orders. Loopback API/DB identities were checked before credentials were consumed. Build/runtime used matching explicit ci target and isolated aliases; proxy variables were removed. Service-role credentials seeded only dummy Auth/tenant/profile/role fixtures and performed aggregate verification; negative tenant requests used actual user JWTs.

| Verification | Actual result | Evidence |
| --- | --- | --- |
| Fresh migration chain | All41 applied; initial users/tenants/orders0 | native-start.log (redacted), fresh-inventory.log |
| Bun frozen install | Passed;832 packages | frozen-install.log |
| Gate4/config and Auth origin preflight | Exit0 each | gate4.log, auth-preflight.log |
| Unit tests | 60 pass/0 fail,125 expectations | unit.log |
| Typecheck and explicit isolated production build | Exit0 each | typecheck.log, build.log, build-checks.json |
| Auth/tenant metadata probe | 22 checks pass;2 duplicate-role seed conflicts retained | auth-tenant-probe.json |
| Owner-role trigger verification | Exactly2 matching owner roles | owner-trigger-check.log, final-inventory.json |
| Auth UI desktop1440/mobile390 | Existing smoke exit0; real sign-in, RTL/no overflow/no critical hydration, no blocked remote requests | auth-ui.log, auth-ui-result.json, desktop.png, mobile.png |
| Source integrity after execution | All356 Git blobs still match | source-match.json |
| End-of-run aggregates | 2 Auth users/2 tenants/2 matching owner roles;0 orders/products/customers | final-inventory.json |

The tenant probe tested each user's own-tenant visibility and foreign-tenant read/update rejection, foreign-owner tenant insertion rejection, protected profile tenant reassignment rejection, anonymous denial and unchanged stored tenant names. These are bounded cases on tenants/profiles, not comprehensive authorization for every table/RPC. UI smoke used the existing strict context network guard and offline font stub; screenshots use fallback typography.

## Preserved failures and blocking finding

The first Node extraction failed because xz was missing; installing xz enabled the verified archive extraction. First emulator invocation failed because the downloaded Bun archive had no bunx alias; the archived emulator-initial-bunx-failure.log is retained, and bun x started the emulator. No application patch or test weakening was used.

The two seed_role checks returned409 because the existing on_tenant_created trigger already inserts the owner role. The source is supabase/migrations/20260626155758_5beb9f68-eae1-491f-b1f8-16b4b27d5f44.sql. A separate database query proved exactly two correct owner-role rows. The failed22/2 report is preserved unchanged; it is not rewritten as24/0. The archived probe is the exact executed one, not an accepted reusable harness.

**ENV-NATIVE-01 — High, candidate acceptance blocker; independent severity review pending.**
Contract: docs/governance/SECURITY_BASELINE.md, disabled accounts must be denied server-side.
Evidence: fixtureB was banned via local Authadmin (200); new password login failed400; its JWT issued before ban still read its own tenant through PostgREST200. This is an observed account-lifecycle authorization gap, not observed cross-tenant exposure. There was no exemption accepted here.
Required fix: reconcile the supported disable lifecycle with server/database authorization, ensuring existing tokens are denied without deleting history; inspect all affected policies/RPCs before a focused forward-only candidate. A browser redirect alone is insufficient.
Verification: active account positive controls, new login/refresh rejection, pre-disable JWT direct API/RLS/RPC denial, another tenant rejection and preserved historical rows, on the exact fresh candidate. No account-lifecycle source change was implemented in this batch.

## Limits, saving and rollback

No financial write harness, transaction/idempotency/concurrency/rollback suite, full tenant/resource/MCP contract, existing-database upgrade, storage/functions/realtime/mail test, full lint, fresh audit or offline/PWA acceptance ran. Existing build chunk/PWA glob/precache warnings remain. Hosted Quality remains unexecuted on the last observed runnerless failure; this external sandbox run does not replace required GitHub checks or final-head review.

Keys, connection passwords, dummy account credentials and JWTs were redacted before retrieval. No env/fixture/state dump is in this packet. Both screenshots were inspected and show the dummy empty dashboard without credentials. artifact-manifest.json hashes the collected evidence; the compressed transfer hash was verified locally. Actual executed probe/build/UI/packing scripts are archived for audit, not approved for arbitrary target reuse.

Sandbox stopped after evidence retrieval at2026-10-10T19:34:08Z, total duration905775ms; provider confirms status stopped. No snapshot or public endpoint was created. Transient state and credentials were not retained as a runnable target. For this evidence-only commit, rollback is additive revert; preserve failed evidence and never rewrite Lovable history or restore unsafe harness behavior.

ONE NEXT: independently review this exact isolation packet and resolve ENV-NATIVE-01 through the existing security/change gates, then complete missing authorization and required hosted evidence. Financial write tests stay blocked until the isolation gate is accepted. No merge/deployment/pilot approval.
