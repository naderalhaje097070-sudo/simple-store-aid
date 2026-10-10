# Security impact

Remove implicit production fallback; enforce deploy-target/endpoint/alias/baked-runtime pairing; reject secret and privileged JWT formats from public-key fields. Known production host/ref are public identifiers, not credentials. Errors state field names or contract problems rather than keys. Runtime privileged key remains server-only; validation does not prove service-role project ownership or RLS.

Write paths pin loopback Supabase/PostgreSQL targets, reject proxies/service routing/host-address overrides and disable psql startup. Browser interception moves to contexts and existing service-worker block remains. Actual browser/WebSocket/redirect/network-level containment has not been executed and remains an independent acceptance question. Read-only visual smoke PR48 hardening is reused, not promoted into a write authorization.

Astra attempt failed at usage limit before review; no independent approval. Security PR53 acceptance/audit/lint/CI blockers stay open. No bypass based on passing local tests.
