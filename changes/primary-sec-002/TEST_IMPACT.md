# PRIMARY-SEC-002 Test Impact

## Added Coverage

`tests/unit/dependency-security.test.ts` now guards the patched dependency floors for:

- `@modelcontextprotocol/sdk`
- `brace-expansion`
- `browserslist`
- `fast-uri`
- `ip-address`
- `js-yaml`
- `nanoid`
- `postcss`
- `proxy-addr`
- `shell-quote`
- `source-map-js`

The `brace-expansion` guard is major-aware because compatible patched floors differ for major 1, 2, and 5.

`tests/unit/mcp-dependency-compatibility.test.ts` covers four synthetic adapter
checks: initialize, list/invoke a Zod tool, invalid arguments, and missing bearer.
It was moved from the review packet into the normal unit-test directory so the
existing Quality job runs it. No test was weakened.

## Verification

- Bun 1.3.14 frozen install: passed.
- Bun 1.2.14 frozen install: passed.
- Typecheck: passed.
- Unit tests after remediation, under CI's Bun 1.2.14: 44 passed, 0 failed, 94 expectations.
- Production build with local Supabase fixture values: passed.
- Changed-source lint for both dependency-security and MCP compatibility tests: passed.
- `git diff --check`: passed.

## Not Covered

No browser E2E, live MCP runtime exercise, Supabase write, financial-rule, or deployment verification ran in this batch.

The in-process synthetic MCP checks do not prove the application's authorization
or tenant isolation. Hosted CI remains blocked by the observed account billing
annotation; local success does not waive it.
