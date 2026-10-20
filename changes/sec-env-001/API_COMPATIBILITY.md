# SEC-ENV-001 — API and Compatibility Impact

## Application API/RPC

No RPC or HTTP application contract changes.

## Environment contract change

Current behavior treats missing values as permission to use production fallback. Target behavior requires explicit environment/deployment intent.

Supported inputs remain:
- `VITE_SUPABASE_URL` / `SUPABASE_URL`;
- `VITE_SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_PUBLISHABLE_KEY`;
- project ID aliases where still required.

## Intentional compatibility break

A preview/local/CI build that previously succeeded only because variables were absent and production fallback was injected will fail closed instead. This is intentional and security-positive.

## Production compatibility

Production deployment must have an explicit supported configuration path verified before implementation. Production success may not depend on ambiguous missing-variable fallback.

## Generated client

`src/integrations/supabase/client.ts` should continue consuming Vite/SSR values and retain a missing-value guard. Direct editing of generated code should be avoided unless generation/source ownership is explicitly resolved.