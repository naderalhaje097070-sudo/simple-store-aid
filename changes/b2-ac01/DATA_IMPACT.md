# Data Impact

No schema/table/index/backfill changes. Existing data and ACLs preserved by CREATE OR REPLACE. Successful scans still write their normal audit rows; rejected requests must leave every public row and private closure marker unchanged. Fixtures are synthetic and disposable only.
