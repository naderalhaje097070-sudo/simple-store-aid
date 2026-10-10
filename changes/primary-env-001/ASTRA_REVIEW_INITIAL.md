# Independent Astra review — 2026-10-10

Outcome: **Changes required**. Review resumed successfully after the earlier capacity error. Reviewed local HEAD7c9e0ae, whose55 changed files matched remote PR54 headf5db53d430648926daa586993abb8b1c35059d36.

ENV-A1 — High. All four browser guards validated the initial request and called route.continue_(). Playwright redirect processing does not re-run the handler on each destination;307/308 can forward a dummy write body to a forbidden origin and302 can navigate there before final URL checks. Locations: sale-dashboard-close.py209-224; rapid-click-sale.py339-352; isolated-auth-smoke.py135-150; mobile-rtl-smoke.py261-281. Required fix: prevent automatic redirects at interception/egress boundary and verify with disposable loopback recorders.

ENV-A2 — High. None of the four contexts intercepts WebSockets. HTTP routing is not a WebSocket boundary; stale/injected pages could contact remote services with auth/messages. Required fix: context WebSocket blocking before pages, tested with a dummy local recorder.

ENV-A3 — Medium. Write/auth predicates permit non-navigation writes to arbitrary loopback schemes/ports. Astra executed pure predicates without harness body/network and reproduced acceptance of POST to localhost:9999/rest/v1/rpc/create_sale_with_items and https://127.0.0.1:4443/auth/v1/token. Required fix: exact configured application/Supabase origins and POST/XHR negative cases.

Independent checks:60 unit tests/125 expectations; E1-E10 offline probe;8 actual server-wrapper/stub cases; typecheck passed. No concrete resolver/public-key/alias/baked-runtime defect found. Review does not cover application auth/RLS/tenant/finance or release acceptance. No edits, live DB/E2E flow, production access, merge or deployment performed.

Primary references: https://playwright.dev/docs/network#redirects ; https://playwright.dev/python/docs/api/class-browsercontext#browser-context-route-web-socket ; https://playwright.dev/python/docs/api/class-websocketroute . Findings are source/API-contract evidence; browser reproduction follows in a remediation packet.
