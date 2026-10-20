# Proposed ONE NEXT — OWNER-CLOSURE-IMPLEMENT-01 (not authorized here)

This is a bounded implementation proposal for planning after the effective catalog
receipt. OWNER-RETENTION-01 is approved policy, not approval to run this proposal.
Do not implement until planning/owner authorize the exact source/design, closure
action, fixture boundary and checks. Main and the unmerged stack must first be rechecked.

## Smallest enforcement boundary proposed

Retain the Auth user, tenant ownership, role/profile links and every business/audit row.
Represent closure as persistent application authorization state rather than Auth
hard-delete, tenant delete, role unlink or a temporary ban pretending to be closure.
Reuse monjez_private.actor_is_active/assert_active_actor and their existing RLS/RPC
consumers; do not redesign financial formulas, delete guards or cascade relationships.

One forward-only migration could add a private minimal owner-closure record with a
stable user ID, tenant ID and closed_at, locked from ordinary DML. References must not
CASCADE-delete history or erase identity; a non-cascading user/tenant reference must be
reviewed against the final catalog and future explicit erasure workflow. Do not add
email/name copies or invent retention duration. This design choice is a proposal,
not an approved new schema or a declaration of perpetual retention.

Update the existing private active-actor predicate to deny a persisted closed owner,
using a SECURITY DEFINER query with safe search_path and verified owner privileges,
without a profile-RLS recursion. Add one transactional, least-privilege closure entry
for the authenticated owner to close only their own account/store. No arbitrary target
ID, cross-tenant closure, employee closure, reopening, transfer, new access grants,
subscription cancellation, account/tenant deletion or public cleanup endpoint.
Repeated authorized closure should be idempotent with no repeated state/audit effect;
closed callers must have no route to clear the state via generic profile/table writes.

Before code, fix the action/actor/result/error contract and source dependency map.
Explicitly resolve account-wide versus store-scoped closure from actual ownership
cardinality (including standalone unique indexes, not only pg_constraint). A closed
account must lose its existing application access without changing other identities'
rights. An already-closed actor's idempotent repeat needs a narrow explicitly designed
result path, with no reopening or protected data read exception.
The proposed record itself can be the auditable closure event; if another audit append
is specified, its exact allowed metadata delta must be explicit and transactional.
Current Auth may still issue tokens to a retained user; all old/new tokens must be
denied application access through the persisted state. Blocking provider sign-in is a
separate supported-provider design if required; do not quietly claim it from RLS.

The catalog confirms authenticated TRUNCATE on21publictables. RLS does not mediate
that privilege, although no ordinary-user SQL/REST reachability was demonstrated.
Planning must resolve its scope before claiming all retained-data authorization paths
are closed: remove unused destructive grants in an explicitly included forward-only
hardening boundary, or record an accepted narrower surface pending separate repair.
Do not assert an RLS closure predicate revokes TRUNCATE. No privilege repair occurred
in the verification batch, and its approval does not authorize that future change.

No financial amount, balance, debt, custody, rights, obligation, stock or order-state
transition is part of closure. No customer/courier history or financial audit link is
edited. Keep staff/admin/other tenants' existing permissions as they were; closure
must not confer access on anybody. UI feature expansion and erasure policy are excluded.

## Test boundary and acceptance proposed

Nonempty financial testing is still gated. The implementation batch is not ready to
execute until a separately explicit disposable fixture boundary is accepted under the
isolation/financial-write rules. Use existing approved RPC/domain logic; no direct SQL
financial insert shortcut or silent bypass. If this gate prevents a representative
fixture, stop and report the blocker rather than weakening the history test.

Use one fresh local stack, full immutable migration chain plus only the proposed new
migration, existing genuine OAuth/PKCE and actual Nitro/TanStack /mcp harness. Two owners
A/B in separate tenants; deterministic B product/order/item/payment/audit and known
independent amounts/stock/identity links. Snapshot all public rows and financial tables,
including expenses/day-close/counters at their actual fixture baseline; an order-number
RPC may populate counters. Require the baseline unchanged after closure; evaluate
expected values independently.

1. B and A have proven valid identities and successful own REST, read-only RPC and MCP
   initialization/tool calls before closure; no empty-output-only history control.
2. One supported authorized B closure persists exactly once. Foreign/unauthenticated/
   wrong-role or malformed closure attempts have explicit rejection and trusted no-effect.
3. Reuse B's exact unchanged, unexpired token after closure; old and genuinely new B
   tokens deny application data/protected operations because of closure. No expiry,
   ban/delete/logout substitution. An initialize response alone is not access denial.
4. A's original still-valid token succeeds after B negatives and A data is unchanged;
   no blanket denial accepted. Failed generic HTTP500/timeout/[] is not proof.
5. B Auth user/tenant/ownership/profile/role and prior financial/audit rows remain, with
   identical financial values/rights/obligations/stock and identity links. Only the exact
   private closure state/audit delta in the contract is allowed; no SET NULL or relink.
6. Generic writes cannot reopen/clear closure, change ownership or grant access.
   Repeated closure produces no duplicate event or financial effect. Definer/RLS
   privilege/recursion regression checks target the changed authorization predicate.
7. Clean migration application and relevant upgrade-path proof, focused Quality,
   containment, secret quarantine, cleanup and independent adversarial review on the
   final source. State precisely whether the reviewer replayed live or read logs.

Acceptance is closure within that tested scope only. Nonempty foreign isolation,
concurrency/in-flight semantics, Cloudflare/proxy/production, personal-data duration/
erasure, commercial cancellation and release remain separate. integration_accepted=false.
Do not close broader gates from a small fixture.

## Stopping and rollback

One implementation candidate PR only; no merge/deploy/production/cost/history rewrite.
If source/runtime or fixture constraints invalidate the design, preserve failure and
propose a smaller repair intake rather than widening scope. A closed owner must not be
silently reopened as rollback; forward compensation needs explicit authorization.
For tests only, destroy the disposable stack without backup. Production rollback is
not authorized by this proposal. Stop at reviewed evidence and handoff to planning.
