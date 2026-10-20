# SEC-ENV-001 — Change Design

## Root cause

The build-time resolver treats **absence of explicit Supabase configuration as implicit authorization to use production**. `vite.config.ts` then injects those production values into the client build, so the runtime missing-value guard is bypassed.

## Smallest correct change

1. Introduce an explicit deployment target into the build resolver.
2. Remove unconditional production fallback for missing variables.
3. Preserve VITE-over-server-alias precedence only after deployment target validation.
4. Reject the production Supabase project when the deployment target is non-production.
5. Allow production only with explicit production intent plus explicit approved production configuration.
6. Add target-aware tests before implementation.
7. Add isolated-CI target assertion before app-based test writes where needed.

## Proposed affected files

- `config/supabase-build-config.ts`
- `tests/unit/supabase-build-config.test.ts`
- `vite.config.ts`
- focused CI/test helper only if needed to assert isolated target
- SEC-ENV documentation

Avoid directly editing generated `src/integrations/supabase/client.ts` unless evidence shows the source contract cannot be enforced at the resolver/build boundary.

## Deployment-target contract

Do **not** infer deployment safety from `NODE_ENV`, Vite production-mode bundling, branch name, hostname, or the presence/absence of Lovable preview behavior. Those are not accepted authorization signals for production data access.

Use one explicit server/build-only variable, proposed name:

`MONGEZZ_DEPLOY_TARGET`

Allowed values:

- `local`
- `ci`
- `preview`
- `staging`
- `production`

The variable is consumed by the build resolver and is not required to be injected into the browser bundle.

### Non-production targets

For `local`, `ci`, `preview`, and `staging`:

- URL and publishable key are required;
- the known production project ID/host is rejected;
- missing or blank values fail before application build/client use;
- CI additionally proves the local/disposable Supabase sentinel before financial/auth writes.

### Production target

For `production`:

- `MONGEZZ_DEPLOY_TARGET=production` is necessary but not sufficient;
- URL and publishable key must be provided explicitly;
- project ID/host must match the approved production allowlist;
- missing, blank, or mismatched configuration fails closed;
- no production URL/key/project ID is stored as a fallback inside resolver source code.

## Lovable / hosting decision

The previous open question is resolved by **not depending on a hidden or inferred Lovable production signal**.

Official Lovable documentation confirms that Lovable projects are Vite applications and that `VITE_*` values are embedded at build time. It also documents explicit environment-variable configuration for externally hosted production builds. Lovable preview/development behavior must therefore never be treated as implicit permission to use the production Supabase project.

For any deployment path that cannot provide the explicit deployment-target contract, the build must fail closed rather than silently select production. If a future Lovable-native production path needs support, it must supply an explicit reviewed adapter/configuration for `MONGEZZ_DEPLOY_TARGET=production`; it does not receive a source-code fallback exception.

## Compatibility strategy

- Keep existing Supabase value aliases where needed.
- Add one explicit deployment-target contract.
- Intentionally break misconfigured non-production builds that relied on silent production fallback.
- Keep application RPC/schema/business behavior unchanged.

## Gate 4 safety-net expectations

Before implementation, tests must prove the current unsafe baseline and then define the target contract:

1. missing deployment target fails;
2. missing URL/key fails;
3. `ci|preview|staging|local` + known production project fails;
4. `production` + non-production project fails;
5. `production` + approved explicit production project succeeds;
6. alias precedence cannot bypass target validation;
7. blank strings are treated as missing;
8. browser/build and SSR resolution produce the same approved target;
9. no test requires production database access.

## Rollout

Gate 4 tests → focused resolver implementation → exact-head build/unit/auth isolation verification → independent security review → explicit human merge.

## Acceptance criteria

- zero implicit production fallback;
- non-production fails closed;
- production requires explicit approved intent/configuration;
- CI cannot resolve production;
- browser and SSR/build paths agree;
- no production access required for tests.