# C5-RESTORE-01 — diagnostic tested; restore acceptance failed

4 November 2026. Repository naderalhaje097070-sudo/simple-store-aid.
Branch integration/g0-g1-reconcile-2026-10-18.
Exact executable: `46373de654b8ecb5deb60315da763b9377c67c3e`.
Base: `be0f128f82e23da094ddce56d3f06dabef018dc9`. Main220fc206 remains unchanged.

## Result

The new nonempty logical-restore test is implemented and its failure is reproduced on both fresh and upgraded source databases. **Restore acceptance FAILED**. Do not promote this diagnostic result to successful restore, full C5, merged or released status.

Both final native jobs in [run41793455289](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41793455289) fail at pg_restore with exit2 from the driver. The safe receipt identifies pg_cron/extension and a create-extension database restriction. Tools and server are all PostgreSQL17.6 (server170006). The earlier administrator ownership/authentication obstacles were passed after using the attested existing local admin and the disposable container's own password entirely inside its environment. The current remaining failure is the unsupported restore topology.

The full source dump contains pg_cron, while the test restores into a different database (`monjez_c5_restore`) in the same cluster. Upstream [pg_cron setup](https://github.com/citusdata/pg_cron#setting-up-pg_cron) specifies one installation database per cluster, default postgres, configured by cron.database_name. That explains the observed restriction. This proves the current harness design cannot accept full-stack restore; it does not prove customer data loss or a defect in MONJEZ financial accounting.

No archive filtering, --no-owner/--no-acl, ignored restore error, special extension test-name exception, role grant, password change or HBA edit was used to force success.

## Checks that passed

- Current [G041793455447](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41793455447) and [B141793455484](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41793455484) SUCCESS attempt1 on46373de6.
- Full types/lint/builds,97unit/300expectations,0lint errors/15warnings,43read-server/11read-browser cases, full audit raw{}.
- New source admission479 protected entries;55 migrations and all prior manifests/verifiers/application/SQL/dependencies preserved except the explicitly admitted capture dispatch and4 test/CI additions.
- New19negative source controls pass locally and in hosted precredential checks. Local syntax and fixed-vocabulary privacy guards also pass. No local Docker/Postgres execution is claimed.
- Original financial/browser seed tests pass on the current source:108fresh/111upgrade controls, actual-component desktop/mobile collection retry and genuine second payment, financial_acceptance=true in the inherited pre-restore receipt.
- Final native cleanup/publication passed with zero unexpectedIPv4/IPv6 rejects and removal of status/state/stack/private JSON files. Private full dump deletion is implemented in finally; the failed receipt has no independent archive-removal assertion. No dump bytes or credentials are artifacts.

G1[41789737769](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41789737769) passed on80e56afc, before subsequent restore-driver-only diagnostics. This is explicitly a historical exact-source result, not a G1 run on46373de6.

## Unverified

pg_restore stops before row/catalog comparison and restored authenticated replay/new-payment/denial tests. Those checks exist in code but **did not run to successful completion**. Original database post-restore rehash did not execute after the failed restore; code review shows restore commands target only the separate target, while source accesses in that phase are reads. This is not production/managed backup/PITR, global-role recovery, restored HTTP/Auth services or full application financial-journey evidence.

The inherited financial-result.json has restore_executed=false because it precedes the separate restore step. The new restore-result.json also has restored=false. Neither is acceptance.

## Failure history and evidence

[Verification repair history](VERIFICATION_REPAIR.md) records: coarse initial RuntimeError; exact copied-checkout Git ownership handling; actual pg_restore SET ROLE rejection; admin boolean JSON encoding correction; admin local password-authentication failures; and the final pg_cron topology restriction. Only fixed public error vocabulary and tool versions were published; no raw private stderr.

[Artifact index](evidence/manifest.json) preserves19 original safe runner ZIPs with verified SHA256, including all failed native attempts and successful surrounding checks. [Finding](FINDINGS.md) and [next design](NEXT_DESIGN.md) define the concrete resume point. No failed run is relabelled.

## Resume

**ONE NEXT: replace the secondary-database fixture with a fully independent disposable PostgreSQL/Supabase recovery target**, preserving the original database name and extension configuration, original owners/ACL/RLS and necessary isolated roles. Then complete the existing row, replay, denial and new-payment assertions. Do not weaken the dump or acceptance gate to accommodate pg_cron.

Current batch status: implemented/tested diagnostic; restore acceptance BLOCKED by harness topology. Full C5/C6/C7 remain open. Five original drafts27/35/39/49/50 and main are unchanged. No merge/deploy/production/closure/new subscription or product/financial contract change.
