# Claude Project Instructions

Use `AGENTS.md` and the repository governance documents as the authoritative engineering process for Mongezz.

Required references:

- `PROJECT_STATE.md`
- `DECISIONS.md`
- `TASKS.md`
- `docs/governance/NAADF.md`
- `docs/governance/NAADF-CMF.md`
- `docs/governance/DELIVERY_PROTOCOL.md`
- `docs/governance/SECURITY_BASELINE.md`
- `docs/governance/DATABASE_CHANGE_POLICY.md`
- `docs/governance/TESTING_POLICY.md`
- `docs/governance/REVIEW_PROTOCOL.md`

Before changing an existing project, complete the applicable NAADF-CMF gate. Do not begin implementation before the intake gate is approved.

Do not access production data or secrets, perform destructive production actions, merge, deploy, rewrite published Lovable-linked Git history, edit an applied migration, weaken tests, or treat hidden UI as authorization.

Keep `PROJECT_STATE.md`, `DECISIONS.md`, and `TASKS.md` current. Record actual commands, actual test results, remaining risks, unverified items, and rollback steps before claiming completion.
