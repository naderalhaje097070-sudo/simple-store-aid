# PRIMARY-SEC-002 Impact Analysis

## User Impact

No user-facing behavior is intentionally changed. The change reduces dependency risk in build/server support paths, including MCP server support code bundled into the server output.

## Engineering Impact

The lockfile now resolves patched versions for the previous Critical/High audit groups:

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

`@lovable.dev/mcp-js` resolves from `0.20.0` to `0.20.1`; review remediation pins that already-resolved 0.20.1 in the root manifest to prevent a regeneration downgrade. Because that package still declares `@modelcontextprotocol/sdk: 1.28.0`, the patched SDK floor is enforced by root override/resolution and verified by lock tests.

## Risk

Primary risk is transitive dependency compatibility. Mitigation:

- Keep patched versions within the existing major where possible.
- Use the official minimum patched SDK `1.31.0`, not the newer v2 client line.
- Preserve `brace-expansion` major-specific lock entries rather than force one global major across incompatible parents.
- Verify with Bun 1.2.14 frozen install, typecheck, unit tests, and build.

## Result

`bun audit` changed from 65 package/advisory records with 2 Critical and 33 High records to 16 records with only Low and Moderate severities.

The review remediation replaces the lock with generator output rather than manual
entries. No new package version is introduced versus the prior PR53 candidate;
retained package metadata/integrity is identical. Optional/orphan graph pruning is
documented in `LOCK_REGENERATION.md`. The synthetic MCP fixture now lives in
`tests/unit/mcp-dependency-compatibility.test.ts`, so normal Quality runs include it.
