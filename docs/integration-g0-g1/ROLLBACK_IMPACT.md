# Rollback and containment

Candidate isolated on integration/g0-g1-reconcile-2026-10-18; original Draft72 remains6da4dad and main43d6edb. No production or data change to undo. Abandoning this unpublished candidate leaves original branches intact; preserve claim/reports/failed evidence.

If a partial withdrawal is needed, create a new forward commit. Restore the affected source from the recorded prechange parent; never reset/force/rebase published history. Formatter-only scope can restore from6da4dad; typed scope fromd0a172e (plus actual nullable shared-item/Set types together); generator/build scope must revert nine outputs, postprocessor, manifest, scripts and workflow invocation together to retain build consistency. Observer scope restores egress_trace.py/workflow and removes its new unit test, while retaining historical failure receipts.

Any source-changing rollback requires a newly reviewed exact integrated manifest, affected verification and visible failed results. Do not use git restore inside a verification job to hide generator mutation. No SQL compensation/backfill/provider reversal applies. No merge/deploy authorization implied.
