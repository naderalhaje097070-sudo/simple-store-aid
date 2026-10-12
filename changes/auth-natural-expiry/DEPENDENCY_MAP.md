# Dependencies

New natural_expiry_probe subclasses TanStackRouteProbe for unchanged process/HTTP/isolation.
Reuses McpProbe.oauth_token/initialize/invoke, Probe fixtures/REST/RPC/SQL/control,
McpProbe22table snapshot, app_environment and tanstack_route_build, preload and write_harness_guard.
New crypto helper imports existing pinned jose6.2.3; compactVerify+jwtVerify only, never signing.
New focused workflow consumes same dependencies, config/source routes/build/locked43migrations.
No new SDK/server architecture. The only client POST grants are password and authorization_code;
refresh grants and revocation endpoints rejected. Both old/new credentials are kept separately.


Small shared PKCE fixture compatibility correction: handle200autoapproved redirect_url for existing consent. No app or provider policy changes. Offline consent tests4; configured consumers regressions run automatically.
