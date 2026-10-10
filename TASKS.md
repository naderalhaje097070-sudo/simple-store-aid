## Current queue checkpoint — PRIMARY-ENV-001 runner feasibility, 2026-10-10

- [x] Re-read PR54 head `0e616d0013fd72de244686f10c8de5a12488f312`, PR53 base and unchanged main directly from GitHub.
- [x] Cloud metadata: old validation project INACTIVE; organization Free. No accepted schema/data provenance or restore suitability; no cloud action.
- [x] Container prerequisites absent; user namespace creation denied; UID/GID mappings only permit root and non-root transition fails.
- [x] Discovered official native-stack alternative; scratch CLI2.120.0 archive SHA256 verified and actual help inspected. Clean default native bootstrap exits1: PostgreSQL cannot run as root. No database service or migration started.
- [x] Re-read latest Quality job: failure, runner_id0, steps[]. No blind rerun or spending change.
- [ ] ONE NEXT: capable disposable Docker runner using existing CLI2.101.0, or separately evaluated experimental native non-root runner. Execute fresh exact-candidate migration/Auth/tenant/RLS/disabled-user proof before requesting isolation acceptance.
- [ ] Required hosted checks, isolation gate and financial tests remain blocked; existing security/lint/PWA blockers unchanged.

Evidence: changes/primary-env-001/{RUNNER_FEASIBILITY.md,runner-feasibility.json}. Older checkpoints remain history.

## Current queue checkpoint — PRIMARY-ENV-001 Astra remediation, 2026-10-10

- [x] Independent Astra source review resumed; original ENV-A1/A2/A3 findings recorded.
- [x] Shared context guard: redirect/retry blocking, WebSocket interception, exact configured auth/destructive HTTP origins.
- [x] Rereview fixes: exact offline font stylesheet with fallback-font limitation; production-build/no-HMR prerequisites; real positive popup coverage.
- [x] Actual browser regression: original47/36 failing cases; final67/0. Astra independently reproduced67/0 and closed the bounded findings; no overall acceptance.
- [x] Changed-source Gate4/lint and seven Python/shell/YAML/diff checks; final source/evidence fingerprints saved in existing draft PR54.
- [ ] ONE NEXT: provision a capable isolated runner, then validate fresh local stack/migrations and production-built Auth/tenant/RLS/disabled-user behavior on the exact candidate.
- [ ] Matching Playwright browser/hosted required checks: current local substitute browser is explicit; GitHub quota/spending startup remains blocked. No blind retries or account spending changes.
- [ ] Financial acceptance after isolation gate: stored values, stock/custody/transaction boundaries, concurrency/idempotency and rollback; no financial harness execution yet.
- [ ] Previous security/full-lint/PWA gates and11Moderate/5Low findings; no merge/deploy/pilot acceptance.

Evidence: changes/primary-env-001/{REMEDIATION_VERIFICATION.md,ASTRA_REVIEW_FINAL.md,ISOLATED_STACK_READINESS.md,remediation-evidence.json}. Earlier queues below are historical.

## Historical initial ENV queue — 2026-10-10

- [x] Local ENV reconciliation: reuse current PR48 source on PR53, preserve dependencies; explicit environments, matching build/runtime, guarded harnesses.
- [x] Candidate fixes: privileged-public-key negative regression; deterministic proxy fixtures + explicit proxy rejection; context routing for auth/destructive harnesses.
- [x] Offline verification:60 unit tests/125 expectations; Gate4 target-green;8 actual server-wrapper cases with stub entry; typecheck/changed lint/two isolated builds/syntax.
- [ ] ONE NEXT: independent exact-candidate review. Astra was attempted but stopped at usage limit before review; no approval.
- [ ] ENV acceptance: hosted/current-head checks and isolated DB/auth/RLS/tenant/browser containment evidence. No write-capable financial flow before proof and acceptance.
- [ ] Security acceptance: PR53 final review, prior CI/lint gates and remaining11Moderate/5Low findings remain open.
- [ ] Release/PWA: retain and investigate existing build warnings including empty glob/precache; do not claim offline release readiness from these builds.
- [ ] GitHub Actions startup: no invoice observed; $0 stop-usage budget/quota blocks execution. No account spending change; no blind retries.

Evidence: changes/primary-env-001. The old queue below is historical and does not schedule new work.

## Current queue checkpoint — 2026-10-10

