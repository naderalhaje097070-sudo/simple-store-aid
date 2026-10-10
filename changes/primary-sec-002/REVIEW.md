# PRIMARY-SEC-002 Source and Evidence Review

Date: 2026-10-10 (Africa/Tripoli).
Repository: `naderalhaje0970-droid/simple-store-aid`.
Reviewed PR: #53; base `13d81250122c890a98b0c94e4f07f2745bdb40ed`;
head `4a5dda42d6470ded52edfb667d582d04d2a28165`;
tree `f41ee57c3d31591824a4ccd0348790d46517f2de`.
Main re-read at `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`.

Outcome: **Changes required**. This review pass is separate from the original
implementation. It is not a GitHub approval, a review of later commits, or
permission to merge/deploy. Follow-up compatibility tests and documentation
added with this report still require final-candidate review.

## Findings

### SEC2-R1 - Missing hosted verification (High, acceptance blocker)

- File or contract: required final-source Quality evidence.
- Evidence: run `38034986903`, job `114163446036`, head above, completed failure,
  `runner_id: 0`, empty steps. No checkout, install or test step executed.
  The job-log endpoint returned 404 BlobNotFound. The connector does not expose
  the check-run annotation endpoints requested during diagnosis.
- Risk: local success cannot establish that hosted checks ran against the
  candidate. Empty steps do not prove a billing, quota or application defect.
- Required fix: inspect the run's actual startup annotation/account Actions
  eligibility and resolve the demonstrated cause, then execute the required
  workflow on the final candidate. No evidence waiver or speculative YAML fix.
- Verification: record final SHA, real executed steps/logs and check conclusions.

### SEC2-R2 - Manual generated-lock edits (Medium, disposition required)

- File or contract: `bun.lock`, DEC-017; generated-file ownership in
  `docs/governance/DELIVERY_PROTOCOL.md` and the primary delivery plan.
- Evidence: implementation recorded manual replacement of four brace-expansion
  entries because Bun 1.3.14 did not apply nested override rules. Frozen install
  validates the supplied lock; it does not prove the original generation method.
- Review experiment: Bun 1.3.14 `install --lockfile-only --ignore-scripts` and
  the same command with `--force` re-save a copy of the existing lock unchanged.
  Generation from only the manifest/config produces the exact same four
  brace-expansion entries, including metadata and integrity. However, it produces
  a broader 909-package graph versus the candidate's 989-package graph. That graph
  was not adopted, installed, audited or accepted as the candidate.
- Risk: an exception based on hand-editing could become the next agent's normal
  dependency-update method. This review did not find corrupted brace entries;
  independent generation corroborates their contents.
- Required fix: establish and record a bounded, generator-owned dependency update
  procedure, preserving compatible major lines and the existing guard. Do not
  introduce the broad clean graph without reviewing its full impact. Do not
  describe unsupported path rules as enforced security policy.
- Verification: capture generator command/version and bounded graph diff, then
  frozen install, audit, guard, compatibility checks and required quality checks.

### SEC2-R3 - Stale next-step instruction (Low, corrected)

- File: top `PROJECT_STATE.md` block and current `TASKS.md` queue.
- Evidence: the current state still instructed creating the already-open PR #53;
  the task queue selected ENV work while security review/CI were unresolved.
- Risk: agents could repeat packaging or bypass the current acceptance work.
- Fix: record PR #53, this review outcome and security-remediation ONE NEXT.
- Verification: the two current blocks now agree; historical records remain intact.

## Source Identity

Local Git blob hashes matched the reviewed remote tree:

| File | Git blob SHA |
| --- | --- |
| package.json | `299041193cbb6250ce9f034ee088601ff98176c0` |
| bun.lock | `41beedae06bc6299a33e47f8ee63f6ca3d2b4648` |
| tests/unit/dependency-security.test.ts | `1f84656009a1ff6c81f4f3a59491e9f3676e7a5b` |

## Additional Runtime Evidence

`review-mcp-compatibility.test.ts` uses synthetic tools and in-process Requests.
It imports the actual installed Lovable adapter, SDK and Zod. No project tools,
database, production credentials or financial writes are used.

Four checks passed: initialize; list/invoke a Zod tool; invalid arguments cannot
invoke the handler; a protected fixture rejects a missing bearer. This does not
prove positive JWT verification, project-tool authorization or tenant isolation.
The fixture initially had import-path and auth-helper mistakes; the retained
auth-helper failure is a test-fixture defect, not a product failure.

Reproduction command from the repository:

```sh
bun test changes/primary-sec-002/review-mcp-compatibility.test.ts
```

Local diagnostic evidence is under `../sec-evidence/`: `review-refresh.log`,
`review-force-refresh.log`, `review-clean-generation.log`,
`review-mcp-fixture-error.log`, `review-mcp-persisted.log`, `review-mcp-lint.log`.
The persisted test passed 4/4 with 8 expectations; its lint passed.
Running it together with `tests/unit` passed 44/44 with 94 expectations
(`review-combined-tests.log`); `git diff --check` also passed.

## Unchanged Acceptance Limits

- Earlier typecheck/build/unit results remain historical command evidence for the
  reviewed source; they are not a hosted result or proof of financial correctness.
- Previous full-lint and PR52/CI/toolchain blockers remain open. Quality uses Bun
  1.2.14 and does not pin Node. No workflow change is part of this review.
- The recorded audit has 11 Moderate and 5 Low findings; none are release-accepted.
- Financial writes, migration chain, auth/tenant isolation, recovery and pilot
  acceptance remain pending. The financial environment gate was not advanced.
- Rollback for this review-only follow-up: close the draft or add a revert of
  the review/test/doc additions. Do not rewrite Lovable-linked history or revert
  production to vulnerable dependencies.

ONE NEXT: resolve SEC2-R2 through a bounded generator-owned update and SEC2-R1
through usable hosted evidence; review the final candidate before ENV acceptance.
