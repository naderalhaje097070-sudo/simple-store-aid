# SEC-ENV-001 — Test Impact

## Existing tests

`tests/unit/supabase-build-config.test.ts` currently asserts missing variables resolve to production fallback. That test must become expected-RED evidence for the new fail-closed contract before implementation.

## New Gate-4 scenarios

1. Non-production + no variables → reject.
2. Non-production + blank variables → reject.
3. Non-production + explicit local VITE variables → accept.
4. Non-production + server aliases → accept only when non-production target is allowed.
5. Non-production + production Supabase URL/project → reject.
6. Explicit production intent + approved production configuration → accept.
7. Explicit production intent + missing required values → reject.
8. URL/project mismatch where deterministically detectable → reject.
9. CI isolated marker + local Supabase → accept.
10. CI isolated marker + production target → reject.

## Integration verification

- Build app using the resolved configuration.
- Confirm generated Vite values match approved target.
- Confirm client creates against approved target only.
- Auth/financial isolated workflows continue using local Supabase.

## Regression requirements

- Existing VITE-over-alias precedence remains deterministic.
- Blank values never override usable values.
- No production access is required.
- Do not weaken isolated financial/auth tests.

## Evidence rule

Exact commit, environment mode, resolved target classification, and actual pass/fail must be recorded.