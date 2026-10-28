# B4 / APP-02 current source review

Reviewer: `/root/foundation_a_independent_review` (independent of implementation). Date: 2026-10-21 UTC.

**Outcome: Changes required for the reviewed local prototype.** Two Medium source findings require correction/disposition. Native evidence and an exact executable B4 SHA remain pending. The whole integration head separately remains Changes required because DEP-20261021 High and the existing A/B identity mismatch are unresolved. This report grants no B4, B5/B6, merge or production acceptance.

## Exact inputs and evidence boundary

Base: `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0`. These are unpublished working-source inputs, not a final commit:

| File | SHA256 |
| --- | --- |
| src/lib/subscription-webhook.server.ts | 58828eb01b35d32b3364e158c485a41420a5c3e95c83957cf312628a3e3f251e |
| src/routes/api/public/payments/webhook.ts | be7da785c48e97a340d2f35c2e2525abd90881a21abefabcb92b8ad6977881f6 |
| changes/b4-app02/WEBHOOK_PERSISTENCE.sql | 9df379f65dfa8c2e22b0f143da0203b44dea501f1c596f8214871c34cdcbe408 |

Byte-identical text snapshots are retained under `current-source-inputs/`, with `current-source-inputs.json`. I also inspected the actual unchanged billing query, old schema/grants/live-actor migration, and the B3 grant correction. The findings below are source-confirmed control-flow cases. `current-source-counterexamples.json` records a deterministic source-derived sort witness; it does not execute SQL.

No provider, production, database, signature test, deployed HTTP request, historical suite, or native test was run by this reviewer. Root is preparing the actual locked-SDK/disposable-database harness separately.

## B4-SOURCE-01 — legacy/public ordering can disagree with the new binding

**Severity:** Medium. **Claim:** confirmed within source reasoning; not a live SQL/UI execution. **Status:** open on the hashes above; implementation owner has proposed a fail-closed correction.

**Affected contract:** SQL lines 183–215 learn/order provider creation time and choose the binding; lines 234–244 write provider creation time only for new subscription rows and preserve existing public creation time. The unchanged billing consumer selects `subscriptions` by tenant/environment ordered by public `created_at DESC`, limit one.

**Reproducible source case:**

1. Legacy subscription A has provider creation 10:00 but public creation 13:00 because its old handler inserted on arrival. A valid matching snapshot establishes A's private provider creation identity; existing public creation time stays 13:00.
2. A created notification for B has provider creation 12:00 and active state. A is canceled. The function correctly sees B as newer than A's known 10:00 private binding, writes B with public creation 12:00, binds B and projects B active.
3. The function returns a committed outcome, while the unchanged billing query still selects A at 13:00 and displays its canceled state.

**Risk:** the correction introduces a populated-upgrade case where successfully committed billing state and the real consumer disagree. The entitlement helper's existing any-eligible-subscription behavior is not shown bypassed; no new paywall impact is claimed.

**Required fix:** keep the consumer/order contract coherent or fail closed before an ambiguous created binding is accepted. A guard using the target row's actual stored creation time, rejecting any other same-tenant/environment row with creation time greater than or equal to it, can contain the live case without rewriting legacy rows. The unchanged billing query is also used for sandbox: do not omit the corresponding ambiguity decision merely because sandbox has no global tenant projection. A declared non-current outcome must not be represented as proof that cache and UI select the same subscription.

**Verification:** populated fixture A(public13/provider10) → matching A snapshot → created B(provider12), with A canceled/B active; assert either the explicit 503/no-mutation contract or coherent target selection. Cover existing target rows, same-time rows and both environments. Preserve an ordinary new A→B successful control and the updated-B-before-created-B control.

## B4-SOURCE-02 — surviving receipts do not preserve stream identity after the public row is absent

**Severity:** Medium. **Claim:** confirmed within source reasoning under the explicit missing-row precondition; provider exploit reachability is unproven. **Status:** open on the hashes above.

