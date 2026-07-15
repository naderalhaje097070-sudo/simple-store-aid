# Claude Operating Rules for Mongezz

`AGENTS.md` is the primary agent instruction file for this repository. Read it before any analysis or change.

## Required references

- `AGENTS.md`
- `PROJECT_STATE.md`
- `DECISIONS.md`
- `TASKS.md`
- `docs/governance/NAADF.md`
- `docs/governance/NAADF-CMF.md`

## Operating constraints

1. Treat repository files as the source of truth. Do not rely on prior chat context when the repository can answer the question.
2. Classify the work and identify the current NAADF or NAADF-CMF gate before editing.
3. Do not begin implementation before the required intake, baseline, impact, design, and safety-net work is approved.
4. Do not access Production, real secrets, or customer data.
5. Do not merge, deploy, force-push, rebase published commits, or perform destructive operations automatically.
6. Keep PRs focused and reviewable. Separate documentation, migrations, authorization, domain behavior, UI, and unrelated refactoring when they are independently reviewable.
7. Preserve Mongezz financial invariants, especially `Delivered != Settled`, returned-order behavior, exact money types, and RPC-controlled financial writes.
8. Update `PROJECT_STATE.md`, `DECISIONS.md`, and `TASKS.md` whenever the project state, a durable decision, or the active work plan changes.
9. Report actual commands, tests, failures, unverified items, risks, and rollback steps. Never state that work is complete based only on code generation.
