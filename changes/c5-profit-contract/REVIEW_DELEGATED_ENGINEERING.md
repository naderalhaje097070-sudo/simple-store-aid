# Independent engineering decision review — /root/engineering_decision

Actual separate read-only programming/security agent, explicitly requested by owner. Confirmed live1c8f43c76471332bb80248929a47a66a1c80af8e. Read AGENTS, design/impact documents, actual consumers, all55 migration files and relevant C5 harness source. No files/GitHub/data/workflows changed; no native tests.

Verdict: **ADOPT** additive SELECT-only security-invoker gross/net projection. No blocking architecture defect found. Adoption does not mean implementation or native acceptance.

Evidence and conditions:
- Effective close_day SQL20261010223557_enforce_live_account_state.sql240–271 stores/returns before-expense margin. Old meaning must remain.
- Initial day_closes schema uses numeric NOT NULL. View type generation may still mark nullable: validate required values rather than Number(null) silently producing zero.
- Base authenticated DML/owner policies already exist; no RPC-only/historically-audited claim. Later restrictive live-actor RLS remains applicable through the invoker view.
- db.ts782–820 requires typed gross/net additions preserving legacy property/cache key; weak DayCloseRow needs explicit financial fields.
- app.tsx230,250–266,300–302 discards read state and treats missing data as empty/open. Preserve query state and reuse financialReadState/retry for affected day-close/pilot controls; avoid unrelated global blocking.
- Existing realizedRevenue at app.tsx366–370 is omitted from returned totals382–396/AppTotals37–50. Expose it for the current ProfitScreen estimate equation; no new formula. Correct false profit-gap=debt+custody wording.

Mandatory acceptance includes raw135/server130/UI130, fresh56/populated55→56 with row hashes, actual roles+DataAPI, view DML denial/catalog ACL/reloptions, unavailable/stale read behavior, decimal/negative/time/reclose/replay/API/admin and actual desktop/mobile.

Critical dependency: journey_identity.py12–19,52–80 admits only test-only delta and55migrations; native.py37–40 also calls prior collection source/history guards. Add a reviewed explicit layered financial delta/new55→56 upgrade while preserving old55 proofs. Never simply change the count or relax guards.

Local host currently lacks docker/supabase. Existing c5-journey.yml39–55,90–149 provides the isolated pinned CLI2.101.0/Docker/firewall path. Keep the existing pin; no opportunistic CLI3 migration. Full C5 and independent C6 remain pending.

Official primary references independently checked: PostgreSQL17 CREATE VIEW; Supabase RLS; current Supabase changelog. Simple views may be updatable: explicit SELECT-only grants and runtime negatives required.
