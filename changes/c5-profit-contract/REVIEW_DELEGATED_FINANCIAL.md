# Independent financial decision review — /root/financial_decision

Requested explicitly by owner at the pending decision stage; actual separate read-only agent. Reviewed live1c8f43c76471332bb80248929a47a66a1c80af8e, AGENTS, design/data/test packet and actual SQL/UI/db consumers. No files, GitHub, SQL, workflows or data modified; no native tests.

Verdict: **ADOPT**, with precise collection-based operational terminology and two bounded presentation corrections.

Source findings:
- supabase/migrations/20261010223557_enforce_live_account_state.sql240–258 allocates item margin to payments and records expenses separately;260–272 reclose updates the snapshot.
- app.tsx2542–2553 already subtracts expense in close-day preview.
- db.ts782–820 preserves the old reader meaning; platform-admin510–527 needs an explicit before-expense label.
- ProfitScreen54–59 displays payment-period collected beside invoice-period ratio-based realizedCogs, so its displayed equation can be false.
- ProfitScreen86–89's debt+custody equality is false. A sale100/cost40/payment50 has profit gap30 but debt50; identical expense subtraction does not repair that equality.

Recommended split: retain old payment-weighted before-expense margin, add its explicit alias and net=saved margin−saved expense once. Fixture225collected−90allocatedcost=135margin;135−5=130net. Preserve old APIs/rows, no backfill/new formula/clamp/rounding. Historical/manual source validity is unproved, and the projection is not an audit certificate or statutory profit statement.

Use existing realizedRevenue for the invoice-period estimate if actually available; engineering/root source reread confirms it is locally computed but must be exposed through returned totals and AppTotals. Keep collected separately labelled. Replace equality with separate-balance explanation. Include prior-invoice collection today and distinct time scopes in acceptance without changing allocation algorithms.

Acceptance: raw135+server130+UI130; historical stability, actor/tenant permissions, reclose/replay, desktop/mobile and date-basis tests. Financial source/design review only, not native acceptance. Delegated lead adoption allowed for this precise decision; no merge/deploy authority.
