## Current checkpoint — G1-ACCEPTANCE-REPAIR-01, 2026-10-14

Canonical repository naderalhaje097070-sudo/simple-store-aid; owner continued after G0/G1 delivery. PR72/eef73a0ad14cce993741c5880bcefc4c0ad46b0a is the starting candidate; main43d6edbccb66fb06ce0fcb93734ad59532d1aeae remains unchanged. #55/6173791297 is the single active continuation claim. Prior delivery #55/6169708623 remains valid historical failed evidence, not acceptance.

One outcome: repair the stale visual CI test contract and diagnose/complete exact named SSR denial plus after-state/native counters. Application/auth/dependencies/41migrations/financial contracts remain unchanged; original CI run body changes only for equivalent stronger semantic proof. No G0 waiver, broad lint cleanup, dependency upgrade, account chain or financial candidates. G0 remains unaccepted (1117errors/13warnings and11Moderate/5Low); existing G2 preissued-banned-JWT defect remains known. See docs/g1-acceptance-repair/INTAKE.md.

Status: bounded implementation/verification in progress, not accepted. ONE NEXT: complete affected G1 evidence and independent review, save exact SHA and handoff, then stop without merge/deploy. Historical checkpoints below are preserved.

## Current execution checkpoint — PRIMARY-ENV-001 real native runner, 2026-10-10

A capable disposable Vercel sandbox executed exact PR54 source `84c3444fcdf5fa2825809192cda5b15561c950cf`, preserving reviewed implementation0e616d0013fd72de244686f10c8de5a12488f312. All356 tracked blobs matched before and after execution. Main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae; no merge/deployment occurred.

Fresh experimental Supabase CLI2.120.0 native PostgreSQL/Auth/PostgREST stack applied all41 migrations on a non-root runner. Initial Auth users/tenants/orders were0. Bun1.2.14 frozen install, Gate4, Auth preflight,60 unit tests/125 expectations, typecheck and isolated production build passed. Existing Auth UI smoke passed on desktop1440/mobile390 with Playwright1.62.0/matching Chromium151 and strict browser containment. Screenshots and redacted logs are saved in changes/primary-env-001/native-runner; details in NATIVE_RUNNER_VERIFICATION.md. Repository CLI2.101.0/Docker workflow remains unchanged.

Actual Auth/tenant probe:22 passed checks and2 retained duplicate owner-role seed conflicts. Existing tenant trigger already created the roles; independent aggregate proves exactly2 correct rows. Own/foreign tenant metadata cases passed for both real user JWTs. No comprehensive tenant/RPC/financial acceptance is inferred.

**ENV-NATIVE-01 blocks acceptance:** banning fixtureB rejected new login400 but its previously issued JWT still read its own tenant via PostgREST200. This violates the strict disabled-account baseline; no cross-tenant exposure was observed. No account-lifecycle fix was implemented. Existing isolated write-test gates stay closed.

Final aggregates:2 Auth users/2 tenants,0 orders/products/customers. No financial harness, production access, old cloud-project restore, billing/payment change, migration edit, merge or deploy. The sandbox was stopped after retrieval; no snapshot/public route. This removes the earlier database-runtime availability blocker only. Experimental native tooling and external execution do not replace matching hosted CI, independent gate acceptance, full authorization evidence, existing security/lint/PWA blockers or remaining11Moderate/5Low findings.

ONE NEXT: independent review of this real isolation packet and a focused gated resolution of ENV-NATIVE-01, then remaining authorization/hosted evidence before financial write tests. Older checkpoints below remain historical.

## Current execution checkpoint — PRIMARY-ENV-001 runner feasibility, 2026-10-10

