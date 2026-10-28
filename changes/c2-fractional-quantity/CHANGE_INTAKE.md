> FINAL C2 amendment: tested source3726567;4existing source changes (including centralized current-SQL creation-cent rounding) plus explicit new quantity files. Local18quantity+5cent controls; native69fresh,13baseline+60upgrade,desktop/mobile allpass, full compatibility pass. G0frozen-B identity remains failed; no independent/full-C/merge acceptance. See RESULT.md and VERIFICATION.json; earlier preparation text below is retained context.

# C2 fractional quantity intake

Owner explicitly selected fractional selling (weight/length/partial units), resolving reserved C1 decision. Standing implementation plan and this decision authorize the bounded C2 change. Claim55/6481133997. Existing branch integration/g0-g1-reconcile-2026-10-18; base5601d634, accepted main220fc206 unchanged.

Goal: match inventory, sale lines and return/delete effects for fractions such as0.25. Preserve existing order-item precision of two decimal places and existing monetary/courier/idempotency policies. High financial-data risk; implement a forward-only migration and current product/two sale UI paths with isolated fresh/populated/authenticated/concurrent evidence. No provider/production/new cost/merge/PR closure or C3/C4 implementation.

Technical precision assumption: preserve current numeric(12,2) item scale, maximum9999999999.99; accept exact values at that precision and reject excess precision, negative/nonfinite/overflow. This does not add third-decimal/weight-unit conversion policy. Unknown production historic inconsistency remains a release preflight, not an invented backfill.