# Security Review Method — MONJEZ

Owner-requested addition, 2026-10-13 (Africa/Tripoli). This method supplements
[REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md), [TESTING_POLICY.md](TESTING_POLICY.md)
and the existing NAADF-CMF gates. It does not replace the delivery plan or expand
a task's authorized environment, data, operations or release authority.

## Purpose and proportional use

Use explicit coverage and reproducible evidence to find meaningful authorization,
tenant-isolation and financial-integrity defects. Model reputation, agent count,
files read, test count and social-media benchmark percentages are not security
acceptance criteria.

Apply the method to the affected boundary of a security-sensitive batch. Reuse
the batch's existing source map, catalog, tests, findings and evidence links.
Keep one coverage ledger in its existing packet; link to it rather than copying
it into several reports. A small fix does not require a new whole-project audit,
a new model, a fixed number of agents or new approval for already-authorized work.

## 1. Pin scope and the tested source

Before review, identify repository, base/head SHA, applicable contract, permitted
environment and operations, and the issue claim/implementer. Inventory actual
entry points and their downstream dependencies. In MONJEZ these may include
REST, RPC, the Nitro/TanStack MCP route, database grants/RLS/definer functions,
background jobs and external callbacks where present in the affected scope.

Record exclusions and unverified surfaces. A successful test of one entry point
must not be promoted to success on another. A draft stack is not the deployed
application. At release-candidate review, reconcile applicable findings and tests
on one integrated candidate, including source and environment differences.

## 2. Maintain a coverage ledger

Each in-scope row describes a security decision, not merely a file opened:

| ID | Actor and account state | Operation / entry point | Resource owner / tenant | Expected allow/deny and data invariant | Source paths / SHA | Evidence level and result | Test or receipt | Gap / disposition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TEMPLATE | Role + active/closed/etc. | Real route or function | Own / other tenant | Contract-derived expectation | Pinned references | Not assessed | None | Assign or explain exclusion |

Use evidence levels: not assessed, source-reviewed, structure-observed, or
runtime-tested. Separately record the result: pass, fail, inconclusive, or not run.
Missing or failed setup is not a pass. A blank result or an empty data response
does not prove unauthorized access was prevented.

For access-denial tests, establish legitimate success before the transition and
an unaffected positive control after it. Record the reason for denial; expiry,
blanket denial, timeout or HTTP500 must not substitute for the intended protection.
Use populated synthetic data only when its fixture boundary is already authorized.
Empty-table tests do not establish preservation or cross-tenant isolation of
nonempty financial history.

Coverage counts require a named inventory and denominator. "12 of 15 in-scope
authorization cases runtime-tested" is a limited measurement; it is not a
percentage of all vulnerabilities found. Keep source, structural and runtime
coverage separate. Record critical uncovered paths even when file coverage is high.

## 3. Split review by risk when useful

Possible review responsibilities are identity/session authorization, database
privileges and tenant isolation, financial business logic, and evidence validation.
These are responsibilities, not a requirement to launch four agents.

Use subagents only when permitted by the current task or applicable instructions.
Assign each a non-overlapping question, bounded source/dependency map, exact SHA,
available evidence, expected output and stopping condition. Read-only independent
reviews may run in parallel when their inputs are stable. One implementing owner
controls each change; do not let parallel agents rewrite the same files or shared
test database. Dependent investigations remain sequential.

A review independent from implementation checks original source and evidence,
not only the implementer's summary. Disclose reviewer identity, independence,
source SHA, commands actually rerun, recorded results replayed, and any live
environment not rerun. A second agent is not evidence of a second live test or
human release approval; agents may share blind spots.

## 4. Keep a finding register with honest evidence

Use the existing severity rules in REVIEW_PROTOCOL.md. Extend each finding with:

- Stable finding ID and affected contract/source references.
- Claim status: suspected, confirmed within stated scope, disproved, or unresolved.
- Preconditions and reachable entry point, or explicit unknown reachability.
- Reproduction command/test and actual versus expected result.
- Proven impact separated from plausible or untested impact.
- Required fix, regression test, current disposition and remaining limitation.
- Exact source/environment/artifact and independent review evidence.

A confirmed excessive grant may be recorded without running a destructive
statement. That does not prove a remote exploit or production compromise.
Conversely, unknown reachability does not erase a verified privilege defect.
Do not execute destructive actions merely to upgrade an evidence label.

For a fix, preserve the prior failure where feasible and demonstrate the changed
behavior plus a legitimate positive control. Use existing tests and safe tools;
do not weaken assertions, manufacture exploit results or accept generic failures.
Deduplicate related reports by their shared root cause without discarding
distinct affected paths.

## 5. Review cross-boundary exploit chains

After individual reviews, the lead checks whether findings compose across trust
boundaries. Record each candidate chain as:
entry point -> prerequisite -> boundary crossed -> next capability -> impact.

Reference evidence for every link and state missing links. Reachable findings
may compose; two suspected weaknesses are not automatically a proven exploit.
Use an isolated proof only within the authorized test scope. Mark static-only
chain reasoning as a hypothesis. Resolve contradictory agent results before
drawing a combined impact conclusion.

Review chains touching the current change and previously recorded adjacent risks.
Do not launch an unbounded attack search after every small fix.

## 6. Close the batch and continue delivery

Stop when its acceptance criteria and independent-review requirements are met,
or when a specific blocker prevents them. Report residual risks and one next task.
Reuse unchanged evidence with explicit provenance; rerun only for changed
dependencies, a concrete unresolved risk, or a required gate.

Critical/High findings and Medium dispositions retain the existing merge rules.
Policy text is not CI enforcement. Tests passed on a runnable SHA and a later
documentation-only SHA must be distinguished. Skipped/pending is not green.
No automatic merge, deployment, production access, financial-policy change or
new cost is authorized by this method.

Adoption is prospective and proportional: the current SEC-TRUNCATE-01 worker may
reference its before/after privilege matrix as the coverage ledger and add missing
evidence labels at handoff. This does not restart its completed tests, change its
scope or close owner-retention/financial/release gates.

## Sources and limitations

- [OWASP Authorization Testing Automation](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Testing_Automation_Cheat_Sheet.html):
  roles, features and data form an authorization matrix linked to integration tests.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system):
  bounded task delegation and coordination; a research-system account, not proof
  of penetration-testing recall or a MONJEZ security certification.

Sources consulted 2026-10-13. No claimed 40%/90% vulnerability-detection rate or
model ranking from the supplied social-media post is adopted.
