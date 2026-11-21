# Item 3.4 — B5 post-merge failures on `d4616d0`: corrections and evidence

Base: integration `d4616d06e7a3ccf6541c75af232780bb6011a3ed`, the merge of #103.

Failing run: [B5 44798187106](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/44798187106).
- **Passed:** lifecycle fresh.
- **Passed on the same commit:** B50 Real Token Expiry 44798187438, release-finance 9/9, G0 and B1.
- **Context:** this was the first B5 run on integration source. Every earlier B5 run was on a PR into main with 50 migrations.

This change is limited to test harness code: no product code, migration, workflow or acceptance predicate changes. Each item below is marked **confirmed** or **hypothesis**.

## 1. Billing (fresh): `new_RPC_actual_body_matches_forward_correction`

**Confirmed by source review and independent artifact review:**
- The historical reference `changes/b4-app02/WEBHOOK_ERRORS.sql` equals the October migration `20261021140746`.
- The reviewed C-PADDLE-01 migration `20261110130000_paddle_webhook_no_key_update_01.sql` redefines `apply_subscription_webhook`.
- Its only change is the tenant lock, `FOR UPDATE` → `FOR NO KEY UPDATE`, with three comment lines.
- All other `security_catalog` conditions still hold statically:
  - no `40001`;
  - 14 `P0001` codes;
  - `SECURITY INVOKER` with a pinned `search_path`;
  - `EXECUTE` granted to `service_role` only.

**Correction, in commit `239d4cc`.** `tests/b5-lifecycle/billing_probe.py` overrides `security_catalog`.
- **Query:** identical to the historical one. Rendering both gives the same 1506 characters.
- **Assertions:** the same. Only the expected body changes, and two checks replace the one. The two new checks:
  - `final_RPC_reference_is_pinned_ledger_definition_with_exact_reviewed_delta` requires that:
    - the last ledger definition of the RPC is `20261110130000`;
    - its bytes match the manifest-pinned blob;
    - the B4 fixture still equals the October definition;
    - the body differs from the B4 fixture by exactly the reviewed five-line delta.
  - `final_RPC_actual_body_matches_reviewed_ledger_definition` requires the live body to equal that definition.
- **Not changed:** `webhook_persistence_probe.py`, which keeps the dormant B4 workflow from triggering.
- **Unit tests in `test_contract.py`:**
  - the real tree is accepted;
  - a changed final body, unpinned final bytes, B4 drift and October drift are refused;
  - an inexact delta (4 variants) is refused;
  - a later redefinition is refused.

## 2. Lifecycle (upgrade): `old_full_route_denial_list_products`

**Confirmed from the artifacts:**
- `closure-progress.json` records HTTP 200 in both fresh (passed) and upgrade (failed).
- No response body is recorded for the failed assertion.
- MCP answers 200 for both a tool error and a success, so the status cannot classify the failure.

**Confirmed from the source:**
- `list_products` does not call `assertCurrentAccountActive`; it reads `products` directly.
- The restrictive `monjez_live_actor` policy returns false; it does not raise.

**Hypotheses, unproven:**
1. An empty successful tool result.
2. A tool error with other text.

**Evidence improvement, candidate-only (commit `9e04458`, which supersedes `782a5b7`); no predicate change.**
- `tests/b5-lifecycle/candidate_evidence.tool_response_outline()` returns one of six fixed classes:
  - `tool_error_account_inactive`
  - `tool_error_other`
  - `tool_success`
  - `protocol_error`
  - `unexpected_shape`
  - `non_200`
- For a successful list tool it also returns the item count. It never returns text, a hash of text, identifiers or row content.
- `composed.py` attaches the outline to its own `denied_state` records. Through its `invoke`/`record` overrides it also attaches it to the inherited `closed_controls` denial records (`*_full_route_denial_*`).
- `account_tool_denial`, `mcp_probe.py` and `owner_closure_probe.py` are unchanged.

## 3. SSR: deferred `bounded_egress_trace_collected`

**Confirmed from the artifacts and the source:**
- `runtime-failure.json` names only this check.
- `egress-conflict.json` has 1 unfinished syscall and 0 unparsed lines. The matching phase has 0/0.
- `native_unexpected_outbound_zero` passed.
- `trace_complete` requires `unfinished_calls == 0`.

**Hypothesis, unproven:** the conflict-mode process was stopped (`pkill -TERM`) while a traced call was blocked.

**Evidence improvement, candidate-only (commit `9e04458`, which supersedes `fa69c48`); no predicate change.**
- `candidate_evidence.unfinished_outline()` mirrors the line grammar of `egress_trace`. It returns:
  - the number of unfinished calls;
  - their allowlisted names (`TRACED_CALLS`, a copy of `egress_trace.CALLS`, else `other`), with counts;
  - how many of those threads later show an exit or kill marker.
