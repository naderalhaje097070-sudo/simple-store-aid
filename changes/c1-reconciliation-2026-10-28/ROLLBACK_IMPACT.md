# Rollback and compensation

C1 changes only integration documentation,17 historical Markdown restores and an inert reproducibility ZIP. Main, original five PRs, source388/50SQL/workflows and production remain unchanged. Rollback is an additive revert of this documentation commit on the integration branch; no force-push or original-branch deletion.

Later C2/C3/C4 must use forward-only database compensation and retained idempotency history. Do not drop reservation records to roll back correctness, reopen a non-idempotent authenticated write, silently round existing quantities, or edit applied August/October SQL. Code rollback after release is not proof of database rollback; rehearse both in isolated C5/RC scope. No production restore or rollback drill is performed here.
