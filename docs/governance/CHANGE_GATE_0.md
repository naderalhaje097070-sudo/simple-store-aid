# Change Gate 0 — Governance Bootstrap

Status: Approved

## Work mode

Existing Project Change

## Change type

- Governance and engineering process change.
- Documentation change.

## Risk level

Medium for the documentation change itself; High for the employee-account feature that this governance will control.

## Change goal

Make NAADF and NAADF-CMF the repository-maintained engineering process for Mongezz and establish project-state, decision, task, delivery, security, database, testing, and independent-review records.

## In scope

- Governance documentation.
- Agent and tool guidance links.
- Current project state.
- Current decisions and governed task plan.

## Out of scope

- Feature code.
- Database schema or data changes.
- Migrations.
- Dependencies.
- CI behavior changes.
- Production access.
- Merge or deployment.

## Owner

Nader — product and repository owner.

## Expected outcome

A documentation-only pull request that can be reviewed and merged by a human before the Employee Accounts change proceeds to Change Gate 1.

## Explicit assumptions

- `main` is the approved baseline.
- Pull request #17 remains open and unmerged.
- Published Lovable-linked Git history will not be rewritten.
- No automatic merge or deploy is permitted.
