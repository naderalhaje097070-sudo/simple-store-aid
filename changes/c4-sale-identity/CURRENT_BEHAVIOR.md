# CURRENT BEHAVIOR

Current typed client uses revoked create_sale_with_items. Original50 candidate uses one sessionStorage slot/30-minuteTTL and clears on unvalidated data. C1 CLIENT_RESULT.json records nine actual callback cases: four confirmed TTL/reload/slot/null defects, controls retained. Current two sales carts lose local draft on reload and PaymentSheet swallows failure. C3 already proves actual server replay/conflict/atomic rollback/concurrency, all54SQL unchanged; no new SQL needed.
