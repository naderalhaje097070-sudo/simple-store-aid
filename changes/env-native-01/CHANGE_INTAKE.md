# ENV-NATIVE-01 — lifecycle denial preparation

Gate 0 candidate, S2.4a in the existing six-stage plan. Owner: repository owner;
implementer: continuing Codex agent. Change type: authorization defect correction.
Urgency P0; High candidate severity pending independent review. No release approval.

Goal: an Auth-banned actor's preissued JWT cannot read or mutate protected MONJEZ
data, including direct PostgREST and privileged RPC paths. Preserve active-account
and tenant/role boundaries and financial/audit history.

This batch delivers Gates 0–3 analysis, a negative-case execution specification,
and an offline evidence regression oracle. It implements no authorization correction.
Baseline is draft PR56 b9aa56bc3bb30948d95961c06fd493dfb866f476, stacked above PR54.
Main remains 43d6edbccb66fb06ce0fcb93734ad59532d1aeae.

Proposed implementation scope after intake approval: one forward-only migration
adding a caller-bound live account check, protecting direct table policies and all
exposed SECURITY DEFINER entry points reached by this actor. App-owned enforcement
only where a reachable protected handler escapes those boundaries. Exact catalog,
grants and provider Auth schema must be verified on a fresh isolated runner first.

Excluded: employee/invitation features, new financial policy/formulas, finance
PR27/49/50 adoption, production, applied migration edits, costs, new cloud projects,
merge/deploy, dependency upgrades and unrelated security refactoring. Storage,
Realtime and email workers are inventoried but not claimed tested or fixed.

Assumption: existing Auth ban is the lifecycle signal for this defect; no public
profile disabled column or client-writable authorization claim is introduced.
Missing blockers: approved exact implementation intake/design; live catalog/Auth
schema reconciliation; regression execution on a verified disposable target;
independent source/evidence review. Routine preparation is owner-authorized.

Approval boundary: AGENTS.md requires the applicable intake approved before
implementation; NAADF-CMF Gate 0 says “Stop and obtain approval before implementation.”
This packet is concrete review material. Implementation and lifecycle Gate-4 live
fixture execution await that approval. Financial write suites separately remain
blocked until isolation is accepted. Passing offline tests does not open either gate.
