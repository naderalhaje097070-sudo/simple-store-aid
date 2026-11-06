# Acceptance matrix — implementation pending

The current executable oracle remains unchanged and failing. After explicit contract adoption, replace the ambiguous single check with TWO mandatory evidence layers: unchanged raw legacy gross135 AND server-view net130, plus existing UI net130 and all other fields. Do not merely switch130to135. Preserve original raw ZIPs and provenance.

| Case | Required evidence |
|---|---|
| Frozen fixture | sales275,collected225,expense5,gross135,net130,debt0,custody0,stock7.75 |
| Zero/negative/decimal expense vectors | Exact independent literals in acceptance-vectors.json; no zero clamp/new rounding |
| Fresh chain | All55old migrations exact, generated56 applies; view/types/API work |
| Populated upgrade/history | Existing row hashes/counts/gross/expense bytes unchanged; derived net uses saved snapshot |
| Live data changed after old close | No reconstruction of historical net from mutable current payments |
| Reclose/replay | Legacy upsert behavior unchanged, no extra cash/debt/stock effects; net reflects saved row once |
| Tenant/actor | Active owner own rows and unaffected actor positives; foreign/inactive/anon negative through SQL role AND actual Data API |
| View write attempts | Authenticated INSERT/UPDATE/DELETE denied; base permissions unchanged, not misrepresented |
| View unavailable/read failure | Existing read-state boundary surfaces the error; no empty/zero/open-day healthy fallback |
| Admin/old API | Legacy response shapes and scope unchanged; gross label explicit |
| UI desktop/mobile | Existing fractional/response-loss/collection/courier/return/expense journey, both modes; explicit net/gross checks |
| Network/publication | All source/credential/cleanup/egress and zero unexpected request assertions retained; blocked_external remains open |
| Tool/build | Exact-head typecheck/lint/unit/build/source checks, native evidence and independent review |

This design batch validates Decimal arithmetic of proposal vectors only. It does not create a financial regression test, prove Postgres syntax/RLS/runtime, or claim a green C5. New implementation tests belong to the adopted final candidate; avoid rerunning historical suites without source/scope reason.