Source verified directly from GitHub: draft PR54 head `0e616d0013fd72de244686f10c8de5a12488f312`, base PR53 `54c930166a776828566876771efdec86a997fa53`; main remains `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. No merge/release occurred. This read-only/runtime-feasibility packet supersedes the older assumption that Docker is the only possible local runtime, without approving a toolchain change.

The old `mongezz-pr35-validation` cloud project is INACTIVE in a Free organization. Metadata does not expose pause date, schema/data provenance or exact-candidate migration compatibility. No restore, keys, SQL, backup download or cloud provisioning was performed; it is not accepted as a test target.

Current official Supabase documentation supports experimental native local stacks in CLI >=2.119.0. Downloaded scratch CLI2.120.0 was verified against the official release SHA256 and its help. A clean-environment/default-config native bootstrap failed before starting PostgreSQL: **PostgreSQL cannot be run as root**. This runtime maps only UID/GID0; both non-root transition and user-namespace probes fail. No container runtime/socket exists either. A new CLI executable alone cannot overcome these runtime restrictions; the repository CLI2.101.0 pin and application source remain unchanged.

GitHub Quality run38073032780/job114274195972 on the reviewed head is failure with runner_id0 and empty steps. No new retry was requested; current specific startup annotation remains unverified. Prior billing/quota evidence remains historical, not a new billing inspection.

Evidence: changes/primary-env-001/RUNNER_FEASIBILITY.md and runner-feasibility.json. No new unit/browser/application/database/financial test passed in this packet; preserve the previous bounded67-case evidence without promoting it to integration acceptance.

ONE NEXT: run the exact candidate on a capable disposable runner: preferably the existing Docker/CLI2.101.0 workflow once hosted capacity returns; alternatively assess CLI2.120.0 native on a supported non-root runner as an explicit experimental tooling change. Prove fresh migrations/Auth/RLS/two-tenant/disabled-user isolation and obtain its gate acceptance before financial write tests. No new cost, production access, merge or deployment.

## Current execution checkpoint — PRIMARY-ENV-001 Astra remediation, 2026-10-10

This top checkpoint supersedes the initial ENV review/capacity status below. Existing draft PR54 is extended additively; main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Only naderalhaje0970-droid/simple-store-aid is active.

Independent Astra review resumed and found three browser transport gaps: redirected requests escaped routing, WebSockets were unintercepted, and auth/destructive policies allowed unrelated loopback origins. The shared context guard now blocks redirects without retries, intercepts/closes WebSockets before pages, and pins the exact app/API HTTP origins. Rereview also corrected the existing font dependency with an exact offline stylesheet stub and standardized local/CI prerequisites on the production-built emulator. Screenshots use fallback fonts. No application, schema, financial or dependency change.

Actual browser evidence: original47 cases/36 failures; final67 cases/0 failures on recorded substitute Chromium153. Astra independently reproduced67 passing cases and closed the three initial findings and font compatibility defect for the reviewed source. Outcome remains **Blocked pending missing evidence**, not release/merge approval. Source fingerprints and logs are in changes/primary-env-001/remediation-evidence.json; final review in ASTRA_REVIEW_FINAL.md. Initial60 unit/125 expectations,8 wrapper/stub cases, typecheck/build evidence remains applicable to unchanged application source; changed Gate4/lint/Python/shell/YAML/diff checks passed.

No working Docker/Podman/Supabase/PostgreSQL tooling is present; the loopback fixtures are not an application/database stack. Real migration/Auth/RLS/tenant/disabled-user and financial/concurrency/rollback evidence is missing. Hosted checks still lack runner execution under the quota/spending blocker. Prior security/full-lint/PWA gates and11Moderate/5Low findings remain open. No database writes, migration, production access, merge, deployment or payment/budget change occurred.

ONE NEXT: obtain a capable isolated runner and execute the exact candidate's fresh stack/production-build Auth and tenant-isolation sequence in ISOLATED_STACK_READINESS.md, then obtain matching hosted checks and gate acceptance before financial write tests. Preserve main and current draft history.

## Historical initial ENV checkpoint — 2026-10-10

This checkpoint supersedes older scheduling below. Work continues only in naderalhaje0970-droid/simple-store-aid. main remains 43d6edbccb66fb06ce0fcb93734ad59532d1aeae. The owner authorized local ENV implementation despite hosted Actions limits; security/release acceptance gates remain open.

Prepared an isolated reconciliation candidate by reusing PR48 head31958e53438b377a9896dd0bf7e9c268c1f14aef on PR53 head54c930166a776828566876771efdec86a997fa53. Removed implicit production fallback, enforce explicit build/runtime target identity, guarded write preflights and context browser routing. Corrected privileged-public-key acceptance with before/after regression, proxy-contaminated positive fixtures with explicit proxy negatives, and page-only auth/destructive interception. Package/lock match PR53 unchanged.

Local evidence: 60/60 unit tests,125 expectations; Gate4 E1-E10 target-green; eight real server-wrapper cases with a stub entry; typecheck, changed-source lint, explicit-env build and mode-file build passed. Python/bash syntax and diff evidence are in changes/primary-env-001/VERIFICATION.md/evidence.json. Builds retain existing PWA glob/precache/chunk warnings; no offline/PWA release acceptance.

Independent Astra review was attempted but failed at usage limit before reviewing source. No independent acceptance. Hosted checks, real isolated database/browser/auth/tenant/financial execution and previous security/full-lint gates remain unverified. No database test writes, production data access, migration, merge or deployment occurred.

Billing clarification: earlier startup annotation listed payment failure OR spending limit; subsequent account inspection showed no outstanding invoice, October billed $0 and Actions budget $0 with stop-usage. A quota/spending restriction is the supported explanation, not proof of an unpaid invoice. No payment/budget changes were made. Do not repeat runnerless jobs while this remains unchanged.

ONE NEXT: independent exact-candidate ENV review when reviewer capacity is available; then close findings and obtain isolated integration/required CI evidence before financial write tests. Safe planning may continue meanwhile.

## Current execution checkpoint — PRIMARY-SEC-002, 2026-10-10

This top block supersedes older current checkpoints below. Application main still remains unmodified at `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`. A second focused security candidate batch is prepared in this working tree, continuing from PRIMARY-SEC-001, and is not merged or released.

Resolved the remaining current Critical/High dependency-audit groups by pinning compatible patched transitive versions for MCP SDK, proxy address parsing, shell quoting, brace expansion, browserslist, URI/IP/YAML parsing, PostCSS, NanoID and source-map parsing. `bun audit` changed from 65 package/advisory records with 2 Critical and 33 High records to 16 records with 0 Critical and 0 High records. Remaining findings are Low/Moderate only and are not release-accepted.

Native evidence: Bun 1.3.14 frozen install passed; Bun 1.2.14 frozen install passed; typecheck passed; unit tests passed at 40/40 with 86 expectations; build passed using local Supabase fixture values; changed-file lint for the dependency guard passed; `git diff --check` passed. Hosted Quality attempts on PR53 failed before runner execution (`runner_id:0`, empty steps), so they are infrastructure evidence only. Details: `changes/primary-sec-002/VERIFICATION.md` and `evidence.json`.

Known limits: no successful hosted CI, accepted final-candidate review, application MCP/auth/tenant test, financial write test, migration, merge, or deployment ran. PRIMARY-SEC-001 acceptance blockers still apply until exact-head PR/CI/review evidence exists.

Review checkpoint (2026-10-10): draft PR #53 already exists, stacked on PR #52, with reviewed head `4a5dda42d6470ded52edfb667d582d04d2a28165`. The manifest, lock and dependency guard were matched to that remote tree by Git blob hashes. A separate source/evidence review is recorded in `changes/primary-sec-002/REVIEW.md`; outcome: Changes required. Four isolated Lovable/MCP compatibility checks passed, but they do not prove application authorization or tenant isolation. The original manual brace-expansion lock edits conflict with the generated-file rule; independent clean generation reproduces all four entries, while a full regenerated graph has broader changes that were not adopted. Hosted CI still has no executed steps; its specific cause remains unverified.

Remediation checkpoint (2026-10-10; after PR53 head `479b0cef278497d8d7d455facd4aa797aa2af30b`): replaced the manually edited lock with Bun 1.4.0 generator output starting from the verified original PR52 lock. Removed unsupported brace-expansion resolution paths and pinned the already-resolved Lovable MCP version 0.20.1. Independent regeneration produced the identical lock; retained package versions/metadata are unchanged versus the previous candidate. Generator pruning removed 30 unique optional/orphan package versions; see `changes/primary-sec-002/LOCK_REGENERATION.md`. Moved the four synthetic MCP checks into `tests/unit` so the existing Quality job includes them. Bun 1.2.14 and 1.3.14 frozen installs passed; Bun 1.2.14 ran 44/44 tests with 94 expectations; typecheck, isolated build, changed-source lint and diff check passed. Audit remains 0 Critical / 0 High / 11 Moderate / 5 Low. SEC2-R2 is remediated in the candidate, pending final review.

CI diagnosis is now proven from the signed-in GitHub run page for run `38035862590` / job `114166024458`: GitHub prevented startup because recent account payments failed or the spending limit needs increasing. The annotation does not distinguish these two conditions. No account billing or spending setting was changed. Actual hosted execution is still missing; SEC2-R1 remains an acceptance blocker.

ONE NEXT: owner resolves the GitHub Billing & plans blocker; then run required checks and independent review on the final candidate. Do not repeat runnerless jobs while billing is unchanged. PRIMARY-ENV-001 follows stable security evidence; no financial write-capable tests before isolation proof.

## Current execution checkpoint — PRIMARY-SEC-001, 2026-10-09

This top block supersedes the planning-only status below. Application main remains43d6edbccb66fb06ce0fcb93734ad59532d1aeae. A focused security candidate is prepared on sec/primary-sec-001-tanstack-2026-10-09, stacked on PR51's planning branch. It is a draft, not accepted on main or released.

Pinned compatible TanStack transport/router/plugin and Seroval1.6.7; generated lock/route tree; corrected two provider error-boundary prop annotations. Native frozen install, typecheck and isolated build pass;29/29 unit tests pass. Full lint remains1117errors/13warnings; changed-file lint fails on340pre-existing errors/1warning in app.tsx, with zero added diagnostics proven by text comparison.

Wider audit:65 package/advisory records (2Critical/33High/25Moderate/5Low),25 fewer than baseline and no new records. These are untriaged scanner reports, not proof of deployed exploitation. Hosted runners still lack usable evidence; CI Bun1.2.14 cannot enforce minimumReleaseAge and Node is unpinned. Independent review and runtime/auth/finance validation remain pending. Details and source fingerprints: changes/primary-sec-001/VERIFICATION.md and evidence.json.

ONE NEXT: PRIMARY-SEC-002, triage remaining Critical/High dependency chains and exploit conditions into focused fixes. Security gate is open; PRIMARY-ENV-001 follows. No financial write harness, migration, merge or deployment ran.

# Project State

Last reconciled: 2026-10-09 (Africa/Tripoli).

## Current state — authoritative within this review branch

- Repository: `naderalhaje0970-droid/simple-store-aid` (original Lovable project).
- Verified main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
- Packet: `PRIMARY-GOV-001` — start plan pinned as documentation candidate.
- Plan: [PRIMARY_DELIVERY_PLAN.md](docs/PRIMARY_DELIVERY_PLAN.md).
- Code baseline remains a functional MVP with financial/security blockers.
- This branch contains documentation only; no runtime, dependency or DB fix is accepted.
- Historical main/PR statuses below are not current task instructions.
- No main merge, release, pilot or production-data authorization is granted by this packet.

## ONE NEXT

`PRIMARY-SEC-001`: prepare a focused TanStack dependency-security candidate.
Start by re-reading live main, applicable governance, package/lock resolution,
Lovable compatibility and open PRs. Follow the detailed four-step task and
applicable intake/safety requirements in the plan. Native verification gaps
keep the candidate blocked; no security override or unsafe environment fallback.

Following dependency: reconcile PR48/environment isolation, then financial gate
and PR49, followed by PR50/idempotency. No financial write test before isolation proof.

## Current evidence limits

Main confirmed at the SHA above; PR48/49/50 metadata re-read, all unmerged.
No application tests, database runs or dependency upgrade performed in this
documentation session. CI and independent review results belong to the actual
PR head and must be recorded separately, not inferred from earlier green runs.
Detailed audit and remaining acceptance conditions are summarized in the plan.

## Historical state — superseded scheduling, retained evidence

The following 2026-08-09 snapshot is retained verbatim as history. Its headings
such as Current stage / Immediate next task do not override the current block.
Existing financial invariants and release controls remain effective.

---

# Project State

Last updated: 2026-08-09

## Current stage

`RELEASE-BASELINE-RECON-002` — reconcile the effective `main` branch with the fixed Pilot RC1 plan before any new P0 implementation is authorized.

Reconciliation start `main`:

`a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`

Accepted current Phase-0 baseline after human merge of PR #44:

`975a34a854c510f3da7dbe45caa9791bb0375e2d`

The current P0 Gate-4 workstreams were created from or stacked on the older governed baseline:

`983b746e5c6639dcdc5e6557381ad5619abaa046`

At reconciliation start, `main` was 11 commits ahead of that older baseline and changed five paths. Before PR #44 was merged, additional direct repository history landed. The accepted current `main` is now 21 commits ahead of the older Gate-4 baseline with net changes across nine paths:

- `.github/workflows/isolated-auth-smoke.yml`
- `.lovable/plan.md` removed/moved into a dated plan file
- `.lovable/plan/اختبار-الضغط-المتكرر-على-زر-بيع-وحفظ-الفاتورة-mobile-390px-2026-08-09.md`
- `package.json`
- `bun.lock`
- `src/features/layout/BottomNav.tsx`
- `src/routes/_authenticated/app.tsx`
- `docs/rapid-click-sale-results.md`
- `tests/e2e/rapid-click-sale.py`

The application source drift still consists of the client-side sale-save guards already classified as defense in depth. The later rapid-click files are test/planning/evidence artifacts; they do not provide server-side idempotency and are not authorized for production execution.

The project remains a Functional MVP being stabilized into a reproducible, financially safe owner-only release candidate. No pilot or production-release authorization exists yet.

## Current release freeze

Until Pilot RC1 is explicitly approved:

- no new product features enter the release critical path;
- no employee accounts, payroll, attendance, GPS, chat, commissions, multi-branch, AI, or broad analytics;
- no direct product/dependency change to `main` outside a reviewed PR path;
- no automatic merge or deploy;
- no production data/secrets are used by isolated verification;
- any Critical/High financial-correctness or tenant-isolation defect blocks pilot;
- published Lovable-linked history is not rewritten;
- applied migrations remain immutable and corrections use forward-only migrations.

## Completed / resolved

### Governance and financial design

- Governance bootstrap merged through PR #19.
- Employee-account prototype PR #17 was superseded and closed without merge.
- AUDIT-001 baseline restoration merged through PR #23.
- FIN-COURIER-001 Gates 0–3 were owner-approved and merged through PR #24.
- SEC-CI-001, SEC-ENV-001, and FIN-IDEM-001 Gates 0–3 were owner-approved on 2026-07-28; their implementation remains gated.

### OPS-GHA-001 / Issue #36

Resolved on 2026-08-01. GitHub-hosted Actions again reaches real workflow steps and logs after the monthly Actions quota reset. Remaining failures are repository/test evidence, not runner acquisition failures.

### BASELINE-RUNTIME-001 / Issue #42

Resolved by explicit human merge of PR #44 as `975a34a854c510f3da7dbe45caa9791bb0375e2d`.

Evidence sequence:

- Phase-0 PR #41 originally reached a successful isolated Supabase start, QA seed, and production build, then failed before Playwright because the generated Worker compatibility date was `2026-08-09` while the local workerd binary supported through `2026-08-08`.
- PR #43 tested a dependency rollback hypothesis and reproduced the same failure, so it was closed without merge.
- PR #44 changed one local Auth Smoke command only, passing `--compatibility-date 2026-08-08` to `wrangler dev`.
- On PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937`, Quality, Ephemeral Financial Rules / T1–T15, and Isolated Auth UI Smoke all passed; Playwright executed successfully.
- No application logic, financial logic, dependency rollback, production access, or deployment was performed.

