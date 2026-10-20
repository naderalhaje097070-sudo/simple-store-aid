## Current repository authority — MONJEZ v2.2, 2026-10-10

The owner transferred the active repository to `naderalhaje097070-sudo/simple-store-aid`.
Verify this exact owner/repository, main, branch/head, open PRs and execution claims
before material work. The repository ID remains 1281463067. The earlier owner path
in preserved records below is historical identity, not a second active repository.
`naderalhaje0970-droid/mongezz` remains separate; do not move changes between repositories.

Read the top current blocks in PROJECT_STATE.md and TASKS.md, the current notice in
docs/PRIMARY_DELIVERY_PLAN.md, and execution index issue #55. Do not repeat completed
candidate work or treat unmerged changes as main/released. Historical billing or
runner failures must not override a later observed successful attempt on the same SHA.
Check status, run attempt and actual steps, then scope new checks to the current change.

One implementer owns each task; inspect the task's issue/PR claims before writing.
Routine isolated development, verification, documentation and draft PR preparation
are authorized. Protected merge, production deployment, destructive action, new cost,
core financial-contract change or security/governance bypass still requires owner approval.
No automatic merge/deployment and no published-history rewriting.

The original Lovable notice and accepted architecture/governance rules below remain
binding. Older active-repository/scheduling statements are superseded by this notice.

---

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

## Primary project execution — 2026-10-09

- Work only in `naderalhaje0970-droid/simple-store-aid` for active Mongezz delivery.
  Verify remote, base/head and target environment before material work.
- Read the current (top) PROJECT_STATE block and docs/PRIMARY_DELIVERY_PLAN.md.
  Historical state and the separate mongezz repository never select ONE NEXT.
- Search implementations, callers and tests before adding functions or policies;
  reuse approved domain logic and avoid duplicate finance implementations.
- Verify real locked APIs/schema; do not invent provider behavior or hide uncertainty
  with casts, any, silent error swallowing or weakened tests.
- Keep one outcome per batch; assign non-overlapping file ownership when agents
  are authorized. Separate sensitive implementation and adversarial review.
- Use independent expected financial values and preserve failed evidence.
  Failed/incomplete reads must not masquerade as zero or healthy finance.
- After two failed attempts at the same boundary without new evidence, diagnose
  rather than repeat patches. Do not repeat successful checks without a reason.
- Do not promote tests or approval from another repository/head/environment.
- Save actual source, changes, results, limitations, blocker and ONE NEXT before
  ending a batch. Routine authorized steps proceed without repeated permission.
- Written rules are not proof of CI enforcement. Record missing enforcement and
  actual check outcomes. Existing financial and release gates remain in force.

## Scoped security-review method — 2026-10-13

For security-sensitive changes, follow [SECURITY_REVIEW_METHOD](docs/governance/SECURITY_REVIEW_METHOD.md)
alongside the existing review and testing policies. Reuse the batch's coverage
ledger and evidence; distinguish source review, observed structure and runtime
proof. Check cross-boundary chains and disclose independent-review limits.
Scale review to the affected risk; do not restart historical suites or require
a fixed agent count. This method grants no extra test, data or release authority.
