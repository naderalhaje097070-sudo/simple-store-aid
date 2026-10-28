# B1 decision coverage and limits

Candidate9979d4e1c9859719c7999f9ed6db0b773d4513be. This is composition coverage, not a security acceptance percentage.

| Decision / operation | Actor / state / tenant | Invariant and source | Evidence level | Result / gap |
|---|---|---|---|---|
| Preserve accepted A | Existing main18700dee | All original paths retained;284/288 protected paths exact;four exact B contract changes explicitly reviewed | Git-tree/blob/mode comparison | PASS preservation; not runtime equivalence for four changes |
| Preserve SQL history | Original41 plus4 B migrations |41 A blobs/modes and4 B blobs/modes exact | Git-tree comparison | PASS immutability;45-migration runtime deferred B5 |
| Derive MCP issuer | Explicit local/ci/remote configuration | Existing fail-closed target/key/alias validation still precedes issuer derivation | Source review; new unit tests in native CI | PASS frozen units; B5 real-token behavior pending |
| MCP authorization | Valid vs bad signature/issuer/audience/expiry/client claim | Actual application handler and locked SDK; positive control before negative cases | Synthetic JWKS unit fixture, no live auth service | PASS frozen synthetic JWKS controls; not OAuth lifecycle acceptance |
| Price lookup account guard | Active/inactive/transport failure/timeout | Current account RPC before gatewayFetch; no tenant required for public price lookup | Source review and account-state unit tests | PASS frozen units; native route/gateway ordering remains B5 |
| AC-01 scan privilege | Regular/admin/service/inactive | Ordinary user cannot invoke privileged security scan | Known inherited finding, no new runtime | OPEN B2; include admin/service positives and data invariance |
| AC-02 trial/billing mutation | Client INSERT/UPDATE vs legit onboarding/settings | Protect trusted trial/billing fields without changing policy | Known inherited finding, no new runtime | OPEN B3 |
| APP-02 event durability | Partial failure/replay/order/env | No HTTP success before durable event/subscription writes | Known inherited finding, no provider call | OPEN B4 |
| Owner/lifecycle/retention | Active/closed/banned; old/new JWT; cross-tenant; REST/RPC/MCP/server | Preserve history/audit, deny inactive operations, scoped TRUNCATE privileges | Exact imported source/evidence only | NOT RUN on45 migrations; fresh+populated isolated upgrade required B5 |
| Wire serialization | Success and three business failures | Original four result/error round-trip assertions remain intact | Native frozen compatibility | PASS all four original round trips; restored-cache failure retained separately |
| Historical identity gates | A288/41; older B43 | Reject source drift, never relabel historical acceptance | Unmodified verifier and workflows | A G0 source identity rejects B superset; B5 explicit adapter required |
| OC-EVID-02 historical evidence labels | Owner closure proof counts | Keep original Low label/count limitation visible; do not imply complete B acceptance | Archived B findings, no new runtime | OPEN Low; reconcile honestly in B5 disposition |
| Four helper formatting changes | Test-only ESM modules | Executable AST unchanged by locked Prettier3.8.3 | Independent Acorn AST comparison | PASS4/4; no lifecycle execution implied |

No production database, real gateway/provider, deployment or PR closure was performed. Only one bounded native compatibility batch is used; missing lifecycle acceptance is preserved as a specific later plan requirement.