## Current P0 workstreams

### 1. SEC-CI-001 / Issue #29

Goal: deterministic and secret-safe release CI.

Current evidence:

- Gate-4 PR #37 is Draft and unmerged.
- SEC-CI Gate-4 policy probe reached real execution and passed.
- Standard Quality reached lint/format validation and failed on formatting in `tests/gate4/sec-ci/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Required before implementation:

- reconcile the Gate-4 branch to the accepted current release baseline;
- correct test-quality failures without weakening the contract;
- prove the final stable Supabase CLI/tool pin on a real runner;
- preserve T1–T15 and Auth Smoke;
- independently review exact-head evidence;
- explicit human Gate-4 approval.

### 2. SEC-ENV-001 / Issue #30

Goal: local/CI/preview/staging must fail closed and must not silently target production Supabase.

Current evidence:

- Gate-4 PR #38 is Draft and unmerged.
- SEC-ENV Gate-4 isolation probe reached real execution and passed.
- Standard Quality reached repository validation and failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`.
- Gate 4 is **NOT APPROVED**.

Approved target remains:

`MONGEZZ_DEPLOY_TARGET = local | ci | preview | staging | production`

Non-production requires explicit non-production configuration and rejects the production target. Production requires explicit production intent and explicit approved configuration. No source-code production fallback is accepted.

