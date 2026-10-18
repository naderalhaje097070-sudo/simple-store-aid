# Missing-customer debt UI regression

From the repository root with its frozen dependencies and existing pinned Python
Playwright tooling installed:

```bash
bun tests/app-debt-missing-customer/build.ts /tmp/debt-ui
python3 tests/app-debt-missing-customer/browser.py /tmp/debt-ui
```

For an image supplying system Chromium rather than a Playwright browser download:

```bash
DEBT_TEST_CHROMIUM=/usr/bin/chromium python3 tests/app-debt-missing-customer/browser.py /tmp/debt-ui
```

The builder selects both original screen declarations with the TypeScript parser;
it bundles their actual shared components and financial selector with synthetic
props. It never imports the authenticated route, database, credentials or router.
The browser blocks all HTTP and WebSocket requests and records any attempted
request or page error as a failure. Nine scenarios verify independently expected
debt **60** (invoice100, paid40), loading/absence/recovery, invalid-action blocking,
normal navigation and isolation of unrelated/returned/pending invoices.

This is a component UI regression, not a live database, authenticated full-app,
financial write, release or G1 acceptance test. The original failure receipt and
verification limits are retained in docs/app-debt-missing-customer-01.
