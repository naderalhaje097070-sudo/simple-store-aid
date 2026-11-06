# C5-PROFIT-BASIS-01 — adopted under specific owner delegation

Date: 2026-11-06 Africa/Tripoli. Decision maker: /root, technical lead. Source reviewed: 1c8f43c76471332bb80248929a47a66a1c80af8e; integration/g0-g1-reconcile-2026-10-18. Decision batch C5-PROFIT-DELEGATED-DECISION-01, claim6687511352.

## Authority and status

The owner's direct instruction after the concrete proposal was: «انت المسؤول عند مرجله اتخاذ القرار شغل ما يلزم من ايجنت مالي و برمجي اتخاذ افضل قرار».

This specifically delegates the pending profit-contract choice to the lead with financial and engineering advisers. Two actual separate read-only agents supplied independent source-backed ADOPT verdicts. The lead now **ADOPTS** the bounded contract below. The former owner-adoption blocker is resolved for this choice; no repeat owner approval is required for its routine isolated implementation. This does not grant general financial-policy authority, protected merge, production deployment, destructive operations, new expenditure or security/governance bypass.

**Financial/report contract: ADOPTED. Implementation: Planned, not Implemented/Tested/Merged/Released.**

## Adopted meaning

| Contract | Meaning | Original fixture |
|---|---|---:|
| Existing day_closes.realized_profit / old realizedProfit mapping | Recorded payment-weighted item margin before recorded closing expenses | 135 |
| New realized_margin_before_expenses | Explicit alias of that recorded margin | 135 |
| New realized_net_profit | Recorded margin minus recorded expenses, exactly once | 130 |
| Existing expenses | Recorded closing expenses, retained separately | 5 |

Formula: net = saved realized_profit − saved expenses, using PostgreSQL numeric semantics. Do not add rounding, a nonnegative clamp or a second expense deduction. The figures are a fixture, not hardcoded production values.

This is an operational metric on a collection-and-allocated-cost basis. It is not a claim of statutory/accrual-accounting net income. close_day can upsert/reclose; the snapshot is not being made immutable by this change. Sales, collections, customer debts, courier custody, settlements, returns and stock retain their separate existing contracts.

## Chosen implementation

Adopt the additive SELECT-only security-invoker view shape already set out in DESIGN.md, keeping all old RPC signatures and meanings. Keep old rows byte-identical: no UPDATE/backfill/reconstruction from today's mutable invoices or payments. Maintain tenant/date behavior and admin cross-tenant scope. Document admin's old135 field as margin before expenses. Historical/manual provenance is not established by code review; derived net does not certify historical input correctness.

Explicitly revoke all PUBLIC/anon/authenticated privileges on the view, grant authenticated SELECT only, and prove invoker/RLS/live-account effects with actual SQL roles and Data API. Do not infer read-only behavior from a simple view's syntax. Base-table direct-DML grants are not newly hardened or certified here.

Retain the typed legacy field and add explicit gross/net fields through DBDayClose and DayCloseRow. Generated view nullability must not be hidden by Number(null), arbitrary casts, defaults or a zero amount. Reuse the existing financial-read state/retry boundary for missing/error/stale view reads; day-close/pilot/close controls must not treat unavailable data as empty, healthy or an open day. Avoid blocking unrelated screens.

## Two bounded presentation corrections adopted

1. app.tsx366–370 already computes realizedRevenue, but its returned totals382–396 and AppTotals omit it. Expose that existing value through totals/types; use it in ProfitScreen's invoice-period paid-ratio estimate. Keep actual payment-period collected as a separately labelled cash fact. Do not change the estimate formula, payment-date logic or invoice selection.
2. Replace ProfitScreen86–89's false equality between the profit gap and debt+custody. Debt and custody are separate current balances. Example sale100/cost40/paid50/expense5: full net55, estimate25, gap30, debt50. This is not an equality. Label the estimate and saved collection-based net distinctly.

Also correct the old app comment claiming its invoice-period estimate universally matches close_day. It does not imply a new accounting/reallocation algorithm or universal equality across dates.

## Nonnegotiable acceptance

- Same original fixture: raw legacy135 AND server projected net130 AND UI net130, with sales275, collected225, expense5, debt0, custody0 and stock7.75 retained. Do not merely replace130with135; keep old failed ZIPs/oracle provenance.
- Exact-source clean56 and populated55→56 migration. Save row hashes/counts before and after; preserve every old55 migration. Generate the new migration with pinned CLI2.101.0 after --help; no invented timestamp.
- Explicit layered admission for application/schema changes. Current journey_identity admits test-only deltas and55 migrations; native also invokes prior collection/history guards. Preserve original55 proofs; do not disable a guard, broaden exclusions or merely change55to56.
- Owner/staff allowed rows, foreign tenant/inactive/anon negatives, SQL roles AND Data API, view writes denied, catalog ACL/reloptions inspected. Service-role reads are insufficient.
- Decimal/negative values, reclose/replay, historical snapshot stability, previous-invoice payment today, tenant timezone boundaries, legacy API/admin compatibility, missing/error/stale read, actual desktop/mobile.
- Typecheck/lint/build and scoped relevant regressions on the actual final source, then independent implementation review. Existing C5 network/unexpected-request gates stay mandatory.

## Order and exit boundaries

1. This decision is complete and ready for implementation; see IMPLEMENTATION_INTAKE.md.
2. Execute one bounded implementation batch: additive generated migration, typed/read-state consumers and the above labels/mapping, plus exact source admission and regression/contract coverage.
3. Verify fresh/populated/security/history/desktop/mobile on the candidate. Existing safe native GitHub runner is the established execution path; current local host has no Docker/Supabase. Neither native availability nor results are implied.
4. Complete remaining C5 journey/network gates, then full independent C6, then protected owner C7/main verification/settle original drafts. RC/Pilot remains separate.

Rollback remains clients first, then a separately generated forward compensation DROP VIEW ... RESTRICT, no CASCADE or row/history rewriting. No source, SQL, data, oracle, workflow, dependency or runtime modification occurred in this decision batch.
