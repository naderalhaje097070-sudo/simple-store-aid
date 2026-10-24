# Impact and design

Change only CI routing, test adapters and the exact B manifest. Current B5/B1/G0/dependency gates receive main-targeting PR opened/synchronize/reopened events for relevant app/config/script/test/SQL/package/workflow paths. Application checkout and EXPECTED_SOURCE use the actual PR head with github.sha fallback for push; checkout has full history and no persisted credentials. There are no PR-number skips or ignored failures. Six general workflows remain byte-exact.

Seven phase workflows become manual historical benchmarks. An explicit40-hex historical source is distinct from the routing SHA. Validate format before checkout, then actual HEAD, phase41/43/45 and clean worktree before credentials. Original run commands and Python oracles stay unchanged. Job check names include Historical, phase and selected SHA, preventing an old manual green from masquerading as a current gate. This is explicit manual source selection, not an approved-source allowlist. No historical manual run is claimed.

The B50 expiry adapter copies only run_expiry orchestration. It replaces the43-only preflight with fixed B50/original41 inventory and adds private3/Auth identity-link invariance. Original real180-second token lifetime, unchanged wall clock/monotonic wait, signature/identity, exact challenges, same-token replay, fresh peers and zero refresh remain inherited. Keep public22 snapshots, empty finance, UID egress, secret scans and cleanup.

Risks concern CI enforcement and test attribution. Required branch settings remain unknown. The graph of mandatory current checks must be observed on the new PR head before requesting merge. Pure source tests cannot replace genuine elapsed-token expiry or current database/runtime proof.
