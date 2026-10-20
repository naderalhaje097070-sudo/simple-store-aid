# Findings and acceptance limits

## OC-APP-01 — Medium — retained server-function authorization gap

Status: confirmed source-reviewed missing lifecycle check; no live exploit or provider call.
Sources: `src/utils/payments.functions.ts` / resolvePaddlePrice;
`src/integrations/supabase/auth-middleware.ts` / requireSupabaseAuth;
`src/lib/paddle.server.ts` / gatewayFetch. These source blobs are unchanged by this PR.

The authenticated price-resolution server function validates token claims then calls the
payment gateway. It does not consume actor_is_active/current_tenant_id or closure state.
Auth identity intentionally stays valid, so marker enforcement does not supply authorization
for this surface. Broad "all application access is disabled" is not an accepted claim.
No Paddle/API gateway call, production/resource/cost/billing/contract repair was executed.
Existing runtime matrix covers protected REST/RPC/four full MCP tools only.

Required before merge: explicit owner disposition and separately scoped lifecycle guard
or accepted product-scope decision. Do not quietly expand this batch into billing changes,
edit generated auth middleware, or accept generic provider failures as closure proof.
This finding remains open; integration/release/merge acceptance stays blocked. Corrections
in this packet narrow evidence claims, not the underlying server-function behavior.

## OC-EVID-02 — Low — one duplicate observation name per runtime mode

`client_truncate_denied_all22` records checks before and after closure with the same name.
Raw fresh contains166 observations/165distinct names; upgrade171/170. Each failed observation
raises immediately, so duplicates cannot replace a failing check with later success.
Counts are observations, not unique scenarios or vulnerability coverage. The existing
before/after calls verify TRUNCATE22 twice, no destructive statement is executed.

Disposition: record as a scoped follow-up to phase-qualify names and the evidence inventory
in the next relevant harness change. Do not rewrite raw evidence or rerun unaffected runtime
just to alter labels. Also tracked in TASKS.md. No current test assertion weakened.

## Unverified runtime boundaries

One store per owner and staff on A only were created. Multiple stores, extra memberships,
continued staff access in B's closed-owner store and all application/server/UI surfaces are
source reasoning or untested, not runtime proof. Concurrency/in-flight, Cloudflare/proxy,
production performance, broader financial contracts, provider sign-in blocking, commercial
cancellation, personal-data retention/erasure and complete provider-service egress remain
excluded/unverified. Repeated closure acknowledgement is a deliberately narrow self-status
exception, not access to protected public data.
