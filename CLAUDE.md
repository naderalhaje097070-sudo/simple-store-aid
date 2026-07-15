# Claude Operating Entry Point

All agents working on Mongezz must follow `AGENTS.md` as the primary operational contract.

Before changing code or data:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md`.
3. Read relevant entries in `DECISIONS.md` and `TASKS.md`.
4. Select the correct framework:
   - `docs/governance/NAADF.md` for a new standalone project.
   - `docs/governance/NAADF-CMF.md` for any change to Mongezz.
5. Stop at the required approval gates.

Additional constraints:

- Do not access production databases, production secrets, or real customer data.
- Do not merge or deploy automatically.
- Do not rewrite published Git history because the repository is synchronized with Lovable.
- Do not change financial rules, authorization contracts, database invariants, or API contracts without documenting the decision.
- Report failed and unverified checks explicitly.

This file is intentionally concise. Detailed rules are maintained under `docs/governance/` to avoid duplicated or conflicting policy text.