- `ssr_runtime.stop()` adds it to the egress evidence as `unfinished_outline`, reading the same private trace file. No arguments, addresses or raw text are recorded.
- `egress_trace.py` and `trace_complete` are unchanged.
- There is no teardown change: one is not justified until this evidence names the call.

## Historical blob preservation (independent review, rework `9e04458`)

**This PR leaves the shared historical modules byte-identical to integration `d4616d0`.** These are `mcp_probe.py`, `test_mcp_probe.py`, `owner_closure_probe.py`, `egress_trace.py`, `test_egress_trace.py` and `webhook_persistence_probe.py`; the five touched in `782a5b7`/`fa69c48` are restored. That is identity with `d4616d0`, not with the frozen snapshots: at `d4616d0`, `owner_closure_probe.py` already differs from its B50 blob (see below). The PR does change three B50-pinned B5 candidate files. Measured on the head:

| | Result |
|---|---|
| A41 | 288 pinned; 0 changed by this PR |
| B50 | 396 pinned; changed by this PR: only the B5 candidate files `composed.py`, `ssr_runtime.py`, `test_contract.py`, which #103 had already made differ |
| Both frozen manifests | blobs unchanged |
| Migrations tree | `08d0c94e`, unchanged |
| Candidate ledger | unchanged |
| Candidate manifest | re-pins only `billing_probe.py`, `candidate_evidence.py` (new), `composed.py`, `ssr_runtime.py`, `test_contract.py` |

**Inherited from the merged #103, left for separate work so it does not delay these diagnostics.** #103 first made 8 B50-pinned files differ:
- the B5 and B50 workflows;
- `composed.py`, `inventory.py`, `ssr_runtime.py`, `test_contract.py` and `b50-natural-expiry/probe.py`;
- **`tests/account-lifecycle/owner_closure_probe.py`**, a shared historical module. #103 added the `sale_rpc`/`sale_body` hook there; its default stays the legacy sale.

The first seven are the approved candidate wiring. Restoring the B50 bytes of `owner_closure_probe.py` would need a separate candidate-only patch: `ComposedProbe` would supply the keyed sale for `financial_fixture` and `closed_controls` without the base hook. That patch is separate work, and is not part of this PR.

## Verification (local, synthetic; see the PR for exact commands)

| Check | Result |
|---|---|
| `test_contract.py` | passed, including the 4 billing tests and the 3 candidate-evidence tests |
| account-lifecycle unit suites | passed (files byte-identical to `d4616d0`) |
| `test_egress_trace.py` | passed (file byte-identical to `d4616d0`) |
| `test_candidate_identity.py` | passed (real-tree manifest current) |
| `test_integrated_identity.py` | passed (unchanged) |
| `b7` routing contract | passed |
| Candidate verifier on this tree | accepted (63 migrations) |

**Not verified here:** B5 lifecycle, SSR and billing run only on the integration push after merge, or on PRs into main. Their outcome on the merge commit is the acceptance evidence.

## Governance gates

- **Into integration:** routine under `MERGE_DELEGATION.md`, provided the reviewer agrees that item 1 does not weaken a control. Item 1 replaces the expected reference value of one assertion with two stricter checks: a pinned blob, the exact delta, and the B4 fixture still bound to the October definition. If the reviewer considers that a relaxation of an assertion, it is outside the delegation and needs the owner's decision.
- **Into main:** `tests/**` is governed by `tests/release/gate.py`, so the change needs the owner's `gov-ok-<head sha>` label at that step.

## Rollback

Revert the commits. They are test-only, and no migration or product file changed.

## Review correction (`tool_response_outline` shape)

Engineering review of `fa6a2a2` found that a malformed HTTP 200 result was classed `tool_success`. A successful class now requires the historical `mcp_probe.tool_success` to accept the response:
- a result object;
- `isError` not set (absent or false);
- `structuredContent` holding the tool's expected key, with the expected type.

Any other HTTP 200 shape is `unexpected_shape`, and the error classes require `isError` to be exactly `true`. The test `test_tool_response_outline_malformed_success_is_unexpected_shape` covers 14 fabricated malformed shapes and three well-formed successes:
- a missing, null, list or string result;
- missing, null or list `structuredContent`;
- a wrong key or wrong type;
- a summary without `sales`;
- a non-boolean `isError`;
- an unknown tool.

`account_tool_denial` and every predicate are unchanged. The billing SQL and assertions passed independent source review.
