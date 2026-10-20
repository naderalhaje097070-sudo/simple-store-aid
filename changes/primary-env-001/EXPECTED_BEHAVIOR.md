# Expected contract

Every build declares local, ci, preview, staging or production and explicit Supabase URL/public key/project. No fallback selects production. Local/CI accepts HTTP loopback; preview/staging requires a dedicated HTTPS matching Supabase project and rejects approved production identity. Production requires explicit approved host/ref. Browser/server aliases and baked/runtime identity agree before application entry.

Public fields reject sb_secret_ and legacy JWT roles other than anon. This exposure guard does not authenticate keys or attest remote project ownership. Publishable/legacy anon validation by the provider remains required.

Write harnesses require explicit intent and local/CI routing. Credentials/network/database clients are reached only after preflight. Context routing covers popups; service workers stay blocked. Isolated database execution, real browser interception and outbound containment require further evidence before write tests.
