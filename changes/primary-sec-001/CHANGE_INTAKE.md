# PRIMARY-SEC-001 — approved intake

2026-10-09. Owner: Nader; implementer: Codex. Repository: naderalhaje0970-droid/simple-store-aid. Application base: 43d6edbccb66fb06ce0fcb93734ad59532d1aeae; planning base: PR51. The owner explicitly instructed execution with full permissions after the bounded next batch was described. This satisfies intake authorization; it does not approve a release.

Type: dependency security fix. Urgency: Critical upstream advisory GHSA-qx66-fv34-fjm8. Implementation risk: High (server framework).

Goal: a reproducible patched TanStack graph with native compatibility evidence and a guard against vulnerable locks. Scope: affected framework declarations, generated bun.lock, regression test, required records. Exclusions: financial formulas, UI changes, RPC/schema/RLS, live Supabase, billing, deployment and merge.

Expected: all resolved react-start >=1.168.60 and start-server-core >=1.169.39; compatible existing Lovable2.9.1; no test weakening. Missing evidence: GitHub runner cause, final-source checks and independent review. Do not treat a package patch as financial acceptance.

Assumptions: official npm metadata reflects published package manifests; the exact original Git tree can be reconstructed and verified without CLI credentials; loopback fixtures are sufficient for compile-only checks. No authenticated server or write harness is run.

## Proven scope refinement

The security scan proved that the framework's serializer remains locked at affected Seroval1.5.6 and its old override bypasses the new published ^1.6.7 requirement. Include direct/override/resolution pins to1.6.7 and a third advisory guard. The owner authorized routine fixes in this security batch; no financial or release authorization is inferred. Final evidence and the newly prioritized PRIMARY-SEC-002 are in VERIFICATION.md.
