# E2E Tests — Mongezz V2

This directory contains two different classes of E2E tests:

- `isolated-auth-smoke.py` — **read-only** authenticated UI smoke used by CI.
- `rapid-click-sale.py` and `sale-dashboard-close.py` — **destructive** financial E2E harnesses that seed or create financial rows and are therefore restricted to the isolated local/CI Supabase stack.

`write_harness_guard.py` is the shared fail-closed safety layer for destructive harnesses. Gate 4 inventories the checked-in Python E2E files; adding a new harness requires explicit classification before SEC-ENV can remain green.

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
- the browser guard rejects remote Supabase traffic and non-read remote requests.
- preview, staging, and production targets are not valid destructive-test targets.

A stale `.env` file alone is insufficient authorization: `MONGEZZ_E2E_WRITE_TEST=1` must be present in the current process environment.

## Preflight only

Containment can be verified without importing Playwright/requests or performing writes:

```bash
python3 tests/e2e/rapid-click-sale.py --preflight-only
python3 tests/e2e/sale-dashboard-close.py --preflight-only
```

Both commands must reject missing intent, production/remote Supabase configuration, alternate PostgreSQL routing, and accept only the isolated loopback target.

## Sale → dashboard → day close

`tests/e2e/run.sh` performs the shared safety preflight first, then checks the injected isolated session and local dev server before running `sale-dashboard-close.py`.

The flow verifies:

1. **Quick sale** — UI opens the sale screen, adds a seeded product, and issues the invoice with default cash payment.
2. **Dashboard** — re-renders and reflects the new sale in `sales_today` and `cash_today` aggregates, and shows the currency token.
3. **Day close** — calls `close_day` RPC and verifies the resulting `day_closes` snapshot contains the sale and realised profit.

Each run is scoped by a unique `E2E-<ts>` tag and verifies cleanup. Screenshots are local test artifacts only.

## Rapid-click safety

`rapid-click-sale.py` checks UI duplicate-submit resistance under rapid taps and throttled network conditions. It is **not** evidence of server/database idempotency and must never be used as a substitute for FIN-IDEM.

## Operational boundary

These destructive harnesses are not authorized for preview, staging, or production execution. Production access/deployment is outside the E2E test contract.
