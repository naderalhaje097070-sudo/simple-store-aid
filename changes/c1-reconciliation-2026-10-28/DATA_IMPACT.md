# Data impact

No database execution or data change. No production data was read. Current50 migrations remain byte/mode exact. Two old August candidate migrations are examined inside replay.zip only; no active supabase/migrations entry is added by C1.

Future C data scope: orders/items/products/payments/tenant numbering/audit/customer/courier and one financial_idempotency reservation table. Old populated baseline may contain values incompatible with a new quantity rule; do not assume either their existence or absence without an authorized isolated-populated inspection. Never silently round or normalize historical money/quantity. A historical-data assessment and explicit remediation plan are separate from rejecting future invalid input. Ownership closure/history retention must preserve the new table and active-account replay denials.
