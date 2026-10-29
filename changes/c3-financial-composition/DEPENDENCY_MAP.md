# C3 dependencies
idempotent sale → assert_active_actor + current_tenant_id + _assert_staff → tenant/operation/key reservation + exact JSON replay comparison → v2 → one core → product locks, order/items/payment writes + existing audit triggers. Legacy sale → same core, internal-only. Core/v2/legacy bypass revoked from application roles.

legacy courier → assert_active_actor → canonical outcome → actor + locked order + _assert_staff → monotonic state/customer attachment or existing return RPC. Existing _assert_staff/current_tenant_id/private live helpers unchanged.

Searched current db.ts/app.tsx/migrations, original49/50 client and27/35/39 SQL tests during C1/C2 and current composition. Do not whole-file replace typed current db.ts by old50. Native harness reuses C2 QuantityProbe snapshot/seed, account-lifecycle live_probe/scanner_evidence and e2e write_harness_guard. CLI2.101.0, no dependency/toolchain upgrade.
