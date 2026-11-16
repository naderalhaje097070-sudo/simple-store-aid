# Merge delegation — standing owner decision (2026-11-16)

## The decision (owner's own words, 2026-11-16)
> «ألغيت شرط الموافقة اليدوية من GitHub وفعّلت Auto-Merge. أفوضك بالدمج الروتيني بعد نجاح الاختبارات والمراجعات المطلوبة، دون طلب موافقتي أو وسم gov-ok في كل مرة. حدّث الحوكمة بما يتوافق مع هذا القرار، واستمر وفق الخطة المعتمدة.»

In English: the owner removed the manual approval condition in GitHub, enabled auto-merge, and delegates **routine merges after the required tests and reviews pass**, with no per-PR approval request and no `gov-ok-<SHA>` label. This document is the governance record of that decision, and it takes precedence over older text in conflict with it. It does **not** widen anything beyond routine merges.

## Scope
- **Delegated (an agent may merge without asking):** a routine pull request into the integration branch `integration/g0-g1-reconcile-2026-10-18`. That includes product changes, bug fixes, tests, admitted dependency patches, CI maintenance that does not weaken a control, and financial or security fixes that meet the evidence below.
- **Not delegated; the owner still decides:**
  - any production action: DB apply or query, deploy, Publish, or secrets;
  - destructive actions;
  - new cost;
  - fundamental financial-contract choices;
  - security exceptions;
  - any change that **weakens** an acceptance control (removes or relaxes a test or assertion, lowers a required-control count, or removes a required check);
  - changes to this delegation itself;
  - merges into `main`. These are the release step of the approved C6/C7 plan and follow that plan's owner-approved scope.

## Conditions for a delegated merge (all of them, on the exact head SHA)
1. **Head binding:** the merge uses `expectedHeadSha` equal to the head that was verified. A newer push restarts verification.
2. **CI:** every check run on that head has `conclusion=success`. Nothing is pending, queued, failed, cancelled or `startup_failure`, and only the latest attempt counts. The base must not have moved since the checks ran, or the PR is updated and re-verified.
3. **Financial and security changes** (migrations, `FINANCIAL_CORE`, `service_role`):
   - release-finance 9/9, with catalog-guard `missing == []` and `failed == []`;
   - migrations preserved: no applied migration edited, and production-applied files byte-identical (md5);
   - negative controls for new guard rules.
4. **Reviews on that exact head:**
   - a Strix check run with `success` and no open findings;
   - a Codex receipt on that head with no unresolved findings;
   - 0 unresolved review threads;
   - every bot finding answered, either fixed or traced with a reply.
   For financial and security changes, the independent reviews must also have been requested and completed on the head that is merged.
5. **No weakening:** the diff removes no assertion or test and lowers no threshold. Otherwise the PR is outside the delegation.
6. **Record:** the merge commit message states the delegation and the evidence (head, check count, review receipts). `TASKS.md`/`PROJECT_STATE.md` are updated afterwards.

## Known gap (must be closed by rule, not by trust)
Verified on 2026-11-16 through the API:
- Ruleset `main-protection` (26759375) now has `required_status_checks: []`, so `trusted-release-gate` is no longer required on `main`.
- The integration branch has **no** protection.

Until a required check enforces the conditions above (GOV-AUTOMERGE-01), they are enforced only by the merging agent's own verification. For that reason:
- Native auto-merge is **not armed** on any PR, because with no required checks it would merge immediately.
- Agents merge explicitly, with `expectedHeadSha`, after verifying.

Owner action to close the gap:
- require integrated-quality, release-finance (9), quality, compatibility, audit and Strix as required checks on the integration branch;
- restore a required check on `main`.

## Rollback
The owner revokes or narrows this delegation in their own words. Agents then return to asking for every merge.
