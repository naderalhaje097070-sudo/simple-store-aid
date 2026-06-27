# E2E Tests — Mongezz V2

`sale-dashboard-close.py` drives a real browser through the authenticated
preview to verify the most sensitive financial path end-to-end:

1. **Quick sale** — UI opens the sale screen, adds a seeded product, and
   issues the invoice with default cash payment.
2. **Dashboard** — re-renders and reflects the new sale in
   `sales_today` and `cash_today` aggregates, and shows the currency token.
3. **Day close** — calls `close_day` RPC and verifies the resulting
   `day_closes` snapshot contains the sale and realised profit.

Each run is scoped by a unique `E2E-<ts>` tag and cleans up its seeded
product, order, payments, and day-close row at the end (success or fail).

## Run

```bash
bash tests/e2e/run.sh
```

Requires the sandbox env (PG*, LOVABLE_BROWSER_*) and a dev server on
`http://localhost:8080`. Screenshots land in
`/tmp/browser/mongezz-e2e/shots/`.

## Asserts

| Step                  | Check                                             |
|-----------------------|---------------------------------------------------|
| Order row             | `total=100`, `paid=100`, `status='paid'`, `direct`|
| Payment row           | `kind='sale'`, `method='cash'`, `amount=100`      |
| Product stock         | decremented by 1                                  |
| Dashboard aggregates  | `Σsales today` and `Σcash today` both +100        |
| `day_closes` snapshot | `sales≥100`, `collected≥100`, `realized_profit≥40`|

Failures `exit 1` with a clear `❌ FAIL` message; cleanup still runs.
