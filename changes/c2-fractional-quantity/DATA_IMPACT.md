# Data

No production inspection/application. Migration locks products/order_items in ACCESS EXCLUSIVE with5s lock timeout, preflights invalid historical values, converts by exact numeric casts and installs finite/bounded/two-decimal constraints in one transaction. No new table, backfill, row update, grant or permission policy. Table type conversion may rewrite/scan large data and requires a later maintenance/backup plan before release.

Existing fractional historical order items and integer stock may already be inconsistent due to the old bug; this migration preserves their values and cannot infer corrections from incomplete history. The isolated upgrade deliberately retains a reproduced old mismatch while proving all stored rows survive unchanged. Production reconciliation/backup/restore is a separate gated operation.
