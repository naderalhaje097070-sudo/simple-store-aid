# SEC-CI-001 — CI hardening

Status: **Gates 0–3 proposed for review. No workflow implementation is authorized by this documentation.**

Issue: #29

Baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

## Goal

Make release-blocking GitHub Actions deterministic, concise, secret-safe, and capable of producing authoritative exact-head evidence without confusing runner/account failures with product failures.

## Current findings

- `Quality` pins Bun `1.2.14` and does not post PR logs.
- `Ephemeral Financial Rules` and `Isolated Auth UI Smoke` use `supabase/setup-cli@v1` with `version: latest`.
- `Ephemeral Financial Rules` posts raw tails of Supabase startup and T1–T15 logs into PR comments.
- The isolated workflows construct disposable Supabase environment values locally; no production credentials are required by their current workflow definitions.
- FIN-COURIER Gate-4 PR #27 currently shows repeated pre-step workflow failures: jobs are created but contain `steps = None` and no downloadable job log. Those runs are infrastructure/account evidence only and are not accepted as application-test failures.

## Proposed delivery sequence

1. Gate 4 safety net for CI hardening: static workflow-policy tests and redaction/determinism assertions.
2. Focused workflow hardening implementation PR.
3. Exact-head execution proof across Quality, Financial Rules, Auth UI, and the then-current FIN-COURIER Gate-4 workflow.
4. Independent security/CI review.
5. Explicit human merge only.

## Non-goals

No product feature, financial business rule, schema/RPC/RLS change, production access, automatic merge, or deployment.