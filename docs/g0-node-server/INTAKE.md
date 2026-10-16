# G0-NODE-SERVER-01 intake

Owner explicitly authorizes this bounded security batch on existing Draft PR72,
starting `5cbf198d88b0f091a30371676fb09abf92903dc8`. This satisfies the CMF intake
approval for this scope. Canonical repository is naderalhaje097070-sudo/simple-store-aid;
historical owner names do not select a different repository. Claim #55/6222380561.

Goal: remove GHSA-frvp-7c67-39w9 from every resolved adapter copy with the
smallest officially available compatible update. Risk: moderate, transitive HTTP
adapter and Windows static authorization boundary. First prove published 1.x;
registry errors alone cannot prove absence. Only if unavailable, the owner permits
2.0.5 after official fix, locked SDK range, engines and compatibility review.
Stop if SDK/application changes are necessary. No direct dependency is needed.

Allowed: paired constraints, generator-owned complete lock, security guard,
focused offline fixtures, CI and evidence. Preserve Hono, qs, DOMPurify, Babel,
esbuild and all other packages. No lint cleanup, financial/schema/app change,
production, merge, deploy or live G1. Independent review and #55/#70 handoff are
required, followed by a planning stop. G0 acceptance remains separate.

Blocking facts before adoption: actual npm availability and tarball integrity,
minimal version and parent compatibility, complete generated graph, actual
Windows expected-red/patched behavior. Linux alone cannot prove this defect.
Known facts: lock has adapter 1.19.14, SDK 1.31.0 declares ^1.19.9 || ^2.0.5;
the official reviewed advisory identifies 1.19.15 and 2.0.5 as fixed. An initial
local registry HTTP403 and missing GitHub tag are inconclusive, not absence.

Acceptance: frozen Bun1.2.14, whole-graph invariance, all-copy guard with negative
controls, native Windows dummy-file prefix protection, real locked adapter/SDK
loopback HTTP and errors, existing MCP tests, typecheck, both approved builds,
Quality and full supported audit with real exit and residual records. Preserve
failures. Library reproduction is not proof the application is exploitable.
Final-source identity reconciliation and affected G1 rerun remain prerequisites
to integration acceptance; historical G1 evidence belongs to its original lock.
