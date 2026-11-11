# Integration PR check readiness — no branch-protection change yet

Status: **Implemented on an isolated branch; merge and settings NOT authorized.**
Base: `integration/g0-g1-reconcile-2026-10-18`, originally `e88a5cc17e787d87954794e7a5604e5fb98683e2`.
Owner action required to merge and, separately, to enable branch protection.

## Problem and scope

The integration branch currently allows direct writes. Before requiring checks on PRs
targeting this branch, each required GitHub Actions job must actually be emitted on those PRs.
Historically, the candidate gates ran on a push to integration but PR events targeted only
`main`. Required checks in that state can remain permanently Pending.

This change adds `integration/g0-g1-reconcile-2026-10-18` to `pull_request.branches`
for three workflows, without changing their underlying assertions, installed versions,
secrets, code, migrations, or production systems:

- `.github/workflows/release-finance.yml`: all nine financial matrix jobs, no path filter.
- `.github/workflows/integration-verification.yml`: `integrated-quality` and `audit`,
  no PR path filter; existing path-filtered push remains unchanged.
- `.github/workflows/b1-composition.yml`: `compatibility`, no PR path filter for
  either target. This deliberately expands coverage on docs-only PRs to prevent a missing
  required B1 status; existing path-filtered integration push remains unchanged.

`Quality` already has an unfiltered `pull_request` event and is not modified.
`trusted-release-gate` remains scoped to `main` (never require it on integration).

`tests/b7-ci-routing/contract.test.cjs` now requires both target branches on these three
workflows, rejects path filters for them, and retains the historical and main-only gates.
It has new negative controls that remove the integration branch or add a path filter.
These tests must pass on the candidate exact SHA before merge.

## Acceptance before enabling ruleset

1. Create a PR from this feature branch into **integration** and confirm all three
   workflows emit checks; the PR must also run Quality. Verify their actual names and
   GitHub App sources from this PR, rather than guessing contexts.
2. Confirm **all nine** `suite (collection|sale|journey|quantity, ...)` jobs succeeded,
   `integrated-quality`, `compatibility`, and `Quality/quality` succeeded. Record
   any inherited or infrastructure failures without relaxing tests.
3. Confirm no check name collision, especially `quality` and `audit` from other
   workflows. Treat these as advisory until unique contexts are proven.
4. Do not make any check required until its presence on a PR targeting integration is
   established. A checks-required ruleset should be enabled only **after** the routing
   change is merged with the owner's separate approval.
5. Open a disposable, non-sensitive PR into integration after the routing change lands,
   then confirm a failure actually blocks merge and that a legitimate successful PR can
   pass. Do not bypass or force-push.

## Proposed ruleset (owner approval required)

Target only `integration/g0-g1-reconcile-2026-10-18`:
- Require pull request before merging; initially zero formal approvals to avoid locking
  a single-maintainer repository, but retain the independent-review policy for high-risk work.
- Block deletions and force pushes; do not include a bypass list.
- Require status checks only after the above proof. Start with nine finance matrix
  contexts plus `integrated-quality` and `compatibility`; only add a Quality check if
  a uniquely sourced context is proven. Verify exact names in GitHub Settings.
- Consider `Require branches to be up to date` only after proving the merged-head
  semantics against a test PR; do not enable blindly.

## Known limits and operational impact

- Lovable has authored commits on `main`; no evidence that it pushes integration,
  but this is not an exhaustive provider-side verification.
- `naderalhaje0970-droid` has repository Write permission. Do not remove it without
  assessing account dependencies; branch protection is the intended access boundary.
- A PR to integration will now run additional full CI jobs. This may increase runner
  usage and expose existing failures, but must not be treated as permission to waive them.
- GitHub's required-check source selection, ruleset enforcement, and failure blocking
  cannot be verified from YAML alone.
- If CI routing is defective after an authorized merge, use a new reviewed revert PR;
  do not rewrite published history.

No branch protection, collaborator permission, merge, production SQL, or deployment
is performed by this preparation change.
