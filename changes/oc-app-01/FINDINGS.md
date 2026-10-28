# OC-APP-01 disposition and limits

## Original finding

Severity: Medium.
File/contract: src/utils/payments.functions.ts / resolvePaddlePrice.
Evidence: original6807c198 live baseline allowed closedB old/new genuine Auth-valid tokens to invoke dummy gateway and return price;9dummy calls in complete76-observation matrix.
Risk: retained Auth identity/JWT permitted application price access after account closure.
Required fix: server-side current account assertion before gateway/keys, no generated middleware/financial/provider change.
Verification:708e43f3 fixed121 unique observations +Quality70units/172expect and independent source/raw/log review.
Disposition: **addressed in unmerged tested candidate for this function only**. Still unfixed onmain. Integration/release approval remains pending.

## Independent scoped review

No new Critical/High/Medium implementation/evidence finding in this bounded matrix. See FINAL_REVIEW.md for reviewer actions and limits. The two earlier decoder failures remain recorded as harness failures, never substituted for expected-red.

## Outside acceptance scope

All-app/generalroute/UI coverage, concurrency/in-flight/TOCTOU, provider billing/webhooks/real live-or-sandbox behavior, Cloudflare/production, full provider-service egress and broader finance remain unverified. This task does not resolve the integration dependency stack or approve a release.
OC-EVID-02 Low remains the previously deferred closure-harness label issue in TASKS; this task did not modify/replay that harness.

ONE NEXT: planning review of this candidate underG5/#70. No additional implementation authorized by this handoff.
