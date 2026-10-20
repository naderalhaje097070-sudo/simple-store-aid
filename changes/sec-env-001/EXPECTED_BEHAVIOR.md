# SEC-ENV-001 — Expected Behavior

## Canonical environment modes

The application build/runtime must operate under an explicit environment intent rather than infer production from missing values.

### Non-production

Includes local development, CI, preview, staging, and test.

Requirements:
- explicit Supabase URL and publishable key are mandatory;
- missing values fail closed;
- a known production Supabase target is rejected;
- no implicit fallback to production is permitted.

### Production

Production Supabase targeting is allowed only when an explicit production-deployment signal is present and the expected production configuration is supplied by the approved deployment path.

Missing production configuration must fail rather than silently substitute an embedded fallback.

## Build/runtime consistency

- Build-time resolution and runtime client consumption use one approved contract.
- Vite injection must not bypass runtime safety.
- SSR aliases follow the same environment-mode restrictions.

## CI isolation

Before any isolated financial/auth write:
- workflow sets an explicit isolated-CI marker;
- resolved Supabase URL must be local/disposable according to the approved contract;
- production project ID/host is rejected.

## Test expectations

Tests must cover:
- VITE precedence;
- server aliases;
- blanks;
- missing values in non-production;
- production target rejected in non-production;
- explicit production deployment accepted only under approved signal;
- inconsistent URL/project/key combinations fail closed where deterministically detectable.

## Acceptance boundary

SEC-ENV is not complete until browser build, SSR/build resolution, and isolated CI behavior all prove the same deny-by-default contract on an exact verified head.