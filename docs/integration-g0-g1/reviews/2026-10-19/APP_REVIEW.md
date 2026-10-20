# MONJEZ independent application/contracts review — 2026-10-19

**Scoped verdict: Changes required.** No introduced executable defect was confirmed in the nine-file integration type/refinement delta. The inherited application still has a High financial-read presentation defect. Paid billing also has an existing High persistence/error-handling defect. Two existing Medium defects require a decision before merge under REVIEW_PROTOCOL.md. This is not financial database, account lifecycle, CI, deployment, or production approval.

## Exact scope and independence

- Canonical private repository: `naderalhaje097070-sudo/simple-store-aid`, accessed read-only using the owner-selected GitHub connector account.
- Reviewed executable source: `823cbcaf4a83ae8b4bea44e314df4c1215a9ba3b`.
- Reviewed documentation head: `1028441558e7db7b0b25390f2b8ee452b702774b`. Exact connector compare shows one descendant commit, 28 changed documentation/state/evidence paths, no application source change.
- Original PR72 source: `6da4dadbe9391bb48c8c4c41dcb688728003fb81`; inherited application baseline54: `57fb508b9d239aaf4676352dd97654341416c46a`.
- Parent review supplied unchanged main `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`; this subreview did not independently re-fetch main or claims55/70. No self-implementation review is imported as independent acceptance.
- Read AGENTS.md, current top PROJECT_STATE/TASKS/DECISIONS, REVIEW_PROTOCOL, integration REPORT/API_COMPATIBILITY/CHANGED_FILES/REVIEW_REQUEST. The explicit canonical repository instruction supersedes AGENTS' historical droid name.
- No product edits, repository mutations, merges, deployments, CI reruns, provider requests, database requests, production reads, credentials, or network fixtures. Only this report is written. Node fixtures ran entirely in memory.

Remote-pinned source, rather than the partial local directory's apparent state, determined attribution. Local `source72` inputs used for fixtures were Git-blob hashed first. Its app blob is exactly original72 `6c73cdc377a9bbf9f2566ff5570b925c0af115ff`; candidate app differs solely in `new Set<Invoice["items"][number]["productId"]>()`, erased at runtime. Original72 db/billing/webhook blobs are also exactly baseline54 blobs. Thus their defects below predate both the integration and PR72.

## Findings

### APP-01 — incomplete financial reads become healthy zero balances

**Severity: High. Classification: existing, already tracked risk; not introduced by this integration.**

**File/contract:** `src/routes/_authenticated/app.tsx:181–212,278–330,665–684`; `src/lib/db.ts:446–479` at823.

**Evidence:** The invoice/payment/expense queries expose error/loading state, but MongezzApp destructures only `data` and maps undefined to empty arrays. Finance selectors and totals then treat these arrays as complete. DebtsScreen renders total0 and the positive message `لا ديون مستحقة — ممتاز 👍` when invoices are absent. Current customer-loading propagation does not cover invoice/payment/expense completeness.

An offline fixture executed the actual MongezzApp declaration with read hooks returning `{data:undefined,isError:true,error:Error('fixture read failed')}`. The resulting child context contained `invoices:[]` and every financial total0, including customerDebts/unsettledCustody/collected. Executing the actual DebtsScreen declaration with that context rendered money0 and the no-debt success state. This is not a hypothesized malformed RPC response; it is an ordinary initial/failed query state.

Baseline54 contains the same data-only destructuring and empty-array conversion. The docs' already-open “incomplete invoice-read handling” limitation is accurate; the missing-customer9-case proof does not resolve it because those scenarios always supply invoice evidence.

**Risk:** An unavailable or incomplete read can reassure an owner that no money is outstanding or show misleading totals. A customer metadata fix and a green auth/environment smoke do not establish financial-read correctness.

**Required fix:** Carry financial query completeness/error state into financial screens and actions. Render a clear unavailable/loading state; retain known cached amounts with an explicit stale/incomplete indication where appropriate. Show genuine zero/healthy status only after complete successful reads. Do not discard rows or invent amounts to satisfy this rule.

**Verification:** Actual container plus rendered component cases for initial load, invoice-only failure, payment-only failure, expense-only failure, cached-data refetch failure, partial dependency recovery, and complete successful empty data. Assert known debt60 remains visible or explicitly unavailable, never a healthy zero. Backend financial correctness remains separate.

