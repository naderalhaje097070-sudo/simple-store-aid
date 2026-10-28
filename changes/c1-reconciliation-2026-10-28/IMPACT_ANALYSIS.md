# Impact analysis

| Boundary | Current collision / required preservation | Planned action |
|---|---|---|
| App/data hooks | Main db.ts16e9e582 contains typed rpcClient, nullable-result checks and A read/error behavior;50 db.ts44c6c3ce is old and uses any casts | Transplant only the reviewed logical-sale boundary; preserve all unrelated main behavior; typed new RPC contract |
| Sale UI | SaleScreen/QuickSale + PaymentSheet do not submit explicit courier outcome; needsCustomer=remaining>0 differs from approved courier debt policy | Separate bounded C interface integration before C5; reuse invoice-selectors debt definition and approved outcome matrix |
| Schema |50 main SQL + two historical August candidates produce52 chronological source files; backdated append and fresh order differ | Keep every old blob immutable; one forward correction after latest accepted source; no current migration changed |
| Auth/tenancy | Accepted _assert_staff/current_tenant_id call live-actor checks; new canonical/idempotent call chain must preserve them | C3/C5 prove each reachable new/legacy RPC's grants and active/closed/banned/cross-tenant denials, including replay |
| Financial state | Integer stock vs numeric qty; delivered collection vs settled cash; returns/debt/custody | C2 quantity contract first; preserve formulas and existing approved business state rules |
| Idempotency | Unique reservation+exact JSON comparison remains useful; client TTL/single-slot/null clear loses identity | C4 persistent unresolved-operation state until definitive response or explicit reconciliation; no timeout-based correctness |
| CI/tests | Old27 workflow uses CLI latest and phase/baseline assumptions; old SQL often uses postgres with JWT claims | Preserve historical test bytes, do not reactivate old workflow; adapt pinned isolated B environment and real authenticated transport |
| Provider/release | No deployed provider, C, restore, RC or Pilot proof here | Remain outside this batch; no changed policy or external action |

Source inventories list67 historical file records:18 already exact on accepted main,46 absent and3 changed (db.ts plus two historical root state records). Only17 missing historical design/evidence Markdown blobs are restored at their original paths. Code/migrations/test/workflows stay in the exact replay ZIP and original branches until their bounded integration.
