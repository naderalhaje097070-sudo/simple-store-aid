# B4 / APP-02 bootstrap ordering finding and forward correction review

Independent reviewer: `/root/foundation_a_independent_review`. Date: 2026-10-21 UTC.

**Finding B4-SOURCE-03: Medium; confirmed by source reasoning on executable 7c6ed73886aa3a23c03f78c77762e900174ec368.** Its unsupported-bootstrap behavior is corrected at source level in the proposed 49 body reviewed below; final native verification is pending. The earlier 188-control fresh result is genuine evidence for its named cases, not acceptance of the untested arrival-order cases.

## Evidence and actual boundary

The immutable migration 48 `20261021132651_webhook_persistence_01.sql` has SHA256 `95b527271e552f20bfb8a0e07627e0195ed681c46e3f8cbcb7d5daaa4a98a66d`. Its stream ordering skips writes for older events. For existing rows it deliberately keeps product/price on updated/canceled, periods on canceled, and the cancellation flag on canceled. For a missing row, the first updated/canceled snapshot nevertheless seeded a new row. These rules compose differently depending on arrival order.

The retained helper `public.tenant_has_active_subscription` treats a canceled subscription with a future period end as eligible; an expired trial does not mask a missing end date.

`bootstrap_ordering_source_witness.py.txt` and its JSON output provide a rerunnable deterministic trace tied to migration 48's exact hash and relevant source fragments. I ran that **offline model only**. It does not execute SQL, the SDK, HTTP or a provider. The witnesses assume one valid mapped tenant/owner/stream and no competing rows:

| Witness | Normal event order | Reverse arrival |
| --- | --- | --- |
| Created with a future period end, then canceled with null period | Canceled keeps the known future period; helper's relevant branch is true with expired trial | Canceled seeds null; older created is stale; relevant helper branch is false |
| Created → scheduled updated(cancel=true) → canceled with even a full period | Existing canceled keeps true cancellation flag | Canceled seeds false; older snapshots remain stale |
| Created basic plan → updated pro snapshot | Updated preserves basic product/price, as the old handler did | Updated seeds pro; older created stays stale |

This demonstrates loss of the stipulated field semantics, not a live entitlement exploit or a production billing effect.

## Required correction and early design assumption

Do not acknowledge an unseen updated/canceled stream as fully persisted when the fields intentionally preserved from its history are unknown. The narrow correction is 503 with no row/binding/receipt mutation, then created establishes the original fields, then replay of the newer update/cancellation applies the existing semantics and event ordering.

My earlier design support for full-snapshot bootstrap was conditional on preserving complete write state. The actual source shows that a provider snapshot does not recover fields the old contract deliberately kept from previous events. That assumption is therefore withdrawn for unseen non-created streams. The reports remain preserved; no initial design note is promoted into final acceptance.

Existing public rows from the old partial-write handler can still receive a non-current update, and a late created notification can bind their newest stored state. That is recovery of an existing stream, distinct from inventing missing creation history.

## Forward body and harness reviewed

Stage source: `c5a362116d2455077a604c75f27b89198cbb6c11`. Proposal `changes/b4-app02/WEBHOOK_BOOTSTRAP.sql` / generated file `20261021134621_webhook_bootstrap_01.sql` SHA256: `c905a149d7deb0cb9b22080142152a5a06aa2c982b4ee7f907c63a434cff3f75`. Generation is not database application or runtime acceptance.

I compared the 49 function body against 48. Its functional changes are:

1. A missing public stream for updated/canceled raises before history/mapping/binding/writes.
2. Created resolves its flag to the stored value or false, rather than adopting a new snapshot's scheduled-cancel flag.

The latter also addresses the implementer's separately discovered created-field mismatch: the original created handler omitted the flag, so a new row defaulted to false. The route normalizer now agrees with that rule, and the RPC also enforces it. Existing created events retain an existing true flag. Original permissions, invoker mode, search path, UTC, locks, legacy floors and binding logic remain unchanged by this body diff. Migration 48 is not edited.

The revised probe now expects missing updated/canceled streams to return 503 with whole-store invariance, then verifies creation/replay, original plan/price, period and flag preservation. The late-created binding positive uses an explicitly pre-existing legacy B row. The signed created(cancel=true) unit and original-route baseline assert false, and fault/recovery created events also assert false. Actual function-body comparison is added to the catalog probe.

The test adapter's new process exit occurs only after all handler response promises resolve and the safe summary is flushed. It removes test-process keepalive delay; it does not bypass the database response awaited by the handler. This is still direct handler execution with the actual SDK/client, not a deployed HTTP or provider test. Deadline is tested with a supplied persistence promise; discarded response is tested after a completed commit. No network-loss or late database commit experiment is claimed.

One oracle labeling limit remains: updated/canceled equal-creation cases now stop at the missing-stream guard; only created reaches the actual equal-subscription-creation decision. They must not be counted as three independent tie-rule executions.

**Disposition:** no new functional defect found in the bounded 49/body/normalizer/harness delta. B4 remains blocked pending final exact-source native evidence. Whole-head Changes required, DEP-20261021 High, the A/B identity barrier, and no B merge/B5/B6 approval remain unchanged.

