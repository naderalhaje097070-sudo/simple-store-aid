# Migration Impact

One CLI-generated CREATE OR REPLACE function transaction, no table lock/scan/backfill. Function-definition catalog lock may wait for concurrent DDL; normal execution keeps its existing transaction behavior. No row migration. Preserve owner/OID/ACL/default argument; trusted pg_catalog first and pg_temp last prevent temporary catalog shadowing while preserving qualified app names. Old45 immutable. Production application requires separate owner approval.
