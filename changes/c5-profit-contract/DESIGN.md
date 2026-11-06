## Superseding decision — 2026-11-06

C5-PROFIT-BASIS-01 is now **ADOPTED** by the lead under the owner's explicit scoped delegation after two actual financial/programming ADOPT reviews. See [DECISION_ADOPTED.md](DECISION_ADOPTED.md), [financial review](REVIEW_DELEGATED_FINANCIAL.md), [engineering review](REVIEW_DELEGATED_ENGINEERING.md) and [approved implementation intake](IMPLEMENTATION_INTAKE.md). Earlier pending-owner/design-only notices below describe the prior batch and are superseded for this precise decision.

The additive gross/net view is selected; include the two reviewed presentation corrections, required-value/read-state handling and explicit layered55→56 admission in implementation. Implementation remains Planned and untested, not claimed from this decision. Merge/deploy/destructive/new-cost/security-bypass boundaries remain unchanged.

---

# C5-PROFIT-BASIS-01 — concrete owner decision proposal

Status: **PROPOSED, NOT FINANCIALLY ADOPTED OR IMPLEMENTED**. Date2026-11-06 Africa/Tripoli. Source4f7aec69077fa6df9f468c9942008fe33f683adf, existing integration/g0-g1-reconcile-2026-10-18. Owner-directed design batch C5-PROFIT-CONTRACT-DESIGN-01.

## Recommended contract

Preserve the existing stored field and old RPCs. Add a separate, explicitly named net reporting projection over recorded snapshots.

| Meaning | Contract field | Existing fixture |
|---|---|---:|
| Legacy stored payment-weighted margin before expenses | day_closes.realized_profit | 135 |
| Explicit alias of that recorded margin | realized_margin_before_expenses | 135 |
| Net derived once from the recorded margin and recorded expenses | realized_net_profit | 130 |
| Recorded expenses | expenses | 5 |

Net = recorded before-expense margin − recorded expenses. Numeric arithmetic, no new rounding or zero clamp. Negative net remains negative. This is a snapshot-derived reporting contract, not an audit certification of historical input correctness.

**Concrete owner decision requested:** adopt this split, preserving the legacy field/API meaning and adding the net projection. Do not silently reinterpret135as130 in old stored rows. This proposal also explicitly preserves the130net requirement: no green-check-only replacement of130with135.

## Why this option

| Option | Compatibility/history effect | Recommendation |
|---|---|---|
| Change existing realized_profit to net in close_day | Changes the meaning consumed by existing hooks/admin/API; historical rows mixed unless versioned or corrected | Do not choose silently |
| Add a stored/generated net column | Preserves legacy meaning but introduces base-table ALTER/rewrite/lock and generated-type work | More intrusive than needed |
| **Read-only invoker view with explicit gross/net names** | No stored-row update/backfill, legacy contracts unchanged; net derived from the same saved snapshot | **Recommended** |
| UI-only subtraction or simply expect135 | Leaves reporting semantics ambiguous or discards the net requirement | Reject |

## Proposed additive SQL shape — not an applied migration

The implementation must first confirm this new name is absent in the actual isolated catalog. Use the pinned CLI's help and migration generator to create the real forward-only file; no migration timestamp is invented by this design.

```sql
CREATE VIEW public.day_close_profit_report
WITH (security_invoker = true)
AS
SELECT
  dc.id, dc.tenant_id, dc.closed_for,
  dc.sales, dc.collected, dc.expenses,
  dc.realized_profit,
  dc.realized_profit AS realized_margin_before_expenses,
  dc.realized_profit - dc.expenses AS realized_net_profit,
  dc.customer_debts, dc.unsettled_custody,
  dc.note, dc.created_at
FROM public.day_closes AS dc;

REVOKE ALL ON TABLE public.day_close_profit_report
  FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.day_close_profit_report TO authenticated;
```