### APP-02 — subscription persistence errors are acknowledged as success

**Severity: High before paid-billing acceptance. Classification: existing on54/original72; not introduced by type refinement.**

**File/contract:** `src/routes/api/public/payments/webhook.ts:65–90,99–131,158–160` at823. Candidate blob `26f6e0592a5337a929c9a2e0fafdb20872e0e526`; original72/base54 blob `c83bab07ae319dee2a659a4bb6f0a576b9b9d832`.

**Evidence:** None of the subscriptions upsert/update or tenants update results checks its returned `error`. A failed first write does not stop a second write; handleWebhook completes and POST returns200 `{received:true}`.

An offline fixture executed the actual candidate route callback with a synthetic verified subscription-created event and valid tenant/owner lookup. Its supplied subscriptions upsert result was `{data:null,error:{message:'fixture DB write failed'}}`; the tenant update succeeded. Observed calls were subscriptions upsert then tenants update, followed by HTTP200 `{received:true}`. No provider or database existed in this fixture. Existing AST/runtime equivalence confirms the fault predates the integration.

**Risk:** Subscription row and tenant status can diverge after partial failure while the endpoint reports successful handling. BillingPage reads subscriptions, while the webhook separately maintains tenant subscription fields. This review does not assert that current authenticated routing enforces paid entitlements; the inspected authenticated route checks authentication/tenant presence, not subscription state. The defect blocks claiming paid-billing reliability, independently of foundation smoke results.

**Required fix:** Check every persistence error and make event application durably retryable/idempotent, with an explicit consistency boundary for subscription and tenant state. A mere type annotation cannot establish atomicity or event-order safety. Do not report success before the required durable work succeeds or is durably queued.

**Verification:** Offline handler cases for each write failure, plus isolated persistence tests for partial failure, repeated delivery, stale/out-of-order events, cancellation, and environment separation. Real provider verification remains unperformed and separately required before paid billing.

### APP-03 — billing trial status reads a field its query never returns

**Severity: Medium. Classification: existing; the integration's new assertion conceals the incomplete projection.**

**File/contract:** `src/lib/db.ts:67–90`; `src/routes/_authenticated/billing.tsx:91–93,117–118,175–187` at823.

**Evidence:** BillingPage calls useTenant, whose projection and returned object contain only id/name/timezone/business_type. It never selects or returns `trial_ends_at`. New `type TrialTenant = typeof tenant & {trial_ends_at?:string}` plus assertion does not add that field. Generated schema explicitly defines the real tenant column as `string|null` (`src/integrations/supabase/types.ts:860`).

Actual candidate useTenant queryFn was executed against a fixture row with `trial_ends_at:'2099-01-01T00:00:00Z'`. The recording client enforced the actual selected columns. The returned object had no trial field, and the unchanged billing condition selected the expired-trial branch in the absence of an active subscription. The original72/base54 hook and billing behavior are identical.

**Risk:** A tenant with a valid free trial sees “انتهت التجربة المجانية” and a subscription prompt. This is a UI/status correctness problem, not proof of an authorization bypass or access revocation.

**Required fix:** Select and return the field through a truthful shared contract, or use an appropriate focused subscription/trial query. Distinguish unavailable/loading status from expired. Remove the assertion as a substitute for data retrieval.

**Verification:** Execute the actual query and billing component with active/expired/null trial, active subscription, and query failure/loading. Check selected columns and rendered state, not only compilation.

### APP-04 — day-close preview caches the previous timezone

**Severity: Medium. Classification: existing on54/original72; concrete meaning of the inherited tenantTz Hook warning.**

**File/contract:** `src/routes/_authenticated/app.tsx:2345–2384` at823; `useUpdateTenantTimezone` invalidation at `src/lib/db.ts:119–130`.

**Evidence:** DayCloseScreen's memo reads tenantTz but depends only on invoice/payment/expense/rawTotals/totals references. The parent totals memo also omits timezone/todayKey/period from its dependency list (`app278–330`), allowing those references to remain stable after a timezone-only settings refresh. Updating tenant timezone invalidates tenant/today-estimate queries, not the financial arrays.

An in-memory replay of the actual DayCloseScreen declaration implemented React's Object.is dependency comparison and fixed now at2026-10-19T03:00Z. Invoice100 created2026-10-18T23:00Z is outside today's UTC window and inside today's America/Los_Angeles window. First render UTC produced sales0. Re-rendering with only timezone changed and all listed dependency references unchanged kept sales0. Clearing the memo and rendering the same Los_Angeles props produced sales100. No database write was run.

