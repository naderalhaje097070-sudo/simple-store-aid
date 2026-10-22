# B4 d86 native failure triage — unresolved runtime observation

Independent reviewer: `/root/foundation_a_independent_review`. 2026-10-21 UTC.

Run `39611234351` is actually failed on `d86a6278bbd2513d34a45cf5390d2c69fb820611`. Job `119260474327` records `APP02_HARNESS_FAILURE failed positive/isolation control: created_cancel_default_false`. The log records exit 2 and successful cleanup. This failure is retained; it is neither B4 acceptance nor a proven SQL root cause.

I fetched the exact d86 probe, normalizer and adapter read-only. The probe sends a missing-stream updated event, then a created event for the same subscription with a different event ID, then tests the stored flag. Its event dictionary construction does not visibly mutate the original event. The failure artifact does not show the actual flag, row existence before the first call, receipt outcome, or the actual function body at this point.

A targeted local check using actual Paddle 3.8.0 HMAC verification and the normalizer byte-matching d86 produced true for updated(cancel=true), then false for created. Results: `d86-offline-normalization.json`. This ran on local Node 24.19.0; it was not a frozen native Node 22 test, and made no RPC, database or provider call.

The inspected 49 CASE returns false for a new created row and preserves an existing true flag. Consequently changing SQL without observing actual runtime state is not justified. A prior row, a different actual function/input, or an oracle/fixture issue remains possible. The first 503 being named “missing stream” does not prove its actual database reason; snapshot invariance only proves no observed change relative to that snapshot.

Requested bounded diagnostics are booleans/fixed labels/hashes only: row existence and flag before the missing update, after it and after created; receipt type/outcome and normalized request flag; hashed event/subscription identity; and actual body49 comparison before cases. No raw credential, actor state or full identifier dump is needed.

B4 remains blocked pending diagnosis and final exact-source native evidence. Migration 49 must not be edited after application. No production, provider, DB test, source modification or GitHub write was performed by this reviewer.

