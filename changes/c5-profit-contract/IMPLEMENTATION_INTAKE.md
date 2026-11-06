# C5-PROFIT-CONTRACT-IMPLEMENT-01 — approved bounded intake

Status: **Planned / ready for isolated implementation**, not yet Implemented or Tested. Approved by delegated lead after two independent adviser ADOPT verdicts; authority/scope in DECISION_ADOPTED.md. No repeat owner decision needed for this exact contract. Merge/production/destructive/new-cost/security-bypass decisions remain protected.

Goal: implement the adopted collection-based gross/net reporting split without changing old data, RPC meanings or allocation algorithms; correct associated misleading presentation and prevent new report-read failure from masquerading as healthy/open.

Scope:
- Confirm absent view/catalog identity in isolated stack; generate forward-only56th migration using pinned CLI2.101.0 help/generator. Apply read-only invoker view/explicit ACL from DESIGN, no base-table edits/backfill.
- Typed generated view contract/required-value validation; db.ts legacy+explicit gross/net projection, typed DayCloseRow, unchanged invalidation identity.
- Existing read-state/retry boundary in affected day-close/pilot/close controls.
- Clear admin before-expense label; expose already computed realizedRevenue through AppTotals and returned totals; use it for ProfitScreen estimate detail, actual collected separate; remove false gap=debt+custody equality and stale universal-equivalence comments.
- Scoped regression/contract/security/history tests and explicit layered56/source admission across affected C5 harness boundaries. Retain every old55 proof and all unrelated source/security checks.

Out: changing close_day/get_tenant_today_estimate/get_platform_day_close_health signatures or financial allocation/writes; modifying old migrations/rows; unrestricted base-write hardening; new features; patching tests only to green; production data/secrets; PR expansion/closure/merge/deploy/release.

Risk: medium/high financial reporting/security integration; no cash/write formula change. Unknown external/manual historical provenance remains disclosed, not repaired.

Implementation ownership: one implementer/root. Adviser reviews do not create concurrent implementers. Independent review of actual final implementation required; current two reviews cover the decision/source design only.

Baseline: saved original C5 source122d8aa4/run42125234643 FAIL at raw realized_profit135 vs net130 expected; preserved byte-exact ZIPs. Earlier UI net and close_day HTTP controls passed; no transfer of acceptance to future code. Current55migrations/source admitters reject unadmitted financial delta; add explicit safety-net tests before implementation when feasible.

Acceptance/rollback: DECISION_ADOPTED.md and existing TEST_IMPACT/ROLLBACK_IMPACT. Require raw135+server130+UI130, no historical row changes, role/API/ACL denial/visibility, read errors/time/negative/decimal/reclose/API compatibility, fresh/populated and desktop/mobile. Safe native workflow exists; local host lacks Docker/Supabase. No native test yet run for this future candidate.

Resume: verify live branch/claims, take sole implementation claim, prepare exact delta/admission and tests, implement then verify; stop at a concrete result/blocker, not a repeat question asking whether the adopted split is approved.