**Risk:** The displayed day-close preview can disagree with the server's current tenant-timezone calculation until another dependency changes or the screen remounts.

**Required fix:** Make the memo dependencies/date-boundary inputs reflect all values used, and verify the parent totals' date/period dependency contract. Use existing shared finance logic rather than adding competing formulas.

**Verification:** Actual rendered day-close/container tests for timezone-only refresh and day rollover, stable data references, and subsequent close-day result comparison in an isolated database. This review does not certify the server close-day formula.

## Contracts checked and rejected hypotheses

- Independently compared emitted runtime ASTs for db, invoice-pdf, paddle, InvoiceDetailScreen, shared/types, billing, webhook, and email queue against original72, plus exact app emitted-JS equivalence. Only the exact same-client alias, two exact null-TypeError additions, and queue alias were normalized. All9 passed. The implementation's supplied AST test was read but was not used as independent approval; its own baseline is d0a172, not original72.
- `rpcClient` is the same `supabase` object, not a newly configured client. SQL result shapes and nullable arguments were inspected against remote-pinned migration definitions:27201534 today/sale,28105459 delete_product_safe,26233231 courier state. Current SQL today/sale keys match the refined shapes; sale number is integer JSON and order_id UUID string. Nullable arguments do not imply that every null-containing business combination is valid.
- The actual today callback rejects null and propagates query errors; sale rejects null and retains p_paid40, item qty2, customer/courier nulls and wire RPC name. A synthetic `{}` today result still maps missing values to zero, but that behavior predates the delta and the pinned SQL always constructs those keys. It is not a separately asserted current server-schema defect. APP-01 is the ordinary read-error counterexample.
- Stored order_items.product_id is truthfully nullable in generated schema; DBInvoiceItem and shared StoredInvoiceItem propagate it while new-sale/cart InvoiceItem requires string. InvoiceDetail/PDF use snapshot name/qty/price, not a forced product lookup. Recent-product Set now accepts the true type; null finds no matching string product and is skipped. No zero-price substitute or discarded stored invoice was introduced by this type change.
- Invoice PDF removes obsolete DOM ts-ignore uses and adds a comment to an already empty catch. Independently emitted-runtime equivalent; export/printing/layout/font behavior was not visually or browser-verified here.
- Local installed Paddle node SDK3.8.0 notification classes support event discrimination, nullable price/product/currentBillingPeriod/importMeta, customData and scheduledChange fields used by the route. Local email-js0.1.0 EmailSendRequest supports the derived queued sender fields. Package versions match candidate bun.lock. These were read-only installed type inspections, not a fresh package-integrity/install proof.
- Email queue enqueued_at initially looked absent in the earlier email-infra function. That hypothesis was rejected after inspecting remote-pinned later migration20260717180906 (blob81d0bfa72c2a59333591ed2236931c4623a740f3) and generated read_email_batch return type: both include enqueued_at. The message JSON assertion is not runtime payload validation; actual provider send/retry/concurrency safety is not established by typecheck.
- Browser Paddle API is a hand-declared global for an unpinned remote v2 script, not verified by the installed Node SDK. AST equivalence establishes unchanged invocation behavior only. No real browser checkout/provider test was authorized or performed.
- The inherited dashboard paid-ratio calculation differs from day-close payment-date allocation, but ProfitScreen explicitly labels it an estimate based on payments for invoices of the selected period and says later unification remains pending. This review does not elevate that disclosed difference into an introduced integration defect or approve its financial definition.
- AddProductSheet emitted runtime AST is identical from baseline54 to823. Every valid initial product field used by its sync effect is represented in the existing field dependencies. The lint warning alone did not establish a second concrete Hook defect; no finding is fabricated from the warning count.

## Verification actually rerun

