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

## Mongezz Architecture Rules

1. Financial writes must go through approved RPCs.
2. Do not duplicate debt, custody, remaining, or margin formulas in UI screens.
3. Reuse functions from src/domain/finance/.
4. Returned orders must never appear as customer debt or courier custody.
5. Delivered is not settled.
6. One focused change per PR.
7. Never claim a fix is complete until it exists on main.
8. Never use production for destructive E2E tests.
9. Do not add public test cleanup RPCs.
10. No global formatting in functional PRs.

## Engineering process

Repository files are the source of truth. Read `PROJECT_STATE.md`, `DECISIONS.md`, and `TASKS.md` before material work.

Use `docs/governance/NAADF.md` for new projects or independently designed subsystems. Use `docs/governance/NAADF-CMF.md` for every change to the existing application. Complete and approve the applicable intake gate before implementation.

Follow:

- `docs/governance/DELIVERY_PROTOCOL.md`
- `docs/governance/SECURITY_BASELINE.md`
- `docs/governance/DATABASE_CHANGE_POLICY.md`
- `docs/governance/TESTING_POLICY.md`
- `docs/governance/REVIEW_PROTOCOL.md`

Do not access production data or secrets, perform destructive production actions, merge, deploy, rewrite published history, edit applied migrations, weaken tests, or rely on UI visibility as authorization. Record actual verification results, remaining risks, unverified items, and rollback steps before claiming completion.
