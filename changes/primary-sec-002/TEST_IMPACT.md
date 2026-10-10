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

## Verification

- Bun 1.3.14 frozen install: passed.
- Bun 1.2.14 frozen install: passed.
- Typecheck: passed.
- Unit tests: 40 passed, 0 failed, 86 expectations.
- Production build with local Supabase fixture values: passed.
- Changed-file lint for `tests/unit/dependency-security.test.ts`: passed.
- `git diff --check`: passed.

## Not Covered

No browser E2E, live MCP runtime exercise, Supabase write, financial-rule, or deployment verification ran in this batch.
