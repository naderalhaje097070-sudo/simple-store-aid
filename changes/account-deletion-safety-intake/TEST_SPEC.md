# Minimum next isolated deletion verification — DESIGN ONLY

This document is a proposed test specification, **not executed tests, not deletion permission and not a retention policy**. Its decisive prerequisite is OWNER-RETENTION-01 (REPORT_AR.md). Source-predicted CASCADE is an observation, never the product pass oracle. No runnable new script, workflow, fixture, API or cleanup RPC is added here.

## Why a single unconditional success oracle is impossible today

The owner FK is auth.users -> tenants ON DELETE CASCADE. With no schema/app repair, deleting an owner that has an extant tenant cannot both prove absent Auth row **and** retained same tenant as a guaranteed current-source success. In populated finance, audit append may instead abort deletion. Counting a failed delete as a deleted identity is false evidence; treating erased history as safe because CASCADE predicted it is also false evidence.

After the owner decision, choose ONLY the branch matching the approved contract. If it needs a different schema/ownership boundary, do a separately scoped implementation intake first; do not weaken the test to accept current data loss. No retest of completed expiry/ban/soft-delete suites is warranted just for this design.

## Fixture and source boundary

Use one fresh disposable loopback-only runner, existing CLI2.101.0 / Auth2.188.1 / PostgreSQL17.6 family / PostgREST14.10 and full43 pinned migrations from exact authorized stacked source. Reuse correction/mcp_tanstack probes, OAuth/PKCE fixture, genuine application Nitro/TanStack route, network UID/fetch barriers, redaction/quarantine and stop/key/no-backup receipts. Do not use cloud/linked production project, backups or existing business IDs.

Initial trusted check must prove empty stack and exact runtime/source. Capture **effective full incoming FK actions and enabled triggers across auth/public/storage as present**, constraint modes, RLS, grants/role memberships, definer bodies and43 hashes. Compare SOURCE_MAP before any destructive call. Capture any incoming single-ID references from outside the deletion tenant; explicit fixture links must be same-tenant. A basic metadata positive does not establish nonempty foreign financial isolation. Specifically reconcile authenticated TRUNCATE grants without executing TRUNCATE; never disable triggers/FKs or impersonate service_role for user-negative controls.

Smallest populated-history branch: two real unbanned owners A/B, two distinct tenants; A own nonempty read metadata positive and B own product+one direct paid order+one item+one payment+financial audit row, with explicit actor links. Direct fully-paid order avoids customer/courier fixtures; stock/price/cost and payment amounts fixed and independently calculated. Seven financial tables = orders/order_items/payments/expenses/day_closes/tenant_counters/financial_audit_log: snapshot **all**, including zero-row ones. All public tables plus targeted Auth state are snapshotted before action. Capture Paddle-shaped subscription metadata only if approved contract requires it, no external service request.

**Fixture approval dependency:** this branch needs successful nonempty financial fixtures, which current financial-write/isolation gates do not authorize. This design proposes a separate trusted deterministic fixture boundary: no product transaction coverage claim, independent stored oracle, exact source/constraints/triggers on and no public cleanup. Do not bypass the gate by relabeling direct SQL inserts as harmless metadata. Both destructive action and nonempty fixture permission must be explicit before execution.

Do not add staff to the owner-only baseline. Non-owner identity SET NULL is a separate diagnostic scenario if later needed, not proof of owner safety.

## Ordered observable controls