**Affected contract:** SQL lines 106–122 validate environment, customer and tenant/user identity against `v_old` only. The receipt lookup at lines 113–116 checks only creation time and is scoped to the requested environment. The later previous-receipt state is not used as an immutable identity check.

**Source case:** process an event for subscription S / live / tenant A / owner A / customer A. Its receipt survives. Remove the public subscription row through a fixture operation or a legitimate parent deletion; the existing schema cascades subscriptions when a tenant is deleted, and the proposed receipt deliberately has no foreign key. Send a later, new event ID for the same S and same creation time with tenant B/owner B/customer B, where B is a valid current tenant-owner pair. With `v_old=NULL`, all three old-row identity comparisons are skipped, mapping comes from the incoming input, and the function can insert S under B while the old A receipt remains. Requesting the other environment additionally avoids the receipt creation-time/history lookup entirely. A concurrent global lock serializes this case but does not enforce historical identity.

**Risk:** the stated no-reassignment and cross-environment identity contract is lost exactly when the persistent receipt is the remaining source of known stream identity. This is not a claim that a client can forge a Paddle signature or a service credential. Existing tenant DELETE grants/policy and the subscription cascade establish an inherited possible deletion path at source level; no destructive client action was performed.

**Required fix:** consult retained history for the globally known provider ID and enforce environment/tenant/user/customer identity when relevant, or simply reject a missing public row when that stream already has receipts. The latter is a narrow fail-closed option; it does not require resurrection or a new retention policy. Existing exact duplicates may still acknowledge a previously committed receipt without recreating deleted rows.

**Verification:** after a committed synthetic event, remove only the fixture's public subscription row and send a new event ID attempting same-environment reassignment and cross-environment reuse. Require non-200 and no new public row/binding/receipt mutation, plus normal same-identity service behavior with its row intact. Do not treat an expired JWT or generic setup failure as the denial reason.

## Source properties that address the earlier design concerns

The current handler verifies through the original selected-environment helper before persistence; rejects explicit invalid environments; normalizes supported snapshots; retains 1–6 fractional timestamp digits; accepts only named committed statuses including `non_current`; and returns 503 for persistence errors, malformed/missing results or deadline uncertainty. It logs fixed reason labels. These are source observations, not signature/runtime proof.

The proposed RPC is SECURITY INVOKER, checks the actual database role rather than request role text, revokes PUBLIC/anon/authenticated execution, and uses explicitly restricted private tables with RLS. Existing private schema USAGE for service_role is supplied by the retained account-state migration. Its safe search path, UTC setting, consistent subscription/event/tenant serialization, checked binding/subscription/receipt rowcounts and absence of exception swallowing support an atomic boundary. Effective deployed privileges and rollback still need the native catalog/transaction tests.

The new binding separates event chronology from subscription identity. Non-current updated/canceled streams do not replace the existing pointer; a late created notification can bind using the stored newest stream state. Equal event time with different state fails; the event-ID secondary sort does not choose between conflicting state because those conflicts raise before insertion. A same-time equal-state receipt is harmless. The frozen legacy floor is retained separately, and stale receipts are excluded from the next stream-state watermark. These mechanisms require actual concurrency, legacy and partial-failure tests before acceptance.

Conditional cache update avoids rewriting an already matching cache. A tenant-write fault test must change a required projected field so it exercises the actual write; a skipped unnecessary update is not a successful fault injection.

## Required next review boundary

Correct the two scoped cases, retain this failing-source review, and pin the resulting migration/route/tests/workflow to one exact executable SHA. Then independently inspect the actual fresh/populated native receipts, signed-handler execution, permission matrix, failure/rollback/retry/concurrency results and original-source preservation. No historical full suite or B3 acceptance rerun is requested here. General dependency remediation remains outside this B4 code change and remains required before broader acceptance.

