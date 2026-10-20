# G0/G1-ACCEPTANCE-01 — authorized bounded intake

Authority: owner instruction in #55/comment6163164423, execution claim #55/comment6163288583, 2026-10-14. Canonical repository: naderalhaje097070-sudo/simple-store-aid. Historical droid repository references in source54 do not override this owner instruction.

Goal: assess the smallest #51–#54 acceptance candidate against main; reuse unchanged evidence and close only missing G0/G1 verification. No merge, deployment or production access. This is an acceptance harness, not a declaration that the application is complete on main.

Baseline main43d6edbccb66fb06ce0fcb93734ad59532d1aeae; source54 57fb508b9d239aaf4676352dd97654341416c46a; separate comparison48 31958e53438b377a9896dd0bf7e9c268c1f14aef. Chain51 2b2b28589a85b9fa7bc3777aef3dde40dbfeb52d →52 13d81250122c890a98b0c94e4f07f2745bdb40ed →53 54c930166a776828566876771efdec86a997fa53 →54. Heads, claims and dependency bases checked before implementation. Existing #70/comment6153966539 comparison: 18paths, 8identical and 10explained changes; unchanged Git blobs permit reuse.

## Change and impact gate

Owner approved the bounded acceptance batch. Implementation reads existing application source; new files only: push workflow, structured command receipts, disposable runtime controller, source manifest, this intake. All383 original54 blobs remain exact, including 41SQL migrations. No source application, package/lock, generated authentication file, financial contract or existing workflow edits.

Eight impact areas: UI unchanged, only existing Auth smoke is invoked; application/API unchanged; data model unchanged; tenancy real2user positive/negative metadata checks in fresh local stack; financial formulas/contracts untouched and zero financial-flow execution; authentication unchanged with known old-banned-JWT G2 defect retained; environment/runtime checks use existing guard and actual Cloudflare SSR with matching/conflicting configuration; delivery adds bounded evidence with real audit/lint exit codes preserved.

Assumptions/limitations: Source54 is a stacked candidate, not integrated main. Existing Quality run38080476062 attempt2/job114311070422 exact54 proves frozen Bun1.2.14, typecheck, changed-file lint, 60unit/125expect, 8wrapper stub and 67dummy-browser transport checks, mode-env builds. It does not prove full lint, fresh audit, real Auth or G2–G6. PR53 archived official Bun1.4.0 targeted lock provenance is reused because package/lock are byte-identical; fresh frozen installs verify consumption without adopting today's drifting resolution.

## Scope, checks and acceptance

New independent jobs: fresh audit/full lint without converting failure to pass; unchanged SECENV Gate4 and write-target preflight/AST checks only; CLI2.101.0 fresh41 local schema, two fictitious Auth/tenant fixtures, unchanged Auth desktop/mobile smoke, actual default Cloudflare SSR match and named mismatch denial. Build/provider packages already locked; emulator tool Wrangler4.149.0 and Playwright1.62.0 pinned separately. No real provider, financial write script or production endpoint invoked. Native worker UID IPv4/IPv6 reject rules, precredential canary, browser existing exact-origin/HTTP/WS guard, private credentials/logs, receipt scan and cleanup verified.

Mandatory failure is an unmet gate, not a waiver. G2 known ENV-NATIVE-01: source54 ban prevents new login but preissued JWT retained own-tenant access; original evidence stays known, no #59 fix copied. #49/#50 and whole account chain #56–#71 are excluded. G6 financial acceptance requires separate authorization. Unresolved advisories/full-lint failures block G0 even when inherited; no broad repair or test weakening within this batch.

Actual need for new branch: source54's stacked base does not trigger the main-only SECENV/Auth/SEC-CI workflows. Existing SEC-CI workflow includes unauthorized financial flows. New isolated push harness executes only authorized missing checks. One Draft may carry this minimal harness above54; do not retarget existing PRs or main merely to cause financial jobs. Compare the full application candidate to main in the report. A passed bounded check is not a substitute for pending financial/release gates.

## Review, rollback and handoff

Independent reviewer checks source retention, runtime isolation and actual logs/receipts; record which checks they rerun. Preserve failed attempt evidence. Rollback is discard the isolated harness branch after planning decides; no data migration or original branch history change exists. Cleanup stops fresh stack without backup and removes credentials and worker processes. Final short #70 summary and #55 handoff link carry exact SHA, gates, #48 recommendation, blockers and one next step. Stop at delivery to planning; do not close #48, merge or deploy.
