# Rollback and rollout

Implementation order after adoption: additive view/ACL migration → generated types and compatible reader/labels → tests/review. Roll back clients to the retained legacy reader first if necessary; existing table/RPC fields remain compatible. Any database compensation is a NEW separately reviewed migration to revoke new view access/drop only the introduced view after dependent clients are removed. Use DROP VIEW public.day_close_profit_report RESTRICT; never CASCADE. If dependencies remain, stop and review them. Do not drop base tables/columns, recalculate old closes or rewrite migration history.

A source revert is additive. Production rollout/rollback, protected merge and data correction remain owner-controlled. Because the proposal does not change monetary writes or old row values, no ledger compensation is planned. New view/API availability failures are surfaced, not silently converted to zero. No migration or rollout has happened in this design batch.