- [x] PRIMARY-SEC-002 local candidate: Critical/High audit triage and compatible dependency corrections prepared; audit now reports 0 Critical and 0 High records; native frozen install/typecheck/unit/build/changed-file lint/diff-check evidence saved. Candidate only; not on main.
- [x] PRIMARY-SEC-002 PR packaging: draft PR #53 stacked after PRIMARY-SEC-001; hosted Quality attempts failed before runner steps (`runner_id:0`, empty steps).
- [x] PRIMARY-SEC-002 source/evidence review of PR #53 head `4a5dda42d6470ded52edfb667d582d04d2a28165`: Changes required; see `changes/primary-sec-002/REVIEW.md`. This is not a GitHub approval or final-head merge acceptance.
- [x] PRIMARY-SEC-002 compatibility evidence: four synthetic Lovable/MCP runtime checks passed; clean Bun generation independently matched all four brace-expansion entries. No application tenant/finance proof claimed.
- [x] SEC2-R2 candidate remediation: generator-owned Bun 1.4.0 update from the verified original PR52 lock; independent regeneration matches byte-for-byte. Unsupported brace paths removed; Lovable MCP stays at 0.20.1. Frozen installs, 44 unit tests, typecheck, isolated build, changed-source lint and audit verified; final review still pending.
- [x] SEC2-R1 startup diagnosis: GitHub run 38035862590 visibly reports failed recent account payments or a spending-limit restriction. The account must resolve it; no billing/spending change was made.
- [ ] ONE NEXT — owner resolves GitHub Billing & plans; then execute required CI and review the final candidate. Preserve failed evidence; no blind retries while billing is unchanged.
- [ ] PRIMARY-SEC-002 acceptance: final-candidate review and required checks remain open; do not waive remaining Low/Moderate findings or previous lint/CI blockers.
- [ ] PRIMARY-ENV-001 after security PR evidence is stable: reconcile fail-closed environment isolation before write-capable financial tests.
- [ ] Track remaining security maintenance: Moderate/Low findings remain for `@babel/core`, `@hono/node-server`, `dompurify`, `esbuild`, `hono`, and `qs`.
- [ ] Financial gates remain blocked until environment isolation and canonical financial write evidence are proven.

Evidence: changes/primary-sec-002/VERIFICATION.md. Earlier PRIMARY-SEC-002-as-next statements below are historical.

## Current queue checkpoint — 2026-10-09

- [x] PRIMARY-SEC-001 candidate preparation: official transport/serializer patch verification, generated lock, three negative/positive advisory guards, minimal ErrorComponentProps compatibility, native29 tests and typecheck/build evidence saved. Candidate only; not on main.
- [ ] PRIMARY-SEC-001 acceptance: independent review; hosted CI evidence; disposition/fix of pre-existing lint gates. No checks waived.
- [ ] ONE NEXT — PRIMARY-SEC-002: triage2Critical and33High audit records by package chain, runtime/tooling exposure, exploit condition and compatible correction. Do not interpret65 scanner records as65 exploited product defects. Resolve security before real-store use.
- [ ] Track tooling/CI: Bun1.2.14 lacks release-age resolution support; Node>=22.12 required by the new framework but Quality does not pin Node; PR51 job runner_id0/empty steps cause remains unproved.
- [ ] PRIMARY-ENV-001: reconcile PR48 and prove fail-closed isolation before write-capable tests.

Evidence: changes/primary-sec-001/VERIFICATION.md. Earlier PRIMARY-SEC-001-as-next statements below are historical planning state. Financial contract, PR49 and PR50 gates remain in force.

# Governed Tasks

## Current queue — 2026-10-09

See [primary plan](docs/PRIMARY_DELIVERY_PLAN.md) and the current block in PROJECT_STATE.md.
Only this queue schedules new work; the preserved August queue below is history.

| Task | Status | Acceptance |
| --- | --- | --- |
| PRIMARY-GOV-001 | Documentation candidate prepared | Identity/state/task/decision links agree; diff limited to docs; no release acceptance implied |
| PRIMARY-SEC-001 | ONE NEXT: preparation | Official advisory + compatible lock/build + required final-head evidence and review |
| PRIMARY-ENV-001 | Follows security candidate and prerequisites | Reconcile PR48/current SEC-CI; prove isolated targets before write tests |
| FIN-COURIER-001 | Existing gate/contract retained | Diagnose current Gate4 and evaluate PR49; backend -> reports -> UX |
| FIN-IDEM-001 | Depends on canonical financial write | Evaluate PR50; all relevant writes, concurrency/replay/lost response |
| PILOT-RC-001 | Blocked by release gates | One accepted source with recovery, security, finance and complete journeys |
| PILOT-000 / commercial | Not started | Actual stores, reconciliations, costs and accepted billing lifecycle |

