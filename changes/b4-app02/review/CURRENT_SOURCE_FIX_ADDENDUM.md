# B4 current source fix addendum

Date: 2026-10-21 UTC. Independent reviewer: `/root/foundation_a_independent_review`.

**B4 disposition: Blocked pending missing evidence.** Both Medium findings in `CURRENT_SOURCE_REVIEW.md` are corrected at source level by the SQL inspected below. Runtime closure remains pending. The initial failing-source report and its inputs remain unchanged. The whole head still requires changes because the general High dependency and identity barriers are open.

## Reviewed working inputs

Base remains `dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0`; no final executable B4 commit exists in this review.

- Proposed SQL SHA256: `1fbf7363cf0ce80f4e8891668b113adc6112288afe42cc25a072327bad62fa16`.
- Probe SHA256 at final read: `98e1c9335d39af9fd41e5244308d24b30333f3bb4403f7c97744b038df3be144`.
- Handler and route remain the hashes recorded in the prior source review for this bounded SQL delta.

I read the complete diff against the retained failing SQL, relevant probe fixtures/assertions, and the actual signed-handler adapter. I parsed the probe with Python's AST parser without executing it or creating source cache files. No database, SDK test, provider, production action or historical suite was run. The implementer's reported 21 Node tests/type/lint results are not independently rerun results here.

## Source findings disposition

**B4-SOURCE-01 — corrected in source, native verification pending.** The created-event guard covers both environments and rejects an outranking legacy public timestamp whose provider creation identity does not match that stored timestamp. The separate live projection guard checks the target's actual public creation time, using the existing row time when present, and rejects another row at or above it. Both checks precede binding/subscription/receipt writes. The original A(public13/provider10) → B(provider12) source case therefore raises rather than committing a contradictory projection. Existing records are not rewritten. Ordinary older known streams can remain non-current; this does not claim global cache/UI agreement for every receipt or repair all inherited legacy data.

The probe contains matching legacy live and sandbox denial cases, each with full snapshot invariance. It also retains normal replacement, late older-stream and updated-B-before-created-B controls.

**B4-SOURCE-02 — corrected in source, native verification pending.** After the global provider-ID lock and public-row lookup, the function now reads retained receipt history across environments. A known stream with a missing public row or another environment raises before mapping and mutation. Consequently the missing-row path can no longer silently recreate that stream under a new owner/customer/environment. Previously committed exact duplicate acknowledgement remains a receipt acknowledgement and does not recreate a row.

The first reassignment test originally reused the old event time, so the former equal-time conflict could mask the identity flaw. I flagged that oracle issue. The final probe read explicitly uses `2026-09-01T00:00:01Z` after the original `00:00:00Z`, so it reaches the old vulnerable transition. The cross-environment case and both all-data-invariance checks are present. These remain unexecuted native regressions in this review.

## Remaining bounded checks before final acceptance

- Observe both regression families and positive controls against the generated final migration on fresh and populated native stacks; do not infer those results from source or syntax.
- Add the policy's disabled-employee transition/old-JWT denial case for the new RPC, with unaffected active/service controls. The inspected probe has two active staff and banned/closed owners, which do not constitute a disabled-employee execution.
- Support the new cross-environment provider-ID history lookup with an appropriate leading-key index or equivalent fixed-environment lookups using the current index. Its current index begins with environment. This is a structural growth observation, not a measured latency claim or a new security defect.
- Pin and independently verify the resulting SQL, source, tests and workflow at one actual SHA. Preserve all 47 old migrations, existing B2/B3 contracts, original source evidence, raw advisor warnings and unresolved general gates.

No additional functional source defect was found in this bounded delta. This permits progressing to generation and isolated verification; it is not runtime, B5/B6, whole-B or merge approval.

