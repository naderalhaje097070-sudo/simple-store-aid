# Rollback

Before merge: close Draft PR; no deployed change or user data to restore.
If later owner-merged: additive revert of new test/workflow/docs; retain old evidence, no force/rebase/amend.
Disposable CI cleanup stops app UID processes, stops Supabase --no-backup, removes keys,
checks no processes/containers/status files remain. Do not operate production.

