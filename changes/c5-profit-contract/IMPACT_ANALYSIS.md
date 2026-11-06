# Source impact inventory

Exact source4f7aec69. Read all130 code files under src/ and supabase/functions (matching ts/tsx/js/mjs/cjs/sql), plus all55 applied-source SQL files. Seven source files match the combined profit/day-close terms, including PilotScreen close-date-only usage. There are no scanned edge-function matches. This is a repository-source inventory, not a claim about deployed external callers or manual SQL.

| Source | Current role | Proposed handling |
|---|---|---|
| src/lib/db.ts:191–209 | Legacy today estimate gross mapping | Preserve mapping/RPC shape; document before-expense basis; no current internal hook caller |
| src/lib/db.ts:782–820 | Saved close reader and DBDayClose | Use new view with old field/property retained; add explicit gross/net fields |
| src/features/shared/AppContext.ts | Totals / DayCloseRow contract | Propagate explicit saved-row metrics without relabeling invoice-period estimate as cash snapshot |
| src/routes/_authenticated/app.tsx:300–302 | Closed-date detection | Preserve closedFor/date behavior |
| src/routes/_authenticated/app.tsx:370 | General estimated net | Keep existing invoice-period arithmetic; explicit estimated after-expense label |
| src/routes/_authenticated/app.tsx:2542–2553 | Day-close preview cash-basis net | Keep values and scope; correct comment describing relation to gross legacy RPC |
| src/features/reports/ProfitScreen.tsx:42–50 | Estimated profit display | Clarify net-after-expense label; keep estimate disclaimer |
| src/features/pilot/PilotScreen.tsx | Close-date counts only | Regression: unchanged counts/latest date |
| src/routes/_authenticated/platform-admin.tsx:471–527 | Privileged legacy report135 | Keep admin RPC signature/scope; label before-expense margin explicitly |
| src/integrations/supabase/types.ts | Generated table/RPC types | Generate new View types from actual isolated schema; never edit generated output manually |

Current effective monetary writer is close_day in20261010223557_enforce_live_account_state.sql. Historical definitions and cleanup/delete paths remain immutable; no writer modification recommended for this option. Base owner direct INSERT/UPDATE grants/RLS exist, so historical/manual basis cannot be certified from source. Detailed blob/line inventory in evidence/consumer-inventory.json. Security/API/data/migration/test/rollback records cover the affected boundaries.
