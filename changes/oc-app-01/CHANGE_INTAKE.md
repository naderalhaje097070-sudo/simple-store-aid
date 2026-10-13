# OC-APP-01 — authorized intake and design (2026-10-14 Africa/Tripoli)

Owner explicitly authorizes planning #55/6156792432 and6156803010; execution claim6156865890.
Base PR69 exact92ebd529c79ae1df98ec02245d3c22d6bcfc557f. main43d6edbccb66fb06ce0fcb93734ad59532d1aeae unchanged.
One implementer /root; independent readonly reviewer /root/oc_app_review.
Risk: security authorization Medium; urgency close source-reviewed Medium before integration.
Goal: current account state denial before resolvePaddlePrice gatewayFetch/secrets. Scope this one function, non-generated helper and focused tests/receipts/docs.
Out: generated auth middleware, paddle.server, price/financial/subscription/webhook/UI contracts, migrations, provider calls, production/cost/merge/deploy.
No blocking product information. User card is intake approval; no redundant permission required.

Root cause: requireSupabaseAuth authenticates getClaims/sub only while retained Auth tokens remain valid after closure.
Use existing zeroarg current_tenant_id RPC: effective definition always PERFORM monjez_private.assert_active_actor() before nullable profile tenant return.
Ignore returned tenant intentionally: successful execution is trusted explicit assertion completion, not inference from empty rows. No role/tenant restriction added. Active account without tenant is positive control.
Current actor predicate reuses live Auth ban/delete and private permanent closure marker; same bearer context.supabase, no service-role, cache/client status/private data exposed.
Exact42501/account_inactive denial -> account_inactive. Any other error/throw/bounded timeout -> account_state_unavailable before gateway. Await guard first; deadline/abort in finally. No success fallback.
No migration/backfill/schema/RPC modification;45 immutable sources preserved.

Callers: src/lib/paddle.ts resolvePriceId -> resolvePaddlePrice; initializePaddle frontend flow unchanged. Only createServerFn occurrence in application is this entry (rg inventory). middleware establishes context.supabase/userId/claims. gatewayFetch reads provider keys only on call.
Compatibility: method GET, input shape priceId/environment, encoding, returned firstpriceid and Price not found preserved. Guard only adds lifecycle/service refusal.
Rollback: close unmerged candidate; additive revert of helper/import/await restores known vulnerability, therefore no production rollback recommendation. Do not clear closure or revoke retention.

Safety net before patch: local45 full immutable schema, synthetic Auth A/B + staff identity without tenant, real OAuthPKCE, compiled TanStack function manifest/protocol. Original handler unchanged expected-red must return dummy price for closed B old/new tokens with gateway counter delta1; active controls must pass first. No finance fixture.
Provider substitute only: test Node --import preload intercept exact existing connector GET/prices for allowlisted synthetic IDs, return dummyprice, record calls. Fixed dummy keys only, no URL change/adapters/toggles in application. Native UID firewall denies nonloopback IPv4/IPv6; credential-free redirect canary before keys; local Supabase requests remain real. Error injection only later focused transport tests, explicitly separated from live activity checks.
After fix: A/B active, no-tenant staff, live/sandbox selection and escaped/missingprice compatibility; closedB old unchangedunexpired/newgenuine validtokens denied, A afterward; missing/invalid/expiredtokens; ban/delete; servicefailure/transport/timeout no calls. Snapshot public/Auth identity retained except private marker1; no financial writes. Cleanup/secret quarantine. Quality affected source plus required existing checks; no historical full matrices.
Acceptance requires actual local runtime evidence, not source review or generic500. Serialized named Error is required; status alone insufficient.
Not claimed: allappsurfaces/Cloudflare/production, in-flight revocation/TOCTOU, finance acceptance, release integration. integration_accepted=false.
Independent design review confirmed existingRPC reuse with no tenant constraint; requested live no-tenant positive and exact errors/deadline. Final source/evidence review pending.
