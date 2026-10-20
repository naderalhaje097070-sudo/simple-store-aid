## Current execution notice — MONJEZ v2.2, 2026-10-10

Active repository: `naderalhaje097070-sudo/simple-store-aid`.
Verified main: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
Current unmerged lineage: PR51 -> PR52 -> PR53 -> PR54
(`57fb508b9d239aaf4676352dd97654341416c46a`).
Execution index: [issue #55](https://github.com/naderalhaje097070-sudo/simple-store-aid/issues/55).
Reconciliation evidence: [PRIMARY-RESUME-001](../changes/primary-resume-001/VERIFICATION.md).

The six stages, scope and accepted contracts in this plan are retained.
The original 9 October start packet and its next-task notices below are historical.
Read the top PROJECT_STATE/TASKS checkpoints for scheduling, rather than repeating
PRIMARY-SEC-001/002 or the ENV implementation already prepared in the draft stack.

Quality #342 attempt2 reached real steps and passed on the exact PR54 source.
This replaces the current runner-unavailable assumption for that job only;
it is not authorization/financial/independent-review or merge acceptance.

Current bounded packet: S1.1a repository/state/evidence reconciliation.
ONE NEXT: `S2.4a / ENV-NATIVE-01` account-lifecycle intake, dependency mapping
and regression safety net before authorization implementation. Missing independent
reviews and other required checks remain open. Financial write tests require accepted
isolation; candidate availability alone cannot satisfy that dependency.

No second roadmap, new product scope, financial-policy change, billing action,
merge, release or deployment is authorized by this notice.

---

# Primary delivery plan and start packet

Date: 2026-10-09 (Africa/Tripoli).
Repository: `naderalhaje0970-droid/simple-store-aid`.
Verified application baseline: `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
Stage: `PRIMARY-GOV-001` — documentation preparation.
Next: `PRIMARY-SEC-001` — bounded dependency-security preparation.

## Authority and scope

The owner explicitly requested consolidated instructions from both repositories,
an end-to-end plan, and pinned starting steps on 9 October 2026.
This authorizes preparing this documentation on a review branch.
It does not claim a financial gate, merge, production deployment, or pilot is approved.
Existing accepted financial decisions and release boundaries remain in force.
The other repository `mongezz` is a historical source of candidate fixes and governance.
Do not resume PR137/B02 there as the active task or copy successful test counts here.

## Product and six stages

The release is an Arabic owner-only shop operations SaaS: products, inventory,
customers, orders/sales, delivery, collection, debt, courier custody/settlement,
expenses, day summary, receipts and basic export.
Platform account/subscription/support administration must use explicit permissions;
access to tenant order details requires an accepted authorization/privacy matrix.
Employee accounts, multi-branch, payroll, GPS, chat, offline financial writes,
broad analytics, AI features and a delivery-company edition remain deferred.

| Stage | Deliverable | Exit |
| --- | --- | --- |
| S1 Source/governance | One baseline, state, task queue and evidence register | Source and scope reconciled; current/historical state distinguished |
| S2 Security/verification | Patched dependency candidate, safe CI and environment isolation | Native checks on final source; no production fallback in non-production |
| S3 Financial core | Approved state contract, canonical RPC/domain/report behavior | Stored balances and reports reconcile across negative cases |
| S4 Retry/concurrency | One effect per logical write | Replay/conflict/lost response/concurrent session proof |
| S5 RC1 operations | Account recovery, reliable integrations, mobile UX, restore and support | Complete isolated journeys and a tested recovery on one release source |
| S6 Pilot/commercial | Supervised 3–5-store pilot, economics and truthful billing | Reconciliation, stable use, support and payment lifecycle accepted |

Dependencies: isolate before write tests; settle financial contracts before changing
RPC behavior; backend then reports then financial UI. Design idempotency alongside
the canonical financial write, without duplicating it. Unsafe exposed integrations
must be secured or safely contained before real-store use, even if billing is deferred.
Before any runtime/build verification, inspect configuration resolution and use
explicit isolated fixtures; do not start a preview server with implicit production settings.

Historical B01–B20 from plan1.2 retain their identifiers as mapping references:
B01–B03 -> S1/S2; B04–B07 -> S3; B08–B10 -> S4; B11–B15 -> S5;
B16–B20 -> S6. Their acceptance status is not inherited by this repository.

## Current evidence and conflicts

Live main is still the reviewed baseline above. PROJECT_STATE/TASKS previously
described an August baseline and immediate PR41 work. Those blocks are now marked
historical; do not infer current readiness or a new approval from them.

PR48 is open/unmerged, head `31958e53438b377a9896dd0bf7e9c268c1f14aef`.
Its body still names older `e078...` evidence: inspect current-head checks before acceptance.
PR49 is draft/unmerged, head `3106b4710fb9214d6f406d5a3fe7bf44fa2823e6`,
based on FIN-COURIER Gate4 branch `86f2b552db3ff83a9091ee2df58b7f4e547717b7`.
PR50 is draft/unmerged, head `193412a01938d752a98689d85acd727664e4dc8e`,
based on PR49. Evaluate these before reimplementing their work.

Source-review report `Mongezz_Original_Project_Audit_2026-10-09.md`
is the retained four-reviewer audit, covering baseline `43d6edb...`.
Its evidence is historical input, not newly executed verification in this packet:
debt overstatement was reproduced in a pure function; return/delete, settlement,
custody transitions and resource-ownership findings also require isolated DB proof.
26/26 limited unit assertions did not prove the build/database/financial release.
The detailed owner instruction archive is
`Mongezz_Agent_Governance_2026-10-09.md`, saved outside the repository.
This repository packet is the operational summary; retrieve the audit before
working on an individual financial finding, preserving its original identifier.

## First three work packets

### PRIMARY-GOV-001 — current documentation packet

Goal: pin the start without modifying application behavior.
Files: AGENTS.md, PROJECT_STATE.md, TASKS.md, DECISIONS.md,
this plan, and a historical notice on the older execution plan.
Acceptance: one next task, repository identity explicit, old history preserved,
accepted financial/release boundaries unchanged, and remote diff documentation-only.
Verification: content/diff/path/link consistency. No application test result claimed.
Rollback: close the draft or use an additive revert; never rewrite published history.

### PRIMARY-SEC-001 — next bounded packet

Owner: implementing agent; acceptance review follows REVIEW_PROTOCOL.
Urgency: dependency issue classified Critical in the retained original-source audit.
Implementation risk: medium/high because framework packages affect build/runtime.
Goal: prepare the smallest compatible TanStack security update, with evidence.

1. Re-read current main and governance, the final documentation branch, open PRs,
   package.json, bun.lock, Lovable configuration, native test commands and CI status.
   Complete applicable NAADF-CMF intake/impact/safety records.
2. Verify the official advisory and currently compatible patched version set.
   Inspect transitive resolution and Lovable compatibility. Do not hand-edit a
   generated lockfile or introduce a broad framework upgrade by assumption.
3. Prepare a separate focused candidate after applicable gates are satisfied.
   Run frozen install, typecheck, lint, unit and build with explicit isolated
   configuration; add only meaningful regression/security checks for the change.
4. Record final head, diff, results and unexecuted checks; obtain separate review
   before proposing merge. If native verification cannot execute, retain a blocked
   draft with the exact tool/network/runner cause and next action.

Allowed implementation scope after gates: dependency declarations/generated lock
and strictly necessary compatibility changes/tests, each justified.
Excluded: UI redesign, financial formulas, schema/RPC/RLS, production access,
provider billing, automatic merge/deploy, bypassing deployment security checks.
Success: resolved affected packages outside advisory range, compatible build,
required final-source checks and review with no blocking findings.
Reverting to vulnerable packages is not an acceptable production rollback:
keep production unchanged while candidate is unaccepted; choose a verified safe
version or revised forward fix if compatibility fails.

### PRIMARY-ENV-001 — following packet

Evaluate/reconcile PR48 on current main, verify its current diff, reviews and checks.
Confirm SEC-CI status from actual history and workflows, not stale task checkboxes.
Prove fail-closed isolation for all write-capable harnesses before executing them.
Preserve existing tests and record real failures separately from unavailable runners.
Do not blindly copy PR48 or reopen already accepted design decisions.

After these three packets, calibrate effort and remaining timeline from real results.
A blocker permits independent authorized read/design work, not dependent unsafe execution.

## Financial acceptance and unresolved decisions

Retain DEC-003 through DEC-014. Resolve missing policy before dependent changes:
recognition/profit, inventory cost, opening balances, money precision/currency,
settlement method/fees, returns/refunds/corrections, cutoff and day close,
scope of accounting/tax claims, and SaaS revenue/entitlement.
Prior accepted decisions are reused, not repeatedly sent to the owner.

Minimum examples to turn into tests:
- invoice100, collect40 then60 -> debt60 then0 in storage/report/close;
- stock10, sell2, return then delete -> stock10, never12;
- pending/returned/cross-tenant settlement -> rejected without effects;
- courier collects60 of100 -> custody60, debt40, store receipts0;
  settlement -> custody0, receipts60, no new sale;
- store collection40 plus proposed custody100 on invoice100 -> invalid;
- duplicate/replayed/concurrent request -> one committed effect;
- failed/truncated reads -> no false zero balance or financial-health assurance;
- old invoice/new receipt/return in later period -> accepted metric definitions;
- restore -> reconciled records, balances, ownership and files.

Each finding record needs original ID, severity, source/head, proof category,
expected/actual values, dependency, owner, test, review and closure evidence.
Critical/High findings block acceptance; Medium needs a recorded disposition.
Multiple agents must not count the same defect as separate completed work.

## Operational and commercial completion

RC1 needs owner recovery, tenant isolation, audit/support, safe migrations,
complete data/reporting, Arabic/mobile/slow-network/error flows, backup and tested
restore, known limitations and one source identity for deployment.
Use independent expected values; a test that mirrors a bad formula is insufficient.

Pilot proposal: 3–5 stores, 2–4 weeks of observation, subject to prior owner
selection and measurable activity criteria. Time alone does not pass the gate.
Require no unexplained financial variance or confirmed duplicate/lost effects,
no tenant exposure, and successful core journeys without code intervention.
Measure first sale, usage, failed writes, support load, retention and willingness to pay.

Before charging, prove actual cost/payment eligibility, truthful plan limits,
cancellation/refund/expiry/export policy and sandbox event reliability.
Store sales are not Mongezz subscription revenue.
Human commercial/policy choices stay separate from routine engineering decisions.

## Session contract

One lead maintains state. Each authorized agent receives base, scope, file ownership,
expected output and stopping condition. No concurrent writers of shared files.
A fresh reviewer checks contracts and evidence rather than approving a summary.
No total-completion percentage without a defined accepted scope and measurement.
Every batch ends with actual changes, evidence, unverified items, blocker and ONE NEXT.
No repeated successful test or re-planning without a changed input or concrete risk.
