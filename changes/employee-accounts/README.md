# Employee Accounts Change Record

This directory is the repository source of truth for the Employee Accounts, Assigned Orders, and Personal Custody change described by issue #16.

## Current gate

NAADF-CMF — Change Gate 1: Baseline and Reproduction.

## Gate 1 documents

- `CHANGE_GATE_1_BASELINE.md` — gate scope, evidence, findings, and exit criteria.
- `CURRENT_BEHAVIOR.md` — behavior verified on `main` before employee-account implementation.
- `EXPECTED_BEHAVIOR.md` — normalized product expectations from issue #16.
- `REPRODUCTION_AND_EVIDENCE.md` — PR #17 verification state and reproduction procedures.
- `PR17_SCOPE_MAP.md` — affected areas and decomposition evidence.

## Boundaries

- PR #17 is evidence and an implementation prototype, not an approved release candidate.
- No feature code, migration, RLS, RPC, dependency, or production change is authorized by this gate.
- Change Gate 2 may begin only after this baseline is reviewed and explicitly approved.
