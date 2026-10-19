# SECURITY IMPACT

Read/action guards are UI correctness controls and do not replace server/RLS authorization. Tenant-resolution failure blocks financial balance-dependent callbacks and retries tenant first. Existing backend guards remain required. Tests use synthetic tenants/customers and stub transport, no credentials or providers. No production access.
