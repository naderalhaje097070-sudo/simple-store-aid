# C2 — fractional quantity candidate implemented and bounded tests passed

28 October2026, Africa/Tripoli. **Status: Implemented + Tested on integration; not Merged/Released or whole-C accepted.** Owner explicitly selected fractional selling. Existing branch integration/g0-g1-reconcile-2026-10-18; actual tested source`3726567d06d2ca21c5fb0d724571bf126c74be7c`, treef102a8ae1c09e604057caa5364efbedd4c1681f0. Main220fc206and original five C heads remain unchanged. Final documentation-only publication identity is recorded in55/70.

## Result

- Exact fractional stock/line quantities at existing two-decimal item precision, including0.25and1.50. Unconstrained numeric columns plus bounded precision CHECKs reject excess precision instead of typemod/int rounding. Raw quantity validation precedes numbering/financial writes. CLI-generated forward migration; all old50SQL unchanged.
- Inventory decimal input no longer strips the decimal separator. Both sale carts accept a validated decimal draft; invalid or pending drafts cannot complete a sale using a previous quantity. Below-one stock, decimal step/sum and unit labeling handled in the existing screens. Current typed hooks retain A error/null behavior and refuse invalid quantities before transport.
- Existing SQL positive per-line cent rounding is centralized in domain creation-total helpers and reused by both carts/line displays.12.50×0.25→3.13; paid3.13does not accidentally become debt. No price/cost/SQL money formula/stored invoice debt/margin policy changed. Supported monetary range remains the original SQL numeric(12,2); overflow/hostile historic-data cases require broader C5 evidence.

## Actual verification

[Final native run40777141082](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/40777141082), attempt1, **all3jobs SUCCESS**. Fresh51:69named checks. Populated50→51:13baseline/expected-red controls, then60passing controls. Counts include fixture setup/invariance, not vulnerabilities or coverage percentage. Real local Auth/REST/RPC, persistent orders/items/payment/stock, exact return/delete, foreign/banned denial, two-session fractional stock race, half-cent money control and all-public/private history preservation pass. Full cleanup/status/private-state removal and zero unexpected probe egress verified in both raw artifacts.

Real shared component browser controls pass on desktop/mobile, including invalid draft completion refusal. This uses synthetic save callbacks, not a full live sale-screen E2E. [B1 compatibility40777140992](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/40777140992) SUCCESS: frozen install, types, full lint, unit/wire/build/generated-source invariance. Supported audit job123129252794inrun40777141124SUCCESS. Local18quantity +5cent controls,5actual callback controls with fake transport, syntax and locked formatting pass.

**Integrated G0 identity remains FAILED:** run40777141124/job123129252474, exact errorProtected source path set changed. B's immutable source manifest was not changed to accept C. Explicit C manifest/adapter and broader composed acceptance remain mandatory. C2's bounded inventory verifies384baseline entries exact,4declared source changes,11pinned new files and the head-pinned C manifest; it does not waive the frozen gate.

## Preserved failures and limits

Firstsourcea547 native run40775290985fails in snapshotSQL (extra parenthesis beforeFROM); baseline13and fresh23earlier controls are preserved, not relabeled. Corrected source87b806native all3jobs pass; final372adds invalid-draft guard and all3affected jobs pass again. Raw failed and finalZIPs are stored here with Gitblob/SHA256 matched to GitHub artifact metadata. Original G0 rejection remains explicit; no test/assertion was weakened.

No new independent review. C3/C4, full C5/T1–T15/canonical/idempotency/restore, C6 and C7 remain open. Historical stock/line discrepancies are preserved and require separate reconciliation; no production data was inspected or adjusted. Hostile historical-data preflight failure/rollback is source-checked, not independently native-exercised. No merge/deploy/new PR/closure/cost/production action.

ONE NEXT: C3 forward financial composition of49/50 above A+B+C2; retain this quantity contract/live guards and reconcile canonical adapters/grants. Source/evidence receipt inVERIFICATION.json; CLI/telemetry diagnosis inTELEMETRY.md; rollback remains forward-compatible with fractional data, never cast it back to integer or edit applied SQL.
