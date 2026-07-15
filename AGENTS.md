<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

# Mongezz Agent Rules

These rules apply to every automated or assisted change in this repository.
Repository files are the source of truth; chat history is not.

## Required work mode

1. Classify the request before changing files: New Project, Existing Project Change, Bug Fix, Feature, Refactor, Database Change, Security Change, or Dependency Upgrade.
2. Use **NAADF** for new projects or isolated new products.
3. Use **NAADF-CMF** for every change to this existing application.
4. Complete and record the required gate before moving to the next gate.
5. Do not write implementation code before the approved design and safety-net gates.

Detailed processes:

- [NAADF](docs/governance/NAADF.md)
- [NAADF-CMF](docs/governance/NAADF-CMF.md)
- [Delivery Protocol](docs/governance/DELIVERY_PROTOCOL.md)
- [Security Baseline](docs/governance/SECURITY_BASELINE.md)
- [Database Change Policy](docs/governance/DATABASE_CHANGE_POLICY.md)
- [Testing Policy](docs/governance/TESTING_POLICY.md)
- [Independent Review Protocol](docs/governance/REVIEW_PROTOCOL.md)

## Non-negotiable project invariants

1. Financial writes must go through approved, authorized RPCs or server transactions.
2. Do not duplicate debt, custody, remaining, settlement, or margin formulas in UI screens.
3. Reuse the canonical finance-domain functions.
4. Returned orders must never appear as customer debt or courier custody.
5. **Delivered is not settled.** Courier collection remains custody until owner settlement.
6. Tenant isolation and authorization must be enforced server-side and in PostgreSQL RLS where applicable.
7. The UI is never the only authorization or business-rule boundary.
8. Money uses exact decimal or integer-minor-unit types, never floating point.
9. Applied migrations are immutable. Use new forward-only migrations.
10. Do not use Production, Production secrets, or real customer data for agent testing.
11. Do not add public test-cleanup RPCs or Production-only test bypasses.
12. Do not hard-delete financial or employee history that is required for auditability.

## Delivery rules

- One feature or one coherent change per PR.
- Do not mix a feature with broad refactoring, global formatting, or unrelated dependency upgrades.
- No automatic merge or deploy. A human must explicitly approve destructive actions, merge, and deployment.
- Never force-push or rewrite published history.
- Do not weaken, skip, or rewrite a valid test merely to make a change pass.
- Do not claim completion without actual verification results.
- Record new decisions in `DECISIONS.md`, current status in `PROJECT_STATE.md`, and work items in `TASKS.md`.

## Required completion report

Every completed gate or change must report:

- Summary
- Root Cause, when applicable
- Changed Files
- Contracts Changed
- Database Changes
- Commands Executed
- Tests Executed and actual results
- Acceptance Criteria: Passed / Failed / Not verified
- Security Review
- Remaining Risks
- Known Limitations
- Unverified Items
- Rollback Procedure
- Next Recommended Task
