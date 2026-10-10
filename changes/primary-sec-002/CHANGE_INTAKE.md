# PRIMARY-SEC-002 Change Intake

Date: 2026-10-10

## Request

Triage the remaining Critical and High dependency-audit records after PRIMARY-SEC-001, identify actual dependency chains and exploit conditions, apply compatible fixes where safe, and preserve evidence.

## Scope

In scope:
- Dependency lock corrections for remaining registry Critical/High advisories.
- Minimal `package.json` override/resolution policy needed to keep the corrected lock stable.
- Regression tests that fail if the protected dependency floors regress.
- Evidence records for audit delta, dependency chains, and verification commands.

Out of scope:
- Runtime feature changes.
- Database migrations or financial writes.
- Production data, secrets, deployment, or merge.
- Medium/Low advisory remediation beyond any incidental dependency updates.

## Source Baseline

Started from the PRIMARY-SEC-001 candidate tree, stacked on the current governance/security draft flow. Main remains unmodified.

## Acceptance

- Critical/High package/advisory records from `bun audit` are removed or explicitly classified as blocked.
- Native frozen install, typecheck, unit tests, build, changed-file lint, and diff check pass.
- Remaining audit findings are documented by severity and not described as accepted for release.

## Authorized Review Remediation

The owner's 2026-10-10 instruction authorizes resolving the recorded lock-generation
finding and diagnosing CI startup. Scope includes a generator-owned bounded lock,
removing unsupported resolution intents, preserving the current Lovable MCP version,
and moving the synthetic compatibility fixture into the existing CI unit-test path.
Risk remains dependency compatibility; no runtime feature, database, financial,
production or billing-setting change is part of this packet. Acceptance still needs
usable final-source hosted checks and independent final-candidate review.
