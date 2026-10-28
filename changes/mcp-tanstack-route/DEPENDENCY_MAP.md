# Inspected dependency and caller map
Unchanged src/server.ts: runtime source consistency and baked build validation before lazy @tanstack/react-start/server-entry.
Unchanged vite.config.ts: tanstackStart server entry=server; existing validated build defines; @lovable.dev/vite-tanstack-config2.9.1 uses defaultPreset cloudflare-module.
Installed nitro3.0.260603-beta: dist/_chunks/nitro.mjs resolves NITRO_PRESET before defaultPreset; native node-server runtime serves nitroApp.fetch. No custom MCP test server.
Generated src/routes/mcp.ts and src/routes/[.well-known]/oauth-protected-resource.ts: createTanStackMcpHandler/createTanStackOAuthProtectedResourceMetadataHandler; resourcePath /mcp, metadataPath fixed, trustForwardedHost true. Never manually edited.
Installed @lovable.dev/mcp-js0.20.1 adapter: first X-Forwarded-Host changes advertised resource; forwarded proto not enabled by TanStack wrapper. Definition issuer/JWKS fixed via validated config. JWT signature/issuer/aud/clientclaim checks stay unchanged.
Existing tests/account-lifecycle/mcp_probe.py: OAuth code/PKCE, real fixture superclass, initialize/initialized/catalog, snapshot, tool_success/account_tool_denial reused. New subclass supplies real route HTTP and orchestration. Existing direct-handler harness untouched.
Native process starts .output/server/index.mjs with containment-only Node --import preload. Preload imports no application/SDK handler and adds no /mcp or metadata routes.
