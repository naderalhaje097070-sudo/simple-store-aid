# B4 initial design addendum — binding revision

Date: 2026-10-21 UTC. Reviewer: `/root/foundation_a_independent_review`. Base remains `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0`; no exact executable B4 head has been approved.

After the initial report, I read the local first SQL prototype and `src/lib/subscription-webhook.server.ts`. These are working files, not a published/tested source identity. The implementation owner agreed to replace the first prototype's cross-subscription latest-event projection and proposed a second private binding table.

The revised direction is acceptable for implementation subject to final source and runtime review:

- A binding separates the identity selected for a tenant from each subscription stream's newest state. Created events may replace a non-null binding under an explicit creation-order rule. Non-current updated/canceled events may persist their own state and a non-current receipt without replacing another subscription's cache.
- Verified immutable provider subscription creation time can order subscriptions, independently of event occurrence time. The same subscription ID must not be allowed to learn a different creation time from a later payload. Equal creation time for different IDs is ambiguous; no lexical-ID tie break is justified.
- A valid snapshot may bootstrap an empty binding. A late created event can establish a newer binding using that stream's already stored newest state, even when the created snapshot is stale for stream updates. The older snapshot must never overwrite that newest state.
- Unknown legacy binding chronology remains fail-closed. A verified matching-pointer snapshot may establish its creation identity; a different subscription cannot claim a binding by silently treating the server write timestamp as provider creation time.
- Provider creation time on **new public subscription rows** intentionally changes `created_at` from receipt-time insertion ordering to entity-creation ordering. Document that compatibility decision explicitly; do not rewrite existing row timestamps. The unchanged billing query orders this field, so checking the private binding alone is insufficient: equal creation times must not leave two newly admitted ambiguous rows that the UI can select nondeterministically.
- A repair must still validate environment, immutable mapping, current pointer and newer projection state. A successful no-op receipt cannot lower the legacy floor.

This is narrower than rejecting all multi-subscription events, and does not introduce a plan/status priority policy. The extra private binding table needs the same explicit client-denial, invoker, retention and populated migration analysis as the receipt table.

The current normalizer retains input timestamp text and explicitly accepts at most six fractional digits, addressing the precision condition in the initial report. Its persistence deadline treats a late commit as uncertain and returns 503; it does not claim that aborting the fetch canceled the transaction. The final state allowlist must include any newly introduced committed `non_current` outcome, with an actual positive test. The SQL must enforce the documented rejection of customer/owner/environment reassignment rather than merely ignoring a conflicting input field.

No new final finding is asserted from the unfinished prototype. The initial review, inherited APP-02 High failure, current general DEP-20261021 High barrier and missing exact-source/native evidence remain unchanged. No tests, DB/provider action, source modification or GitHub write were performed in this addendum.