The newly landed `tests/e2e/rapid-click-sale.py` reinforces this requirement: its historical evidence says it used an injected owner session and could leave undeletable paid test orders. The script is not wired into an approved release gate and must not be run against production; future execution must use an isolated tenant and fail-closed environment proof.

### 3. FIN-COURIER-001 / Issue #22

Priority: P0 financial workflow blocker.

Approved business contract remains unchanged:

- direct fully paid: customer optional;
- direct debt: customer required;
- courier pending: customer optional and outside settlement;
- courier fully collected: customer optional; collected money is courier custody and becomes immediately settlement-eligible;
- courier partial/none that creates customer debt: customer required;
- courier-collected money does not enter store receipts before settlement;
- Advanced Sale is primary; Quick Sale is a secondary direct/cash/fully-paid shortcut;
- Delivered is not Settled.

Current exact-head evidence on PR #27 head `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:

- Quality: GREEN;
- Ephemeral Financial Rules / T1–T15: GREEN;
- Isolated Auth UI Smoke: GREEN;
- FIN-COURIER UI contract: GREEN;
- FIN-COURIER backend contract: real execution reached the consolidated safety net and failed with exit code `3`.

This is a real Gate-4 evidence failure, not infrastructure failure. Gate 4 is **NOT APPROVED**. PR-A / PR-B / PR-C remain blocked.

