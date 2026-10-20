# PRIMARY-SEC-002 Dependency Map

## Critical/High Chains Fixed

| Package | Before | After | Chain |
| --- | ---: | ---: | --- |
| `@modelcontextprotocol/sdk` | 1.28.0 | 1.31.0 | `@lovable.dev/mcp-js` |
| `proxy-addr` | 2.0.7 | 2.0.8 | `@modelcontextprotocol/sdk` -> `express` |
| `shell-quote` | 1.9.0 | 1.11.0 | `@lovable.dev/vite-tanstack-config` -> `@tanstack/devtools-vite` -> `launch-editor` |
| `brace-expansion` | 1.1.14 / 2.1.1 / 5.0.5 | 1.1.21 / 2.1.7 / 5.0.12 | `minimatch` via ESLint and Workbox tooling |
| `browserslist` | 4.28.2 | 4.29.3 | Babel/Vite/Workbox/TanStack build tooling |
| `fast-uri` | 3.1.2 | 3.1.8 | `ajv` via MCP SDK and Workbox |
| `ip-address` | 10.2.0 | 10.7.3 | `express-rate-limit` via MCP SDK |
| `js-yaml` | 4.1.1 | 4.3.2 | ESLint and `xmlbuilder2` |
| `nanoid` | 3.3.12 | 3.3.19 | `postcss` |
| `postcss` | 8.5.15 | 8.5.29 | `vite` |
| `source-map-js` | 1.2.1 | 1.2.2 | `postcss` and Tailwind tooling |

## Exploit-Condition Notes

- `proxy-addr`: official advisory requires trust proxy subnet configurations such as IPv4-mapped IPv6 short prefixes. The project did not add custom Express trust-proxy configuration in this change, but the MCP SDK server path pulled the vulnerable package, so the package was patched.
- `shell-quote`: official maintainer advisory is High while registry audit classified the same advisory as Critical. The vulnerable path is dev tooling (`launch-editor`). It was patched because the lock contained the vulnerable range.
- `@modelcontextprotocol/sdk`: official advisory affects OAuth clients using `authProvider`/`withOAuth`/token flows against untrusted MCP servers; MCP servers and stdio clients are not affected. The app exposes MCP server routes through `@lovable.dev/mcp-js`; no direct SDK OAuth client use was found, but the SDK was patched to the official fixed floor.

## Tooling Constraint

Bun 1.3.14 did not apply the scoped rules used in the original candidate. That manual-lock approach was rejected by SEC2-R2 review. The current candidate uses Bun 1.4.0's transitive update generator from the original PR52 lock, preserves all three compatible major lines and removes unsupported resolution paths. See `LOCK_REGENERATION.md` for the reproduced output and graph pruning. Frozen installation with the existing Bun 1.2.14 CI version remains verified; no package-manager runtime upgrade is required to install this lock.