No SECURITY DEFINER helper, no table-policy alteration, no new public write operation. This simple view may be automatically updatable by PostgreSQL; SELECT-only grants are therefore mandatory, not optional. Base-table privileges/RLS remain independently relevant. Ordinary owner INSERT/UPDATE permissions already exist on the base table; this packet does not claim RPC-only base protection or change those permissions.

## Consumer behavior after approved implementation

1. Keep close_day, get_tenant_today_estimate and get_platform_day_close_health signatures/results and the old realized_profit field unchanged.
2. Read saved day closes via the new view; retain DBDayClose.realizedProfit as a documented legacy before-expense property for compatibility, and add explicit realizedMarginBeforeExpenses / realizedNetProfit fields.
3. Preserve current date/closedFor behavior used by app/pilot. Propagate the new fields through the actual DayCloseRow type rather than bypassing it.
4. Label platform-admin's unchanged legacy135 column as margin before expenses. Do not grant ordinary tenant users the admin's cross-tenant RPC scope or route that admin RPC through the new tenant view.
5. Label general ProfitScreen's existing computation as **estimated net after expenses**. Its invoice-period paid-ratio estimate is not universally identical to a payment-date cash-basis day-close snapshot. No broad reallocation algorithm rewrite in this batch.
6. Day-close preview retains its existing payment-date net arithmetic; correct the misleading comment to refer to the net reporting projection, not the unchanged gross close_day return.
7. Future current-today consumers must not treat get_tenant_today_estimate.realized_profit as net. There is no current in-repo caller of useTenantTodayEstimate in the scanned source, but external callers are unknown; retain its legacy mapping and document it.

## Stronger acceptance contract

The existing failed archive remains immutable. The approved replacement comparison must separately require legacy stored margin135 AND server-projected net130 AND displayed net130. Keep all other fields, stock/debt/custody/replay assertions. This is an explicit contract split with stronger gross/net checks, not an unexplained old130→135 waiver. Until adoption and implementation, leave the current executable test untouched and failing.

## Fixed next stages

| Stage | Deliverable | Exit evidence |
|---|---|---|
| 1 Evidence extraction | Existing first-failure packet | Complete on4f7aec69; no rerun |
| 2 Impact/design/review | This concrete contract, source inventory and acceptance matrix | Current batch |
| 3 Owner contract adoption | Approve the exact split above or choose another reviewed meaning | Protected decision, OPEN |
| 4 Isolated implementation | Additive generated migration/view, typed consumers/labels, explicit source admission | No main/production change |
| 5 Targeted native acceptance | Fresh55→56 and populated55→56, gross/net/security/history + actual desktop/mobile | Exact final source; all required checks |
| 6 Remaining C5 then full C6 | Resolve network attempts/remaining journey without waivers; independent whole-candidate review | No unresolved blockers |
| 7 C7 owner merge then main verification | Smallest final financial package; verify actual main before settling five original PRs | Explicit owner merge; RC/Pilot separate |

## Bounds and historical meaning

All seven source close_day bodies store before-expense margin. However authenticated owner direct base-table writes and privileged/external writers exist or may exist; source does not certify every historical/manual row. The view derives from recorded legacy values only, without reconstructing old payments or altering a byte of old rows. Contradictory historical/manual provenance blocks treating derived values as audited facts and requires separately authorized assessment, not invented corrective backfill.

New view grants must preserve base row visibility for active owners/staff and deny inactive/foreign/anon access in the actual isolated runtime. No service-role-only test can prove user RLS.

## Public technical references checked

- [PostgreSQL17 CREATE VIEW](https://www.postgresql.org/docs/17/sql-createview.html): invoker privileges/RLS, nonmaterialized projection, automatic update behavior.
- [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security): grants and policies both matter.
- [Supabase changelog](https://supabase.com/changelog): checked current CLI breaking changes. Keep repository CLI2.101.0 pinned; no opportunistic CLI3 upgrade or flag migration in this task.

Only source review/design and decimal acceptance-vector validation have run. No new Postgres/view/RLS/migration/native implementation is claimed.
