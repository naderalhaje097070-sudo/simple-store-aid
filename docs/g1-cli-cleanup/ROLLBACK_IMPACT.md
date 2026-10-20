# Rollback

Revert this batch's test/CI/checkpoint additions additively on Draft72 if needed; never rewrite published history. No application/database rollout occurs, so there is no production compensation. Stop only the new disposable stack with no-backup, remove its credentials and verify process/container absence; any verification failure stays failed. Existing failed artifacts remain immutable.