| Check | Actual independent outcome |
|---|---|
| Remote SHA-pinned fetches and docs-head compare | PASS; doc-only publication confirmed |
| Local original72 source Git-blob identity | PASS for fixture app/db/PDF/Paddle/detail/billing/webhook/queue/schema inputs |
| Independent emitted-runtime comparison |9files PASS, plus AddProductSheet54→823 PASS |
| Exact candidate RPC callbacks | Valid today, null today, supplied-error today, sale wire, null sale checked; malformed-object probe recorded, not promoted to real-schema failure |
| Actual missing-customer declarations |4focused offline assertions PASS: absent row retains60/blocks direct handler; absent detail retains60/blocks; no selection invents no amount; present navigation unchanged |
| Actual parent failed-read context + debt screen | Reproduced APP-01 |
| Actual useTenant projection + billing branch | Reproduced APP-03 with future2099trial |
| Actual DayCloseScreen memo replay | Reproduced APP-04, stale0 versus fresh100 |
| Actual webhook route with supplied persistence error | Reproduced APP-02,200success after failed first write |

Runtime: local Node24.19.0 and local TypeScript5.9.3. Independent AST parsing used available Babel parser7.29.2; no claim of rerunning the candidate's fully locked toolchain is made. Read-only dependencies came from `/workspace/scratch/ff955bed6c94/mongezz-work/node_modules`; that directory's application source/history was not treated as this candidate. All fixtures used explicit synthetic clients and stub process environment, no credentials or network.

**Not independently rerun:** the nine Chromium UI cases, real authenticated app/browser journey, full lint/typecheck/unit/build/audit, native G0/G1, SQL migrations or persisted finance flows, provider/subscription/email integration, database upgrade/rollback/concurrency/isolation, production. Native counts in integration REPORT are implementation evidence, not fresh execution by this reviewer. The focused fixture counterexamples do not establish a live production occurrence.

## Minimal offline reproductions for a complete exact checkout

These commands read source and execute callbacks in memory. They do not import the app's database/provider modules. Run from a complete checkout with its dependencies; this review used the equivalent exact source retrieved through the connector, since the supplied local directory is partial.

```js
// node <<'JS' ... JS
const fs = require('node:fs');
const ts = require('typescript');
const assert = require('node:assert/strict');
function emit(path) {
  return ts.transpileModule(fs.readFileSync(path, 'utf8'), {
    fileName: path,
    compilerOptions: { target: ts.ScriptTarget.ESNext,
      module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.React }
  }).outputText.replace(/^import[^;]+;\n/gm, '').replace(/^export /gm, '');
}
// APP-03: valid future-trial row, actual projection and returned contract.
let projection;
const row = {id:'t',name:'Shop',timezone:'UTC',business_type:'general',
             trial_ends_at:'2099-01-01T00:00:00Z'};
const fixture = {from(){return {
  select(s){projection=s;return this}, eq(){return this},
  async maybeSingle(){return {data:Object.fromEntries(
    projection.split(',').map(k=>[k,row[k]])),error:null}}
}}};
const useTenant = new Function('supabase','useQuery','useMutation',
  'useQueryClient',emit('src/lib/db.ts')+';return useTenant;')(
    fixture,x=>x,x=>x,()=>({}));
(async()=>{
  const tenant=await useTenant('t').queryFn();
  assert.equal(tenant.trial_ends_at,undefined);
  console.log({projection,tenant,branch:'expired despite future DB trial'});
})();
```

APP-01 can be reproduced by extracting MongezzApp/DebtsScreen with `ts.createSourceFile`/`ts.isFunctionDeclaration`, supplying read hooks returning error plus undefined data and recording the child context. Expected counterexample is `invoices:[]`, all-zero totals, and DebtsScreen's no-debt success. APP-04 uses the actual DayCloseScreen declaration and a useMemo fixture that caches by Object.is on its supplied dependency array; retain all array/totals references while changing only tenantTz with the dates given above. APP-02 extracts the actual webhook module through the same emit helper, supplies `createFileRoute:()=>x=>x`, a verified synthetic event, and a recording client whose first upsert resolves an error while tenant update resolves success; call `Route.server.handlers.POST` and observe200. All three reproductions were actually executed during this review, with their concrete outputs recorded above; these instructions do not claim a full rendering/SQL/provider test.

## Disposition

Retain the missing-customer repair and truthful nullable types; their focused behavior and runtime preservation were independently checked. Resolve APP-01 before claiming the inherited authenticated application is financially safe. APP-02 remains a High block before paid billing. APP-03/04 require explicit disposition before merge. A foundation-only promotion would need an explicit, narrower owner/reviewer decision retaining these inherited risks and all other reviewers' findings; this report does not issue that approval.

No financial49/50, October RPC composition, account-chain, deployment, pilot, or production readiness is approved by this application subreview.