Do not mark old mongezz B01–B20 as accepted here. Preserve original finding/task IDs,
map dependencies, and use additive history. No full rewrite, speculative transfers,
financial-policy changes or new product scope in the initial dependency packet.

## Historical task snapshot

The content below is preserved as historical evidence; old Active/queue headings
do not schedule the current branch. Actual acceptance is verified from the
relevant current source, review and result, never a historical checkbox.

---

# Governed Tasks

## Active

### RELEASE-BASELINE-RECON-002 — Current main reconciliation before Pilot RC1

- Priority: P0 sequencing prerequisite.
- Change type: Governance / source-of-truth synchronization only.
- Reconciliation-start `main`: `a0f3b8c30743860ec0c06dd37e8e5d43b34e6c5b`.
- Accepted current Phase-0 baseline after human merge of PR #44: `975a34a854c510f3da7dbe45caa9791bb0375e2d`.
- Previous P0 Gate-4 baseline: `983b746e5c6639dcdc5e6557381ad5619abaa046`.
- At reconciliation start, `main` was 11 commits ahead / five changed paths relative to the old Gate-4 baseline.
- After concurrent repository history and PR #44, the accepted current `main` is 21 commits ahead / nine net changed paths relative to that old baseline.
- Net current drift categories:
  - sale UI `busy`/`saving` duplicate-click guards;
  - `@lovable.dev/vite-tanstack-config` `2.7.7` → `2.9.1` plus lockfile changes;
  - Lovable plan relocation/update;
  - rapid-click sale QA result/script artifacts;
  - isolated Auth Smoke compatibility-date containment from PR #44.
- Rapid-click artifact classification:
  - `docs/rapid-click-sale-results.md` reports 6/6 UI duplicate-click scenarios passed;
  - this remains UI evidence only and does not close FIN-IDEM-001;
  - `tests/e2e/rapid-click-sale.py` reads target configuration/session context and performs financial writes, so it is **not authorized for production execution** and future use must be isolated/fail-closed.
- Out of scope:
  - production financial logic;
  - workflow hardening implementation;
  - environment resolver implementation;
  - migrations/RPC/RLS changes;
  - deployment or pilot execution.
- Done when:
  - `PROJECT_STATE.md`, `TASKS.md`, and the reconciliation record agree;
  - final PR #41 diff relative to accepted `main` is documentation/governance only;
  - required checks on one exact final head are reviewed;
  - a human explicitly merges PR #41;
  - the resulting `main` SHA is recorded before Phase 1 begins.

## Fixed P0 execution queue

### P0-1 — SEC-CI-001: deterministic and secret-safe CI

- Issue: #29.
- Design PR: #32.
- Gate-4 PR: #37.
- Status:
  - Gates 0–3: owner-approved;
  - Gate-4 probe: reached real execution and passed;
  - Quality previously failed on formatting in `tests/gate4/sec-ci/probe.ts`;
  - Gate 4: **NOT APPROVED**.
- Required next actions after RELEASE-BASELINE-RECON-002 merge:
  1. branch/reconcile SEC-CI Gate 4 from the accepted release baseline;
  2. preserve exact policy sentinels;
  3. fix only test-quality/format issues required for Quality;
  4. validate the final stable Supabase CLI candidate on a real runner with fresh migrations + T1–T15 + auth smoke;
  5. prove concise/redacted reporting and least-privilege permissions;
  6. independent evidence review;
  7. explicit human Gate-4 approval;
  8. focused SEC-CI implementation PR;
  9. exact-head verification and explicit human merge.
- Exit:
  - release-blocking workflows are deterministic, isolated, secret-safe, and distinguish infrastructure failure from assertion failure.

### P0-2 — SEC-ENV-001: fail-closed environment isolation

- Issue: #30.
- Design PR: #33.
- Gate-4 PR: #38.
- Status:
  - Gates 0–3: owner-approved;
  - Gate-4 probe: reached real execution and passed;
  - Quality previously failed on `explicit-any`/formatting in `tests/gate4/sec-env/probe.ts`;
  - Gate 4: **NOT APPROVED**.