The effective `main` contains client-side sale-save guards in BottomNav, Quick Sale, and PaymentSheet. The rapid-click QA artifact reports 6/6 human-style duplicate-click scenarios passed on one injected session, but this remains UI evidence only and does not alter the approved financial or idempotency contract.

### 4. FIN-IDEM-001 / Issue #31

Priority: P0 financial retry-safety blocker.

Current state:

- Gates 0–3: owner-approved.
- PR #39 is preparation/readiness only and remains dependency-blocked by the canonical FIN-COURIER sale v2.
- Current UI `saving`/`busy` guards and rapid-click results do not satisfy server-side idempotency.

Required contract:

- scope key by `tenant_id + operation + idempotency_key`;
- same key + same canonical request returns original result without a second financial effect;
- same key + different request fails deterministically;
- concurrent same-key calls commit one financial effect;
- failed transaction does not poison the key;
- replay still requires normal authorization and tenant isolation.

## Baseline drift impact

Compared with old Gate-4 baseline `983b746e5c6639dcdc5e6557381ad5619abaa046`, accepted current `main` `975a34a854c510f3da7dbe45caa9791bb0375e2d` is 21 commits ahead with nine changed paths. Material categories are:

1. client-side duplicate-click/save guards in the sale UI;
2. `@lovable.dev/vite-tanstack-config` `2.7.7` → `2.9.1` and lockfile changes;
3. planning-history relocation/update;
4. rapid-click sale QA script/results artifacts;
5. isolated Auth Smoke local-emulator compatibility-date containment merged through PR #44.

