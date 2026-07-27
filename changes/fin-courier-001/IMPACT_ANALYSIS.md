# FIN-COURIER-001 — Impact Analysis (NAADF-CMF Change Gate 2 — summary)

Status: Proposed target based on product-owner direction; pending formal Gate
approval. This is the **summary**; the detailed Gate-2 artifacts required by
`docs/governance/NAADF-CMF.md` are separate documents:

- [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md) — callers/consumers of every affected RPC and read model.
- [DATA_IMPACT.md](DATA_IMPACT.md) — data-shape and integrity impact, historical rows.
- [SECURITY_IMPACT.md](SECURITY_IMPACT.md) — authz, tenant isolation, RLS, grants.
- [API_COMPATIBILITY.md](API_COMPATIBILITY.md) — RPC surface, v2 + adapter, client contract.
- [MIGRATION_IMPACT.md](MIGRATION_IMPACT.md) — forward-only migration steps (constraints, RPCs, health).
- [TEST_IMPACT.md](TEST_IMPACT.md) — which suites change and how; new cases map.
- [ROLLBACK_IMPACT.md](ROLLBACK_IMPACT.md) — reversal for every layer + data verification.

## Corrected scope headlines (independent review)

1. **Two enforcement layers, not one.** Relaxing the RPC is insufficient — the
   `NOT VALID` CHECK constraints `orders_customer_required_when_unpaid` and
   `orders_courier_requires_customer_id` block customer-less courier orders on
   every new write and must be replaced (CURRENT_BEHAVIOR §1a,
   COURIER_STATE_CONTRACT §1, MIGRATION_IMPACT).
2. **The transition RPC needs work.** `update_courier_order_state` takes no
   `customer_id`; a customer-less `pending` order can transition into a
   debt-creating state with no customer. An atomic resolution contract is
   required (COURIER_STATE_CONTRACT §3). The earlier "no change needed" claim is
   withdrawn.
3. **Not all aggregates are outcome-safe.** `close_day` is correct; but
   `get_platform_financial_health` **false-positives** on valid customer-less
   courier orders, `get_tenant_today_estimate` returns no debt/custody, and
   `get_platform_admin_overview` / `get_platform_tenants_health` **under-report**
   customer debt by excluding courier `delivered_partial`/`delivered_none`
   (finding 4). The earlier blanket "all aggregates already handle all five
   states" claim is withdrawn (CURRENT_BEHAVIOR §5/§5a).
4. **RPC decisions (5A/5C).** Named `create_sale_with_items_v2` with typed
   `p_courier_state` (no DEFAULT) + six-param adapter; named
   `update_courier_outcome_v2` transition (matrix + monotonic custody) with the
   old RPC as adapter (API_COMPATIBILITY, COURIER_STATE_CONTRACT).
5. **Constraint is NULL-safe, `returned`-aware, and `NOT VALID`** with a deferred,
   preflight-gated validation (5B; MIGRATION_IMPACT).

## Impact by area (summary)

- **UI:** default flow (4 entry points), payment sheet outcomes + outcome-based
  `needsCustomer`, courier wording, success screen, operational status display
  (PR-C). Detail in DEPENDENCY_MAP.
- **RPC contracts:** new `create_sale_with_items_v2`, adapter, atomic transition
  RPC (PR-A). Detail in API_COMPATIBILITY.
- **Schema/constraints:** replace two CHECK constraints (PR-A). Detail in
  MIGRATION_IMPACT / DATA_IMPACT.
- **Reporting/health:** outcome-aware health predicates + `_rows`, **and**
  outcome-aware `open_customer_debts` / `open_debts` debt totals using the
  single-source debt contract (PR-B). Detail in DEPENDENCY_MAP / DATA_IMPACT /
  TEST_IMPACT.
- **Auth / tenant isolation / RLS:** unchanged; transition RPC adds same-tenant
  customer validation. Detail in SECURITY_IMPACT.
- **Financial reports:** `close_day` unchanged and re-verified as regression.
- **Performance / employee / CI / env:** out of scope.
- **Deploy / rollback:** forward-only; ROLLBACK_IMPACT.
- **Backward compatibility:** adapter + more-permissive constraint; no
  previously-successful call breaks (BACKWARD_COMPATIBILITY).

## Cross-change conflicts to avoid

Do not bundle with BUGFIX-APP-001, PERF-APP-001, EMP-*, FIN-SETTLEMENT-METHOD-001,
or FIN-IDEM-001. Keep PR-A/B/C scoped (DEC-009, Architecture Rule 6).
