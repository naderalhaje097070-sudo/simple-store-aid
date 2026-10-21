# DEP-20261021 — current general merge blocker

Observed on executable117f59289a01c56aeb764be27acfbb45663ec439, Integrated G0 run39568502010 attempt1, audit job119116554257. Actual supported full audit exits1:11 package/advisory entries,8 distinct advisory URLs;3 distinct High and5 Moderate. This is separate from the known A protected-manifest failure in quality job119116554749. Frozen compatibility run39568502102 passes76 unit tests/typecheck/full lint/original wire/build/tracked-generation invariance; it does not override the audit.

Package/lock and all prior346 protected blobs are exact from B2. Locked versions: @modelcontextprotocol/sdk1.31.0, hono4.13.7, launch-editor2.14.1, vite8.0.16. The package-version matches are confirmed by the current audit; application exploit reachability has not been established for every advisory. Source-only rg of src/config/vite found no taskStore, maxToolInputElements, serveStatic or launch-editor token; wrappers/transitive libraries are not covered by that negative search and no exemption is claimed.

| Advisory | Reported package(s) | Reported severity | Reported title |
|---|---|---|---|
| GHSA-22jm-h49p-29qw | @modelcontextprotocol/sdk | high | MCP TypeScript SDK: Experimental tasks were not tied to the session that created them |
| GHSA-6prh-2h8m-c8cw | @modelcontextprotocol/sdk | moderate | MCP TypeScript client SDK: HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies |
| GHSA-46jr-4wx8-v453 | @modelcontextprotocol/sdk | high | MCP TypeScript SDK: One HTTP request within the default size limit could exhaust server memory during validation |
| GHSA-rvq5-wwqv-78pq | @modelcontextprotocol/sdk | moderate | MCP TypeScript SDK: Server bearer authentication accepted tokens issued for another service |
| GHSA-5r4p-p66f-jhc7 | hono | moderate | Hono: `serveStatic` decodes the request path a second time, leading to bypass of middleware on static paths |
| GHSA-698v-4r3x-3vcv | launch-editor, vite | moderate | launch-editor: escapeCmdArgs() omits % escaping on Windows |
| GHSA-r825-w8mm-5pxw | launch-editor, vite | moderate | launch-editor: Editor CLI flag misinterpretation causing arbitrary command execution for some editors |
| GHSA-587h-7wmj-h5pm | launch-editor, vite | high | launch-editor: `fs.existsSync()` existence check can be bypassed on Windows |

Primary advisory pages reviewed21Oct: GitHub GHSA-22jm-h49p-29qw (shared experimental taskStore precondition; patched1.32.0), GHSA-46jr-4wx8-v453 (request validation memory exhaustion; upgrade1.32.0 plus explicit maxToolInputElements, upgrade alone does not enable a limit), GHSA-5r4p-p66f-jhc7 (serveStatic middleware decode precondition; patched4.13.11) and GHSA-587h-7wmj-h5pm (Windows launch-editor path check; patched2.14.2, appropriate Vite lines include8.1.6). The other four entries are preserved as auditor-reported findings, not independently reproduced exploits. Advisory contents and downstream compatibility must be reread when undertaking remediation; these are repair starting points, not an applied upgrade plan.

Disposition: unresolved High general release/merge blocker. No B merge, RC acceptance, waiver or dependency upgrade is included in AC-02. Canonical ONE NEXT remains B4 / APP-02; the implementer must resolve current audit findings and retain existing protected A guards before B5/B6 final candidate acceptance. Owner: current implementation stream; track in #55/#70 and TASKS. This issue does not imply AC-02 introduced vulnerable code, and B3 runtime success does not remove it. Preserve exact source and new audit after repair; do not suppress the audit or weaken A identity gates.

Evidence: raw final-audit.json, raw full-audit ZIP and actual G0 audit/quality job logs in this packet's evidence directory. Local advisor output is independent:45 performance warnings (43 auth_rls_initplan,2 multiple_permissive_policies), not a clean-advisor result; unchanged policy/function catalog proves these definitions were not altered by B3.