Therefore no P0 Gate-4 approval may rely solely on stale exact-head evidence. Each workstream must reconcile its relevant assumptions to the accepted release baseline and run authoritative checks on its final exact head.

Client-side duplicate-click protection remains defense-in-depth only. It does not replace `FIN-IDEM-001`.

## Fixed critical path

1. Complete `RELEASE-BASELINE-RECON-002` and human-merge it.
2. Record the resulting `main` SHA.
3. SEC-CI Gate 4 reconciliation → exact-head proof → independent review → human approval.
4. SEC-CI focused implementation → exact-head verification → human merge.
5. SEC-ENV Gate 4 reconciliation → exact-head proof → independent review → human approval.
6. SEC-ENV focused implementation → exact-head verification → human merge.
7. FIN-COURIER Gate 4 backend-failure diagnosis/reconciliation → exact-head proof → independent financial review → human approval.
8. FIN-COURIER PR-A → PR-B → PR-C, each focused and release-verified.
9. FIN-IDEM Gate 4 against canonical sale v2 → human approval → focused implementation.
10. Create one exact Pilot RC1 commit and run all financial/security/reliability/UX/recovery gates together.
11. Explicit human RC1 approval.
12. Controlled owner-only pilot with 3–5 stores.

## Financial decisions that must not change

