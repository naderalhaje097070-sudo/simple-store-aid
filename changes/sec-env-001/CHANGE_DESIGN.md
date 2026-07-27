# SEC-ENV-001 — Change Design

## Root cause

The build-time resolver treats **absence of explicit Supabase configuration as implicit authorization to use production**. `vite.config.ts` then injects those production values into the client build, so the runtime missing-value guard is bypassed.

## Smallest correct change

1. Introduce an explicit environment/deployment mode into the build resolver.
2. Remove unconditional production fallback for missing variables.
3. Preserve VITE-over-server-alias precedence.
4. Reject production target when mode is non-production.
5. Allow production only with an approved explicit production-deployment signal and explicit configuration.
6. Add mode-aware tests before implementation.
7. Add isolated-CI target assertion before app-based test writes where needed.

## Proposed affected files

- `config/supabase-build-config.ts`
- `tests/unit/supabase-build-config.test.ts`
- `vite.config.ts`
- focused CI/test helper only if needed to assert isolated target
- SEC-ENV documentation

Avoid directly editing generated `src/integrations/supabase/client.ts` unless evidence shows the source contract cannot be enforced at the resolver/build boundary.

## Environment contract

### Non-production

- mode explicitly or reliably resolved as non-production;
- URL/key required;
- production host/project rejected;
- missing values throw before build/client use.

### Production

- explicit verified production-deployment signal required;
- explicit URL/key required;
- expected production project may be allowlisted by project ID/host if needed;
- missing configuration throws.

## Open design decision before Gate 4 approval

Determine the reliable production-deployment signal exposed by the actual Lovable deployment path. No implementation should guess using `NODE_ENV=production`, because preview builds commonly use production-mode bundling too.

## Compatibility strategy

- Keep existing environment variable aliases.
- Intentionally break misconfigured non-production builds that relied on silent production fallback.
- Keep application RPC/schema/business behavior unchanged.

## Rollout

Gate 4 tests → focused resolver implementation → exact-head build/unit/auth isolation verification → independent security review → explicit human merge.

## Acceptance criteria

- zero implicit production fallback;
- non-production fails closed;
- production requires explicit approved intent/configuration;
- CI cannot resolve production;
- browser and SSR/build paths agree;
- no production access required for tests.