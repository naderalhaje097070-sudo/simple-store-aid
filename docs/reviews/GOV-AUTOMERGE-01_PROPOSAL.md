# GOV-AUTOMERGE-01 — conditional automatic merge: design proposal (for review, not active)

Status: **proposal**, prepared 2026-11-16 for review by ChatGPT and the owner. Nothing is enabled, and no ruleset, workflow on `main` or label is changed by this document.

Source: the revised owner direction on PR #77 (comments 6907770098, 6907942737 and 6907963406), and the owner's instruction of 2026-11-16 to follow it.

## 1. Facts this design relies on (verified, not assumed)
- **Current gate:** `release-gate-trusted.yml` runs on `pull_request_target` into `main`, from main's copy. It fetches the PR head as git objects only, and its token is read-only. `gate.py --governance` accepts acceptance-defining changes only with the label `gov-ok-<full head sha>`, whose latest event must be a direct owner `labeled` event.
  - Ungoverned prefixes: `src/`, `public/`, `supabase/migrations/`, `supabase/functions/`, `docs/`, top-level `*.md`.
  - `FINANCIAL_CORE` and the `service_role` markers are governed as well.
- **Ruleset 26759375 on `main`:** no bypass actors. It requires PRs with 0 approvals and the strict check `trusted-release-gate` only. `allow_auto_merge=true` was set by the owner.
- **`integration/g0-g1-reconcile-2026-10-18` has no protection.** A PR into it can be merged with red checks.
- **Actions incident:** the trusted runs on #77 (43097344210, 43098463569, 43098499782) have been queued with 0 jobs since 2026-11-11. Until GitHub Support resolves this, no PR into `main` can pass `trusted-release-gate`.
- **Shared identities:** agents use the linked owner identities. So an approval, comment or label made through those accounts does not prove a separate human act. The design must not rely on a native GitHub review as proof of independence.

## 2. Target policy
Classes are computed by the trusted base copy of the gate, from the changed paths.

| Class | Paths | Merge rule |
|---|---|---|
| **P** product | application paths that are not financial core, and `docs/` | automatic once the acceptance predicate holds |
| **F** financial or security | `FINANCIAL_CORE`, `supabase/migrations/`, files carrying the `service_role` markers | automatic once the predicate holds, with the stricter F evidence set |
| **G** acceptance-defining | workflows, `tests/`, `scripts/`, the gate, manifests (`package.json`, `bun.lock`, `bunfig.toml`, `vendor/`, `patches/`), `AGENTS.md`, `docs/governance/` | **owner decision kept**: the existing exact-head label, used only for these rare changes |

Owner decisions stay reserved, outside any merge automation, for:
- production deployment or a production database apply
- destructive actions
- spending
- fundamental financial-contract changes
- security exceptions

A merge into `integration` or `main` is never a production deployment.

## 3. Acceptance predicate: the new trusted check `trusted-acceptance`
- **How it runs:** a new workflow, from the **base copy** only, on `pull_request_target`.
  - It also re-evaluates on `check_suite`/`workflow_run` completion, `pull_request_review` and `issue_comment`.
  - Token: `contents: read`, `checks: read`, `pull-requests: read`.
  - No checkout or execution of PR code.
- **The check succeeds only if all of these hold on the exact `head.sha`:**
  1. **Head binding:** the head SHA equals the event's head, and the base is current.
  2. **Required evidence for the class:** read from a reviewed manifest in the base. Every listed check run has conclusion `success` on that SHA, and its provenance matches: GitHub Actions app id 15368, with the workflow file path taken from the base copy. If any check is missing, failed, cancelled, `startup_failure` or stale, the predicate fails. Queued or in-progress leaves it pending, never success.
     - P: quality, compatibility, integrated-quality, audit.
     - F: P plus release-finance 9/9, including the catalog guard with its required control count.
  3. **Independent review on that exact SHA:**
     - The Strix check run has `success`, from the Strix app id.
     - The latest Codex review-state marker has `code_review.commit_sha == head` and `has_unresolved_findings == false`.
     - Unresolved review threads = 0.
     - Graphify is advisory only, because its index is not on the PR base.
  4. **Class G:** additionally the existing `gov-ok-<head>` owner label, with the unchanged `owner_approved` logic.
- **Merge mechanism:** an agent enables native auto-merge only for a PR in class P or F. GitHub merges only when every required check is green. A new push changes the SHA, so no earlier success carries over.

## 4. Ruleset changes (owner admin action; the connector cannot do this)
1. `main` (26759375): add `trusted-acceptance` to the required checks, keep `trusted-release-gate`, keep strict mode, and add no bypass actors.
2. **A new ruleset on `integration/*`**, with the same two required checks and no bypass. Without it, auto-merge into integration has nothing to enforce.

## 5. Bootstrap and order
1. GitHub Support resolves the queued/no-jobs incident, and a fresh `trusted-release-gate` run starts and completes.
2. The PR introducing `trusted-acceptance` is itself class G: it needs the existing exact-head owner label **once**.
   - It must pass on an isolated draft candidate first, with the negative cases in §6.
   - The candidate code changes the same gate and tests as #77, so it is coordinated with #77 (financial-core scope, migration preservation).
   - #77 is not released unchanged.
3. The owner adds the ruleset requirements (§4).
4. Only after that may agents arm auto-merge.

## 6. Negative cases that must block (unit tests on recorded API fixtures)
- A required check is missing, failed, cancelled, `startup_failure`, or still queued.
- A check with the right name from the wrong app or the wrong workflow path.
- A success recorded on an older SHA, or a base that is not current.
- Strix is missing or failed; the Codex marker is on an older SHA or has unresolved findings; any review thread is unresolved.
- A class G change without the exact-head direct owner label, or with the label added through an app.
- A file renamed from G into P, or a new file outside the known prefixes, which defaults to G.
- A PR that edits the acceptance manifest or workflow cannot affect its own evaluation, because both come from the base.

## 7. Rollback
- Remove `trusted-acceptance` from the rulesets, or set `allow_auto_merge=false`; either restores the current label-only behaviour.
- Revert the PR that introduced the check.

## 8. Open questions for review
1. Is Strix + Codex + zero unresolved threads enough as "independent review" for class F? Or does class F into `main` (not integration) keep an owner decision until the C6/C7 production plan has run?
2. Should dependency manifests stay class G? They are acceptance-defining because they change what the tests execute.
3. Who arms auto-merge: an agent on request, or the trusted check itself through a separate, minimal write-scoped job? The latter needs `contents: write`/`pull-requests: write` in a privileged context, so the agent route is proposed.
