# PRIMARY-ENV-001 — isolate the security candidate

Date: 2026-10-10. Repository: naderalhaje0970-droid/simple-store-aid.
Authority: owner explicitly requested Sol implementation and separate Astra review
of environment isolation after choosing to continue locally without paid Actions.
This authorizes candidate preparation; merge, deployment and production access
remain excluded. Existing SEC-ENV Gate4 approval (#47) and business decisions stand.

## Goal and baseline

Reconcile the existing PR48 implementation at
`31958e53438b377a9896dd0bf7e9c268c1f14aef` with security candidate PR53 at
`54c930166a776828566876771efdec86a997fa53`. Main remains
`43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.
PR48's body cites an older head and its historical green ancestor is not current
acceptance evidence. Inspect current source and reuse it rather than reimplement.

## Scope and gates

Risk: high, because build/runtime identity and write-capable test routing change.
In scope: PR48's 18 configuration/runtime/harness/workflow paths, relevant bounded
regressions and reconciliation evidence. Out: dependencies/lock, financial formulas,
RPC/RLS/schema, migration, tenant/customer data, provider payment, merge/deploy.
Gate0 approval is supplied by the owner's implementation instruction above.
Before changing behavior, reproduce missing-config fallback and record baseline;
inspect all affected callers and imported PR48 protections. Keep independent
expected results and existing negative sentinels. No live financial harness runs.

## Expected contract

Missing/ambiguous targets fail closed. Local/CI uses explicit loopback configuration;
preview/staging uses a distinct project; production requires explicit intent and
the approved identity. Build and runtime identities must match before app imports.
Browser, REST and PostgreSQL test routing remains isolated. Public bundles never
receive privileged keys. No successful DB/isolation release proof is assumed.

## Acceptance and rollback

Pure boundary/unit/probe checks, typecheck, changed-source lint, isolated build and
offline harness preflights; final separate Astra source/evidence review. Hosted five
workflow execution and DB/auth/financial journeys remain pending if unavailable.
Save hashes, commands, failures, limits and one next action. Keep main unchanged;
rollback closes the draft or adds a revert, never rewrites Lovable history.
