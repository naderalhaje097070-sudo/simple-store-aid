# GOV-AUTOMERGE-01 — conditional automatic merge: design proposal v2 (for review, not active)

Status: **proposal v2**, 2026-11-16.
- Revises v1 (commit 1405685) against the independent review on PR #77, comment 6924366221 (P1×4, P2×1).
- Nothing is enabled. No ruleset, label, workflow on `main` or PR state is changed by this document.
- Owner direction: no repetitive owner action for routine work. Owner decisions are kept only for the reserved list in §2.

## 1. Facts this design relies on (verified, not assumed)
- **release-finance tests the merge ref, integrated-quality tests the PR head.** release-finance checks out the default `pull_request` ref, which is the merge commit (`github.sha`). integrated-quality checks out `github.event.pull_request.head.sha`. Both report check runs on the head SHA's PR. A check's name alone therefore does not say *which tree* was tested (review P1.1).
- **The trusted gate today:** `release-gate-trusted.yml` runs on `pull_request_target` into `main` only. It uses main's copy of `gate.py`, and needs an exact-head owner label for acceptance-defining paths. That set includes `FINANCIAL_CORE` and migrations, which is why routine F work still needs a label today.
- **Migration ordering:** `verify_migrations` rejects a new migration older than the base's newest one. Integration carries `20261107214500`, older than its `20261110*` migrations, and that is legitimate (production ledger). Reusing the main ordering rule on integration would reject #92-like PRs (review P1.3).
- **Rulesets:** ruleset 26759375 on `main` has no bypass actors, 0 approvals and a strict `trusted-release-gate`. The integration branch is unprotected. `allow_auto_merge=true`.
- **Actions incident:** the trusted runs on #77 have been queued with 0 jobs since 2026-11-11.
- **Shared identities:** agents act through the owner's linked identities. Neither a GitHub review, a comment, a label nor an actor string proves a separate human act.
- **Events:** workflows triggered by `workflow_run`, `check_suite` or `issue_comment` run with default-branch context. GitHub also does not deliver `check_suite` events for suites created by GitHub Actions. A read-only job on those events cannot by itself publish a required check on the candidate SHA (review P1.1).

## 2. Classes (computed by the trusted base copy; a mixed PR takes the highest class; unknown fails closed)
| Class | Content | Merge |
|---|---|---|
| **P** product | `src/`, `public/`, `supabase/functions/`, `docs/` (except `docs/governance/`) | automatic |
| **T** additive tests | new test files, and additions to existing test files that remove or relax no assertion (see §4.3) | automatic |
| **D** admitted dependency delta | `package.json` and `bun.lock` changes admitted by a per-delta verifier (the `sec-dep-20261116` pattern: exact pins and rows, byte rebuild, release-age and vendor unchanged), with `audit` green | automatic |
| **F** financial or security | `FINANCIAL_CORE`, `supabase/migrations/`, `service_role` markers | automatic **into integration** with F evidence (§3, §5); into `main` only through C6/C7 |
| **G** acceptance policy | trusted workflows (`release-gate-trusted.yml`, `trusted-acceptance.yml`), the acceptance manifest, `gate.py`/`test_gate.py`, catalog-guard rule removal or a lowered required-control count, removed or relaxed test assertions, dependency **policy** (`bunfig.toml`, existing admission verifiers), `AGENTS.md` and `docs/governance/` authorization rules | owner decision (exact-head label, as today) |

**Owner decisions reserved outside any merge automation:**
- production deployment or apply
- destructive actions
- spending
- fundamental financial-contract choices
- security exceptions
- any G change

## 3. Evidence binding (answers P1.1)
1. **Tree identity:** every evidence item records `{tested_tree_sha, head_sha, base_sha, workflow_path, workflow_id, run_id, run_attempt, job_name, conclusion}`.
   - Acceptance requires `head_sha` equal to the PR head and `base_sha` equal to the current base tip.
   - `tested_tree_sha` must be either the head or the merge of exactly that head and base. Each workflow's checkout ref is declared in the base manifest.
   - Only the **latest attempt** of each run counts.
2. **Receipts, not names:** each required workflow on the trusted list emits a small machine receipt with the fields above as a run artifact.
   - The evaluator downloads receipts through the API using a read-only token, and cross-checks them against the run's own API metadata: workflow path from the API, not from the receipt; app id 15368; event; head SHA.
   - A candidate-edited workflow cannot forge a pass: the trusted list and the expected job set come from the base, and a workflow file that differs from the base copy makes the PR class G.
3. **Publishing on the exact SHA:** a minimal **trusted publisher** job.
   - It runs on `workflow_run` (completed) for an **explicit allowlist** of triggering workflows only, and never for itself, so it cannot recurse.
   - It also runs on `pull_request_target` (synchronize/opened/reopened) and on a schedule, to catch missed events.
   - It runs base-branch code only and never checks out or executes candidate code.
   - It holds `checks: write` and nothing else, and creates or updates the check run `trusted-acceptance` on the PR **head SHA** through the Checks API.
   - Third-party reviews (Strix, Codex) are read by polling on those triggers, because their events don't reliably reach Actions.
