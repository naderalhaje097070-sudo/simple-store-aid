# SEC-ENV-001 — Change Intake

## Change goal

Make non-production Supabase targeting explicit and fail-closed so local, CI, preview, and staging cannot silently build against production.

## Change type

Security / environment-resolution change under NAADF-CMF.

## In scope

- Build-time Supabase URL/key/project resolution.
- Client/SSR environment handoff.
- Explicit production-vs-non-production deployment intent.
- CI/preview safeguards against production target.
- Unit and integration safety tests.

## Out of scope

- CI log redaction/tool pinning (`SEC-CI-001`).
- FIN-COURIER business logic.
- FIN-IDEM financial retry safety.
- Production database changes, migrations, or deployment.

## Urgency

P0 pilot blocker.

## Risk level

High security/financial-environment risk because an unintended fallback can point test/preview execution at production.

## Owner

Nader — product and repository owner.

## Expected outcome

A single canonical environment-resolution contract that fails closed outside explicit production deployment and is proven by tests across Vite/client/SSR/CI paths.

## Missing blocking information

The precise environment signal that reliably distinguishes an intentional Lovable production deployment from Lovable preview must be verified before implementation. No heuristic production detection is approved yet.

## Explicit assumptions

- `main = 983b746e5c6639dcdc5e6557381ad5619abaa046` is the baseline.
- Production public URL/key are not treated as secrets, but accidental production targeting is still prohibited.
- Production secrets/data remain outside agent access.
- No automatic merge or deploy.