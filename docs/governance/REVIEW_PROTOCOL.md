# Independent Review Protocol

Independent review is required before a high-risk change is proposed for merge. The reviewer must not treat successful tests as proof that the product requirement or architecture is correct.

## Review questions

### Root cause and scope

- Is the root cause proven and addressed?
- Is the change the smallest correct change?
- Does the PR contain unrelated refactoring, formatting, dependency, or cleanup work?
- Are all assumptions explicit?

### Contracts and architecture

- Did an API, RPC, database, state, or authorization contract change?
- Are source-of-truth and state ownership clear?
- Are UI, domain/application, and infrastructure responsibilities separated?
- Is any business rule duplicated or implemented only in the UI?
- Is backward compatibility preserved or intentionally managed?

### Database and financial integrity

- Are transaction boundaries correct?
- Are constraints, indexes, grants, and RLS appropriate?
- Is the migration forward-only and tested through the full chain?
- Are retries, duplicate requests, concurrency, and partial failure safe?
- Could money, debt, inventory, or custody be posted twice or lost?
- Is rollback or compensation executable?

### Security

- Is authorization server-side and deny-by-default?
- Is tenant and assignment isolation preserved?
- Can a user bypass the UI through direct API, RPC, or table access?
- Is there IDOR, mass assignment, injection, role escalation, or account-lifecycle risk?
- Are logs and artifacts free of secrets and unnecessary personal data?

### Tests and evidence

- Do tests prove the real stored behavior?
- Are negative, cross-tenant, cross-employee, disabled-account, duplicate, retry, concurrency, and illegal-state scenarios covered where applicable?
- Were any tests weakened?
- Is every claimed command result supported by actual evidence?
- Are unverified items stated explicitly?

## Findings format

Record each finding as:

```text
Severity: Critical / High / Medium / Low
File or contract:
Evidence:
Risk:
Required fix:
Verification method:
```

Critical and High findings block merge. Medium findings require an explicit decision before merge. Low findings may be deferred only when recorded in `TASKS.md` or an issue.

## Final review outcome

Use one outcome:

- Approved for human merge.
- Changes required.
- Blocked pending missing evidence.

Review approval does not perform merge or deployment. Those actions remain explicit human decisions.

## Coverage, evidence and coordinated review

Apply [SECURITY_REVIEW_METHOD.md](SECURITY_REVIEW_METHOD.md) to the affected scope.
Reuse the existing batch packet for the coverage ledger and findings register;
record evidence levels, reachability limits and any cross-boundary exploit-chain
hypotheses. Reviewers must disclose what they reran and what they only inspected.
This supplements the questions and severity/merge rules above; it does not add
a mandatory whole-project audit or waive any existing acceptance gate.
