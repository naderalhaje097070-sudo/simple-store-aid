# PRIMARY-SEC-002 Security Impact

## Improvements

The candidate removes all current Critical and High package/advisory records reported by `bun audit` for this tree.

Before:

- 18 packages
- 65 package/advisory records
- 2 Critical
- 33 High
- 25 Moderate
- 5 Low

After:

- 6 packages
- 16 package/advisory records
- 0 Critical
- 0 High
- 11 Moderate
- 5 Low

## Remaining Findings

Remaining audit names:

- `@babel/core`
- `@hono/node-server`
- `dompurify`
- `esbuild`
- `hono`
- `qs`

These are not fixed by this Critical/High batch. They remain queued for later security maintenance and do not imply release acceptance.

## Primary Sources Used

- `proxy-addr` official advisory: https://github.com/jshttp/proxy-addr/security/advisories/GHSA-jqcg-44mw-7w3h
- `shell-quote` official advisory: https://github.com/ljharb/shell-quote/security/advisories/GHSA-pqg4-j6r4-53mv
- MCP TypeScript SDK official advisory: https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-6qxp-vccf-f47h

## Limits

This is dependency risk reduction, not a full release security sign-off. Runtime auth, tenant-isolation, financial-write, hosted CI, and independent review gates remain open.
