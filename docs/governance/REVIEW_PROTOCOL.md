# Independent Review Protocol

Independent review is required for High-risk changes and for changes affecting money, authentication, authorization, RLS, tenant isolation, migrations, employee access, settlement, or irreversible data behavior.

## Reviewer posture

Review the implemented change against repository requirements and contracts, not against the author's explanation alone. Assume client inputs can be malicious, requests can be duplicated or concurrent, and partial failures can occur.

## Required questions

### Business rules

- Is the documented requirement implemented exactly?
- Is the rule centralized at the correct boundary?
- Are illegal transitions rejected?
- Are returns, debt, custody, payment, and settlement meanings preserved?

### Data and transactions

- Are transaction boundaries correct?
- Can partial execution leave inconsistent rows?
- Are exact money types used?
- Are constraints, indexes, and locks adequate?
- Can retry or concurrency duplicate a financial effect?

### Authentication and authorization

- Is identity verified server-side?
- Is access deny-by-default and least privilege?
- Are tenant, role, ownership, assignment, active status, and state checked?
- Can UI restrictions be bypassed through direct API, RPC, or table access?
- Are RLS, grants, and security-definer functions reviewed together?

### Contracts and compatibility

- Did an API, RPC, schema, event, state, or report contract change?
- Are callers and consumers updated?
- Is backward compatibility required and preserved?
- Is the migration order safe?

### Code quality

- Is the change the smallest correct solution?
- Is there hardcoded Production behavior, mock-only behavior, silent fallback, broad catch, dead code, or unnecessary abstraction?
- Are module boundaries and names clear?
- Is domain logic duplicated in UI or infrastructure?

### Verification and operations

- Do tests prove real behavior and negative paths?
- Are concurrency and idempotency covered where needed?
- Are logs safe and actionable?
- Is rollback or compensation executable?
- Are remaining risks and unverified items explicit?

## Finding format

Every finding contains:

- **Severity:** Critical / High / Medium / Low / Informational
- **File or contract**
- **Evidence**
- **Risk**
- **Required fix**
- **Verification method**

Critical and High findings block acceptance unless a human owner explicitly accepts the risk in `DECISIONS.md`.

## Review completion

The reviewer produces:

- Findings list
- Requirements coverage assessment
- Security assessment
- Database and migration assessment
- Test-evidence assessment
- Rollback assessment
- Recommendation: Approve / Request changes / Not verifiable

Review approval does not perform merge or deployment.
