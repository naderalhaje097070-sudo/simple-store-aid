# E2E Tests — Mongezz V2

This directory contains two different classes of E2E tests:

- `isolated-auth-smoke.py` — **read-only** authenticated UI smoke used by CI.
- `rapid-click-sale.py` and `sale-dashboard-close.py` — **destructive** financial E2E harnesses that seed or create financial rows and are therefore restricted to the isolated local/CI Supabase stack.

`write_harness_guard.py` is the shared fail-closed safety layer for destructive harnesses. `browser_network_guard.py` supplies common transport containment for all four browser harnesses. Gate 4 inventories the checked-in Python E2E files; adding a new harness requires explicit classification before SEC-ENV can remain green.

## Destructive-test safety contract

Before any destructive harness may import browser/network clients or perform API/SQL writes, all of the following must be explicit:

```bash
MONGEZZ_E2E_WRITE_TEST=1
MONGEZZ_DEPLOY_TARGET=local   # or ci only
VITE_SUPABASE_URL=http://127.0.0.1:54321
VITE_SUPABASE_PUBLISHABLE_KEY=<isolated-local-key>
PGHOST=127.0.0.1
PGPORT=54322
PGUSER=postgres
PGDATABASE=postgres
```

Additionally:

- `PGHOSTADDR` must be unset or loopback only.
- `PGSERVICE` and `PGSERVICEFILE` are forbidden.
- destructive PostgreSQL subprocesses use explicit host/port/user/database routing and `psql -X` so startup files cannot redirect the session.
- destructive/auth browser HTTP is pinned to the exact configured application and Supabase origins, including resource reads and writes; another loopback port is a different service.
- context routing is installed before pages, covering each popup's first request; service workers stay blocked.
- browser HTTP uses `route.fetch(max_redirects=0, max_retries=0)` and aborts every3xx response, including same-origin redirects, before the browser can follow it. No automatic retry may repeat a write.
- all browser WebSockets are blocked without connecting to a server; these harnesses therefore do not prove Realtime behavior.
- the application's exact Google Fonts stylesheet URL is fulfilled offline with empty CSS only for a non-navigation stylesheet GET. Other requests to that URL fail closed. Screenshots use fallback fonts and do not establish the final Tajawal typography or external font availability.
- visual smoke blocks non-read HTTP methods. This is a stricter test policy, not a production browser behavior change.
- preview, staging, and production targets are not valid destructive-test targets.

A stale `.env` file alone is insufficient authorization: `MONGEZZ_E2E_WRITE_TEST=1` must be present in the current process environment.

## Preflight only

Containment can be verified without importing Playwright/requests or performing writes:

```bash
python3 tests/e2e/rapid-click-sale.py --preflight-only
python3 tests/e2e/sale-dashboard-close.py --preflight-only
```

Both commands must reject missing intent, production/remote Supabase configuration, alternate PostgreSQL routing, and accept only the isolated loopback target.

## Browser transport regression without an application or database

Use a Python3.12 virtualenv with `tests/gate4/sec-env/requirements.txt`, install the matching Playwright headless Chromium and run:

```bash
python tests/gate4/sec-env/browser-network.py
```

The probe binds disposable HTTP recorders on loopback8080/54321 and a randomly allocated forbidden port, using dummy traffic only. It measures whether redirects, alternate-origin POSTs, WebSocket handshakes and popup navigation reach the forbidden recorder; allowed app reads/API POSTs must still work. It loads actual pure policies through AST without executing financial harness bodies or importing app/database code. Ports must be unused; never run this alongside a real local stack. Quality CI includes this probe with pinned Playwright1.62.0. Alternate Chromium executable/argument env overrides are test-only and must be recorded; they are not real-app or matching-CI browser acceptance.

## Sale → dashboard → day close

`tests/e2e/run.sh` performs the shared safety preflight first, then checks the injected isolated session and local production emulator before running `sale-dashboard-close.py`. Local/CI browser flows require an environment-specific production build served by the local Cloudflare emulator. The read-only visual harness also supports explicitly configured preview/staging production builds. Do not use Vite dev/HMR because every WebSocket attempt is recorded as a containment failure. Follow the production-build/emulator configuration in `.github/workflows/isolated-auth-smoke.yml` with an independently verified isolated stack; do not copy production keys or target values. Actual application/DB compatibility remains unverified until that flow executes on the accepted candidate.

The flow verifies:

1. **Quick sale** — UI opens the sale screen, adds a seeded product, and issues the invoice with default cash payment.
2. **Dashboard** — re-renders and reflects the new sale in `sales_today` and `cash_today` aggregates, and shows the currency token.
3. **Day close** — calls `close_day` RPC and verifies the resulting `day_closes` snapshot contains the sale and realised profit.

Each run is scoped by a unique `E2E-<ts>` tag and verifies cleanup. Screenshots are local test artifacts only.

## Rapid-click safety

`rapid-click-sale.py` checks UI duplicate-submit resistance under rapid taps and throttled network conditions. It is **not** evidence of server/database idempotency and must never be used as a substitute for FIN-IDEM.

## Operational boundary

These destructive harnesses are not authorized for preview, staging, or production execution. Production access/deployment is outside the E2E test contract.