- Approved contract:
  - `MONGEZZ_DEPLOY_TARGET = local | ci | preview | staging | production`;
  - non-production requires explicit non-production Supabase configuration;
  - missing configuration fails closed;
  - non-production rejects the known production project;
  - production requires explicit production intent and explicit configuration;
  - no source-code production fallback.
- Additional current evidence requirement:
  - financial-write test harnesses, including `tests/e2e/rapid-click-sale.py`, must be prevented from running against production or ambiguous targets.
- Required next actions:
  1. reconcile Gate 4 from the accepted release baseline;
  2. correct test-quality issues without weakening sentinels;
  3. verify client, SSR, build-time, runtime, and financial-write test-harness resolution paths share the approved fail-closed contract;
  4. exact-head Gate-4 evidence;
  5. independent review;
  6. explicit human Gate-4 approval;
  7. focused resolver/build implementation PR;
  8. exact-head verification and explicit human merge.
- Exit:
  - local/CI/preview/staging and write-capable test harnesses cannot silently target production Supabase.

### P0-3 — FIN-COURIER-001: courier sale/customer/custody correction

- Issue: #22.
- Gate-4 PR: #27.
- Gates 0–3: owner-approved and merged through PR #24.
- Current exact-head evidence on `86f2b552db3ff83a9091ee2df58b7f4e547717b7`:
  - Quality: GREEN;
  - Ephemeral Financial Rules / T1–T15: GREEN;
  - Isolated Auth UI Smoke: GREEN;
  - UI Gate-4 contract: GREEN;
  - backend Gate-4 contract: real execution failed with exit code `3`.
- Rapid-click main-branch artifact reports 6/6 human-style duplicate-click scenarios passed, but it is UI-only evidence and does not alter the approved FIN-COURIER contract.
- Classification: real Gate-4 evidence blocker, not runner failure.
- Gate 4: **NOT APPROVED**.
- PR-A / PR-B / PR-C: **BLOCKED**.
- Required next actions after SEC-CI and SEC-ENV are closed:
  1. reconcile #27 assumptions against the accepted release baseline, including the UI `saving`/`busy` guards and rapid-click artifacts;
  2. identify the exact backend sentinel producing exit `3`;
  3. determine whether the cause is probe defect, stale baseline assumption, false evidence, or a genuine current contract mismatch;
  4. correct Gate-4 test/evidence only if required; do not implement financial behavior while the gate is unapproved;
  5. rerun Quality + T1–T15 + Auth Smoke + backend/UI Gate-4 on one exact final head;
  6. independent financial review;
  7. explicit human FIN-COURIER Gate-4 approval.

#### FIN-COURIER implementation after Gate-4 approval

**PR-A — canonical financial write**

- forward-only constraint/schema changes;
- `create_sale_with_items_v2`;
- atomic `update_courier_outcome_v2`;
- same-tenant customer validation;
- legal/monotonic courier state transitions;
- custody/debt/stock transaction correctness;
- SQL/concurrency/backward-compatibility/rollback safety tests.

**PR-B — reporting/financial-health alignment**

- outcome-aware reporting;
- canonical debt/custody/store-cash separation;
- regression proof against PR-A semantics.

**PR-C — sales UX**

- Advanced Sale primary on desktop/mobile/post-sale;
- Quick Sale secondary direct/cash/fully-paid/customer-free shortcut;
- courier-specific wording/statuses;
- mobile RTL + desktop exact-flow tests;
- preserve loading/failure states and client-side duplicate-click guards as defense in depth.

### P0-4 — FIN-IDEM-001: financial retry safety

- Issue: #31.
- Design PR: #35.
- Gate-4 preparation PR: #39.
- Status:
  - Gates 0–3: owner-approved;
  - full target behavior intentionally dependency-blocked until FIN-COURIER PR-A provides canonical `create_sale_with_items_v2`;
  - current UI duplicate-click guards and rapid-click 6/6 result are not accepted as server-side idempotency.
- Required target contract:
  - key scope = `tenant_id + operation + idempotency_key`;
  - same key + same canonical request returns original result with no second financial effect;
  - same key + different request returns deterministic conflict;
  - concurrent same-key calls produce exactly one committed financial effect;
  - failed transaction does not poison the key;
  - authorization/tenant isolation still applies on replay.
- Required tests before implementation:
  - sequential replay;
  - same-key conflict;
  - concurrent duplicate calls;
  - lost-response retry;
  - failure-then-retry;
  - tenant isolation;
  - result fidelity;
  - exactly-one stock/payment/debt/custody effect.
