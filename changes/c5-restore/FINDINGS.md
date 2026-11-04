# C5-RESTORE-TOPOLOGY-01

Severity: High **acceptance blocker in the test harness**, not an established production vulnerability.

Contract: tests/c5-restore/restore.py restores a full Supabase database into a second database in the same cluster.

Evidence: executable46373de654b8ecb5deb60315da763b9377c67c3e, native run41793455289, jobs126451925529/126451925833. Both restore-result receipts report restored=false, phase pg_restore, tool/server17.6 and pg_cron create-extension database restriction. Underlying108/111financial/browser controls and final cleanup pass.

Risk: accepting a filtered/partial restore as complete could hide lost schema, privileges or idempotency state. No restored financial comparison has passed. This is a harness topology limitation; no actual customer incident or financial corruption is demonstrated.

Required fix: independent disposable recovery cluster with the original database name, required extensions and equivalent isolated roles/owners/ACLs. No second-database pg_cron installation in the source cluster. See NEXT_DESIGN.md.

Verification: full fail-fast restore, all selected relation data and catalog/ACL/RLS comparisons; old-key no-write replay, foreign/payload-conflict atomic denial, genuine new payment; source unchanged, private archive deletion and complete target cleanup attested. Independent C6 review still required.