4. **Re-evaluation:** a new head or a base update makes the previous `trusted-acceptance` stale. Strict "up to date" in the ruleset forces a re-run against the new base.
5. **Proof required before activation:** run on isolated draft PRs, not fixtures alone, and show the check attaching to the exact head SHA in these cases:
   - pass;
   - missing check;
   - failed check;
   - stale attempt;
   - base moved;
   - spoofed workflow.

## 4. Classification and trust boundary (answers P1.2)
1. The class is computed from the base copy over the PR diff. Renames count as delete plus add, and paths outside known prefixes default to G.
2. **The legacy gate changes with it:** the trusted `gate.py` stops requiring the label for F and T, and keeps it for G only. Migration integrity stays mandatory: base migrations are preserved byte-for-byte (§5).
3. **What counts as "additive" for T:** for each modified existing test file, the base copy's assertions must still be present.
   - Checked by a structural diff: no deleted `assert`/`expect`/`deny`/`check` lines, and no lowered numeric thresholds.
   - A required-control count in a workflow may only stay equal or rise.
   - Anything else is G.
4. **Negative tests for the evaluator itself**, run on recorded fixtures and on isolated PRs:
   - a #92-like change (migration plus catalog-guard rule) classed F and accepted with F evidence;
   - a #93-like change (dependency delta plus a new verifier) classed D/T, with the new verifier admitted only as an addition;
   - a test weakening (deleted assert, lowered `len(required)`) classed G;
   - a spoofed workflow (edited `release-finance.yml` posting green) classed G and rejected;
   - unknown paths classed G;
   - a stale attempt rejected;
   - the wrong tree SHA rejected.

## 5. Integration base and rollout (answers P1.3)
1. **Two migration policies:**
   - **Integration (append-only):** every base migration must be preserved by path and bytes. New migrations are recorded with their md5, and any timestamp is allowed. An already-applied production migration such as `20261107214500` is admitted by md5 match against a reviewed list, never by a generic legacy exception.
   - **Main (canonical order):** unchanged ordering rule. The release-order constraint stays as documented in C6C7_PLAN §2: `20261107214500` enters `main` with, or before, the `20261110*` migrations.
2. **F evidence (into integration):** release-finance 9/9 plus the catalog-guard receipt (`controls == required`, `missing == []`, `failed == []`), together with the §6 review evidence.
3. **Consistency:** the same evaluator code runs for both bases. The base manifest selects the migration policy, and **both** rulesets require `trusted-acceptance` before auto-merge is armed anywhere. No unprotected gap during rollout: the integration ruleset is installed first, with `trusted-acceptance` required, in **report-only** mode for a trial period during which agents still merge manually after reading it.
4. **Bootstrap:**
   1. The Actions queued/no-jobs incident is resolved.
   2. The evaluator PR, class G, passes on isolated drafts.
   3. The owner gives the exact-head label once.
   4. The owner adds the rulesets.
   5. The ruleset and publisher provenance are verified.
   6. Only then are merges armed, one PR at a time.

## 6. Review validity (answers P1.4)
1. **Authenticated reviewer receipts:**
   - Strix: a check run from the Strix app id with `conclusion=success` on the exact head, plus the latest Strix summary for that head reporting no open findings.
   - Codex: a review or receipt from the Codex app id on the exact head with `has_unresolved_findings=false`. The app id is verified through the API, not trusted from a text marker.
   - **No unresolved findings**, not just resolved threads: every thread on the head must be resolved, *and* every bot finding must be closed with a reply that references a commit or a reason.
2. **Necessary, not sufficient, for F:** F also requires:
   - negative behavioural tests for the change, such as a red-then-green catalog-guard rule or negative controls;
   - an **independent review** by a reviewer other than the implementing agent, as a recorded review comment on the exact head (like the ChatGPT reviews on #90 and #77). The author is never its own reviewer. With shared identities, independence is established by the reviewer process and its recorded receipt, not by account.
3. **Scope:**
   - F into integration may be automated once §3–§5 are demonstrated.
   - F into `main` stays under C6/C7 and its separately approved scope.
   - Fundamental financial-contract choices stay owner decisions.

## 7. Rollback (answers P2)
Disabling auto-merge alone is **not** a rollback: it doesn't restore label checks and doesn't stop direct merges. The procedure:
1. **Freeze:** set `trusted-acceptance` to fail closed through a base-manifest flag, or remove merge eligibility.
2. **Disarm** every pending auto-merge, by listing open PRs with `auto_merge != null`.
3. **Restore** the previous gate and ruleset configuration from the recorded snapshot.
4. **Verify** the state: rules, required checks, no armed PRs.
5. **Resume.**

None of this implies any release or deployment.

## 8. Open items for the owner
1. Approve the class split in §2, especially T and D as automatic.
2. Accept the report-only trial period on integration before arming.
3. Add the two rulesets when the evaluator is ready. This needs an admin action the connector cannot perform.