- Exit:
  - explicit human Gate-4 approval and focused server/database implementation verified on exact head.

### P0-5 — PILOT-RC-001: one exact release candidate

- Master tracker: Issue #34.
- Dependency: P0-1 through P0-4 complete and human-merged.
- Create one exact `PILOT_RC1_SHA` and freeze it for release verification.
- Required proof on that same SHA:

Financial:
- T1–T15 GREEN;
- FIN-COURIER approved contract GREEN;
- idempotency/retry/concurrency GREEN;
- debt/courier-custody/store-cash reconciliation matches canonical rules;
- returns and stock restoration GREEN;
- day close/reconciliation GREEN.

Security/environment:
- local/CI/preview/staging cannot target production;
- write-capable test harnesses cannot target production or ambiguous configuration;
- tenant isolation GREEN;
- no raw credentials/secrets in CI output or artifacts;
- least-privilege release workflows.

Reliability:
- frozen dependency install;
- typecheck/lint/unit/build GREEN;
- fresh isolated migration chain GREEN;
- authenticated UI smoke GREEN;
- failure/retry paths verified.

UX:
- Advanced Sale primary;
- Quick Sale secondary only;
- mobile RTL and desktop core flows GREEN;
- loading/error/retry states verified.

Operations:
- release notes;
- known limitations;
- environment and secret inventory;
- backup procedure;
- restore procedure tested;
- rollback/compensation procedure reviewed;
- incident checklist.

- Exit: explicit human RC1 approval. No automatic deploy.

### P0-6 — PILOT-000: owner-only controlled pilot

- Target: 3–5 owner-operated stores under direct supervision.
- No employee-account dependency.
- Pilot mode: fix-only for release-critical defects; feature requests are collected but not automatically implemented.
- Measure:
  - activation and time-to-first-sale;
  - daily sales/expenses/debt/day-close/courier-settlement usage;
  - reconciliation variance;
  - failed/duplicate writes;
  - D1/D7/D14/D30 retention;
  - willingness to pay.
- Exit: pilot evidence reviewed and accepted before deciding the next product roadmap.

## Deferred until after owner-only pilot evidence

### EMP-001 → EMP-005 — Team/employee edition

Employee identity, RBAC, assignment, personal custody, employee UI, and employee E2E remain deferred until the owner-only financial core has real pilot evidence and the corresponding change gates are approved.

### Other deferred scope

- payroll;
- attendance;
- automatic commissions;
- GPS tracking;
- internal chat;
- custom per-button permissions;
- multi-branch expansion;
- broad analytics expansion;
- AI product features.

## Completed

### BASELINE-RUNTIME-001 — Auth Smoke local runtime containment

- Issue #42.
- PR #43 tested a dependency rollback and was closed without merge after exact-head evidence reproduced the failure.
- PR #44 exact head `7e12e9c2af64ce12fbfe09c88f52d787df44a937` passed Quality, T1–T15, and real Playwright Auth Smoke.
- PR #44 was explicitly human-approved and merged as `975a34a854c510f3da7dbe45caa9791bb0375e2d`.
- Scope was one local emulator command-line compatibility-date pin only.
- No deployment or production access occurred.

### OPS-GHA-001 — GitHub-hosted Actions execution restoration

- Issue #36.
- Resolved 2026-08-01 after monthly Actions quota reset.
- Hosted runner reached real shell steps/logs.
- No weakened tests, public-repo workaround, unmanaged self-hosted runner, merge, or deploy was used.

### FIN-COURIER-G0-G3

- PR #24.
- Owner-approved and merged.
- Establishes the financial/customer/courier/primary-sale contract.

### AUDIT-001

- PR #23.
- Reviewed and merged.
- Restored a governed pilot baseline before the later drift recorded by RELEASE-BASELINE-RECON-002.

### GOV-001

- PR #19.
- Governance bootstrap merged.

### EMP-000

- PR #20.
- Employee-account baseline/decomposition merged; no implementation authorization.

### PR17-PROTOTYPE

- Closed without merge as superseded oversized prototype.

## Permanent financial invariants

- Sale != Cash.
- Delivered != Settled.
- Customer debt != Courier custody.
- Returned => zero debt/custody + approved stock restoration.
- Customer required only when customer debt is created.
- Courier-collected money remains custody until settlement.
- No UI-only authorization or UI-only duplicate-write protection is accepted as the financial safety boundary.
