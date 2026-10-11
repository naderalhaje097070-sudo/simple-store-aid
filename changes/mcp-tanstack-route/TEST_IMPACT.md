# Test impact
Reuse prior strict oracle and real OAuth fixture. Local before-CI: shared oracle6tests and new acceptance5tests passed; node --check preload passed.
Dedicated CI: exact checkout/frozen bun lock; narrow tests/unit/mcp-issuer.test.ts preserves signature/issuer/audience tests; OS/runtime redirect containment; build unchanged app; actual HTTP metadata/auth/session/catalog/lifecycle/conflict tests; fingerprints/empty finance/source unchanged; cleanup and private log scans.
Required existing Quality workflow runs on candidate. Do not re-run PR60/61 historical broad integration suites; do not repeat direct-handler real-stack proof as a substitute.
Every failed attempt must remain linked with cause. If app bug: save reproduction and stop. Final observations/outcomes/review to be appended after CI.