- Sale is not Cash.
- Delivered is not Settled.
- Customer debt is not Courier custody.
- Returned orders create no customer debt and no courier custody and restore stock only through the approved return transaction.
- A customer is required only when an operation creates customer debt.
- Money explicitly recorded as collected by a courier is custody, not store cash, until settlement.
- Pending courier delivery remains outside settlement until an outcome is recorded.
- Financial writes use authorized server-side/database transactional boundaries.
- Tenant isolation is enforced server-side and with RLS.
- No UI-only control is accepted as the sole protection for financial correctness or authorization.

## Pilot scope

The first pilot remains owner-only and targets 3–5 directly supervised stores. Employee accounts remain deferred until owner-only pilot evidence is reviewed.

Pilot entry is blocked by:

- FIN-COURIER-001;
- SEC-CI-001;
- SEC-ENV-001;
- FIN-IDEM-001;
- final exact-head Pilot RC1 verification;
- explicit human release approval.

## Immediate next task

Complete exact-head checks on Phase-0 PR #41 after synchronizing its tree to accepted `main = 975a34a854c510f3da7dbe45caa9791bb0375e2d`, preserving all concurrent repository history. Then require an explicit human merge. After that merge, record the resulting `main` SHA and begin SEC-CI reconciliation from that exact baseline.

Do not begin SEC-CI implementation, SEC-ENV implementation, FIN-COURIER PR-A/B/C, FIN-IDEM implementation, pilot execution, or deployment before their stated gate is satisfied.

## Standard verification

```bash
git diff --check
bun install --frozen-lockfile
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

When a change affects financial or authenticated application behavior, the appropriate isolated financial and authenticated UI suites are additionally mandatory. GitHub checks on the exact final PR head are the authoritative verification source.
