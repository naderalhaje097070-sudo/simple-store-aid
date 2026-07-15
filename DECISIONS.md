# Mongezz Decisions

This file records durable project decisions. Material changes require a new dated entry; do not silently rewrite established decisions.

## DEC-001 — Repository files are the source of truth

**Status:** Accepted  
**Date:** 2026-07-15

Project state, decisions, tasks, contracts, and verification evidence must be recorded in the repository. Conversation memory is not an authoritative project artifact.

## DEC-002 — NAADF and NAADF-CMF govern delivery

**Status:** Accepted  
**Date:** 2026-07-15

Use NAADF for new projects and NAADF-CMF for changes to Mongezz. Implementation does not begin before the required gates are documented and approved.

## DEC-003 — No automatic merge or deployment

**Status:** Accepted  
**Date:** 2026-07-15

Agents may create branches, commits, issues, and PRs when authorized. A human must explicitly approve merge, deployment, destructive operations, and Production data changes.

## DEC-004 — Published Git history is immutable

**Status:** Accepted  
**Date:** 2026-07-15

Because Lovable synchronizes repository history, do not force-push, rebase, amend, squash published commits, or otherwise rewrite history. Correct forward with new commits.

## DEC-005 — Financial state is server-owned

**Status:** Accepted  
**Date:** 2026-07-15

Financial writes and state transitions are enforced in approved server-side RPCs or database transactions. UI code must not be the source of truth for debt, custody, settlement, returns, or margin.

## DEC-006 — Delivery and settlement are separate states

**Status:** Accepted  
**Date:** 2026-07-15

A delivered order is not settled. Money collected by a courier remains courier custody until an authorized owner settlement records the transfer.

## DEC-007 — Database changes are forward-only

**Status:** Accepted  
**Date:** 2026-07-15

Never edit an applied migration. Use a new forward-only migration, document data and lock impact, and define rollback or compensating steps.

## DEC-008 — PR #17 is not an approved release candidate

**Status:** Accepted  
**Date:** 2026-07-15

PR #17 remains an implementation reference until the employee-account change completes NAADF-CMF baseline, impact, design, safety-net, independent review, and verification gates. It must not be merged automatically.
