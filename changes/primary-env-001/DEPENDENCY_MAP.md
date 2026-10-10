# Dependency map

vite.config.ts -> config/supabase-build-config.ts -> browser defines + baked server identity.
src/server.ts -> binding allowlist -> runtime/build comparison -> server alias hydration -> lazy TanStack server-entry -> existing application.
Consumers searched: src/integrations/supabase/client.ts, client.server.ts and auth-middleware.ts. Existing public/admin client contracts stay unchanged.

Guarded callers: sale-dashboard-close.py -> write_harness_guard.py; rapid-click-sale.py retains its already-existing in-file guard; both use context routing. isolated-auth-smoke.py validates origin before credentials. mobile-rtl-smoke.py uses PR48 canonicalization/context interception. Financial shell runner pins psql routing. E2E shell runner calls preflight before curl/session/flow.

PR53 package.json and bun.lock blob IDs remain 293395a676487cfc742caa642517f2c2323bdbac and efbffd2d5d0073978c374bb27b1f6398a322b8c6. No dependency regeneration in this packet.