| Phase | Required observation | Acceptance / reject false evidence |
| --- | --- | --- |
| Precondition | A/B Auth rows exist; deleted_at NULL, no active ban; B owner linkage/role/tenant exactly known; provider-issued B token signature/sub/aud/issuer/client verified | Real code/PKCE token supports same MCP path. No local crafted token, no ban or soft-delete substitution |
| Token lifetime | Lock original B token in memory; verify enough remaining exp for entire bounded run (e.g.>=600seconds, measure rather than force); autoRefreshToken=false; same-token fingerprint internal | Recheck exp at every post-delete negative. Expiry cannot be the cause; no clock manipulation, refresh or natural-expiry suite rerun |
| Baseline active | B own REST tenant + read-only summary RPC + actual /mcp initialize/initialized/catalog + four real tools succeed; A own REST/RPC/MCP positives too | Nonempty B orders/product payload confirmed from trusted oracle; empty zero summary not positive proof of history |
| History baseline | Exact IDs, tenant links, monetary values, stock, closed summaries, audit contents and actor map; all22public hashes; effective FK/trigger baseline captured | Taken BEFORE deletion/hostile reads; oracle from explicit expected values, not copied application math |
| Authorized owner lifecycle action | Exactly one operation matching approved contract; capture method/mode and sanitized error or success. No added deletion feature | Auth DELETE hard mode must be distinct from should_soft_delete=true. UI logout/role unlink/ban cannot stand in |
| Stored outcome | Trusted reader proves either actual missing Auth row and authorized metadata deltas, or rejected action and full atomic no-effect | API200 alone not enough. FK/trigger failure retains Auth: record blocker/rejection and do not claim deleted-user denial |
| Financial preservation | Compare allfinancial seven tables and business balance/stock oracle after action, apart from exact identity changes/additive audit allowed in the approved contract | No loss/relink of business rows, amounts or custody accepted unless separately approved. Account/tenant FK cascade prediction cannot waive the invariant. Preserve old audit rows; new audit rows evaluated separately. SET NULL/updated_at must be labeled |
| Deleted JWT denial branch only | ONLY when B Auth absence actually verified: old unchanged unexpired B token gets no own/foreign data via REST/RPC/full MCP and cannot execute protected entries | Exact auth rejection/42501 account_inactive or pinned provider user-not-found; 5xx/timeout/invalid signature/expiry or generic empty [] is NOT standalone denial proof. Transport may allow initialize from valid JWT; then protected tool/RPC must explicitly deny. No numeric success-as-denial |
| Unaffected A | Same A positive sequence after all B negatives; A trusted rows/values/links unchanged, no blanket deny | Cannot substitute new A when old A failed; control token stays unexpired. A must remain active |
| Closure | Capture source/runtime/mode and sanitized observations, before/after diff, provider error, cause classification, containment, credential scan and cleanup | Failure/partial setup retained and never converted to expected PASS. No in-flight/concurrency coverage inferred |

## Contract-specific minimum branches

1. **If approved rule prohibits owner hard-delete with history:** protected deletion attempt must be rejected before any record loss; compare full atomic preservation. It is an owner-retention test, **not** a deleted-account token test. Existing raw Auth admin/SQL has no application guard surface, so any policy-enforcement work requires separate intake; do not claim the audit-FK accident is the intended protection.
2. **If approved rule preserves tenant/history via ownership transition or tombstone:** implementation/financial contract must be separately approved and tested first. Then one two-owner populated run measures precisely permitted metadata deltas and B absent/inactive semantics. Disabled/tombstone B is not hard-deleted; report exact state.
3. **If populated hard-delete fails and the missing-user gate is still separately authorized:** retain failure receipt and use a **separate disposable run** with the same two-account design; B owns no tenant/financial data, A has the separately approved retained-history fixture. Hard-delete B proves missing-user token denial plus A unaffected/history stable only. It proves **nothing** about deleting the owner of populated tenant B. Do not empty B finance or drop its tenant just to obtain a passing deletion.

These are alternative authorized scopes, not a request to execute all three. Minimum next activity right now is owner contract decision, not test execution. No concurrency, broadL01–L15 closure, Cloudflare/proxy/production/provider upgrade or old matrix replay in this proposal.

## Exit states

- Design ready for owner decision: this intake.
- Policy/fixture/deletion permission missing: BLOCKED; zero live action.
- Deletion aborted/trigger error: observation/contract failure or blocker; B not deleted. Do not run user-absent claims.
- B missing but own financial history erased: safety invariant FAIL, retain receipt; no repair here.
- Exact approved contract + legitimate post-action denies + A positive + trusted financial invariants + cleanup all satisfied: Tested candidate scope only; independent review required, no main/release/integration acceptance.

Rollback for this documentation packet: close Draft PR, or additive documentation revert if human-merged. A later destructive test rollback is destruction of the disposable runner only, never a production compensating migration/restore.
