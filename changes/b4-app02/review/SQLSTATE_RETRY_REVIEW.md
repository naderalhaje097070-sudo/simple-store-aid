# B4 application SQLSTATE retry finding and source-50 review

Independent reviewer: `/root/foundation_a_independent_review`. Date: 2026-10-21 UTC.

**B4-SOURCE-04 — High, introduced reliability/availability defect.** Claim: native delayed mutation is observed; the retry mechanism is strongly supported by official source/documentation and the observed version class, without a driver/backend execution trace. Source-50 correction is verified at source level; final native closure is pending. This is separate from inherited APP-02 and the general DEP-20261021 High barrier.

## Runtime evidence and cause boundary

The earlier d86 run failed `created_cancel_default_false`. Its artifact lacked the actual flag/body at the point of failure, so `D86_FAILURE_TRIAGE.md` deliberately left the cause unresolved.

The subsequent diagnostic on `f4e24001d6a08128da7c63fa0ee3600bfcbeb333`, run `39612546949`, fresh job `119265021125`, removes that ambiguity:

- The updated request returns 503, with immediate data invariance.
- `creation_recovery_stream_absent` confirms no existing stream before created.
- Created returns 200; its receipt request flag and resolved flag are both false, and outcome is applied.
- The subsequently read public row flag is true.

I read those actual controls from the diagnostic ZIP and matched its bytes to GitHub artifact `12352285260`: SHA256 `1145b4e15981daf4074c643404780e0313337e30ba1bff2172784a8888b72b67`. This establishes a later write inconsistent with the created receipt's own false state; it does not by itself identify a backend PID or prove a measured CPU flood.

The supplied created input is independently narrowed further by `d86-offline-normalization.json`: actual local Paddle 3.8.0 HMAC verification and the d86-matching normalizer return false for created. That local check used Node 24.19.0, not frozen native Node 22, and made no database/provider request.

The proposed functions manually raised SQLSTATE 40001 for application refusals, including missing creation state and permanently ambiguous legacy/order conditions. Official Supabase troubleshooting documents repeated transactions for custom 40001 on PostgREST 14 and recommends P0001; PostgREST's upstream fix disables those retries in version 16. The inspected Hasql source has a retry loop and routes 40001 into it. Earlier successful runtime image receipts in this same pinned CLI setup show PostgREST v14.10. The diagnostic's late flag mutation is consistent with the prior updated call remaining retried after its client timeout, then succeeding after created makes the stream available.

That last causal link is a source-backed inference, not an observed driver trace. No production impact, actual provider exploit or measured CPU/connection exhaustion is claimed.

## Impact and required correction

A refusal intended to return control to the delivery/reconciliation process instead becomes repeated database work and can take effect after the caller receives 503. Persistent legacy/identity ambiguity can cause an unbounded backend retry workload on the affected server version. The public callback requires a valid selected-environment signature; direct ordinary-user RPC access remains denied. Legitimate out-of-order signed callbacks are sufficient to reach the problematic domain condition.

Do not encode application refusals as serialization failures. Preserve the transactional rollback and route-level retryable HTTP response while using a non-retrying application error class. Do not change engine-generated serialization/deadlock semantics, weaken the guard, or upgrade unrelated dependencies in this correction.

Earlier source reviews assessed the intended application retry rule without accounting for this transport-level internal retry classification. The actual native failure exposed that gap. Those reports/failures remain preserved and were never final B4 acceptance.

## Reviewed correction and exact identity

Stage `4385e95799980d12890d18579c964b0d14e6f151` supplies `WEBHOOK_ERRORS.sql`; final executable source is `f3b702440a4ffd17038f3c668a2f446620a97919`, complete Git tree `6bc91e3b942dccfa5beab67b57f0c22c15b78917`.

I compared function bodies: source 50 is exactly source 49 with **ten manually raised ERRCODE 40001 values replaced by P0001**. No other body or grant/path/lock/ordering/binding change is present in that diff. The route continues converting an RPC error to HTTP503; this does not claim that PostgREST itself maps P0001 to 503.

CLI-generated migration `20261021140746_webhook_errors_01.sql` SHA256 is `a5cff8d91149a61424f1d6cd62bf60cc42a334623085eec7e706ac3b0f38f955`. Its generator ZIP matches GitHub artifact `12352122067`, run `39614071707`, SHA256 `74df1e2fb9b3f617458c0cecad2d8d78c9c158ea904a1aa383f25101342fc60c`. The generated payload exactly matches the reviewed proposal. Generation started no database. Applied 48 and 49 remain byte-exact.

Independent complete-tree comparison against B3 `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0` observes 358 protected paths / 50 SQL files. All 47 original migrations are exact; the only changed pre-existing protected file is the intended webhook route. There are no deleted paths. Records are retained in `source50-identity.json` and `source50-complete-tree.json`.

Local source is a blob extraction, not a checkout: 352 available protected blobs match, six known binary blobs are absent locally, and two extracted shell files lack the Git executable bit. Official Git tree modes are preserved. No local frozen or complete-checkout proof is inferred.

## Remaining native verification

The new fresh-50 and populated-47→50 stacks start without old retry backends. The probe compares actual function body to 50, rejects manual 40001, checks no delayed receipt before explicit updated replay, checks created false then updated true, and retains atomic fault/recovery, ordering, identity and permissions cases. It now exports safe before/after populated fingerprints/catalog hashes, allowing independent comparison when artifacts arrive.

No new functional defect was found in this bounded source-50 delta. Runtime acceptance remains pending on the exact final source; earlier 48/49 successes/failures are not promoted. No protected merge, deployment, production access or driver upgrade is performed by this review.

## Primary sources

- [Supabase: SQLSTATE 40001 in RPC functions causes infinite retries](https://supabase.com/docs/guides/troubleshooting/high-cpu-and-infinite-transaction-retries-when-using-custom-error-codes-in-rpc-functions-77326b), consulted 2026-10-21.
- [PostgREST issue 3673](https://github.com/PostgREST/postgrest/issues/3673) and [fix 4222](https://github.com/PostgREST/postgrest/pull/4222).
- [Hasql transaction retry implementation at 2a9a710](https://github.com/nikita-volkov/hasql-transaction/blob/2a9a710bd6230cb0abae84f14f852ab14fc3fa85/library/Hasql/Transaction/Private/Sessions.hs).

The Hasql source illustrates the mechanism cited by PostgREST; I do not claim its exact source commit is the binary embedded in the diagnostic image.

